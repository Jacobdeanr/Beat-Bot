import discord
import asyncio
from Search.Youtube.YouTubeSearchHandler import YouTubeSearchHandler
from Search.Youtube.YouTubeURLHandler import YouTubeURLHandler
from Search.Youtube.YouTubeDataHandler import YouTubeDataHandler
from Control.queuecontrol import QueueControl
from discord import VoiceChannel, TextChannel


class BotCommands:
    _event_loop = None

    @staticmethod
    def set_event_loop(loop):
        BotCommands._event_loop = loop
        print("Event loop set in BotCommands")

    # play command is tricky. It's actually used more of a search, or request, and playback begin function.
    # an example of how it will be used:
    # 1. !play mac miller small worlds
    # 2. !play https://www.youtube.com/watch?v=VzAjXdBJsEc&list=PLb23bTgg3GgWKc53aZ-GAhED0G6iA9T-_
    # 3. !play https://www.youtube.com/watch?v=nHc_7yeiLvc
    @staticmethod
    async def play_command(message):
        print('\n\nBotCommands.play_command(message):')
        guild = message.guild
        guild_id = guild.id
        voice_client = guild.voice_client   
        voice_channel = message.author.voice.channel
        
        query = message.content.replace('!play', '').strip()
        is_url = YouTubeDataHandler.validate_url(query)
        if is_url:
            url = query
            print(f'this is a single URL request: {url}')
        else:
            # Search YouTube for the query and get the first result URL
            print(f'not a url request. Searching: {query}')
            url = await YouTubeSearchHandler.search(query)

        if not url:
            return

        #Check if the URL is a playlist
        if YouTubeURLHandler.is_playlist_url(url):
            video_urls = YouTubeDataHandler.fetch_playlist_urls(url)
            if not video_urls:
                return
        else:
            video_urls = [url]

        # Step 3: each videos to the queue, one by one.
        for video in video_urls:
            await QueueControl.add_song(guild_id, video)

        if not voice_client and voice_channel:
            voice_client = await voice_channel.connect()

        if voice_client and not voice_client.is_playing():
            next_song_queue = await QueueControl.retrieve(guild_id)
            print(f'next_song_queue = {next_song_queue}')
            if next_song_queue:
                next_song_path = next_song_queue.pop(0)
                if next_song_path:
                    BotCommands.play_audio(voice_client, guild_id, next_song_path)
                    print(f'playing {next_song_path}')
    
    @staticmethod
    def play_audio(voice_client, guild_id, path):
        source = discord.FFmpegPCMAudio(path, executable="ffmpeg")
        voice_client.play(source, after=lambda e: BotCommands.after_play_wrapper(voice_client, guild_id))

    @staticmethod
    def after_play_wrapper(voice_client, guild_id):
        BotCommands.after_play(voice_client, guild_id)

    @staticmethod
    def after_play(voice_client, guild_id):
        print(f'\n\nBotCommands.after_play()')
        if BotCommands._event_loop:
            print('event_loop')
            BotCommands._event_loop.create_task(BotCommands.play_next(voice_client, guild_id))
        else:
            print('nothing happened')
            return None

    @staticmethod
    async def play_next(voice_client, guild_id):
        next_song_queue = await QueueControl.retrieve(guild_id)
        if next_song_queue:
            next_song_path = next_song_queue.pop(0)
            if next_song_path:
                source = discord.FFmpegPCMAudio(next_song_path, executable="ffmpeg")
                voice_client.play(source, after=lambda e: BotCommands.after_play(voice_client, guild_id))

    #if we're playing, pause, then do nothing.              
    @staticmethod
    async def pause_command(voice_client):
        if voice_client and voice_client.is_playing():
            voice_client.pause()

    #if we're paused, resume
    @staticmethod
    async def unpause_command(voice_client):
        if voice_client and voice_client.is_paused():
            voice_client.resume()
    
    #call to the queuecontrol and remove the first song in the array.
    @staticmethod
    async def skip_command(voice_client, guild_id):
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            QueueControl.remove_song(guild_id)
            next_song_queue = await QueueControl.retrieve(guild_id)
            if next_song_queue:
                next_song_path = next_song_queue.pop(0)

                if next_song_path:
                    BotCommands.play_audio(voice_client, guild_id, next_song_path)
            else:
                print("Queue is empty. No song to skip to.")
        else:
            print("No song is currently playing.")
    
    #if we're playing audio, stop, call to the queue control, clear the queue, disconnect from voice.
    @staticmethod
    async def stop_command(voice_client, guild_id):
        if voice_client:
            if voice_client.is_playing():
                voice_client.stop()
            QueueControl.clear(guild_id)
            await voice_client.disconnect()

    #cleanup the queue and disconnect.
    @staticmethod
    async def disconnect_command(voice_client, guild_id):
        QueueControl.clear(guild_id)
        if voice_client:
            await voice_client.disconnect()

    #join the voice channel, do nothing.
    @staticmethod
    async def join_command(voice_channel):
        if voice_channel:
            await voice_channel.connect()
    
    async def clear_command(guild_id):
        QueueControl.clear(guild_id)
    
    #todo:implement
    #async def info_command(message):
    #    return

    #async def radio_command(message):
    #    return