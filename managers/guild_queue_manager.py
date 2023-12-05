from colorama import Fore
from config import DOWNLOAD_THRESHOLD, VIDEO_MAX_LENGTH
from concurrent.futures import ThreadPoolExecutor, as_completed

from handlers.guild_queue import GuildQueue

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot.beat_bot import BeatBot
    from factories.audio_service import AudioServiceFactory

from models.song_info import SongInfo

class GuildQueueManager():
    def __init__(self, beatbot: 'BeatBot'):
        self.beatbot: 'BeatBot' = beatbot
        self.song_queues = {}
        self.audio_service_factory: 'AudioServiceFactory' = beatbot.audio_service_factory

    def get_guild_queue_by_id(self, guild_id: int) -> GuildQueue:
        print(Fore.LIGHTCYAN_EX + 'GuildQueueManager.get_guild_queue_by_id()')
        guildqueue = self.song_queues.setdefault(guild_id, GuildQueue())
        return guildqueue

    def add_songs_bulk(self, guild_id: int, urls: list, position: int = None) -> None:
        print(Fore.LIGHTCYAN_EX + 'GuildQueueManager.add_songs_bulk()')
        guild_queue_object: GuildQueue = self.get_guild_queue_by_id(guild_id)

        for url in urls:
            song_info: SongInfo = SongInfo(url=url)
            guild_queue_object.add_audio(song_info, position)

        self.handle_queue_update(guild_queue_object)

    def remove_song_and_update_queue(self, guild_id: int, song_index=0) -> SongInfo:
        print(Fore.LIGHTCYAN_EX + 'GuildQueueManager.remove_song()')
        guild_queue_object: GuildQueue = self.get_guild_queue_by_id(guild_id)

        if not 0 <= song_index < len(guild_queue_object.queue):
            return None

        removed_song: SongInfo = guild_queue_object.remove_audio(song_index)
        self.handle_queue_update(guild_queue_object)
        return removed_song

    def clear_guild_queue(self, guild_id: int):
        print(Fore.LIGHTCYAN_EX + 'GuildQueueManager.clear()')
        guild_queue_object: GuildQueue = self.get_guild_queue_by_id(guild_id)
        guild_queue_object.clear()

#Getters and Setters for GuildQueue
    def retrieve_guild_song_queue(self, guild_id: int) -> list:
        print(Fore.LIGHTCYAN_EX + 'GuildQueueManager.retrieve_guild_queue()')
        guild_queue_object: GuildQueue = self.get_guild_queue_by_id(guild_id)
        return guild_queue_object.get_queue()

    def retrieve_guild_queue_current_song(self, guild_id: int) -> SongInfo:
        print(Fore.LIGHTCYAN_EX + 'GuildQueueManager.retrieve_guild_queue()')
        guild_queue_object: GuildQueue = self.get_guild_queue_by_id(guild_id)
        return guild_queue_object.get_current_song()

    def set_guild_queue_current_song(self, guild_id:int, song_info: SongInfo) -> None:
        print(Fore.LIGHTCYAN_EX + 'GuildQueueManager.set_guild_queue_current_song')
        guild_queue_object: GuildQueue = self.get_guild_queue_by_id(guild_id)
        guild_queue_object.set_current_song(song_info)

#None of these interact with the guildqueue. Only on SongInfo objects.
#Stop gap to prevent hundreds of songs to be downloaded at once.  
    def handle_queue_update(self, guild_queue: GuildQueue):
        print(Fore.LIGHTCYAN_EX + f'GuildQueueManager.handle_queue_update()')
        results = []

        with ThreadPoolExecutor(max_workers=5) as executor:
            # Access the queue attribute of guild_queue
            futures = []
            for song in guild_queue.queue[:DOWNLOAD_THRESHOLD]:
                if not song.full_path:
                    future = executor.submit(self.process_song, song)
                    futures.append(future)

            # Wait for all futures to complete
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as exc:
                    print(f'Song processing generated an exception: {exc}')

        # Process the results
        for was_successful in results:
            if was_successful:
                print(f"Processing completed successfully.")
            else:
                print(f"Processing failed or was refused.")
        return all(results)

#Actually updates a given SongInfo object.
    def process_song(self, song_info: SongInfo) -> bool:
        print(Fore.LIGHTCYAN_EX + 'GuildQueueManager.process_song()')

        audio_service = self.beatbot.audio_service_factory.get_service(song_info.url)
        if not audio_service:
            audio_service = self.beatbot.audio_service_factory.get_default_service()

        # Update video data
        if song_info.url and not song_info.id:
            audio_service.update_song_info(song_info)
        
        if song_info.length > VIDEO_MAX_LENGTH:
            print(f'Refuse Downloading. Duration is too long!')
            return False

        # Download the song if needed
        if not song_info.full_path:
            self.download_song_if_needed(song_info, audio_service)
        return True

    def download_song_if_needed(self, song_info: SongInfo, audio_service) -> None:
        print(Fore.LIGHTCYAN_EX + 'GuildQueueManager.download_song_if_needed()')
        if not song_info.full_path:
            downloaded_file_path = audio_service.download_song(song_info.url, song_info.id, song_info.length)
            if downloaded_file_path:
                song_info.update_song_info(full_path=downloaded_file_path)