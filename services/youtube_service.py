from colorama import Fore
from typing import Union, List
from interfaces.audio_service import AudioService
from handlers.youtube.youtube_searcher import YouTubeSearcher
from handlers.youtube.youtube_data import YouTubeData
from handlers.youtube.youtube_downloader import YouTubeDownload
from handlers.youtube.youtube_url import YouTubeURL

from models.song_info import SongInfo

class YouTubeService(AudioService):
    def __init__(self):
        self.search_handler = YouTubeSearcher()
        self.data_handler = YouTubeData()
        self.download_handler = YouTubeDownload()
        self.url_validator = YouTubeURL()

    def validate_url(self, url: str) -> bool:
        print(Fore.LIGHTCYAN_EX + 'YouTubeService.validate_url()')
        return self.url_validator.is_youtube_url(url)

    def search_song(self, query: str) -> Union[str, List[str]]:
        print(Fore.LIGHTCYAN_EX + 'YouTubeService.search_song()')

        if self.validate_url(query):
            if self.url_validator.is_playlist_url(query):
                # If it's a playlist, process and return all video URLs in the playlist
                return self.data_handler.get_playlist_video_urls(query)
            else:
                # If it's a single video URL, return it wrapped in a list
                return [query]
        else:
            # If not a valid URL, perform a search and wrap the result in a list
            search_result = self.search_handler.search_for_one_song(query)
            return [search_result] if search_result else []

    def download_song(self, url: str, id: str, duration: int) -> str:
        print(Fore.LIGHTCYAN_EX + 'YouTubeService.download_song()')
        return self.download_handler.download_audio(url, id, duration)

    def update_song_info(self, song_info: SongInfo):
        print(Fore.LIGHTCYAN_EX + 'YouTubeService.update_song_info()')
        self.data_handler.update_video_information(song_info)

    def update_song_meta_data(self, song_info: SongInfo):
        print(Fore.LIGHTCYAN_EX + 'YouTubeService.update_song_data()')
        self.data_handler.update_video_data(song_info)