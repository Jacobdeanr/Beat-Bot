import discord
from colorama import Fore
from commands.base_command import BaseCommand

class ResumeCommand(BaseCommand):
    async def execute(self, message: discord.Message) -> None:
        print(Fore.LIGHTCYAN_EX + '\nResumeCommand.execute()')
        voice_client: discord.VoiceClient = message.guild.voice_client
        if voice_client and voice_client.is_paused():
            voice_client.resume()
            await message.add_reaction("✅")