from giteapy import Configuration, ApiClient, RepositoryApi
from pprint import pprint

REPO_URL = "https://gitea.radium.group/radium/project-configuration"
REPO_HOST = "https://gitea.radium.group"
REPO_ORG = "radium"
REPO_NAME = "project-configuration"


if __name__ == "__main__":
    pprint("Sending request...")

    configuration = Configuration()
    configuration.host = REPO_HOST
    api = RepositoryApi(ApiClient(configuration=configuration))

    repos = api.repo_search()
    pprint(repos)
