import discord
from discord.ext import commands



class BasicCommands(commands.Cog):
    """Basic bot commands like hello, ping, info, etc."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='hello')
    async def hello_command(self, ctx):
        """Command: !hello - Greets the user"""
        await ctx.send(f'Hello {ctx.author.mention}! 👋')

    @commands.command(name='ping')
    async def ping_command(self, ctx):
        """Command: !ping - Shows bot latency"""
        latency = round(self.bot.latency * 1000)
        await ctx.send(f'Pong! 🏓 Latency: {latency}ms')

    @commands.command(name='info')
    async def info_command(self, ctx):
        """Command: !info - Shows bot information"""
        embed = discord.Embed(
            title="Bot Information",
            description="GrebBot - A simple Discord bot",
            color=discord.Color.blue()
        )
        embed.add_field(name="Status", value="Working on something!", inline=True)
        embed.add_field(name="Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="Server Count", value=len(self.bot.guilds), inline=True)
        
        await ctx.send(embed=embed)

    @commands.command(name='say')
    async def say_command(self, ctx, *, message):
        """Command: !say <message> - Makes the bot say something"""
        await ctx.send(message)
        # Try to delete the original command message if bot has permission
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass  # Bot doesn't have permission to delete messages

    @commands.command(name='echo')
    async def echo_command(self, ctx, *, message):
        """Command: !echo <message> - Echoes the message back"""
        await ctx.send(f'You said: {message}')

    @commands.command(name='help_commands')
    async def help_commands(self, ctx):
        """Command: !help_commands - Shows all available commands"""
        embed = discord.Embed(
            title="🤖 GrebBot Commands",
            description="Here are all the available commands:",
            color=discord.Color.blue()
        )
        
        # Basic Commands
        embed.add_field(
            name="📝 Basic Commands",
            value="`!hello` - Greet the bot\n"
                  "`!ping` - Check bot latency\n"
                  "`!info` - Show bot information\n"
                  "`!say <message>` - Make the bot say something\n"
                  "`!echo <message>` - Echo a message back\n"
                  "`!help_commands` - Show this help menu",
            inline=False
        )
        
        # Admin Commands
        embed.add_field(
            name="🛡️ Admin Commands (Manage Server)",
            value="`!subscribe [#channel]` - Subscribe to Sea of Thieves notifications\n"
                  "`!unsubscribe` - Unsubscribe from notifications\n"
                  "`!subscription_status` - Check subscription status\n"
                  "`!cooldown_status [member]` - Check cooldown status\n"
                  "`!reset_cooldown <member>` - Reset member cooldown",
            inline=False
        )
        
        # DM Commands
        embed.add_field(
            name="📬 DM Commands (Any User)",
            value="`!dm_subscribe` - Get DMs when notifications are sent in this server\n"
                  "`!dm_unsubscribe` - Stop getting DMs for this server\n"
                  "`!dm_status` - Check your DM subscription status",
            inline=False
        )
        
        # Advanced Commands
        embed.add_field(
            name="⚙️ Advanced Commands (Manage Server)",
            value="`!serverinfo` - Show detailed server information",
            inline=False
        )
        
        embed.set_footer(text="🏴‍☠️ GrebBot automatically detects when you start playing Sea of Thieves!")
        
        await ctx.send(embed=embed)

# Setup function to add the cog to the bot
async def setup(bot):
    await bot.add_cog(BasicCommands(bot))
