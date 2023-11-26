import asyncio
import discord
from colorama import Fore
from handlers.guild_audio_player import GuildAudioPlayer

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot.beat_bot import BeatBot
    from managers.guild_queue_manager import GuildQueueManager

class GuildAudioPlayerManager:
    def __init__(self, beatbot: 'BeatBot'):
        self.beatbot = beatbot
        self.audio_players = {}

    
    def get_guild_audio_player(self, guild_id: int) -> GuildAudioPlayer:
        print(Fore.LIGHTCYAN_EX + 'GuildAudioPlayerManager.get_guild_audio_player()')
        return self.audio_players.setdefault(guild_id, GuildAudioPlayer(guild_id,self.handle_after_play))

    def stop_song(self, guild_id: int) -> None:
        print(Fore.LIGHTCYAN_EX + 'GuildAudioPlayerManager.stop_song()')
        audio_player: GuildAudioPlayer = self.get_guild_audio_player(guild_id)
        if audio_player.voice_client:
            audio_player.voice_client.stop()

    def skip_song(self, guild_id: int) -> None:
        audio_player: GuildAudioPlayer = self.get_guild_audio_player(guild_id)
        audio_player.skip()
        self.beatbot.schedule_task(self.play_next_song(guild_id))

    def disconnect_from_channel(self, guild_id: int) -> None:
        print(Fore.LIGHTCYAN_EX + 'GuildAudioPlayerManager.disconnect_from_channel()')
        audio_player: GuildAudioPlayer = self.get_guild_audio_player(guild_id)
        asyncio.create_task(audio_player.disconnect_from_voice_client())

    def handle_after_play(self, guild_id) -> None:
        print(Fore.LIGHTCYAN_EX + 'GuildAudioPlayerManager.handle_after_play()')
        self.beatbot.schedule_task(self.play_next_song(guild_id))
        
    @property 
    def guild_queue_manager(self) -> 'GuildQueueManager':
        return self.beatbot.guild_queue_manager
    
    async def play_next_song(self, guild_id: int) -> None:
        print(Fore.LIGHTCYAN_EX + 'GuildAudioPlayerManager.play_next_song()')
        item_to_play = await self.guild_queue_manager.remove_song(guild_id)
        if item_to_play:
            self.play_audio(guild_id, item_to_play)
        else:
            print('No more songs to play!')

    async def play_audio_if_not_playing(self, guild_id: int) -> None:
        print(Fore.LIGHTCYAN_EX + 'GuildAudioPlayerManager.play_audio_if_not_playing()')
        guild_audio_player: GuildAudioPlayer = self.get_guild_audio_player(guild_id)
        print(guild_audio_player)
        if not guild_audio_player.voice_client.is_playing():
            if self.guild_queue_manager is not None:
                song_to_play = await self.guild_queue_manager.remove_song(guild_id)
                if song_to_play:
                    self.play_audio(guild_id, song_to_play)
            else:
                print("Error: guild_queue_manager is not initialized.")

    def play_audio(self, guild_id: int, song_info) -> None:
        print(Fore.LIGHTCYAN_EX + 'GuildAudioPlayerManager.play_audio()')
        audio_player: GuildAudioPlayer = self.get_guild_audio_player(guild_id)
        audio_player.play_audio(song_info)
        self.guild_queue_manager.set_guild_queue_current_song(guild_id, song_info)
    
    def  is_player_in_correct_channel(self, guild_id: int, author_voice_channel: discord.VoiceChannel) -> bool:
        print(Fore.LIGHTCYAN_EX + 'GuildAudioPlayerManager.is_player_in_correct_channel()')
        guild_audio_player: GuildAudioPlayer = self.get_guild_audio_player(guild_id)
        return guild_audio_player.is_connected() and guild_audio_player.is_in_voice_channel(author_voice_channel)
    
    async def connect_player_to_channel(self, guild_id: int, voice_channel: discord.VoiceChannel) -> bool:
        print(Fore.LIGHTCYAN_EX + 'GuildAudioPlayerManager.connect_player_to_channel()')
        guild_audio_player = self.get_guild_audio_player(guild_id)
        if not guild_audio_player.is_connected():
            return await guild_audio_player.connect_to_voice_channel(voice_channel)
        return True