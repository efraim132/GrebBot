import math
import os
import queue
import threading
from asyncio import as_completed
from concurrent.futures import ThreadPoolExecutor
from utils.decorators import devModeOnly

import discord
from discord.ext import commands
import asyncio
import random

import utils.decorators


@utils.decorators.timer
def IsPrime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2

    sqrtN = int(math.sqrt(float(n)))
    workers = os.cpu_count() or 1
    ch = queue.Queue(maxsize=workers)
    step = sqrtN // workers

    def worker(s: int, e: int):
        j = s
        while j <= e:
            if n % j == 0:
                ch.put(False)
                return
            j += 2
        ch.put(True)

    for i in range(workers):
        start = 3 + int(i) * step
        end = start + step
        t = threading.Thread(target=worker, args=(start, end))
        t.daemon = True
        t.start()

    for _ in range(workers):
        if not ch.get():
            return False
    return True


class AdvancedCommands(commands.Cog):
    """Advanced bot commands for power users"""

    def __init__(self, bot):
        self.bot = bot
    
    #@devModeOnly
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

    #@devModeOnly
    @commands.command(name='isPrime')
    async def is_prime(self, ctx, number: int):
        """Checks if the user input is a prime number"""
        number = int(number)
        n = number

        if IsPrime(n):
            await ctx.send(f"The prime number {n} is prime.")
        else:
            await ctx.send(f"The prime number {n} is not prime.")



# Setup function to add the cog to the bot
async def setup(bot):
    await bot.add_cog(AdvancedCommands(bot))
