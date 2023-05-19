from pathlib import Path
from unittest import TestCase
from unittest.mock import mock_open, patch, call, Mock
import pytest
from gdk.common.URLDownloader import URLDownloader
from urllib3.exceptions import HTTPError


class URLDownloaderTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker

    def test_given_URLDownloader_with_dest_when_download_url_then_download_file_to_dest(self):
        mock_response = self.mocker.Mock(status_code=200, content="some-content".encode())
        mock_request = self.mocker.patch("requests.get", return_value=mock_response)
        with patch("builtins.open", mock_open()) as mock_file:
            URLDownloader("some-url").download(Path("some-path"))
        mock_request.assert_called_once_with("some-url", stream=True, timeout=30)
        assert mock_file.call_args_list == [call(Path("some-path"), "wb")]
        assert mock_file.return_value.write.call_args_list == [call(b"some-content")]

    def test_given_URLDownloader_with_dest_when_exception_during_download_then_raise_exception(self):
        mock_response = self.mocker.Mock(
            status_code=404, raise_for_status=self.mocker.Mock(side_effect=HTTPError("Not found"))
        )
        mock_request = self.mocker.patch("requests.get", return_value=mock_response)
        with pytest.raises(Exception) as e:
            with patch("builtins.open", mock_open()) as mock_file:
                URLDownloader("some-url").download(Path("some-path"))
        assert "Not found" in e.value.args[0]
        mock_request.assert_called_once_with("some-url", stream=True, timeout=30)
        assert not mock_file.called

    @patch("zipfile.ZipFile")
    def test_given_dest_exists_when_download_and_extract_then_dowload_and_extract_file(self, mock_zip):
        mock_response = self.mocker.Mock(status_code=200, content="some.zip".encode())
        mock_request = self.mocker.patch("requests.get", return_value=mock_response)
        self.mocker.patch("pathlib.Path.exists", return_value=True)
        self.mocker.patch("pathlib.Path.iterdir", return_value=[Path("dummy-folder1")])

        mock_za = Mock()
        mock_za.return_value.namelist.return_value = ["one"]
        mock_za.return_value.extractall.return_value = None
        mock_zip.return_value.__enter__ = mock_za

        mock_move = self.mocker.patch("shutil.move", return_value=None)
        URLDownloader("some-url").download_and_extract(Path("some-path"))

        assert mock_request.call_args_list == [call("some-url", stream=True, timeout=30)]
        assert mock_move.call_args_list == [call("dummy-folder1", Path("some-path"))]

    @patch("zipfile.ZipFile")
    def test_given_dest_not_exists_when_download_and_extract_then_create_dest_and_dowload_and_extract_file(self, mock_zip):
        mock_response = self.mocker.Mock(status_code=200, content="some.zip".encode())
        mock_request = self.mocker.patch("requests.get", return_value=mock_response)
        self.mocker.patch("pathlib.Path.exists", return_value=False)
        self.mocker.patch("pathlib.Path.iterdir", return_value=["dummy-folder1"])
        mock_create_dir = self.mocker.patch("pathlib.Path.mkdir", return_value=None)
        mock_za = Mock()
        mock_za.return_value.namelist.return_value = ["one"]
        mock_za.return_value.extractall.return_value = None
        mock_zip.return_value.__enter__ = mock_za

        mock_move = self.mocker.patch("shutil.move", return_value=None)
        URLDownloader("some-url").download_and_extract(Path("some-path"))

        assert mock_create_dir.call_count == 1
        assert mock_request.call_args_list == [call("some-url", stream=True, timeout=30)]
        assert mock_move.call_args_list == [call("dummy-folder1", Path("some-path"))]
