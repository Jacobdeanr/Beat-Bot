import os
from pytube import YouTube
from colorama import Fore
import glob
from Search.Youtube.YouTubeDataHandler import YouTubeDataHandler

download_folder = "C:\\test\\"
video_max_length = 10800 # maximum length of a video in seconds.

class DownloadManager:
    currently_downloading = set()

    @staticmethod
    def find_existing_file(video_id):
        print(Fore.LIGHTCYAN_EX + '\nDownloadManager.find_existing_file()')
        pattern = os.path.join(download_folder, f"{video_id}.*")
        files = glob.glob(pattern)
        return files[0] if files else None

    @staticmethod
    async def download_audio(url):
        print(Fore.LIGHTCYAN_EX + '\nDownloadManager.download_audio()')       
        if url in DownloadManager.currently_downloading:
            return None

        video_id = YouTubeDataHandler.fetch_video_id(url)
        print(f'\tchecking if downloaded already: {url}')
        existing_file = DownloadManager.find_existing_file(video_id)
        if existing_file:
            print(f'\tSkipping download, file exists: {existing_file}')
            return existing_file

        if(YouTubeDataHandler.fetch_video_length(url)>video_max_length):
            return None
        
        yt = YouTube(url)
        audio_stream = yt.streams.get_audio_only()
        if audio_stream:
            extension = audio_stream.mime_type.split('/')[-1]
            filename = f"{video_id}.{extension}"
            file_path = os.path.join(download_folder, filename)

            try:
                DownloadManager.currently_downloading.add(url)
                audio_stream.download(output_path=download_folder, filename=filename)
                print(f'\tdownloaded {url} to: {file_path}')
                return file_path
            except Exception as e:
                print(f"\tDownload failed for {url}: {e}")
                return None
            finally:
                DownloadManager.currently_downloading.remove(url)
                print(f'\tremoved from current download list: {url}\n')

        return None
