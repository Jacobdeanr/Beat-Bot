import discord
from colorama import Fore
from commands.base_command import BaseCommand

class PauseCommand(BaseCommand):
    async def execute(self, message: discord.Message) -> None:
        voice_client: discord.VoiceClient = message.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            await message.add_reaction("✅")
        else:
            await message.add_reaction("❌")