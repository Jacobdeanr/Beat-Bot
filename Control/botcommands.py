import discord
import asyncio
import os
from Search.Youtube.YouTubeSearchHandler import YouTubeSearchHandler
from Search.Youtube.YouTubeURLHandler import YouTubeURLHandler
from Search.Youtube.YouTubeDataHandler import YouTubeDataHandler
from Control.queuecontrol import QueueControl
from discord import VoiceChannel, TextChannel
from colorama import Fore, Back, Style

class BotCommands:
    _event_loop = None

    @staticmethod
    async def play_command(message):
        print(Fore.LIGHTCYAN_EX + '\nBotCommands.play_command()')
        guild, guild_id, voice_client,voice_channel = await BotCommands.get_guild_voice_client(message)
       
        query = message.content.replace('!play', '').strip()
        video_urls = await BotCommands.process_song_request(query)

        for video in video_urls:
            print(f'\tAdding {video} to {guild}')
            await QueueControl.add_song(guild_id, video)
        await message.add_reaction("✅")
        
        next_song_queue = await QueueControl.retrieve(guild_id)
        #connect the voice client.
        if not voice_client: 
            print(f'\tConnecting to: {voice_channel}')
            try:
                voice_client = await voice_channel.connect()
            except Exception as e:
                print(f"\tError connecting to voice:{voice_channel}: {e}")
            return

        if not voice_client.is_playing():
            if next_song_queue:
                song_path_to_play = await QueueControl.remove_song(guild_id) # Take the first song out of the queue. and assign it to the song_path_to_play
                print(f'\tCurrent song is now: {song_path_to_play}')

                if song_path_to_play:
                    BotCommands.play_audio(voice_client, guild_id, song_path_to_play)
        return

    @staticmethod
    async def pause_command(message):
        print(Fore.LIGHTCYAN_EX + '\nBotCommands.pause_command()')
        guild, guild_id, voice_client,voice_channel = await BotCommands.get_guild_voice_client(message)
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            await message.add_reaction("✅")
        return

    @staticmethod
    async def unpause_command(message):
        print(Fore.LIGHTCYAN_EX + '\nBotCommands.unpause_command()')
        guild, guild_id, voice_client,voice_channel = await BotCommands.get_guild_voice_client(message)

        if voice_client and voice_client.is_paused():
            voice_client.resume()
            await message.add_reaction("✅")
        return
    
    #call to the queuecontrol and remove the first song in the array.
    @staticmethod
    async def skip_command(message):
        print(Fore.LIGHTCYAN_EX + '\nBotCommands.skip_command()')
        guild, guild_id, voice_client,voice_channel = await BotCommands.get_guild_voice_client(message)

        if voice_client and voice_client.is_playing():
            print('\tstopping audio')
            voice_client.stop()  # Because the queue auto plays the next song when it stops playing, we can just stop here.
            await message.add_reaction("✅")
        else:
            print('Nothing playing')
        return
    
    @staticmethod
    async def stop_command(message):
        print(Fore.LIGHTCYAN_EX + '\nBotCommands.stop_command()')
        guild, guild_id, voice_client,voice_channel = await BotCommands.get_guild_voice_client(message)

        if voice_client:
            if voice_client.is_playing():
                await QueueControl.clear(guild_id)
                voice_client.stop()
            await message.add_reaction("🛑")
            await voice_client.disconnect()
        return

    @staticmethod
    async def disconnect_command(message):
        print(Fore.LIGHTCYAN_EX + '\nBotCommands.disconnect_command()')
        guild, guild_id, voice_client,voice_channel = await BotCommands.get_guild_voice_client(message)  
    
        await QueueControl.clear(guild_id)
        if voice_client:
            await voice_client.disconnect()
            await message.add_reaction("😢")
        return

    @staticmethod
    async def join_command(message):
        print(Fore.LIGHTCYAN_EX + '\nBotCommands.join_command()') 
        guild, guild_id, voice_client,voice_channel = await BotCommands.get_guild_voice_client(message)

        if voice_channel:
            await voice_channel.connect()
            await message.add_reaction("👋")
        return
    
    @staticmethod
    async def clear_command(message):
        print(Fore.LIGHTCYAN_EX + '\nBotCommands.clear_command()')
        guild, guild_id, voice_client,voice_channel = await BotCommands.get_guild_voice_client(message)
        await QueueControl.clear(guild_id)     

        if voice_client.is_playing():
            voice_client.stop()
            await message.add_reaction("💥")
        return
    
    @staticmethod
    async def info_command(message):
        print(Fore.LIGHTCYAN_EX + '\nBotCommands.info_command()')
        guild, guild_id, voice_client,voice_channel = await BotCommands.get_guild_voice_client(message)
        current_song = QueueControl.current_songs.get(guild_id)

        if current_song:
            video_id = BotCommands.extract_song_id(current_song)
            print(f'\tCurrently playing in guild {message.guild}: {current_song}')
            await message.add_reaction("🔎")
            await message.channel.send(f"Currently playing: https://www.youtube.com/watch?v={video_id}")
        else:
            print(f'\tNo song is currently playing in guild {guild_id}.')
        return

    @staticmethod
    async def queue_command(message):
        print(Fore.LIGHTCYAN_EX + '\nBotCommands.info_queue()')
        guild, guild_id, voice_client,voice_channel = await BotCommands.get_guild_voice_client(message)
        queue = await QueueControl.retrieve(guild_id)
        queuelength = len(queue)
        upcoming_songs = queue[:5]

        if queuelength > 0:
            message_parts = []
            print(f'\tqueue length = {queuelength}')
            for song_path in upcoming_songs:
                song_id = BotCommands.extract_song_id(song_path)
                url = f"https://www.youtube.com/watch?v={song_id}"
                title = await YouTubeDataHandler.fetch_video_title(url)
                message_part = f"{title}" if title else f"Title not found for ({url})"
                message_parts.append(message_part)

            message_to_send = "\n".join(message_parts)
            await message.channel.send(f'Songs in queue: **{queuelength}**\nNext song(s): \n{message_to_send}')
        else:
            await message.channel.send('Queue is empty!')
        return

# Everything below this line should probably be in their own class. 
# Helper functions for the various commands.
    @staticmethod
    async def get_guild_voice_client(message):
        print(Fore.LIGHTCYAN_EX + '\nBotCommands.get_guild_voice_client()')
        guild = message.guild
        voice_client = guild.voice_client
        voice_channel = message.author.voice.channel
        return guild, guild.id, voice_client, voice_channel
    
    @staticmethod
    async def process_song_request(query):
        is_url = await YouTubeDataHandler.validate_url(query)

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
        if(YouTubeURLHandler.is_playlist_url(url)):
            video_urls = await YouTubeDataHandler.fetch_playlist_urls(url)
            return video_urls if video_urls else []
        else:
            return [url]       

    @staticmethod
    def play_audio(voice_client, guild_id, song_path_to_play):
        print(Fore.LIGHTCYAN_EX + '\nBotCommands.play_audio()')

        if voice_client.is_playing():
            print(f"\tAlready playing in guild {guild_id}.")
            return

        print(f'\tNow Playing: {song_path_to_play}')
        try:
            source = discord.FFmpegPCMAudio(song_path_to_play, executable="ffmpeg")
            voice_client.play(source, after=lambda e: BotCommands.after_play(voice_client, guild_id))
            QueueControl.current_songs[guild_id] = song_path_to_play # Place the popped song into the current_songs dictionary.
        except Exception as e:
            print(f"\tError playing audio in guild {guild_id}: {e}")
        return

    @staticmethod
    def after_play(voice_client, guild_id):
        print(Fore.LIGHTCYAN_EX + f'\nBotCommands.after_play()')

        if not BotCommands._event_loop:
            BotCommands._event_loop = asyncio.get_event_loop()
        BotCommands._event_loop.create_task(BotCommands.play_next(voice_client, guild_id))
        return

    @staticmethod
    async def play_next(voice_client, guild_id):
        print(Fore.LIGHTCYAN_EX + '\nBotCommands.play_next()')
        next_song_queue = await QueueControl.retrieve(guild_id)

        if next_song_queue and not voice_client.is_playing():
            next_song_path = await QueueControl.remove_song(guild_id)
            if next_song_path:
                print(f'\tPlaying a new song: {next_song_path}')
                BotCommands.play_audio(voice_client, guild_id, next_song_path)
        else:
            print("\tQueue is empty. No song to play next.")
            await voice_client.disconnect()
        return

    def extract_song_id(file_path):
        base_name = os.path.basename(file_path)
        song_id, _ = os.path.splitext(base_name)
        return song_id    
    
    @staticmethod
    def set_event_loop(loop):
        BotCommands._event_loop = loop
        return