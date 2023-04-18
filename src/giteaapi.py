from base64 import b64decode
from collections.abc import Sequence

import aiohttp
import requests


class GitEntry:
    def __init__(self, raw_gitentry: dict):
        self.entry = raw_gitentry

    @property
    def path(self) -> str:
        return self.entry["path"]

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
        self.tree = raw_tree

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


class GiteaRepositoryApi:
    def __init__(self, host: str, org: str, repo: str, branch: str):
        self.base_url: str = f"https://{host}/api/v1"
        self.repo: str = repo
        self.org: str = org
        self.branch: str = branch

    def get_branch_id(self) -> str:
        url = self.base_url + f"/repos/{self.org}/{self.repo}/branches"

        response = requests.get(url)
        if response.status_code != 200:
            raise RuntimeError(f"Failed to retrieve branch {self.branch}")

        branches = map(Branch, response.json())
        for branch in branches:
            if branch.name == branch:
                return branch.id

        raise ValueError(f"No branch {self.branch} in repository")

    async def get_branch_tree(self, page: int = 1) -> GitTree:
        branch_id = self.get_branch_id()
        url = self.base_url + f"/repos/{self.org}/{self.repo}/git/trees/{branch_id}?page={page}"

        async with aiohttp.ClientSession() as session, session.get(url) as response:
            if response.status != 200:
                raise RuntimeError(f"Failed to retrieve branch {self.branch} filepaths")
            return GitTree(await response.json())

    async def get_file_content(self, filepath: str) -> FileContent:
        url = self.base_url + f"/repos/{self.org}/{self.repo}/contents/{filepath}?ref={self.branch}"
        async with aiohttp.ClientSession() as session, session.get(url) as response:
            return FileContent(await response.json())
