import random
import string
from collections.abc import Callable
from pathlib import Path

from project.api.gitea import GiteaRepositoryBranch


def random_filename(length_min: int = 1, length_max: int = 30) -> str:
    return ''.join(random.choices(string.digits + string.ascii_letters, k=random.randint(length_min, length_max)))


def random_filepath(depth_min: int = 1, depth_max: int = 30) -> Path:
    return Path('/'.join(random_filename() for _ in range(random.randint(depth_min, depth_max))))


class TestGiteaRepositoryBranch:
    def test_branch_base_url(self, branch: GiteaRepositoryBranch, expected_base_url: str):
        assert branch.base_url == expected_base_url

    def test_branches_list_url(self, branch: GiteaRepositoryBranch, expected_branches_list_url: str):
        assert branch.get_branches_list_url() == expected_branches_list_url

    def test_branch_tree_url(self, branch: GiteaRepositoryBranch, expected_branch_tree_url: Callable[[str], str]):
        branch_id = ''.join(random.choices(string.digits + string.ascii_letters, k=random.randint(10, 20)))
        assert branch.get_branch_tree_url(branch_id) == expected_branch_tree_url(branch_id)

    def test_filepath_content_url(
        self, branch: GiteaRepositoryBranch, expected_filepath_content_url: Callable[[Path], str]
    ):
        filepath = random_filepath()
        assert branch.get_filepath_content_url(filepath) == expected_filepath_content_url(filepath)
