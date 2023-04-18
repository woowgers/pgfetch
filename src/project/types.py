from pathlib import Path
from typing import Sequence
from base64 import b64decode


class GitEntry:
    def __init__(self, raw_gitentry: dict):
        self.entry = raw_gitentry

    @property
    def path(self) -> Path:
        return Path(self.entry["path"])

    @property
    def is_file(self) -> bool:
        return self.entry["type"] == "blob"

    def __str__(self) -> str:
        return f"{self.path}"

    def __hash__(self) -> int:
        return hash((self.path, self.is_file))

    def __eq__(self, other: "GitEntry") -> bool:
        return self.path == other.path and self.is_file == other.is_file


class GitTree:
    def __init__(self, raw_tree: dict):
        self.tree = raw_tree["tree"]

    @property
    def entries(self) -> Sequence[GitEntry]:
        return tuple(map(GitEntry, self.tree))

    @property
    def files(self) -> Sequence[GitEntry]:
        return tuple(entry for entry in self.entries if entry.is_file)


class FileContent:
    def __init__(self, raw_contents_response: dict):
        self.contents = raw_contents_response

    @property
    def content(self) -> bytes:
        return self.contents["content"]

    @property
    def bytes(self) -> bytes:
        return b64decode(self.content)

    @property
    def text(self) -> str:
        return b64decode(self.content).decode()


class GitBranch:
    def __init__(self, raw_branch: dict):
        self.branch = raw_branch

    @property
    def name(self) -> str:
        return self.branch["name"]

    @property
    def id(self) -> str:
        return self.branch["commit"]["id"]
