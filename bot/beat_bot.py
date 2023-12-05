import discord
import asyncio

from util.event_manager import EventManager
from handlers.message_parser import MessageParser

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
        self.audio_download_manager = None
        self.audio_service_factory = None
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

    def set_managers(self, queue_manager, audio_player_manager, audio_service_factory, download_manager):
        self.guild_queue_manager = queue_manager
        self.guild_audio_player_manager = audio_player_manager
        self.audio_download_manager = download_manager
        self.audio_service_factory = audio_service_factory
        self.initialize_commands()

    def schedule_task(self, coro):
        asyncio.run_coroutine_threadsafe(coro, self.loop)

    async def on_ready(self):
        print(f"Logged in as {self.user.name}")

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return
        await self.handle_message(message)

    async def handle_message(self, message: discord.Message):
        parser = MessageParser(self)
        await parser.parse(message)
    
    async def on_voice_state_update(self, member: discord.Member, before, after):
        if member == self.user and before.channel is not None and after.channel is None:
            print(f"The Bot Left. Good bye!")