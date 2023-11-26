import discord
from colorama import Fore
from commands.base_command import BaseCommand

class ClearCommand(BaseCommand):
    async def execute(self, message: discord.Message) -> None:
        print(Fore.LIGHTCYAN_EX + '\nClearCommand.execute()')
        guild_id: int = message.guild.id
        voice_client: discord.VoiceClient = message.guild.voice_client
        self.guild_queue_manager.clear_guild_queue(guild_id)     

        if voice_client.is_playing():
            voice_client.stop()
            await message.add_reaction("💥")