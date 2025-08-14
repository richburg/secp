from dataclasses import dataclass
from asyncio import StreamWriter


@dataclass
class Message:
    type: str
    args: list[str]

    def has_exact_args(self, count: int) -> bool:
        return len(self.args) == count


@dataclass
class Client:
    nickname: str
    writer: StreamWriter
    admin: bool = False

    async def close(self) -> None:
        self.writer.close()
        await self.writer.wait_closed()
