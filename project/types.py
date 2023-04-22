from pathlib import Path
from typing import Sequence, Self

from dataclasses import dataclass


@dataclass
class GitBranch:
    name: str
    id: str

    @classmethod
    def parse_from_raw(cls, raw_branch) -> Self:
        return GitBranch(raw_branch["name"], raw_branch["commit"]["id"])


@dataclass
class GitEntry:
    path: Path
    is_file: bool

    @classmethod
    def parse_from_raw(cls, raw_entry: dict) -> Self:
        return GitEntry(raw_entry["path"], raw_entry["type"] == "blob")


@dataclass
class GitTree:
    entries: tuple[GitEntry, ...]

    @property
    def files(self) -> Sequence[GitEntry]:
        return tuple(entry for entry in self.entries if entry.is_file)

    @classmethod
    def parse_from_raw(cls, raw_tree: dict) -> Self:
        entries = tuple(GitEntry.parse_from_raw(raw_entry) for raw_entry in raw_tree["tree"])
        return GitTree(entries)
