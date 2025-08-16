import discord
from discord.ext import commands
import asyncio
import random

class AdvancedCommands(commands.Cog):
    """Advanced bot commands for power users"""
    
    def __init__(self, bot):
        self.bot = bot
    
    # Example advanced command - you can add your own here
    @commands.command(name='serverinfo')
    async def server_info(self, ctx):
        """Command: !serverinfo - Shows detailed server information"""
        guild = ctx.guild
        if not guild:
            await ctx.send("This command can only be used in a server!")
            return
        
        embed = discord.Embed(
            title=f"Server Information: {guild.name}",
            color=discord.Color.green()
        )
        embed.add_field(name="Server ID", value=guild.id, inline=True)
        embed.add_field(name="Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
        embed.add_field(name="Member Count", value=guild.member_count, inline=True)
        embed.add_field(name="Created", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="Text Channels", value=len(guild.text_channels), inline=True)
        embed.add_field(name="Voice Channels", value=len(guild.voice_channels), inline=True)
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        await ctx.send(embed=embed)
    

    

# Setup function to add the cog to the bot
async def setup(bot):
    await bot.add_cog(AdvancedCommands(bot))
