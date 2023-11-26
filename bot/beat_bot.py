import discord
from colorama import Fore
import asyncio

from util.event_manager import EventManager

from commands.play_command import PlayCommand
from commands.pause_command import PauseCommand
from commands.resume_command import ResumeCommand
from commands.skip_command import SkipCommand
from commands.stop_command import StopCommand
from commands.clear_command import ClearCommand

from commands.join_command import JoinCommand
from commands.disconnect_command import DisconnectCommand

from commands.info_command import InfoCommand
from commands.queue_command import QueueCommand

class BeatBot(discord.Client):
    def __init__(self, intents):
        super().__init__(intents=intents)
        self.guild_queue_manager = None
        self.guild_audio_player_manager = None
        self.event_manager = EventManager()
        self.loop = asyncio.get_event_loop()  # Store the main event loop

    def initialize_commands(self):
        #PlayBack
        self.play_command = PlayCommand(self)
        self.pause_command = PauseCommand(self)
        self.resume_command = ResumeCommand(self)
        self.skip_command = SkipCommand(self)
        self.stop_command = StopCommand(self)
        self.clear_command = ClearCommand(self)
        #Channel
        self.join_command = JoinCommand(self)
        self.disconnect_command = DisconnectCommand(self)
        #Info
        self.info_command = InfoCommand(self)
        self.queue_command = QueueCommand(self)

    def set_managers(self, queue_manager, audio_player_manager):
        self.guild_queue_manager = queue_manager
        self.guild_audio_player_manager = audio_player_manager
        self.initialize_commands()

    def schedule_task(self, coro):
        asyncio.run_coroutine_threadsafe(coro, self.loop)

    async def on_ready(self):
        print(f"Logged in as {self.user.name}")

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return
        await self.handle_command_prefix(message)
    
    async def on_voice_state_update(self, member: discord.Member, before, after):
        if member == self.user and before.channel is not None and after.channel is None:
            print(f"The Bot Left. Good bye!")
            message = self.generate_message_for_disconnect(member.guild)
            await self.disconnect_command.execute(message)

    def generate_message_for_disconnect(self, guild: discord.Guild) -> discord.Message:
        class MockMessage:
            def __init__(self, guild):
                self.guild = guild
                self.channel = discord.utils.get(guild.channels, name='general')

        return MockMessage(guild)

    #User Commands
    async def handle_command_prefix(self, message: discord.Message):
        if message.content.startswith('!'):
            await self.handle_command(message)
        return

    async def handle_command(self, message: discord.Message):
        content = message.content
        text = content.lower()
        guild = message.guild

        commands = {
            '!play': lambda: self.play_command.execute(message),
            '!pause': lambda: self.pause_command.execute(message),
            '!resume': lambda: self.resume_command.execute(message),
            '!skip': lambda: self.skip_command.execute(message),
            '!stop': lambda: self.stop_command.execute(message),
            '!clear': lambda: self.clear_command.execute(message),

            '!join': lambda: self.join_command.execute(message),
            '!disconnect': lambda: self.disconnect_command.execute(message),

            '!info': lambda: self.info_command.execute(message),
            '!queue': lambda: self.queue_command.execute(message),
        }

        # Check if the author is in a voice channel
        if not message.author.voice:
            await message.add_reaction("🚫")
            await message.channel.send(content="I want to be a good bot for you, but you won't hear me unless you connect to a voice channel. Hop in one and try again.", mention_author=True)
            return

        for command, func in commands.items():
            if text.startswith(command):
                try:
                    print(Fore.LIGHTCYAN_EX + '\n-------- New Command --------')
                    print(f'\t{message.author} {content}')
                    print(f'\tguild = {guild}\n')
                    await func()
                except Exception as e:
                    print(f"Error handling {command}: {e}")
                    #await message.channel.send(f"An error {e} occurred while processing the command: {command}")
                break
        return