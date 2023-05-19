from pathlib import Path
import requests
import logging
import zipfile
from io import BytesIO
import tempfile
import shutil


class URLDownloader:
    def __init__(self, url):
        self.url = url

    def download(self, destination: Path):
        logging.debug("Downloading the content from URL %s to the file %s", self.url, destination.name)
        download_response = self._get_download_response()
        # TODO: Write in chunks so as to not overload the memory in case of large files
        with open(destination, "wb") as file:
            file.write(download_response.content)

    def download_and_extract(self, destination: Path):
        logging.debug("Downloading the content from URL %s to the destination %s", self.url, destination.name)
        download_response = self._get_download_response()
        with zipfile.ZipFile(BytesIO(download_response.content)) as zfile:
            with tempfile.TemporaryDirectory() as tmpdirname:
                # Extracts the zip file into temporary directory - /some-temp-dir/downloaded-zip-folder/
                zfile.extractall(tmpdirname)
                self._create_dir(destination)
                # Moves the unarchived contents from temporary folder (downloaded-zip-folder) to current directory.
                for f in Path(tmpdirname).joinpath(zfile.namelist()[0]).iterdir():
                    shutil.move(str(f), destination)

    def _get_download_response(self) -> requests.Response:
        """
        Returns the response of the download request.
        """
        try:
            download_response = requests.get(self.url, stream=True, timeout=30)
            if download_response.status_code != 200:
                download_response.raise_for_status()
        except Exception:
            logging.error("Failed to download the file from %s", self.url)
            raise
        return download_response

    def _create_dir(self, project_dir: Path):
        """
        Creates a new directory if it does not exist already.
        """
        if project_dir.exists():
            return
        logging.debug("Creating a new project directory '%s'", str(project_dir))
        project_dir.mkdir(parents=True, exist_ok=False)
