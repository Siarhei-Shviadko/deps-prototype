from collections import namedtuple

__all__ = ["FakeCommandProducer", "Command"]

Command = namedtuple("Command", ("channel", "command", "reply_to"))


class FakeCommandProducer:
    def __init__(self) -> None:
        self._sent: list[Command] = []

    @property
    def sent(self) -> list[Command]:
        return self._sent

    @sent.deleter
    def sent(self) -> None:
        self._sent.clear()

    def send(self, channel: str, command: Command, reply_to: str, **kwargs) -> None:
        self.sent.append(Command(channel=channel, command=command, reply_to=reply_to))
