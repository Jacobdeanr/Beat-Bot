from colorama import Fore
from handlers.song_info import SongInfo

class GuildQueue:
    def __init__(self, guild_id):
        self.queue = []
        self.current_song: SongInfo = None

    def __str__(self):
        queue_str = ", ".join(str(song) for song in self.queue)
        current_song_str = str(self.current_song)
        return Fore.LIGHTYELLOW_EX + f'\nSong Queue: {queue_str}'+ Fore.LIGHTBLUE_EX + f'\nCurrent Song: {current_song_str}'

    def add_audio(self, song_info: SongInfo, position: int = None) -> None:
        print(Fore.LIGHTCYAN_EX+'GuildQueue.add_audio()')
        if position is not None and 0 <= position < len(self.queue):
            self.queue.insert(position, song_info)
        else:
            self.queue.append(song_info)

    def remove_audio(self, index: int) -> SongInfo:
        print(Fore.LIGHTCYAN_EX+'GuildQueue.remove_audio()')
        if 0 <= index < len(self.queue):
            return self.queue.pop(index)
        return None
    
    def clear(self) -> None: 
        print(Fore.LIGHTCYAN_EX+'GuildQueue.clear()')
        self.queue = []
    
    def get_queue(self) -> list:
        print(Fore.LIGHTCYAN_EX+'GuildQueue.get_queue()')
        return self.queue
    
    def get_current_song(self) -> SongInfo:
        print(Fore.LIGHTCYAN_EX+'GuildQueue.get_current_song()')
        return self.current_song
    
    def set_current_song(self, song_info) -> None:
        print(Fore.LIGHTCYAN_EX+'GuildQueue.set_current_song()')
        self.current_song = song_info