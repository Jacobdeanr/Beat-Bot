from colorama import Fore

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot.beat_bot import BeatBot
    import discord

class MessageParser:
    def __init__(self, bot: 'BeatBot'):
        self.bot = bot
        self.commands = {
            '!play': bot.play_command,
            '!pause': bot.pause_command,
            '!resume': bot.resume_command,
            '!skip': bot.skip_command,
            '!stop': bot.stop_command,
            '!clear': bot.clear_command,
            '!join': bot.join_command,
            '!disconnect': bot.disconnect_command,
            '!info': bot.info_command,
            '!queue': bot.queue_command
        }

    async def parse(self, message: 'discord.Message'):
        if not message.content.startswith('!'):
            return

        # Check if the author is in a voice channel
        if not message.author.voice:
            await message.add_reaction("🚫")
            await message.channel.send("I want to be a good bot for you, but you can't control me unless you're connected to a voice channel. Hop in one and try again.", mention_author=True)
            return

        command = message.content.split(' ')[0].lower()
        if command in self.commands:
            try:
                print(Fore.LIGHTCYAN_EX + '\n-------- New Command --------')
                print(f'\t{message.author} {command}')
                print(f'\tguild = {message.guild}\n')
                await self.commands[command].execute(message)
            except Exception as e:
                print(f"Error handling {command}: {e}")
                # Optionally send a message back to the channel
                # await message.channel.send(f"An error occurred while processing the command: {command}")