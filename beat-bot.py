import discord
import asyncio
from botcommands import BotCommands

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

#User Commands
async def handle_command_prefix(message):
    if message.content.startswith('!'):
            await handle_command(message)

async def handle_command(message):
    content = message.content
    text = content.lower()
    voice_client = message.guild.voice_client
    guild_id = message.guild

    # Check if the author is in a voice channel
    if not message.author.voice:
        await message.channel.send("You need to be in a voice channel to use this command.")
        return

    if text.startswith('!play'):
        print(f'\n!!!!!New Request!!!!!\n {content}')
        await BotCommands.play_command(message)
        
    elif text.startswith('!pause'):
        print(f'\n!!!!!New Request!!!!!\n {content}')
        await BotCommands.pause_command(voice_client)

    elif text.startswith('!resume'):
        print(f'\n!!!!!New Request!!!!!\n {content}')
        await BotCommands.unpause_command(voice_client)

    elif text.startswith('!skip'):
        print(f'\n!!!!!New Request!!!!!\n {content}')
        await BotCommands.skip_command(voice_client, guild_id)

    elif text.startswith('!stop'):
        print(f'\n!!!!!New Request!!!!!\n {content}')
        await BotCommands.stop_command(voice_client, guild_id)

    elif text.startswith('!disconnect'):
        print(f'\n!!!!!New Request!!!!!\n {content}')
        await BotCommands.disconnect_command(voice_client)

    elif text.startswith('!clear'):
        print(f'\n!!!!!New Request!!!!!\n {content}')
        await BotCommands.clear_command(voice_client)

@client.event
async def on_ready():
    print(f"logged in as {client.user.name}")
    BotCommands.set_event_loop(asyncio.get_running_loop())

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    await handle_command_prefix(message)

@client.event
async def on_voice_state_update(member, before, after):
    if member == client.user and before.channel is not None and after.channel is None:
        print(f"The Bot Left. Good bye!")
        guild_id = before.channel.guild.id
        voice_client = discord.utils.get(client.voice_clients, guild=guild_id)
        BotCommands.disconnect_command(voice_client,guild_id)

client.run('')
