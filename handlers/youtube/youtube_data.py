import datetime
from pytube import YouTube
from pytube import Playlist
from pytube import Channel
from pytube import Stream
from models.song_info import SongInfo
from colorama import Fore

class YouTubeData:
    def __init__(self):
        pass
       
    def get_playlist_video_urls(self, url: str) -> list: 
        print(Fore.LIGHTCYAN_EX + 'YouTubeData.get_playlist_video_urls()')
        try:
            playlist = Playlist(url)
            if playlist.length <= 0:
                return []
            return [url for url in playlist.video_urls]
        except Exception as e:
            print(f"\tGeneral exception occurred: {e}")
            return []

    def get_video_stream(self, url: str) -> Stream:
        print(Fore.LIGHTCYAN_EX + 'YouTubeData.get_video_stream()')
        yt = YouTube(url)
        return yt.streams.get_audio_only()

    def update_video_data(self, song_info: SongInfo) -> None:
        print(Fore.LIGHTCYAN_EX + 'YouTubeData.update_video_data()')
        yt = YouTube(song_info.url)

        video_id = self.get_video_id(yt)
        video_length = self.get_video_length(yt)

        song_info.update_song_info(id=video_id, length=video_length)

    def update_video_information(self, song_info: SongInfo) -> None:
        print(Fore.LIGHTCYAN_EX + 'YouTubeData.update_video_information()')
        yt = YouTube(song_info.url)
        c = Channel(yt.channel_url)

        id = self.get_video_id(yt)
        length = self.get_video_length(yt)
        uploader = self.get_video_author(yt)
        title = self.get_video_title(yt)
        publish_date = self.get_video_publish_date(yt)
        channel_id = self.get_channel_id(c)
        channel_name = self.get_channel_name(c)

        song_info.update_song_info(
            id=id,uploader=uploader, title=title, publish_date=publish_date,
            channel_id=channel_id, channel_name=channel_name,length=length
        )
    
    def get_video_author(self, yt: YouTube) -> str:
        return yt.author if yt else None

    def get_video_title(self, yt: YouTube) -> str:
        return yt.title if yt else None

    def get_video_length(self, yt: YouTube) -> int:
        return yt.length if yt else -1

    def get_video_id(self, yt: YouTube) -> str:
        return yt.video_id if yt else None

    def get_video_publish_date(self, yt: YouTube) -> datetime:
        return yt.publish_date if yt else None

    def get_channel_id(self, c: Channel) -> str:
        return c.channel_id

    def get_channel_name(self, c: Channel) -> str:
        return c.channel_name