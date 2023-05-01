from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GitBranch:
    name: str
    id: str


@dataclass(frozen=True)
class GitEntry:
    path: Path
    is_file: bool


@dataclass(frozen=True)
class GitTree:
    entries: tuple[GitEntry, ...]

    @property
    def files(self) -> Sequence[GitEntry]:
        return tuple(entry for entry in self.entries if entry.is_file)
