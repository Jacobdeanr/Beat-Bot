import discord
from colorama import Fore
from commands.base_command import BaseCommand

class SkipCommand(BaseCommand):
    async def execute(self, message: discord.Message) -> None:
        print(Fore.LIGHTCYAN_EX + '\nSkipCommand.execute()')
        guild_id = message.guild.id

        audio_player_manager = self.beatbot.guild_audio_player_manager

        if audio_player_manager.is_player_in_correct_channel(guild_id, message.author.voice.channel):
            audio_player_manager.skip_song(guild_id)
            await message.add_reaction("✅")
        else:
            print('Player not in the correct channel or nothing playing')
            await message.add_reaction("❌")
