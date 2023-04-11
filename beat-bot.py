import os
import subprocess
import discord
import asyncio
import datetime
import re
import json

from youtube_search import YoutubeSearch
from discord import VoiceChannel, TextChannel

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

client.song_queues = {}
async def handle_skip_command(message, voice_client):
    voice_channel = message.author.voice.channel
    if voice_channel is None:
        print(f"{message.author.name} is not in a voice channel")
        return

    guild = message.guild
    guild_identifier = guild.id
    message_identifier = message.id
    voice_client = guild.voice_client
    #print(f"Skip message Guild ID = {guild} {guild_identifier} {message_identifier} {voice_client}")
    try:
        if voice_client is None or not voice_client.is_connected():
            print(f"voice client is not in voice_client")
            return

        if voice_client.is_playing() or voice_client.is_paused():
            #print(f"Stopping playback")
            voice_client.stop()

            #print(f"SKIPPING TO THE NEXT SONG")
            await play_next_song(client.song_queues[guild_id], voice_client)
        else:
            await play_next_song(client.song_queues[guild_id], voice_client)
    except Exception as e:
        print(f"Error while skipping: {e}")

async def handle_pause(voice_client):
    if voice_client.is_playing():
        print(f"Pausing")
        voice_client.pause()

async def handle_resume(voice_client):
    if voice_client.is_paused():
        print(f"Resuming")
        voice_client.resume()
    else:
        print(f"Player is not paused")

async def handle_disconnect(voice_client):
    print(f"Disconnecting from voice channel")
    if voice_client:
        if voice_client.is_playing():
            voice_client.stop()
        await voice_client.disconnect()
    else:
        print(f"Bot is not currently in a voice channel")
     
async def handle_play_command(message):
    voice_channel = message.author.voice.channel
    if voice_channel is None:
        print(f"{message.author.name} is not in a voice channel")
        return

    guild = message.guild
    voice_client = guild.voice_client

    if voice_client is None:
        print(f"Connecting to voice channel: {voice_channel.name}")
        voice_client = await voice_channel.connect()
    else:
        print(f"Already connected to voice channel: {voice_channel.name}")

    query = message.content.replace('!play', '').strip()
    print(f"Searching for {query}...")

    # Check if the input is a YouTube URL
    youtube_url_pattern = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
    is_url = youtube_url_pattern.match(query)

    if is_url:
        url = query
        # Check if the URL is a shortened YouTube URL
        if "youtu.be" in url:
            video_id = url.split("/")[-1]
            url = f"https://www.youtube.com/watch?v={video_id}"
        
        if "list=" in url:
            url = url.split('&')[0]  # Truncate the URL at the '&' character
            await add_to_queue(url, message, is_playlist=False, is_first_song=False)

            # do nothing for now until I get it properly implemented.
            # This is a playlist URL
            # await add_to_queue(url, message, is_playlist=True, is_first_song=True)
        else:
            print(f"Adding {url} to the queue.")
            await add_to_queue(url, message, is_playlist=False, is_first_song=False)
    else:
        results = YoutubeSearch(query, max_results=1).to_dict()

        if len(results) == 0:
            print(f"No results found for {query}.")
            await message.channel.send(f"No results found for {query}.")
            return

        url = f"https://www.youtube.com{results[0]['url_suffix']}"
        url = url.split('&')[0]  # Truncate the URL at the '&' character
        print(f"Adding {url} to the queue.")
        await add_to_queue(url, message, is_playlist=False, is_first_song=False)

    # If there is only one song in the queue, start playing it.
    if len(client.song_queues[guild.id]) == 1 and not voice_client.is_playing():
        await play_next_song(client.song_queues[guild.id], voice_client)

#Queue management
async def process_playlist_url(url, message):
    proc = await asyncio.create_subprocess_exec(
        'youtube-dl', '--dump-json', '--skip-download', url,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await proc.communicate()

    if proc.returncode == 0:
        stdout_data = stdout.decode().strip()
        if stdout_data:
            print(f"Successfully extracted playlist information from {url}")
            json_lines = stdout_data.splitlines()
            first_song = True

            for line in json_lines:
                video_data = json.loads(line)

                # Check if the extracted data is a playlist entry
                if 'id' in video_data:
                    video_url = f"https://www.youtube.com/watch?v={video_data['id']}"
                    print(f"Adding {video_url} to the queue.")
                    await add_to_queue(video_url, message, is_first_song=first_song)
                    first_song = False
                else:
                    print("The provided URL does not seem to be a playlist.")
                    await message.channel.send(f"The provided URL {url} does not seem to be a playlist.")
        else:
            print("The provided URL does not seem to be a playlist.")
            await message.channel.send("The provided URL does not seem to be a playlist.")
    else:
        print("Empty output from youtube-dl. The provided URL may not be a valid playlist.")
        await message.channel.send("The provided URL may not be a valid playlist.")

async def add_single_song_to_queue(url, message):
    server_id = message.guild.id
    if server_id not in client.song_queues:
        client.song_queues[server_id] = []

    # Download the file before adding it to the queue
    file_path = os.path.expanduser("~/Desktop/songs") + '/' + url.split('=')[1] + ".mp3"
    if not os.path.exists(file_path):
        # check the duration of the video
        duration = await get_video_duration(url)
        if duration > 4500:
            print(f"{url} duration is {duration} seconds, which is longer than 60 minutes. The song will not be added to the queue.")
            await message.channel.send(f":octagonal_sign: {url} duration is longer than 60 minutes, the song will not be added to the queue. :octagonal_sign:")
            return
        else:
            print(f"Downloading file: {file_path}")
            await message.channel.send(f":robot: Playback of {url} will begin after download is complete :robot:")
            await download_song(url)
            client.song_queues[server_id].append(file_path)
    else:
        await message.channel.send(f"{url} has been added to the queue :smile:")
        client.song_queues[server_id].append(file_path)
    
async def add_to_queue(url, message, is_playlist=False, is_first_song=False):
    if is_playlist:
        await process_playlist_url(url, message)
    else:
        await add_single_song_to_queue(url, message)

async def download_song(url):
    proc = await asyncio.create_subprocess_exec(
        'youtube-dl', url,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await proc.communicate()

    if proc.returncode == 0:
        print(f'Successfully downloaded {url}')
    else:
        print(f'Error downloading {url}: {stderr.decode()}')
        await message.channel.send(f"Something went wrong downloading {url}")
    
async def get_video_duration(query):
    results = YoutubeSearch(query, max_results=1).to_dict()
    if len(results) == 0:
        return 0
    duration_str = results[0]['duration']
    duration_parts = duration_str.split(':')
    total_seconds = 0
    for i, part in enumerate(reversed(duration_parts)):
        total_seconds += int(part) * (60 ** i)
        
    print(f'{query} length is {total_seconds}')
    return total_seconds


async def play_next_song(queue, voice_client):
    queuelength = len(queue)
    print(f"Queue length = {queuelength}")
    if len(queue) == 0:
        # If there are no more songs in the queue, disconnect the client
        print(f"No more songs in queue. Disconnecting.")
        await voice_client.disconnect()
        return

    next_song = queue.pop(0)
    source = discord.FFmpegPCMAudio(next_song, executable="ffmpeg")

    def after_play(error):
        if error:
            print(f"Error playing next song: {error}")
        client.loop.create_task(play_next_song(queue, voice_client))

    voice_client.play(source, after=after_play)

@client.event
async def on_voice_state_update(member, before, after):
    # Check if the bot was the one who left the voice channel
    if member == client.user and before.channel is not None and after.channel is None:
        print(f"The Bot Left. Good bye!")
        # Stop playing and clear the queue
        guild_id = before.channel.guild.id
        voice_client = discord.utils.get(client.voice_clients, guild=guild_id)
        if voice_client is not None:
            voice_client.stop()
            client.song_queues[guild_id].clear()

#User Commands
async def handle_command_prefix(message):
    if message.content.startswith('!'):
            await handle_command(message)

async def handle_command(message):
    content = message.content
    guild = message.guild
    voice_client = guild.voice_client
    author_voice = message.author.voice

    # Check if the author is in a voice channel
    if not author_voice:
        await message.channel.send("You need to be in a voice channel to use this command.")
        return

    if content.startswith('!pause'):
        await handle_pause(voice_client)
    elif content.startswith('!resume'):
        await handle_resume(voice_client)
    elif content.startswith('!disconnect'):
        await handle_disconnect(voice_client)
    elif content.startswith('!play'):
        await handle_play_command(message)
    elif content.startswith('!skip'):
        await handle_skip_command(message, voice_client)

@client.event
async def on_ready():
    print(f"logged in as {client.user.name}")
    # Initialize an empty queue for each server
    client.song_queues = {}

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    await handle_command_prefix(message)

client.run('MTA4NDY4OTg5NjcyNTMwMzMzNw.Gxvl8T.3_sVRCMuBNvkoWE96QpnEmEJT6vhz-jrMa-koo')
