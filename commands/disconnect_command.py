import discord
from colorama import Fore
from commands.base_command import BaseCommand

class DisconnectCommand(BaseCommand):
    async def execute(self, message: discord.Message) -> None:
        print(Fore.LIGHTCYAN_EX + '\nDisconnectCommand.execute()')
        guild_id = message.guild.id
        voice_client: discord.VoiceClient = message.guild.voice_client
        self.guild_queue_manager.clear_guild_queue(guild_id)
        if voice_client:
            await voice_client.disconnect()
            await message.add_reaction("😢")