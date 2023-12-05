import discord

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot.beat_bot import BeatBot
    from managers.guild_queue_manager import GuildQueueManager
    from managers.guild_audio_player_manager import GuildAudioPlayerManager


class BaseCommand:
    def __init__(self, beatbot: 'BeatBot'):
        self.beatbot = beatbot

    @property 
    def guild_queue_manager(self) -> 'GuildQueueManager':
        return self.beatbot.guild_queue_manager
    
    @property 
    def guild_audio_player_manager(self) -> 'GuildAudioPlayerManager':
        return self.beatbot.guild_audio_player_manager

    async def execute(self, message: discord.Message):
        raise NotImplementedError("This method should be overridden in subclasses")