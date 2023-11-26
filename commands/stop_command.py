import discord
from colorama import Fore
from commands.base_command import BaseCommand

class StopCommand(BaseCommand):
    async def execute(self, message: discord.Message) -> None:
        print(Fore.LIGHTCYAN_EX + '\nStopCommand.execute()')
        guild_id = message.guild.id
        voice_client: discord.VoiceClient = message.guild.voice_client
        if voice_client:
            if voice_client.is_playing():
                self.guild_queue_manager.clear_guild_queue(guild_id)
                voice_client.stop()
            await message.add_reaction("🛑")