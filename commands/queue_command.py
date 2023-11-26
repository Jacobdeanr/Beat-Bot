import discord
from colorama import Fore
from commands.base_command import BaseCommand

from handlers.youtube.youtube_data_handler import YouTubeDataHandler

class QueueCommand(BaseCommand):
    def __init__(self, beatbot):
        super().__init__(beatbot)
        self.song_data_handler = YouTubeDataHandler()

    async def execute(self, message: discord.Message) -> None:
        print(Fore.LIGHTCYAN_EX + '\nQueueCommand.execute()')
        guild_id=message.guild.id

        queue = self.guild_queue_manager.retrieve_guild_song_queue(guild_id)

        if not queue:
            await message.add_reaction("❌")
            await message.channel.send('Queue is empty! 😬')
            return

        await message.add_reaction("✅")
        message_to_send = await self.construct_queue_message(queue)
        await message.channel.send(f'Songs in queue: `{len(queue)}`\nUp Next: \n{message_to_send}')

    async def construct_queue_message(self, queue) -> str:
        message_parts = []
        for song_info in queue[:5]:
            if not song_info.title:
                await self.song_data_handler.update_video_information(song_info)

            title = song_info.title
            url = song_info.url
            channel_name = song_info.channel_name
            formatted_length = self.format_seconds_to_hms(song_info.length)
            message_part = f"`{channel_name} - {title} ({formatted_length})` - <{url}>"
            message_parts.append(message_part)

        return "\n".join(message_parts)

    def format_seconds_to_hms(self,seconds) -> str:
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        if h > 0:
            return f"{h:02}:{m:02}:{s:02}"
        else:
            return f"{m:02}:{s:02}"