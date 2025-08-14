import asyncio
import re
from typing import Optional

from server.types import Client, Message
from server.variables import clients


async def convert_to_message(data: bytes) -> Optional[Message]:
    message: str = data.decode().strip()
    if not message:
        return None

    parts: list[str] = message.split("|")
    if not parts:
        return None

    type: str = parts[0].upper()
    args: list[str] = parts[1:] if len(parts) >= 2 else []

    return Message(type=type, args=args)


async def write(message: str, writer: asyncio.StreamWriter) -> None:
    writer.write((message + "\n").encode())
    await writer.drain()


async def broadcast_message(message: str) -> None:
    await asyncio.gather(*(write(message, client) for client in clients))


def is_valid_nickname(nickname: str) -> bool:
    return bool(re.fullmatch(r"[a-z0-9]+", nickname))


def is_nickname_taken(nickname: str) -> bool:
    return any(client.nickname == nickname for client in clients.values())


def find_client(nickname: str) -> Optional[Client]:
    return next(
        (client for client in clients.values() if client.nickname == nickname),
        None,
    )
