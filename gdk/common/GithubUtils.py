import requests


class GithubUtils:
    def get_latest_release_name(self, owner, repository):
        latest_release_api_url = f"https://api.github.com/repos/{owner}/{repository}/releases/latest"
        response = requests.get(latest_release_api_url)
        if response.status_code != 200:
            response.raise_for_status()
        return response.json()["name"]
