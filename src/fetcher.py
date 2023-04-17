import asyncio
from base64 import b64decode
from hashlib import sha256
from multiprocessing.pool import AsyncResult
from pathlib import Path

from giteapy import (
    ApiClient,
    Branch,
    Configuration,
    ContentsResponse,
    GitEntry,
    GitTreeResponse,
    RepositoryApi,
)


class RepositoryFilepathFetcher:
    def __init__(self, host: str, org: str, repo: str, branch: str):
        self.host: str = host
        self.org: str = org
        self.repo: str = repo
        self.branch: str = branch
        self.api: RepositoryApi = self._get_repository_api()
        self.branch_id = self._get_branch_id()
        self.filepaths: tuple[str, ...] = self._get_branch_filepaths()

    def _get_repository_api(self) -> RepositoryApi:
        configuration = Configuration()
        configuration.host = self.host
        return RepositoryApi(ApiClient(configuration=configuration))

    def _get_branch_id(self) -> str:
        branch: Branch = self.api.repo_get_branch(owner=self.org, repo=self.repo, branch=self.branch)  # type: ignore
        if branch.commit is None:
            raise RuntimeError(f"No commits in branch `{self.branch}`")

        return branch.commit.id

    def _get_branch_filepaths(self) -> tuple[str, ...]:
        def entry_get_filepath(entry: GitEntry) -> str:
            if entry.path is None:
                raise RuntimeError("Entry doesn't have name")
            return entry.path

        def entry_is_regular_file(entry: GitEntry) -> bool:
            return entry.type == "blob"

        tree_response: GitTreeResponse = self.api.get_tree(owner=self.org, repo=self.repo, sha=self.branch_id, recursive=True, page=1)  # type: ignore
        if tree_response.tree is None:
            raise RuntimeError("Failed to fetch repository tree")

        files_entries = filter(entry_is_regular_file, tree_response.tree)
        filepath_tuple = tuple(map(entry_get_filepath, files_entries))

        return filepath_tuple

    def get_filepath_content(self, filepath: str) -> bytes:
        if filepath not in self.filepaths:
            raise ValueError(f"Path '{filepath}' is not a path of a regular file from repository tree")

        content_response: ContentsResponse = self.api.repo_get_contents(owner=self.org, repo=self.repo, filepath=filepath)  # type: ignore
        if content_response.content is None:
            raise RuntimeError(f"Failed to get {filepath} content")
        if content_response.type != "file":
            raise RuntimeError(f"Unexpected content type (expected 'file', got {content_response.type})")
        if content_response.encoding != "base64":
            raise RuntimeError(f"Unexpected content encoding (expected 'base64', got {content_response.encoding})")

        content = b64decode(content_response.content)

        return content

    async def get_filepath_content_async(self, filepath: str) -> bytes:
        if filepath not in self.filepaths:
            raise ValueError(f"Path '{filepath}' is not a path of a regular file from repository tree")

        async_result: AsyncResult = self.api.repo_get_contents(owner=self.org, repo=self.repo, filepath=filepath, async_req=True)  # type: ignore
        content_response: ContentsResponse = async_result.get()
        if content_response.content is None:
            raise RuntimeError(f"Failed to get {filepath} content")
        if content_response.type != "file":
            raise RuntimeError(f"Unexpected content type (expected 'file', got {content_response.type})")
        if content_response.encoding != "base64":
            raise RuntimeError(f"Unexpected content encoding (expected 'base64', got {content_response.encoding})")

        content = b64decode(content_response.content)

        return content

    def _write_filepath_checksum(self, filepath: str, content: bytes, cksum_file: str) -> None:
        checksum = sha256(content).hexdigest()
        with open(cksum_file, "a") as f:
            f.write(f"{filepath}\t{checksum}")

    def save_filepath_content(self, root_dir: str | Path, filepath: str, cksum_file: str | None = None) -> None:
        root_dir = Path(root_dir)
        if not root_dir.exists():
            root_dir.mkdir(parents=True)

        local_filepath = root_dir / filepath
        parent_dir = root_dir / Path(filepath).parent
        if not parent_dir.exists():
            parent_dir.mkdir(parents=True)

        with open(local_filepath, "w") as f:
            content = self.get_filepath_content(filepath)
            f.write(content.decode())
            if cksum_file:
                self._write_filepath_checksum(filepath, content, cksum_file)

    def save_contents(self, root_dir: Path) -> None:
        if not root_dir.exists():
            root_dir.mkdir(parents=True)

        for filepath in self.filepaths:
            self.save_filepath_content(root_dir=root_dir, filepath=filepath)

    def list_filepath_content(self, filepath: str) -> None:
        print(
            f"=================== {filepath} ===================\n",
            self.get_filepath_content(filepath).decode(),
            f"==================={'=' * len(filepath)}===================",
        )

    async def list_filepath_content_async(self, filepath: str) -> None:
        print(
            f"=================== {filepath} ===================\n",
            (await self.get_filepath_content_async(filepath)).decode(),
            f"==================={'=' * len(filepath)}===================",
        )

    def list_all_contents(self) -> None:
        for filepath in self.filepaths:
            self.list_filepath_content(filepath)

    async def list_all_contents_async(self) -> None:
        tasks = (asyncio.create_task(self.list_filepath_content_async(filepath)) for filepath in self.filepaths)
        await asyncio.gather(*tasks)
