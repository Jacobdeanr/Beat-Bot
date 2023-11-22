import discord
import asyncio
import datetime
from Search.Youtube.YouTubeSearchHandler import YouTubeSearchHandler
from Search.Youtube.YouTubeURLHandler import YouTubeURLHandler
from Search.Youtube.YouTubeDataHandler import YouTubeDataHandler
from Control.queuecontrol import QueueControl
from colorama import Fore

class BotCommands:
    _event_loop = None

    @staticmethod
    async def play_command(message):
        print(Fore.LIGHTCYAN_EX + '\nBotCommands.play_command()')
        guild = message.guild
        guild_id = message.guild.id
        voice_client = message.guild.voice_client
        voice_channel = message.author.voice.channel
       
        query = message.content.replace('!play', '').strip()
        video_urls = await BotCommands.process_song_request(query)

        for url in video_urls:
            print(f'\tAdding {url} to {guild}')
            await QueueControl.add_song(guild_id, url)
        await message.add_reaction("✅")

        next_song_queue = await QueueControl.retrieve(guild_id)
        
        if not voice_client: 
            print(f'\tConnecting to: {voice_channel}')
            try:
                voice_client = await voice_channel.connect()
            except Exception as e:
                print(f"\tError connecting to voice:{voice_channel}: {e}")
                return

        if not voice_client.is_playing():
            if next_song_queue:
                item_to_play = await QueueControl.remove_song(guild_id)
                if item_to_play:
                    BotCommands.play_audio(voice_client, guild_id, item_to_play)
        return

    @staticmethod
    async def pause_command(message):
        print(Fore.LIGHTCYAN_EX + '\nBotCommands.pause_command()')
        voice_client = message.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            await message.add_reaction("✅")
        else:
            await message.add_reaction("❌")
        return

    @staticmethod
    async def unpause_command(message):
        print(Fore.LIGHTCYAN_EX + '\nBotCommands.unpause_command()')
        voice_client = message.guild.voice_client
        if voice_client and voice_client.is_paused():
            voice_client.resume()
            await message.add_reaction("✅")
        return

    #call to the queuecontrol and remove the first song in the array.
    @staticmethod
    async def skip_command(message):
        print(Fore.LIGHTCYAN_EX + '\nBotCommands.skip_command()')
        voice_client = message.guild.voice_client

        if voice_client and voice_client.is_playing():
            print('\tstopping audio')
            voice_client.stop()  # Because the queue auto plays the next song when it stops playing, we can just stop here.
            await message.add_reaction("✅")
        else:
            print('Nothing playing')
            await message.add_reaction("❌")
        return
    
    @staticmethod
    async def stop_command(message):
        print(Fore.LIGHTCYAN_EX + '\nBotCommands.stop_command()')
        voice_client = message.guild.voice_client
        guild_id = message.guild.id
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
        guild_id = message.guild.id
        voice_client = message.guild.voice_client
        await QueueControl.clear(guild_id)
        if voice_client:
            await voice_client.disconnect()
            await message.add_reaction("😢")
        return

    @staticmethod
    async def join_command(message):
        print(Fore.LIGHTCYAN_EX + '\nBotCommands.join_command()') 
        voice_channel = message.author.voice.channel
        if voice_channel:
            await voice_channel.connect()
            await message.add_reaction("👋")
        return

    @staticmethod
    async def clear_command(message):
        print(Fore.LIGHTCYAN_EX + '\nBotCommands.clear_command()')
        guild_id = message.guild.id
        voice_client = message.guild.voice_client
        await QueueControl.clear(guild_id)     

        if voice_client.is_playing():
            voice_client.stop()
            await message.add_reaction("💥")
        return

    @staticmethod
    async def info_command(message):
        print(Fore.LIGHTCYAN_EX + '\nBotCommands.info_command()')
        guild_id = message.guild.id
        current_song = QueueControl.current_songs.get(guild_id)

        if current_song:
            await message.add_reaction("🔎")
            channel_name = current_song['channel_name']
            title = current_song['title']
            length = current_song['length']
            url = current_song['url']
            org_pub_date = current_song['publish_date']
            
            publish_date = datetime.datetime.strptime(str(org_pub_date), "%Y-%m-%d %H:%M:%S").strftime("%m/%d/%Y")
            duration = BotCommands.format_seconds_to_hms(length)

            print(f'\tCurrently playing in guild {message.guild}: {url}')
            await message.channel.send(f"Currently Playing: `{channel_name} - {title} ({duration})`\nPublished on: `{publish_date}`\nLink: <{url}>")
        else:
            print(f'\tNo song is currently playing in guild {guild_id}.')
            await message.add_reaction("❌")
        return

    @staticmethod
    async def queue_command(message):
        print(Fore.LIGHTCYAN_EX + '\nBotCommands.queue_command()')
        guild_id = message.guild.id
        queue = await QueueControl.retrieve(guild_id)
        queuelength = len(queue)
        upcoming_songs = queue[:5]

        if queuelength > 0:
            message_parts = []
            for song_dict in upcoming_songs:
                title = song_dict.get('title', 'Title not found')
                url = song_dict.get('url', 'URL not found')
                channel_name = song_dict.get('channel_name', 'Channel not found')
                length_seconds = song_dict.get('length', 0)
                formatted_length = BotCommands.format_seconds_to_hms(length_seconds)
                message_part = f"`{channel_name} - {title} ({formatted_length})` - <{url}>"
                message_parts.append(message_part)

            message_to_send = "\n".join(message_parts)
            await message.channel.send(f'Songs in queue: `{queuelength}`\nUp Next: \n{message_to_send}')
        else:
            await message.channel.send('Queue is empty!')
        return

# Everything below this line should probably be in their own class. 
# Helper functions for the various commands.

    @staticmethod
    def format_seconds_to_hms(seconds):
        """
            Formats a duration from seconds to a string in hh:mm:ss format or mm:ss if hours are zero.

        :param seconds: Duration in seconds.
        :return: Formatted duration as a string.
        """
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        if h > 0:
            return f"{h:02}:{m:02}:{s:02}"
        else:
            return f"{m:02}:{s:02}"

    @staticmethod
    async def get_guild_voice_client(message):
        print(Fore.LIGHTCYAN_EX + '\nBotCommands.get_guild_voice_client()')
        guild = message.guild
        guild_id = message.guild.id
        voice_client = message.guild.voice_client
        voice_channel = message.author.voice.channel
        return guild, guild_id, voice_client, voice_channel
    
    @staticmethod
    async def process_song_request(query):
        is_url = await YouTubeDataHandler.validate_url(query)

        if is_url:
            url = query
            print(f'\tFound: {url}')
        else:
            print(f'\tSearching: {query}')
            url = await YouTubeSearchHandler.search(query)
            print(f'\tFound: {url}')

        if not url:
            return []

        if(YouTubeURLHandler.is_playlist_url(url)):
            video_urls = await YouTubeDataHandler.fetch_playlist_urls(url)
            return video_urls if video_urls else []
        else:
            return [url]       

    @staticmethod
    def play_audio(voice_client, guild_id, item_to_play):
        print(Fore.LIGHTCYAN_EX + '\nBotCommands.play_audio()')

        song_path_to_play = item_to_play['download_path']
        title = item_to_play['title']

        if voice_client.is_playing():
            print(f"\tAlready playing in guild {guild_id}.")
            return

        print(f'\tNow Playing: {title}')
        try:
            source = discord.FFmpegPCMAudio(song_path_to_play, executable="ffmpeg")
            voice_client.play(source, after=lambda e: BotCommands.after_play(voice_client, guild_id))
            QueueControl.current_songs[guild_id] = item_to_play # Place the popped song into the current_songs dictionary.
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
            item_to_play = await QueueControl.remove_song(guild_id)
            if item_to_play:
                print(f'\tPlaying a new song: {item_to_play}')
                BotCommands.play_audio(voice_client, guild_id, item_to_play)
        else:
            print("\tQueue is empty. No song to play next.")
            await voice_client.disconnect()
        return
    
    @staticmethod
    def set_event_loop(loop):
        BotCommands._event_loop = loop
        return