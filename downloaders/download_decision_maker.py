from typing import Union
from util.file_search import FileSearch
from downloaders.audio_download_manager import AudioDownloadManager
from config import DOWNLOAD_FOLDER, VIDEO_MAX_LENGTH

class DownloadDecisionMaker:
    def __init__(self, download_manager: AudioDownloadManager):
        self.download_manager = download_manager

    async def should_download(self, url: str, stem: str, duration: int) -> Union[str, bool]:
        if await self.download_manager.is_downloading(url):
            return False  # Still downloading, don't download again

        existing_file_path = FileSearch.find_existing_file(DOWNLOAD_FOLDER, stem)
        if existing_file_path is not None:
            print('File already exists.')
            return existing_file_path

        if duration > VIDEO_MAX_LENGTH:
            print(f'File Too Long!')
            return False
        print ('Downloading!')
        return True