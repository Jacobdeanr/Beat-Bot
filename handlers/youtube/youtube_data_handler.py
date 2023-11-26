import time
import datetime
from pytube import YouTube
from pytube import Playlist
from pytube import Channel
from pytube import Stream
from handlers.song_info import SongInfo
from colorama import Fore
from asyncio import gather

class YouTubeDataHandler:
    def __init__(self):
        pass

    async def validate_url(self, url: str) -> str:
        try:
            video = YouTube(url)
            print(f'\t{video.watch_url}')
            return video.watch_url
        except Exception as e:
            #print(f"Exception: {e}") #Exception usually just means we got a search request.
            return None
        
    async def get_playlist_video_urls(self, url: str) -> list: 
        try:
            playlist = Playlist(url)
            if playlist.length <= 0:
                return []

            return [url for url in playlist.video_urls]
        except Exception as e:
            print(f"YouTubeDataHandler.get_playlist_video_urls()\nGeneral exception occurred: {e}")
            return []
    
    async def get_video_stream(self, url: str) -> Stream:
        print(Fore.LIGHTCYAN_EX + '\nYouTubeDataHandler.get_video_stream()')
        yt = YouTube(url)
        return yt.streams.get_audio_only()

    async def update_video_data(self, song_info: SongInfo) -> None:
        print(Fore.LIGHTCYAN_EX + '\nYouTubeDataHandler.update_video_data()')
        yt = YouTube(song_info.url)

        video_id = await self.get_video_id(yt)
        video_length = await self.get_video_length(yt)

        song_info.update_song_info(id=video_id, length=video_length)

    async def update_video_information(self, song_info: SongInfo) -> None:
        print(Fore.LIGHTCYAN_EX + '\nYouTubeDataHandler.update_video_information()')
        yt = YouTube(song_info.url)
        c = Channel(yt.channel_url)

        uploader = await self.get_video_author(yt)
        title = await self.get_video_title(yt)
        publish_date = await self.get_video_publish_date(yt)
        channel_id = await self.get_channel_id(c)
        channel_name = await self.get_channel_name(c)

        song_info.update_song_info(
            uploader=uploader, title=title, publish_date=publish_date,
            channel_id=channel_id, channel_name=channel_name
        )
    
    async def create_yt_object(url: str) -> YouTube:
          return YouTube(url)
    
    async def get_video_author(self, yt: YouTube) -> str:
        print(yt.author)
        return yt.author if yt else None

    async def get_video_title(self, yt: YouTube) -> str:
        print(yt.title)
        return yt.title if yt else None

    async def get_video_length(self, yt: YouTube) -> int:
        print(yt.length)
        return yt.length if yt else -1

    async def get_video_id(self, yt: YouTube) -> str:
        print(yt.video_id)
        return yt.video_id if yt else None

    async def get_video_publish_date(self, yt: YouTube) -> datetime:
        print(yt.publish_date)
        return yt.publish_date if yt else None

    async def get_channel_id(self, c: Channel) -> str:
        print(c.channel_id)
        return c.channel_id

    async def get_channel_name(self, c: Channel) -> str:
        print(c.channel_name)
        return c.channel_name