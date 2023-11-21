import discord
import asyncio
from botcommands import BotCommands
from colorama import Fore, Back, Style

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

COMMAND_PLAY = '!play'
COMMAND_PAUSE = '!pause'
COMMAND_RESUME = '!resume'
COMMAND_SKIP = '!skip'
COMMAND_STOP = '!stop'
COMMAND_DISCONNECT = '!disconnect'
COMMAND_CLEAR = '!clear'
COMMAND_INFO = '!info'
COMMAND_QUEUE = '!queue'

#User Commands
async def handle_command_prefix(message):
    """
    Handle a command prefix.

    Args:
    message (discord.Message): The message object from Discord.

    Checks if the message starts with a command prefix and calls handle_command.
    """
    if message.content.startswith('!'):
        await handle_command(message)
    return

async def handle_command(message):
    """
    Handle a command based on its content.

    Args:
    message (discord.Message): The message object from Discord.

    Processes various commands and invokes the corresponding functions in BotCommands.
    """
    content = message.content
    text = content.lower()
    guild = message.guild
    voice_channel = message.author.voice.channel

    # Command-function mapping
    commands = {
        COMMAND_PLAY: lambda: BotCommands.play_command(message),
        COMMAND_PAUSE: lambda: BotCommands.pause_command(message),
        COMMAND_RESUME: lambda: BotCommands.unpause_command(message),
        COMMAND_SKIP: lambda: BotCommands.skip_command(message),
        COMMAND_STOP: lambda: BotCommands.stop_command(message),
        COMMAND_DISCONNECT: lambda: BotCommands.disconnect_command(message),
        COMMAND_CLEAR: lambda: BotCommands.clear_command(message),
        COMMAND_INFO: lambda: BotCommands.info_command(message),
        COMMAND_QUEUE: lambda: BotCommands.queue_command(message)
    }

    # Check if the author is in a voice channel
    if not message.author.voice:
        await message.channel.send("You need to be in a voice channel to use this command.")
        return

    for command, func in commands.items():
        if text.startswith(command):
            try:
                print(Fore.LIGHTCYAN_EX + '\n-------- New Command --------')
                print(f'\t{content}')
                print(f'\tguild = {guild}\n\tvoice_channel = {voice_channel}')
                await func()
            except Exception as e:
                print(f"Error handling {command}: {e}")
                #await message.channel.send(f"An error {e} occurred while processing the command: {command}")
            break
    return

@client.event
async def on_ready():
    print(f"logged in as {client.user.name}")
    BotCommands.set_event_loop(asyncio.get_running_loop())
    return

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    await handle_command_prefix(message)
    return

@client.event
async def on_voice_state_update(member, before, after):
    if member == client.user and before.channel is not None and after.channel is None:
        print(f"The Bot Left. Good bye!")
        guild_id = before.channel.guild.id
        voice_client = discord.utils.get(client.voice_clients, guild=guild_id)
        lambda: BotCommands.disconnect_command(voice_client,guild_id)
    return

def read_token():
    with open('token.txt', 'r') as file:
        return file.read().strip()
    
token = read_token()
client.run(token)