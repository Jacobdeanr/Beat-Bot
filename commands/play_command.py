import discord

from colorama import Fore
from commands.base_command import BaseCommand

from handlers.youtube.youtube_data_handler import YouTubeDataHandler
from handlers.youtube.youtube_search_handler import YouTubeSearchHandler
from handlers.youtube.youtube_url_handler import YouTubeURLHandler

from enum import Enum, auto

class ErrorType(Enum):
    NO_SONG_FOUND = auto()
    CONNECTION_ISSUE = auto()
    WRONG_VOICE_CHANNEL = auto()

class PlayCommand(BaseCommand):
    def __init__(self, beatbot):
        super().__init__(beatbot)
        self.beatbot = beatbot
        self.song_data_handler = YouTubeDataHandler()
        self.search_handler = YouTubeSearchHandler()
        self.guild_id = None

    async def execute(self, message: discord.Message) -> None:
        self.log_execution()
        self.guild_id = message.guild.id

        author_voice_channel = message.author.voice.channel if message.author.voice else None
        if not author_voice_channel:
            await self.handle_error(message, ErrorType.WRONG_VOICE_CHANNEL)
            return

        if not self.guild_audio_player_manager.is_player_in_correct_channel(self.guild_id, author_voice_channel):
            if not await self.guild_audio_player_manager.connect_player_to_channel(self.guild_id, author_voice_channel):
                await self.handle_error(message, ErrorType.CONNECTION_ISSUE)
                return

        video_list = await self.process_song_request(message)
        if not video_list:
            await self.handle_error(message, ErrorType.NO_SONG_FOUND)
            return

        await self.add_songs_to_queue(video_list, message)
        await self.guild_audio_player_manager.play_audio_if_not_playing(self.guild_id)


    def log_execution(self):
        print(Fore.LIGHTCYAN_EX + '\nPlayCommand.execute()')

    async def process_song_request(self, message: discord.Message) -> list:
        query = message.content.replace('!play', '').strip()
        watch_url: str = await self.song_data_handler.validate_url(query)

        if not watch_url:
            query: str = await self.search_handler.search_for_one_song(query)
        if query:
            if YouTubeURLHandler.is_playlist_url(query):
                # Process as playlist URL
                return await self.song_data_handler.get_playlist_video_urls(query)
            else:
                # Process as single song URL
                return [query]
        return []

    async def add_songs_to_queue(self, video_list: list, message: discord.Message):
        await self.guild_queue_manager.add_songs_bulk(self.guild_id, video_list)
        await message.add_reaction("✅")

    async def handle_error(self, message: discord.Message, error_type: ErrorType):
        error_messages = {
            ErrorType.NO_SONG_FOUND: "Well, this is awkward... It looks like your tastes are so unique, I can't even come close to finding that.",
            ErrorType.CONNECTION_ISSUE: "I'm having trouble connecting to the voice channel.",
            ErrorType.WRONG_VOICE_CHANNEL: "I'm hanging out in a different voice channel. Come join when you're ready to party!"
        }

        await message.add_reaction("🚫")
        await message.channel.send(error_messages.get(error_type, "An unknown error occurred."))