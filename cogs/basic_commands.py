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

# Setup function to add the cog to the bot
async def setup(bot):
    await bot.add_cog(BasicCommands(bot))
