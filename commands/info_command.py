import discord
import datetime
from colorama import Fore

from commands.base_command import BaseCommand

from handlers.youtube.youtube_data_handler import YouTubeDataHandler
from handlers.youtube.youtube_search_handler import YouTubeSearchHandler

class InfoCommand(BaseCommand):
    def __init__(self, beatbot):
        super().__init__(beatbot)
        self.song_data_handler = YouTubeDataHandler()
        self.search_handler = YouTubeSearchHandler()

    async def execute(self, message: discord.Message) -> None:
        print(Fore.LIGHTCYAN_EX + '\nInfoCommand.execute()')
        guild_id: int = message.guild.id
        
        current_song = self.guild_queue_manager.retrieve_guild_queue_current_song(guild_id)
    
        if current_song and current_song.url:
            await message.add_reaction("🔎")

            if not current_song.title:
                await self.song_data_handler.update_video_information(current_song)

            channel_name: str = current_song.channel_name
            title: str = current_song.title
            length: int = current_song.length
            url: str = current_song.url
            org_pub_date:datetime = current_song.publish_date

            publish_date: str = datetime.datetime.strptime(str(org_pub_date), "%Y-%m-%d %H:%M:%S").strftime("%m/%d/%Y")
            print(f'Current Song Length = {length}')
            duration = self.format_seconds_to_hms(length)

            await message.channel.send(f"Currently Playing: `{channel_name} - {title} ({duration})`\nPublished on: `{publish_date}`\nLink: <{url}>")
        else:
            print(f'\tNo song is currently playing in guild {guild_id}.')
            await message.add_reaction("❌")

    def format_seconds_to_hms(self, seconds) -> None:
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        if h > 0:
            return f"{h:02}:{m:02}:{s:02}"
        else:
            return f"{m:02}:{s:02}"