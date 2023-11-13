import discord
import asyncio
from Search.Youtube.YouTubeSearchHandler import YouTubeSearchHandler
from Search.Youtube.YouTubeURLHandler import YouTubeURLHandler
from Search.Youtube.YouTubeDataHandler import YouTubeDataHandler
from Control.queuecontrol import QueueControl
from discord import VoiceChannel, TextChannel
from colorama import Fore, Back, Style

class BotCommands:
    _event_loop = None
    current_songs = {}  # Dictionary to store current song for each guild
    is_playing = {}  # A dictionary to track playing state for each guild

    @staticmethod
    def set_event_loop(loop):
        BotCommands._event_loop = loop

    # play command is tricky. It's actually used more of a search, or request, and playback begin function.
    # an example of how it will be used:
    # 1. !play mac miller small worlds
    # 2. !play https://www.youtube.com/watch?v=VzAjXdBJsEc&list=PLb23bTgg3GgWKc53aZ-GAhED0G6iA9T-_
    # 3. !play https://www.youtube.com/watch?v=nHc_7yeiLvc
    @staticmethod
    async def play_command(message):
        print(Fore.LIGHTCYAN_EX + '\nBotCommands.play_command()')
        guild = message.guild #readable guild name
        guild_id = guild.id #unqique guild id
        voice_client = guild.voice_client   
        voice_channel = message.author.voice.channel
        
        query = message.content.replace('!play', '').strip()
        video_urls = await BotCommands.process_song_request(query)
        for video in video_urls:
            print(f'\tAdding {video} to {guild}')
            await QueueControl.add_song(guild_id, video)
            await message.add_reaction("✅")
        
        next_song_queue = await QueueControl.retrieve(guild_id)
        # Check if the bot is already playing music
        if not voice_client or not voice_client.is_playing():
            if next_song_queue:
                song_path_to_play = await QueueControl.remove_song(guild_id) # Take the first song out of the queue. and assign it to the song_path_to_play
                BotCommands.current_songs[guild_id] = song_path_to_play # Place the popped song into the current_songs dictionary.
                print(f'\tCurrent song is now: {song_path_to_play}')
        
                if song_path_to_play:
                    if not voice_client and voice_channel:
                        print(f'\tConnecting to: {voice_channel}')
                        voice_client = await voice_channel.connect() # Connect to the voice channel if not already connected
                        BotCommands.play_audio(voice_client, guild_id, song_path_to_play)
        
        print('\tQueue is now:')
        for index, song in enumerate(next_song_queue):
            print(f'\t{index}: {song}')
    
    @staticmethod
    async def process_song_request(query):
        is_url = YouTubeDataHandler.validate_url(query)
        if is_url:
            url = query
            print(f'\tFound: {url}')
        else:
            # Search YouTube for the query and get the first result URL
            print(f'\tSearching: {query}')
            url = await YouTubeSearchHandler.search(query)
            print(f'\tFound: {url}')

        if not url:
            return []

        # Check if the URL is a playlist
        if YouTubeURLHandler.is_playlist_url(url):
            video_urls = YouTubeDataHandler.fetch_playlist_urls(url)
            return video_urls if video_urls else []
        else:
            return [url]       

    @staticmethod
    def play_audio(voice_client, guild_id, path):
        print(Fore.LIGHTCYAN_EX + '\nBotCommands.play_audio()')
        if voice_client.is_playing():
            print(f"\tAlready playing in guild {guild_id}.")
            return

        print(f'\tNow Playing: {path}')
        try:
            source = discord.FFmpegPCMAudio(path, executable="ffmpeg")
            voice_client.play(source, after=lambda e: BotCommands.after_play(voice_client, guild_id))
        except Exception as e:
            print(f"\tError playing audio in guild {guild_id}: {e}")

    @staticmethod
    def after_play(voice_client, guild_id):
        print(Fore.LIGHTCYAN_EX + f'\nBotCommands.after_play()')
        if not BotCommands._event_loop:
            BotCommands._event_loop = asyncio.get_event_loop()
        BotCommands._event_loop.create_task(BotCommands.play_next(voice_client, guild_id))

    @staticmethod
    async def play_next(voice_client, guild_id):
        print(Fore.LIGHTCYAN_EX + '\nBotCommands.play_next()')
        next_song_queue = await QueueControl.retrieve(guild_id)
        if next_song_queue and not voice_client.is_playing():
            next_song_path = await QueueControl.remove_song(guild_id)
            if next_song_path:
                BotCommands.play_audio(voice_client, guild_id, next_song_path)
        else:
            print("\tQueue is empty. No song to play next.")

    #if we're playing, pause, then do nothing.              
    @staticmethod
    async def pause_command(voice_client):
        print(Fore.LIGHTCYAN_EX + '\nBotCommands.pause_command()')
        if voice_client and voice_client.is_playing():
            voice_client.pause()

    #if we're paused, resume
    @staticmethod
    async def unpause_command(voice_client):
        print(Fore.LIGHTCYAN_EX + '\nBotCommands.unpause_command()')
        if voice_client and voice_client.is_paused():
            voice_client.resume()
    
    #call to the queuecontrol and remove the first song in the array.
    @staticmethod
    async def skip_command(voice_client, guild_id):
        print(Fore.LIGHTCYAN_EX + '\nBotCommands.skip_command()')
        if voice_client and voice_client.is_playing():
            print('\tstopping audio')
            voice_client.stop()  # Because the queue auto plays the next song when it stops playing, we can just stop here.
    
    #if we're playing audio, stop, call to the queue control, clear the queue, disconnect from voice.
    @staticmethod
    async def stop_command(voice_client, guild_id):
        print(Fore.LIGHTCYAN_EX + '\nBotCommands.stop_command()')
        if voice_client:
            if voice_client.is_playing():
                QueueControl.clear(guild_id)
                voice_client.stop()
            await voice_client.disconnect()

    #cleanup the queue and disconnect.
    @staticmethod
    async def disconnect_command(voice_client, guild_id):
        print(Fore.LIGHTCYAN_EX + '\nBotCommands.disconnect_command()')
        QueueControl.clear(guild_id)
        if voice_client:
            await voice_client.disconnect()

    #join the voice channel, do nothing.
    @staticmethod
    async def join_command(voice_channel):
        print(Fore.LIGHTCYAN_EX + '\nBotCommands.join_command()')
        if voice_channel:
            await voice_channel.connect()
    
    async def clear_command(guild_id):
        print(Fore.LIGHTCYAN_EX + '\nBotCommands.clear_command()')
        QueueControl.clear(guild_id)
    
    @staticmethod
    def info_command(message):
        print(Fore.LIGHTCYAN_EX + '\nBotCommands.info_command()')
        guild_id = message.guild.id
        # Retrieve the current song for the specific guild
        current_song = BotCommands.current_songs.get(guild_id)
        if current_song:
            return print(f'\tCurrently playing in guild {message.guild}: {current_song}')
        else:
            return print(f'\tNo song is currently playing in guild {guild_id}.')
        
    #todo:implement
    #async def radio_command(message):
    #    return