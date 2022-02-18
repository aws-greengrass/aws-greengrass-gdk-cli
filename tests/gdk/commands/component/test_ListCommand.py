from unittest import TestCase

import gdk.common.consts as consts
import gdk.common.exceptions.error_messages as error_messages
import pytest
from gdk.commands.component.ListCommand import ListCommand
from urllib3.exceptions import HTTPError


class ListCommandTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker

    def test_display_list(self):
        components = [1, 2, 4]
        self.mocker.patch.object(ListCommand, "__init__", return_value=None)
        list = ListCommand({})
        list.display_list(components)

    def test_get_component_list_from_github_valid_json(self):
        res_json = {"template-name": "template-list"}
        url = "url"
        mock_response = self.mocker.Mock(status_code=200, json=lambda: res_json)
        mock_template_list = self.mocker.patch("requests.get", return_value=mock_response)
        self.mocker.patch.object(ListCommand, "__init__", return_value=None)
        list = ListCommand({})
        templates_list = list.get_component_list_from_github(url)
        assert templates_list == res_json
        assert mock_template_list.call_count == 1

    def test_get_component_list_from_github_invalid_json(self):
        res_json = {"template-name": "template-list"}
        mock_response = self.mocker.Mock(status_code=200, json=res_json)
        mock_template_list = self.mocker.patch("requests.get", return_value=mock_response)
        self.mocker.patch.object(ListCommand, "__init__", return_value=None)
        list = ListCommand({})
        templates_list = list.get_component_list_from_github("url")
        assert templates_list == []
        assert mock_template_list.call_count == 1

    def test_get_component_list_from_github_invalid_url(self):
        mock_response = self.mocker.Mock(
            status_code=404, raise_for_status=self.mocker.Mock(side_effect=HTTPError("some error"))
        )
        mock_template_list = self.mocker.patch("requests.get", return_value=mock_response)
        self.mocker.patch.object(ListCommand, "__init__", return_value=None)
        list = ListCommand({})
        with pytest.raises(Exception) as e:
            list.get_component_list_from_github("url")
        assert e.value.args[0] == error_messages.LISTING_COMPONENTS_FAILED
        assert mock_template_list.call_count == 1

    def test_run_template(self):
        mock_get_component_list_from_github = self.mocker.patch.object(
            ListCommand, "get_component_list_from_github", return_value=[]
        )
        mock_display_list = self.mocker.patch.object(ListCommand, "display_list", return_value=None)
        list = ListCommand({"template": True})
        list.run()
        mock_get_component_list_from_github.assert_any_call(consts.templates_list_url)
        assert mock_display_list.call_count == 1

    def test_run_repository(self):
        mock_get_component_list_from_github = self.mocker.patch.object(
            ListCommand, "get_component_list_from_github", return_value=[]
        )
        mock_display_list = self.mocker.patch.object(ListCommand, "display_list", return_value=None)
        list = ListCommand({"repository": True})
        list.run()
        mock_get_component_list_from_github.assert_any_call(consts.repository_list_url)
        assert mock_display_list.call_count == 1

    def test_run_none(self):
        mock_get_component_list_from_github = self.mocker.patch.object(
            ListCommand, "get_component_list_from_github", return_value=[]
        )
        mock_display_list = self.mocker.patch.object(ListCommand, "display_list", return_value=None)
        list = ListCommand({})
        with pytest.raises(Exception) as e:
            list.run()
        assert e.value.args[0] == error_messages.LIST_WITH_INVALID_ARGS
        assert mock_display_list.call_count == 0
        assert mock_get_component_list_from_github.call_count == 0
