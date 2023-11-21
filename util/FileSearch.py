import os
import glob
from colorama import Fore

class FileSearch:

    @staticmethod
    def find_existing_file(path, filename):
        """
        Searches for an existing downloaded file with the given video ID.

        :param video_id: The YouTube video ID to search for
        :return: Path to the existing file if found, None otherwise
        """
        print(Fore.LIGHTCYAN_EX + '\nUtil.FileSearch.find_existing_file()')
        pattern = os.path.join(path, f"{filename}.*")
        files = glob.glob(pattern)
        return files[0] if files else None