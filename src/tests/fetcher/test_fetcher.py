import string
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import AsyncMock

from hypothesis import given, strategies as st, assume

import pytest

from project.fetcher import GiteaRepositoryBranchFetcher
from project.giteaapi import BaseRepositoryBranchApi
from project.types import GitTree, GitEntry

pytestmark = pytest.mark.asyncio


def check_files(root_dir: Path, files_contents: dict[Path, str]):
    for filepath in root_dir.glob("**/*"):
        if filepath.is_dir():
            continue

        expected_file_content = files_contents.pop(root_dir / filepath)
        assert filepath.read_text() == expected_file_content

    assert len(files_contents) == 0


@st.composite
def files_contents_strategy(draw):
    path_depth = draw(st.integers(min_value=1, max_value=10))
    file_path_parts = draw(
        st.lists(
            st.text(alphabet=list(string.ascii_letters + string.digits + "_"), min_size=1),
            min_size=path_depth,
            max_size=path_depth,
        )
    )
    file_path = Path("/".join(file_path_parts))
    file_content = draw(st.text())

    assume('\r' not in file_content)

    return file_path, file_content


@given(data=st.data(), files_contents=st.lists(files_contents_strategy()))
async def test_fetch_files(data, files_contents: [Path, str]):
    tmp_path = Path(TemporaryDirectory().name)
    mock_api = AsyncMock(spec=BaseRepositoryBranchApi)
    fetcher = GiteaRepositoryBranchFetcher(api=mock_api)

    files_contents = {
        tmp_path / filepath: file_content for filepath, file_content in files_contents
    }
    git_entries = tuple(
        GitEntry(path=filepath, is_file=True)
        for filepath in files_contents
    )

    mock_api.get_branch_tree.return_value = GitTree(entries=git_entries)
    mock_api.get_file_content.side_effect = lambda filepath: files_contents[filepath]

    await fetcher.fetch_files(
        root_dir=tmp_path, n_tasks_max=data.draw(st.integers(min_value=1))
    )

    check_files(tmp_path, files_contents)

    for filepath in tmp_path.glob("**/*"):
        if filepath.is_dir():
            continue
        filepath.unlink()
