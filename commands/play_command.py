import discord

from colorama import Fore
from commands.base_command import BaseCommand

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot.beat_bot import BeatBot
    from factories.audio_service import AudioServiceFactory

from enum import Enum, auto

class ErrorType(Enum):
    NO_SONG_FOUND = auto()
    CONNECTION_ISSUE = auto()
    WRONG_VOICE_CHANNEL = auto()

class PlayCommand(BaseCommand):
    def __init__(self, beatbot: 'BeatBot'):
        super().__init__(beatbot)
        self.audio_service_factory: 'AudioServiceFactory' = beatbot.audio_service_factory

    async def execute(self, message: discord.Message) -> None:
        print(Fore.LIGHTCYAN_EX + '\nPlayCommand.execute()')
        guild_id = message.guild.id

        author_voice_channel = message.author.voice.channel if message.author.voice else None
        if not author_voice_channel:
            await self.handle_error(message, ErrorType.WRONG_VOICE_CHANNEL)
            return

        if not self.guild_audio_player_manager.is_player_in_correct_channel(guild_id, author_voice_channel):
            if not await self.guild_audio_player_manager.connect_player_to_channel(guild_id, author_voice_channel):
                await self.handle_error(message, ErrorType.CONNECTION_ISSUE)
                return

        video_list = self.process_song_request(message)
        if not video_list:
            await self.handle_error(message, ErrorType.NO_SONG_FOUND)
            return

        await self.add_songs_to_queue(video_list, message)
        await self.guild_audio_player_manager.play_audio_if_not_playing(guild_id)

    def process_song_request(self, message: discord.Message) -> list:
        print(Fore.LIGHTCYAN_EX + '\nPlayCommand.process_song_request()')
        query = message.content.replace('!play', '').strip()

        audio_service = self.audio_service_factory.get_service(query)
        if not audio_service:
            audio_service = self.audio_service_factory.get_default_service()

        return audio_service.search_song(query)

    async def add_songs_to_queue(self, video_list: list, message: discord.Message):
        self.guild_queue_manager.add_songs_bulk(message.guild.id, video_list)
        await message.add_reaction("✅")

    async def handle_error(self, message: discord.Message, error_type: ErrorType):
        error_messages = {
            ErrorType.NO_SONG_FOUND: "Well, this is awkward... It looks like your tastes are so unique, I can't even come close to finding that.",
            ErrorType.CONNECTION_ISSUE: "I'm having trouble connecting to the voice channel.",
            ErrorType.WRONG_VOICE_CHANNEL: "I'm hanging out in a different voice channel. Come join when you're ready to party!"
        }

        await message.add_reaction("🚫")
        await message.channel.send(error_messages.get(error_type, "An unknown error occurred."))