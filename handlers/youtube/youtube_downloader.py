import os
from colorama import Fore
from managers.audio_download_manager import AudioDownloadManager

from config import DOWNLOAD_FOLDER

from pytube import YouTube
from pytube import Stream

class YouTubeDownload:
    def __init__(self):
        self.audio_download_manager = AudioDownloadManager()

    def prepare_download(self, url: str, stem: str) -> tuple[Stream, str]:
        print(Fore.LIGHTCYAN_EX + 'YouTubeDownload.prepare_download()')
        yt = YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        if audio_stream:
            extension = audio_stream.mime_type.split('/')[-1]
            filename = f"{stem}.{extension}"
            full_path = os.path.join(DOWNLOAD_FOLDER, filename)
            return audio_stream, full_path
        return None, None

    def perform_download(self, audio_stream: Stream, full_path: str, url: str) -> str:
        print(Fore.LIGHTCYAN_EX + 'YouTubeDownload.perform_download()')
        if self.audio_download_manager.add_item(url):
            audio_stream.download(output_path=DOWNLOAD_FOLDER, filename=full_path)
            self.audio_download_manager.handle_download_completion(url)
            return full_path
        else:
            print('file already being downloaded')

    def download_audio(self, url: str, stem: str, duration: int) -> str:
        print(Fore.LIGHTCYAN_EX + 'YouTubeDownload.download_audio()')

        if not self.audio_download_manager.is_duration_valid(duration):
            print('Duration is too long.')
            return None
        
        full_path = self.audio_download_manager.find_existing_file(stem) 
        
        if full_path is None:
            audio_stream, full_path = self.prepare_download(url, stem)
            if audio_stream:
                return self.perform_download(audio_stream, full_path, url)
        
        return full_path     