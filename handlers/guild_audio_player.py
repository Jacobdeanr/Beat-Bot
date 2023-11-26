import discord
from colorama import Fore
from handlers.song_info import SongInfo

class GuildAudioPlayer:
    def __init__(self, guild_id: int, after_play_callback):
        self.guild_id = guild_id
        self.voice_client: discord.VoiceClient = None
        self.voice_channel: discord.VoiceChannel = None
        self.after_play_callback = after_play_callback
        self.is_skipping = False  # Flag to indicate if a song is being skipped

    async def connect_to_voice_channel(self, voice_channel: discord.VoiceChannel) -> bool:
        print(Fore.LIGHTCYAN_EX + 'GuildAudioPlayer.connect_to_voice_channel()')
        try:
            self.voice_client = await voice_channel.connect()
            self.voice_channel = voice_channel
            return True
        except Exception as e:
            print('unable to connect to a voice channel')
            return False

    async def disconnect_from_voice_client(self) -> bool:
        print(Fore.LIGHTCYAN_EX + 'GuildAudioPlayer.disconnect_from_voice_client()')
        try:
            await self.voice_client.disconnect()
            return True
        except Exception as e:
            print(f'unable to disconnect from a voice client: {e}')
            return False
        
    def skip(self):
        print(Fore.LIGHTCYAN_EX + 'GuildAudioPlayer.skip()')
        if self.voice_client and self.voice_client.is_playing():
            self.is_skipping = True
            self.voice_client.stop()

    def play_audio(self, song_info: SongInfo) -> None:
        print(Fore.LIGHTCYAN_EX + 'GuildAudioPlayer.play_audio()')
        if self.voice_client and not self.voice_client.is_playing():
            try:
                print(f'\tNow playing: {song_info.full_path}')
                source = discord.FFmpegPCMAudio(song_info.full_path, executable="ffmpeg")
                self.voice_client.play(source, after=lambda e: self.after_play())
            except Exception as e:
                print(f"\tError playing audio in guild {self.guild_id}: {e}")
        else:
            print('Bot is either not in a voice channel, or it is playing.')

    def after_play(self):
        print(Fore.LIGHTCYAN_EX + 'GuildAudioPlayer.after_play()')
        if not self.is_skipping and self.after_play_callback:
            self.after_play_callback(self.guild_id)
        self.is_skipping = False

    def is_connected(self) -> bool:
        print(Fore.LIGHTCYAN_EX + 'GuildAudioPlayer.is_connected()')
        return self.voice_client and self.voice_client.is_connected()

    def is_in_voice_channel(self, voice_channel: discord.VoiceChannel) -> bool:
        print(Fore.LIGHTCYAN_EX + 'GuildAudioPlayer.is_in_voice_channel()')
        return self.voice_channel == voice_channel