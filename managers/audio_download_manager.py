from colorama import Fore
from util.file_search import FileSearch
from config import DOWNLOAD_FOLDER, VIDEO_MAX_LENGTH

class AudioDownloadManager:
    def __init__(self):
        self.download_queue = set()

    def add_item(self,url:str) -> bool:
        print(Fore.LIGHTCYAN_EX + 'AudioDownloadManager.add_item()')
        if not self.is_downloading(url):
            self.download_queue.add(url)
            return True
        else:
            return False

    def is_downloading(self, url: str) -> bool:
        print(Fore.LIGHTCYAN_EX + 'AudioDownloadManager.is_downloading()')
        return url in self.download_queue

    def handle_download_completion(self, url: str) -> None:
        self.download_queue.remove(url)
   
    @staticmethod
    def find_existing_file(stem: str) -> str:
        print(Fore.LIGHTCYAN_EX + 'AudioDownloadManager.find_existing_file()')
        existing_file_path = FileSearch.find_existing_file(DOWNLOAD_FOLDER, stem)
        if existing_file_path is not None:
            print(f'\tFile already exists. {existing_file_path}')
            return existing_file_path
        return None
    
    @staticmethod
    def is_duration_valid(duration: int) -> bool:
        print(Fore.LIGHTCYAN_EX + 'AudioDownloadManager.is_duration_valid()')
        if duration > VIDEO_MAX_LENGTH:
            print(f'\tDuration is too long!')
            return False
        print('\tDuration is valid.')
        return True

