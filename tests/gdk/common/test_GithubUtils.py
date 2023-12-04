from unittest import TestCase

import pytest

from gdk.common.GithubUtils import GithubUtils


class MockGetResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


class GithubUtilsTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker

    def test_GIVEN_latest_release_request_WHEN_request_successful_THEN_return_release_name(self):
        self.mocker.patch("requests.get", return_value=MockGetResponse({"name": "1.0.0"}, 200))
        github_utils = GithubUtils()
        latest_release = github_utils.get_latest_release_name("author", "repo")
        assert latest_release == "1.0.0"
