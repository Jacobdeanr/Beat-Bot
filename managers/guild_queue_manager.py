from colorama import Fore
from config import DOWNLOAD_THRESHOLD

from handlers.guild_queue import GuildQueue
from handlers.youtube.youtube_data_handler import YouTubeDataHandler

from downloaders.audio_download_manager import AudioDownloadManager
from downloaders.download_decision_maker import DownloadDecisionMaker
from downloaders.youtube_downloader import YouTubeDownload

from handlers.song_info import SongInfo

class GuildQueueManager():
    def __init__(self, beatbot):
        self.beatbot = beatbot
        self.song_queues = {}

        download_manager = AudioDownloadManager()
        decision_maker = DownloadDecisionMaker(download_manager)

        self.downloader = YouTubeDownload(decision_maker, download_manager)

#These commands essentially map 1:1 with some of our user commands. 
# !play -> add_song / add_songs_bulk
# !skip -> remove_song
# !clear -> clear
# !queue -> retreive

    def get_guild_queue_object(self, guild_id: int) -> GuildQueue:
        return self.song_queues.setdefault(guild_id, GuildQueue(guild_id))

    async def add_song(self, guild_id: int, url: str, position: int = None) -> None:
        print(Fore.LIGHTCYAN_EX + 'GuildQueueManager.add_song()')
        guild_queue: GuildQueue = self.get_guild_queue_object(guild_id)

        song_info = SongInfo(url = url)
        guild_queue.add_audio(song_info, position)
        await self.trigger_event('song added', guild_id)

    async def add_songs_bulk(self, guild_id: int, urls: list, position: int = None) -> None:
        print(Fore.LIGHTCYAN_EX + 'GuildQueueManager.add_songs_bulk()')
        guild_queue: GuildQueue = self.get_guild_queue_object(guild_id)

        for url in urls:
            print(f'\turl = {url}')
            song_info: SongInfo = SongInfo(url=url)
            guild_queue.add_audio(song_info, position)

        await self.trigger_event('songs added bulk', guild_id)

    async def remove_song(self, guild_id: int, song_index=0) -> SongInfo:
        print(Fore.LIGHTCYAN_EX + 'GuildQueueManager.remove_song()')
        guild_queue: GuildQueue = self.get_guild_queue_object(guild_id)
        
        if not guild_queue:
            print(f"\tNo queue found for guild ID {guild_id}")
            return None

        if not 0 <= song_index < len(guild_queue.queue):
            print(f"Song index {song_index} is out of range for the queue")
            return None

        removed_song: SongInfo = guild_queue.remove_audio(song_index)
        await self.trigger_event('song removed', guild_id)
        return removed_song

    def clear_guild_queue(self, guild_id: int):
        print(Fore.LIGHTCYAN_EX + 'GuildQueueManager.clear()')
        guild_queue: GuildQueue = self.get_guild_queue_object(guild_id)
        if guild_queue:
            guild_queue.clear()
        else:
            print(f"\tNo queue found for guild ID {guild_id}")

#Getters and Setters for GuildQueue
    def retrieve_guild_song_queue(self, guild_id: int) -> list:
        print(Fore.LIGHTCYAN_EX + 'GuildQueueManager.retrieve_guild_queue()')
        guild_queue_object: GuildQueue = self.get_guild_queue_object(guild_id)
        return guild_queue_object.get_queue()

    def retrieve_guild_queue_current_song(self, guild_id: int) -> SongInfo:
        print(Fore.LIGHTCYAN_EX + 'GuildQueueManager.retrieve_guild_queue()')
        guild_queue_object: GuildQueue = self.get_guild_queue_object(guild_id)
        return guild_queue_object.get_current_song()

    def set_guild_queue_current_song(self, guild_id:int, song_info: SongInfo) -> None:
        print(Fore.LIGHTCYAN_EX + 'GuildQueueManager.set_guild_queue_current_song')
        guild_queue_object: GuildQueue = self.get_guild_queue_object(guild_id)
        guild_queue_object.set_current_song(song_info)

# Processing when the queue is updated.
    async def trigger_event(self, event_type: str, guild_id: int) -> None:
        print(Fore.LIGHTCYAN_EX + 'GuildQueueManager.trigger_event()')
        if event_type in ['song added', 'song removed', 'songs added bulk']:
            await self.handle_queue_update(guild_id, event_type)
   
    async def handle_queue_update(self, guild_id: int, event: str) -> None:
        print(Fore.LIGHTCYAN_EX + f'GuildQueueManager.handle_queue_update({guild_id}, {event})')
        guild_queue: dict = self.retrieve_guild_song_queue(guild_id)

        for i, song_info in enumerate(guild_queue[:DOWNLOAD_THRESHOLD]):
            if not isinstance(song_info, SongInfo) or song_info.full_path:
                continue
            await self.process_song(song_info, i)

    async def process_song(self, song_info: SongInfo, iteration: int):
        print(f'GuildQueueManager.process_song()')
        data_handler = YouTubeDataHandler()

        if song_info.url and not song_info.id:
            await data_handler.update_video_data(song_info) #updates a given object

        if not song_info.full_path:
            await self.download_song_if_needed(song_info)

    async def download_song_if_needed(self, song_info: SongInfo):
        print(f'GuildQueueManager.download_song_if_needed()')
        if not song_info.full_path:
            downloaded_file_path = await self.downloader.download_audio(song_info.url, song_info.id, song_info.length)
            if downloaded_file_path:
                song_info.full_path = downloaded_file_path