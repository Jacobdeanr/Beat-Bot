import discord
import datetime
from colorama import Fore

from commands.base_command import BaseCommand

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot.beat_bot import BeatBot
    from factories.audio_service import AudioServiceFactory

class InfoCommand(BaseCommand):
    def __init__(self, beatbot: 'BeatBot'):
        super().__init__(beatbot)
        self.audio_service_factory: 'AudioServiceFactory' = beatbot.audio_service_factory

    async def execute(self, message: discord.Message) -> None:
        print(Fore.LIGHTCYAN_EX + '\nInfoCommand.execute()')
        guild_id: int = message.guild.id

        current_song = self.guild_queue_manager.retrieve_guild_queue_current_song(guild_id)

        if current_song and current_song.url:
            await message.add_reaction("🔎")

            # Use the audio service factory to get the appropriate service
            audio_service = self.audio_service_factory.get_service(current_song.url)
            if not audio_service:
                audio_service = self.audio_service_factory.get_default_service()

            # Update song info if necessary
            if not current_song.title:
                audio_service.update_song_info(current_song)
            print(current_song)

            # Prepare and send the message
            channel_name = current_song.channel_name or "Unknown"
            title = current_song.title or "Unknown Title"
            duration = self.format_seconds_to_hms(current_song.length or 0)
            publish_date = self.format_publish_date(current_song.publish_date)

            await message.channel.send(
                f"Currently Playing: `{channel_name} - {title} ({duration})`\n"
                f"Published on: `{publish_date}`\n"
                f"Link: <{current_song.url}>"
            )
        else:
            print(f'\tNo song is currently playing in guild {guild_id}.')
            await message.add_reaction("❌")

    def format_seconds_to_hms(self, seconds) -> str:
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02}:{m:02}:{s:02}" if h > 0 else f"{m:02}:{s:02}"

    def format_publish_date(self, publish_date):
        if publish_date:
            return datetime.datetime.strftime(publish_date, "%m/%d/%Y")
        return "Unknown"