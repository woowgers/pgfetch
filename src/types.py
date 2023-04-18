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

    @property
    def is_dir(self) -> bool:
        return self.entry["type"] == "tree"

    @property
    def is_commit(self) -> bool:
        return self.entry["type"] == "commit"


class GitTree:
    def __init__(self, raw_tree: dict):
        self.tree = raw_tree["tree"]

    @property
    def entries(self) -> Sequence[GitEntry]:
        return tuple(map(GitEntry, self.tree))

    @property
    def complete(self) -> bool:
        return self.tree["page"] == self.tree["total_count"]

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
    def encoding(self) -> str:
        return self.contents["encoding"]

    @property
    def bytes(self) -> bytes:
        if self.encoding != "base64":
            raise RuntimeError(f"Unexpected encoding: expected 'base64', got {self.encoding}")

        return b64decode(self.content)

    @property
    def text(self) -> str:
        if self.encoding != "base64":
            raise RuntimeError(f"Unexpected encoding: expected 'base64', got {self.encoding}")

        return b64decode(self.content).decode()


class Branch:
    def __init__(self, raw_branch: dict):
        self.branch = raw_branch

    @property
    def name(self) -> str:
        return self.branch["name"]

    @property
    def id(self) -> str:
        return self.branch["commit"]["id"]
