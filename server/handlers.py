import asyncio
import logging

from server.config import ADMIN_IPS
from server.helpers import (
    Message,
    broadcast_message,
    find_client,
    is_nickname_taken,
    is_valid_nickname,
    write,
)
from server.types import Client
from server.variables import bans, clients


async def handle_identify(writer: asyncio.StreamWriter, message: Message):
    if not message.has_exact_args(1):
        return

    if writer in clients:
        await write("IDENTITY_ALREADY_SET", writer)
        return

    nickname: str = message.args[0]

    if not is_valid_nickname(nickname):
        await write(f"IDENTITY_INVALID|{nickname}", writer)
        return

    if is_nickname_taken(nickname):
        await write(f"IDENTITY_TAKEN|{nickname}", writer)
        return

    ip: str = writer.get_extra_info("peername")[0]
    clients[writer] = Client(nickname, writer, admin=True if ip in ADMIN_IPS else False)

    logging.debug(f"{ip} {clients[writer]}")
    await broadcast_message(f"USER_JOIN|{nickname}")


async def handle_message(writer: asyncio.StreamWriter, message: Message):
    if not message.has_exact_args(1):
        return

    if writer not in clients:
        await write("IDENTITY_NOT_SET", writer)
        return

    content: str = message.args[0]
    await broadcast_message(f"INCOMING_MESSAGE|{clients[writer].nickname}|{content}")


async def handle_kick(writer: asyncio.StreamWriter, message: Message):
    if not message.has_exact_args(1):
        return

    if writer not in clients:
        await write("IDENTITY_NOT_SET", writer)
        return

    client = clients[writer]

    if not client.admin:
        await write("UNAUTHORIZED", writer)
        return

    target_nick = message.args[0]
    target_client = find_client(target_nick)

    if not target_client:
        await write(f"CLIENT_NOT_FOUND|{target_nick}", writer)
        return

    if target_client.admin:
        await write("PROTECTED_CLIENT", writer)
        return

    await target_client.close()
    await write(f"CLIENT_KICKED|{target_nick}", writer)


async def handle_ban(writer: asyncio.StreamWriter, message: Message):
    if not message.has_exact_args(2):
        return

    if writer not in clients:
        await write("IDENTITY_NOT_SET", writer)
        return

    client = clients[writer]

    if not client.admin:
        await write("UNAUTHORIZED", writer)
        return

    target_nick = message.args[0]
    target_client = find_client(target_nick)

    if not target_client:
        await write(f"CLIENT_NOT_FOUND|{target_nick}", writer)
        return

    if target_client.admin:
        await write("PROTECTED_CLIENT", writer)
        return

    ip = target_client.writer.get_extra_info("peername")[0]
    bans.add(ip)

    await target_client.close()
    await broadcast_message(f"CLIENT_BANNED|{target_nick}|{message.args[1]}")
