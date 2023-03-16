import os
import subprocess
import discord
import asyncio
import datetime
import re

from youtube_search import YoutubeSearch
from discord import VoiceChannel, TextChannel

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

client.song_queues = {}
async def handle_skip_command(message,voice_client):
    guild = message.guild
    voice_client = guild.voice_client
    try:
        if voice_client is None or not voice_client.is_connected():
            print(f"voice client is not in voice_client")
            return

        if voice_client.is_playing() or voice_client.is_paused():
            print(f"Stopping playback")
            voice_client.stop()

            if len(client.song_queues[guild_id]) > 0:
                print(f"Popping song from queue")
                client.song_queues[guild_id].pop(0)
                
            print(f"Playing next song")
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

#Play Command Stuff
async def add_to_queue(url, message):
    server_id = message.guild.id
    if server_id not in client.song_queues:
        client.song_queues[server_id] = []

    # Download the file before adding it to the queue
    file_path = os.path.expanduser("~/Desktop/songs") + '/' + url.split('=')[1] + ".mp3"
    if not os.path.exists(file_path):
        # check the duration of the video
        duration = await get_video_duration(url)
        if duration > 1200:
            print(f"{url} duration is {duration} seconds, which is longer than 20 minutes. The song will not be added to the queue.")
            await message.channel.send(f"{url} duration is longer than 20 minutes, the song will not be added to the queue.")
            return
        else:
            print(f"Downloading file: {file_path}")
            await download_song(url)
    
    await message.channel.send(f"{url} has been added to the queue.")    
    client.song_queues[server_id].append(file_path)
    
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

async def get_video_duration(url):
    duration = subprocess.check_output(['youtube-dl', '--get-duration', url])
    duration = duration.decode("utf-8").strip()
    if duration:
        duration_time = datetime.datetime.strptime(duration, '%M:%S')
        duration_seconds = duration_time.minute * 60 + duration_time.second
        return duration_seconds
    else:
        return 0
    
async def play_next_song(queue, voice_client):
    # If there is a next song in the queue
    if len(queue) > 0:
        next_song = queue.pop(0)
        source = discord.FFmpegPCMAudio(next_song, executable="ffmpeg")
        voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_next_song(queue, voice_client), client.loop))
    else:
        # If there are no more songs in the queue, disconnect the client
        await voice_client.disconnect()
        
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
        print(f"Adding {url} to the queue.")
        await add_to_queue(url, message)
    else:
        results = YoutubeSearch(query, max_results=1).to_dict()

        if len(results) == 0:
            print(f"No results found for {query}.")
            await message.channel.send(f"No results found for {query}.")
            return

        url = f"https://www.youtube.com{results[0]['url_suffix']}"
        url = url.split('&')[0]  # Truncate the URL at the '&' character
        print(f"Adding {url} to the queue.")
        await add_to_queue(url, message)

    # If there is only one song in the queue, start playing it
    if len(client.song_queues[guild.id]) == 1 and not voice_client.is_playing():
        await play_next_song(client.song_queues[guild.id], voice_client)

@client.event
async def on_voice_state_update(member, before, after):
    # Check if the bot was the one who left the voice channel
    if member == client.user and before.channel is not None and after.channel is None:
        # Stop playing and clear the queue
        guild_id = before.channel.guild.id
        voice_client = client.voice_clients[guild_id]
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
    if content.startswith('!pause'):
        await handle_pause(voice_client)
    elif content.startswith('!resume'):
        await handle_resume(voice_client)
    elif content.startswith('!disconnect'):
        await handle_disconnect(voice_client)
    elif content.startswith('!play'):
        await handle_play_command(message)
    elif content.startswith('!skip'):
        await handle_skip_command(message,voice_client)

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

client.run('MTA4NDY4OTg5NjcyNTMwMzMzNw.GNxbqn.I8J1gnRmIHPGWV959srRRJd_Y0Ilihl0PULGW8')
