from pathlib import Path

import pytest

from project.fetcher import RepositoryBranchFetcher
from project.models import GitEntry, GitTree

pytestmark = pytest.mark.asyncio


def check_files(root_dir: Path, files_contents: dict[Path, str]):
    for filepath in filter(Path.is_file, root_dir.glob("**/*")):
        expected_file_content = files_contents.pop(root_dir / filepath)
        assert filepath.read_text() == expected_file_content

    assert len(files_contents) == 0


async def test_fetch_files(mock_api, tmp_path: Path):
    fetcher = RepositoryBranchFetcher(api=mock_api)

    files_contents = {
        tmp_path / "file1": "content1",
        tmp_path / "file2": "content2",
        tmp_path / "dir1/file3": "content3",
        tmp_path / "dir1/file4": "content4",
        tmp_path / "dir2/file5": "content5",
        tmp_path / "dir2/file6": "content6",
        tmp_path / "dir2/dir3/file7": "content7",
        tmp_path / "dir2/dir3/file8": "content8",
        tmp_path / "dir2/dir3/file9": "content9",
        tmp_path / "dir2/dir3/file10": "content10",
    }
    git_entries = tuple(GitEntry(path=filepath, is_file=True) for filepath in files_contents)

    mock_api.get_branch_tree.return_value = GitTree(entries=git_entries)
    mock_api.get_file_content.side_effect = lambda filepath: files_contents[filepath]

    await fetcher.fetch_files(root_dir=tmp_path, n_tasks_max=100)

    check_files(tmp_path, files_contents)
