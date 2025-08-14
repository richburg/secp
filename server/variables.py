import asyncio

from server.types import Client

clients: dict[asyncio.StreamWriter, Client] = {}
bans: set[str] = set()
