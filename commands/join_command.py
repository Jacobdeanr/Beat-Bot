import discord
from colorama import Fore
from commands.base_command import BaseCommand

class JoinCommand(BaseCommand):
    async def execute(self, message: discord.Message) -> None:
        print(Fore.LIGHTCYAN_EX + '\nJoinCommand.execute()')
        author_voice_channel = message.author.voice.channel if message.author.voice else None
        
        if await self.guild_audio_player_manager.connect_player_to_channel(message.guild.id, author_voice_channel):
            await message.add_reaction("👋")