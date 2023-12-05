import asyncio
import discord
from colorama import Fore
from handlers.guild_audio_player import GuildAudioPlayer
from managers.guild_queue_manager import GuildQueueManager

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot.beat_bot import BeatBot

class GuildAudioPlayerManager:
    def __init__(self, beatbot: 'BeatBot'):
        self.beatbot = beatbot
        self.audio_players = {}

    def get_guild_audio_player(self, guild_id: int) -> GuildAudioPlayer:
        print(Fore.LIGHTCYAN_EX + f'GuildAudioPlayerManager.get_guild_audio_player({guild_id})')
        gq_ap = self.audio_players.setdefault(guild_id, GuildAudioPlayer(guild_id,self.handle_after_play))
        return gq_ap

    def stop_song(self, guild_id: int) -> None:
        print(Fore.LIGHTCYAN_EX + f'GuildAudioPlayerManager.stop_song({guild_id})')
        audio_player: GuildAudioPlayer = self.get_guild_audio_player(guild_id)
        if audio_player.voice_client:
            audio_player.voice_client.stop()

    def skip_song(self, guild_id: int) -> None:
        print(Fore.LIGHTCYAN_EX + f'GuildAudioPlayerManager.skip_song({guild_id})')
        audio_player: GuildAudioPlayer = self.get_guild_audio_player(guild_id)
        audio_player.skip()
        self.beatbot.schedule_task(self.play_next_song(guild_id))

    def disconnect_from_channel(self, guild_id: int) -> None:
        print(Fore.LIGHTCYAN_EX + f'GuildAudioPlayerManager.disconnect_from_channel({guild_id})')
        audio_player: GuildAudioPlayer = self.get_guild_audio_player(guild_id)
        asyncio.create_task(audio_player.disconnect_from_voice_client())

    def handle_after_play(self, guild_id) -> None:
        print(Fore.LIGHTCYAN_EX + f'GuildAudioPlayerManager.handle_after_play({guild_id})')
        self.beatbot.schedule_task(self.play_next_song(guild_id))
       
    #These interact with the GuildQueueManager 
    async def play_next_song(self, guild_id: int) -> None:
        print(Fore.LIGHTCYAN_EX + f'GuildAudioPlayerManager.play_next_song({guild_id})')
        item_to_play = self.beatbot.guild_queue_manager.remove_song_and_update_queue(guild_id)
        if item_to_play:
            self.play_audio(guild_id, item_to_play)
        else:
            print('No more songs to play!')
            self.disconnect_from_channel(guild_id)

    async def play_audio_if_not_playing(self, guild_id: int) -> None:
        print(Fore.LIGHTCYAN_EX + f'GuildAudioPlayerManager.play_audio_if_not_playing({guild_id})')
        guild_audio_player: GuildAudioPlayer = self.get_guild_audio_player(guild_id)
        if not guild_audio_player.voice_client.is_playing():
            if self.beatbot.guild_queue_manager is not None:
                song_to_play = self.beatbot.guild_queue_manager.remove_song_and_update_queue(guild_id)
                if song_to_play:
                    self.play_audio(guild_id, song_to_play)
            else:
                print("guild_queue_manager is not initalized.")
        else:
            print("Bot already playing")

    def play_audio(self, guild_id: int, song_info) -> None:
        print(Fore.LIGHTCYAN_EX + f'GuildAudioPlayerManager.play_audio({guild_id})')
        audio_player: GuildAudioPlayer = self.get_guild_audio_player(guild_id)
        audio_player.play_audio(song_info)
        self.beatbot.guild_queue_manager.set_guild_queue_current_song(guild_id, song_info)

#Logical checks
    def is_player_in_correct_channel(self, guild_id: int, author_voice_channel: discord.VoiceChannel) -> bool:
        print(Fore.LIGHTCYAN_EX + f'GuildAudioPlayerManager.is_player_in_correct_channel({guild_id})')
        guild_audio_player: GuildAudioPlayer = self.get_guild_audio_player(guild_id)
        return guild_audio_player.is_connected() and guild_audio_player.is_in_voice_channel(author_voice_channel)
    
    async def connect_player_to_channel(self, guild_id: int, voice_channel: discord.VoiceChannel) -> bool:
        print(Fore.LIGHTCYAN_EX + f'GuildAudioPlayerManager.connect_player_to_channel({guild_id})')
        guild_audio_player = self.get_guild_audio_player(guild_id)
        if not guild_audio_player.is_connected():
            return await guild_audio_player.connect_to_voice_channel(voice_channel)
        return True