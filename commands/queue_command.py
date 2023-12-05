import discord
from colorama import Fore
from commands.base_command import BaseCommand

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot.beat_bot import BeatBot
    from factories.audio_service import AudioServiceFactory

class QueueCommand(BaseCommand):
    def __init__(self, beatbot: 'BeatBot'):
        super().__init__(beatbot)
        self.audio_service_factory: 'AudioServiceFactory' = beatbot.audio_service_factory

    async def execute(self, message: discord.Message) -> None:
        print(Fore.LIGHTCYAN_EX + '\nQueueCommand.execute()')
        guild_id = message.guild.id

        queue = self.guild_queue_manager.retrieve_guild_song_queue(guild_id)

        if not queue:
            await message.add_reaction("❌")
            await message.channel.send('Queue is empty! 😬')
            return

        await message.add_reaction("✅")
        message_to_send = self.construct_queue_message(queue)
        await message.channel.send(f'Songs in queue: `{len(queue)}`\nUp Next: \n{message_to_send}')

    def construct_queue_message(self, queue) -> str:
        message_parts = []
        for song_info in queue[:5]:  # Assuming you're displaying the first 5 songs

            title = song_info.title or "Unknown Title"
            channel_name = song_info.channel_name or "Unknown"
            formatted_length = self.format_seconds_to_hms(song_info.length or 0)
            url = song_info.url or "#"

            message_part = f"`{channel_name} - {title} ({formatted_length})` - <{url}>"
            message_parts.append(message_part)

        return "\n".join(message_parts)

    def format_seconds_to_hms(self, seconds) -> str:
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02}:{m:02}:{s:02}" if h > 0 else f"{m:02}:{s:02}"