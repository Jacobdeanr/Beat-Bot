import os
from pytube import Stream
from handlers.youtube.youtube_data_handler import YouTubeDataHandler
from config import DOWNLOAD_FOLDER

class AudioDownloadManager:
    def __init__(self):
        self.currently_downloading = set()

    async def is_downloading(self, url: str) -> bool:
        return url in self.currently_downloading

    async def handle_download_completion(self, url: str) -> None:
        self.currently_downloading.remove(url)

    async def prepare_download(self, url: str, stem: str) -> tuple[Stream, str]:
        data_handler = YouTubeDataHandler()
        audio_stream = await data_handler.get_video_stream(url)
        if audio_stream:
            extension = audio_stream.mime_type.split('/')[-1]
            filename = f"{stem}.{extension}"
            absolute_path = os.path.join(DOWNLOAD_FOLDER, filename)
            return audio_stream, absolute_path
        return None, None

    async def perform_download(self, audio_stream: Stream, absolute_path: str, url: str) -> str:
        try:
            self.currently_downloading.add(url)
            audio_stream.download(output_path=DOWNLOAD_FOLDER, filename=absolute_path)
            return absolute_path
        except Exception as e:
            return None
        finally:
            await self.handle_download_completion(url)

    async def download_audio(self, url: str, stem: str) -> str:
        audio_stream, absolute_path = await self.prepare_download(url, stem)
        if audio_stream:
            return await self.perform_download(audio_stream, absolute_path, url)
        return None