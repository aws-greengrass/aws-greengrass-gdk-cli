from unittest import TestCase
import pytest
from pathlib import Path
import os
from gdk.common.URLDownloader import URLDownloader
import requests


class URLDownloaderIntegTest(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker, tmpdir):
        self.mocker = mocker
        self.tmpdir = Path(tmpdir)
        self.c_dir = Path(".").resolve()
        os.chdir(self.tmpdir)
        yield
        os.chdir(self.c_dir)

    def test_valid_url_and_destination_path_when_download_from_url_then_download_file(self):
        download_link = (
            "https://github.com/aws-greengrass/aws-greengrass-component-templates/releases/download/v1.0/HelloWorld-python.zip"
        )
        URLDownloader(download_link).download(self.tmpdir.joinpath("HelloWorld-python.zip"))
        assert self.tmpdir.joinpath("HelloWorld-python.zip").exists()

    def test_given_invalid_url_when_download_from_url_then_raises_an_exception(self):
        download_link = (
            "https://github.com/aws-greengrass/aws-greengrass-component-templates/releases/download/v1.0/invalid.zip"
        )
        with pytest.raises(Exception) as e:
            URLDownloader(download_link).download(self.tmpdir.joinpath("HelloWorld-python.zip"))
        assert not self.tmpdir.joinpath("HelloWorld-python.zip").exists()
        assert type(e.value) == requests.exceptions.HTTPError
