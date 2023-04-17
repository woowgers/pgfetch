from giteapy import ApiClient, Branch, Configuration, GitEntry, GitTreeResponse, RepositoryApi

REPO_HOST = "https://gitea.radium.group/api/v1"
REPO_ORG = "radium"
REPO_NAME = "project-configuration"
REPO_BRANCH = "master"
REPO_SPEC = (REPO_ORG, REPO_NAME, REPO_BRANCH)


def get_branch_id(api: RepositoryApi, owner: str, repo: str, branch: str) -> str:
    raw_branch = api.repo_get_branch(owner=owner, repo=repo, branch=branch)
    if not isinstance(raw_branch, Branch):
        raise RuntimeError("Unexpected SDK return value")
    if raw_branch.commit is None:
        raise RuntimeError(f"No commits in branch `{branch}`")

    return raw_branch.commit.id


def get_branch_filepaths(api: RepositoryApi, owner: str, repo: str, branch_id: str) -> tuple[str, ...]:
    def entry_get_filepath(entry: GitEntry) -> str:
        if entry.path is None:
            raise RuntimeError("Entry doesn't have name")
        return entry.path

    def entry_is_regular_file(entry: GitEntry) -> bool:
        return entry.type == 'blob'

    raw_tree = api.get_tree(owner=owner, repo=repo, sha=branch_id, recursive=True, page=1)
    if not isinstance(raw_tree, GitTreeResponse):
        raise RuntimeError("Unexpected SDK return value")
    if raw_tree.tree is None:
        raise RuntimeError("Failed to fetch repository tree")

    files_entries = filter(entry_is_regular_file, raw_tree.tree)
    filepath_tuple = tuple(map(entry_get_filepath, files_entries))

    return filepath_tuple


if __name__ == "__main__":
    print("Sending request...")

    configuration = Configuration()
    configuration.host = REPO_HOST
    api = RepositoryApi(ApiClient(configuration=configuration))

    branch_id = get_branch_id(api, *REPO_SPEC)
    filepaths = get_branch_filepaths(api, *REPO_SPEC)
    print('\n'.join(filepaths))
