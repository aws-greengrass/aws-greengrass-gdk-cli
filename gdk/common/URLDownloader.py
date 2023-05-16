from pathlib import Path
import requests
import logging


class URLDownloader:
    def __init__(self, url):
        self.url = url

    def download(self, destination: Path):
        logging.debug("Downloading the content from URL %s to the file %s", self.url, destination.name)
        download_response = requests.get(self.url, stream=True, timeout=30)
        if download_response.status_code != 200:
            try:
                download_response.raise_for_status()
            except Exception:
                logging.error("Failed to download the file from %s", self.url)
                raise
        # TODO: Write in chunks so as to not overload the memory in case of large files
        with open(destination, "wb") as file:
            file.write(download_response.content)
