import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv
from art import text2art

# Load environment variables from .env file
load_dotenv()

# Check if DEBUG MODE is enabled
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() in ['true', '1', 'yes']

# Bot setup with intents
intents = discord.Intents.default()
intents.message_content = True  # Required for reading message content
intents.presences = True  # Required for presence updates
intents.members = True  # Required for member updates

# Banner
VERSION = os.getenv('VERSION', 'ERROR')  # Get version from environment variable
print(text2art(F"GrebBot - Discord Bot \nv{VERSION}"))
print("Starting GrebBot...")



# Create bot instance with command prefix
if DEBUG_MODE:
    print("⚠️ DEBUG MODE is ON ⚠️")
    command_prefix = '$'
else:
    command_prefix = '1'

bot = commands.Bot(command_prefix=command_prefix, intents=intents)

@bot.event
async def on_ready():
    """Event triggered when bot is ready"""

    status = os.getenv('bot_status', 'playing with <code>')

    print(f'{bot.user} has logged in!')
    print(f'Bot ID: {bot.user.id}')
    
    # Set bot status
    await bot.change_presence(
        activity=discord.Game(name=status),
        status=discord.Status.online
    )
    print(f'Status set to: {status}')

@bot.event
async def on_message(message):
    """Event triggered when a message is sent"""
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Log all messages (optional - remove if not needed)
    print(f'Message from [{message.author}: {message.content}]', end=' ')
    if message.guild  and DEBUG_MODE:
        print(f"Channel: {message.channel.name} | Guild: {message.guild.name}")
    elif DEBUG_MODE:
        print(f"Direct Message from {message.author}")
    
    # Respond to specific non-command messages
    if message.content.lower() == 'hello':
        await message.channel.send(f'Hello {message.author.mention}!')
    elif message.content.lower() == 'ping':
        await message.channel.send('Pong!')
    
    # Process commands (important: this must be at the end)
    await bot.process_commands(message)

# Error handling
@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"Command not found! Use `!help` to see available commands.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing required argument! Check the command usage with `!help <command>`")
    else:
        print(f"An error occurred: {error}")
        if (isinstance(error, commands.errors.CommandInvokeError) and DEBUG_MODE):
            await ctx.send("I don't have permission to delete the command message :(")
        else:
            await ctx.send(f"An error occurred while processing the command")


# Load cogs
async def load_cogs():
    """Load all cogs"""
    try:
        await bot.load_extension('cogs.basic_commands')
        await bot.load_extension('cogs.advanced_commands')
        await bot.load_extension('cogs.presenceChanges')
        await bot.load_extension('cogs.subscription_manager')
        print("✅ Loaded cogs: basic_commands, advanced_commands, presenceChanges, subscription_manager")
    except Exception as e:
        print(f"❌ Failed to load cogs: {e}")




# Run the bot
async def main():
    """Main function to start the bot"""


    # Load cogs first
    await load_cogs()
    
    # Get token from environment variables
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        print("Error: DISCORD_TOKEN not found in .env file!")
        print("Please add your Discord bot token to the .env file.")
        return
    
    try:
        await bot.start(token)
    except discord.LoginFailure:
        print("Error: Invalid Discord token!")
    except Exception as e:
        print(f"Error starting bot: {e}")

if __name__ == "__main__":
    asyncio.run(main())
