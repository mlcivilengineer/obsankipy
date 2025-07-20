import enum
from pathlib import Path

from utils.helpers import file_encode

import logging

logger = logging.getLogger(__name__)


class MediaState(enum.Enum):
    STORED = enum.auto()
    UNKNOWN = enum.auto()
    NEW = enum.auto()


class Picture:
    data: str | None
    filename: str
    state: MediaState

    def __init__(self, filename):
        self.filename = filename
        self.state = MediaState.UNKNOWN
        self.data = None

    def to_anki_dict(self):
        return {"filename": self.filename, "data": self.data}

    def set_state(self, state):
        self.state = state

    def load_data(self, dir: Path):
        self.data = file_encode(dir / self.filename)


class Audio:
    data: str | None
    filename: str
    state: MediaState

    def __init__(self, filename):
        self.filename = filename
        self.state = MediaState.UNKNOWN
        self.data = None

    def to_anki_dict(self):
        return {"filename": self.filename, "data": self.data}

    def set_state(self, state):
        self.state = state

    def load_data(self, dir: Path):
        self.data = file_encode(dir / self.filename)
