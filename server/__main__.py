import asyncio
import logging

from server.config import HOST, PORT
from server.handlers import (
    handle_ban,
    handle_identify,
    handle_kick,
    handle_message,
)
from server.helpers import broadcast_message, convert_to_message
from server.variables import bans, clients


async def callback(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr: tuple[str, int] = writer.get_extra_info("peername")
    if addr[0] in bans:
        return

    logging.info(f"New connection from {addr}")
    try:
        while True:
            data: bytes = await reader.readline()
            if not data:
                break

            message = await convert_to_message(data)
            if not message:
                continue

            mapping = {
                "IDENTIFY": handle_identify,
                "MESSAGE": handle_message,
                "KICK": handle_kick,
                "BAN": handle_ban,
            }
            if message.type in mapping:
                await mapping[message.type](writer, message)

    except ValueError:
        logging.warning(f"Received a too large message from {addr}")

    except (asyncio.IncompleteReadError, ConnectionError) as e:
        logging.error(f"Connection error with {addr}: {e}")

    finally:
        already_closing = writer.is_closing()
        client = clients.pop(writer, None)

        if client:
            await broadcast_message(f"USER_LEAVE|{client.nickname}")

        if not already_closing:
            writer.close()
            await writer.wait_closed()

        logging.info(f"Connection closed with {addr}")


async def main():
    server = await asyncio.start_server(callback, HOST, PORT)
    logging.info("Server started")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.warning("Keyboard interrupt received. Exiting..")
        exit(0)
