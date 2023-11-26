import discord
from colorama import init
from bot.beat_bot import BeatBot
from managers.guild_queue_manager import GuildQueueManager
from managers.guild_audio_player_manager import GuildAudioPlayerManager

def read_token():
    with open('token.txt', 'r') as file:
        return file.read().strip()
    
intents = discord.Intents.default()
intents.message_content = True

init(autoreset=True)

beatbot = BeatBot(intents)
guild_queue_manager = GuildQueueManager(beatbot)
guild_audio_player_manager = GuildAudioPlayerManager(beatbot)

beatbot.set_managers(guild_queue_manager, guild_audio_player_manager)
beatbot.run(read_token())