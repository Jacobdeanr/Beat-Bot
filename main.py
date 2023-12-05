import discord
from colorama import init
from bot.beat_bot import BeatBot
from managers.guild_queue_manager import GuildQueueManager
from managers.guild_audio_player_manager import GuildAudioPlayerManager
from managers.audio_download_manager import AudioDownloadManager
from factories.audio_service import AudioServiceFactory

def read_token():
    with open('token.txt', 'r') as file:
        return file.read().strip()
    
intents = discord.Intents.default()
intents.message_content = True

init(autoreset=True)

beatbot = BeatBot(intents)
guild_queue_manager = GuildQueueManager(beatbot)
guild_audio_player_manager = GuildAudioPlayerManager(beatbot)
audio_download_manager = AudioDownloadManager()
audio_service_factory = AudioServiceFactory()

beatbot.set_managers(queue_manager=guild_queue_manager, audio_player_manager=guild_audio_player_manager, audio_service_factory=audio_service_factory, download_manager=audio_download_manager)
beatbot.run(read_token())