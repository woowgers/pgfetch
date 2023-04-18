from unittest.mock import patch

import pytest

from ..giteaapi import GiteaRepositoryApi


class TestGetBranchId:
    def test_raises_runtimeerror_if_response_status_not_200(self):
        ...

    def test_returns_proper_id(self):
        ...

    def test_raises_valueerror_if_branch_not_in_repo(self):
        ...


class TestGetBranchTree:
    def test_raises_runtimeerror_if_response_status_not_200(self):
        ...

    def test_returns_proper_tree(self):
        ...


class TestGetFileContent:
    def test_raises_runtimeerror_if_response_status_not_200(self):
        ...
