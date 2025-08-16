import discord
from discord.ext import commands
import json
import os
import time
from typing import Dict, Optional
import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection

class SubscriptionManager(commands.Cog):
    """Manages server subscriptions for Sea of Thieves notifications"""
    
    def __init__(self, bot):
        self.bot = bot
        # MongoDB connection
        self.mongo_url = os.getenv('MONGODB_URL', 'mongodb://localhost:27017')
        self.client: AsyncIOMotorClient = AsyncIOMotorClient(self.mongo_url)
        self.database: AsyncIOMotorDatabase = self.client.grebbot_db
        self.subscriptions_collection: AsyncIOMotorCollection = self.database.sea_of_thieves_subscriptions
        
        # Cooldown tracking: {member_id: {guild_id: last_notification_time}}
        self.notification_cooldowns: Dict[int, Dict[str, float]] = {}
        self.cooldown_duration = 120  # 2 minutes in seconds
    
    async def get_subscription(self, guild_id: str) -> Optional[Dict]:
        """Get subscription for a specific guild"""
        try:
            subscription = await self.subscriptions_collection.find_one({"guild_id": guild_id})
            return subscription
        except Exception as e:
            print(f"Error getting subscription for guild {guild_id}: {e}")
            return None
    
    async def save_subscription(self, guild_id: str, subscription_data: Dict):
        """Save or update subscription for a guild"""
        try:
            await self.subscriptions_collection.update_one(
                {"guild_id": guild_id},
                {"$set": subscription_data},
                upsert=True
            )
            print(f"Saved subscription for guild {guild_id}")
        except Exception as e:
            print(f"Error saving subscription for guild {guild_id}: {e}")
    
    async def get_all_subscriptions(self) -> Dict[str, Dict]:
        """Get all active subscriptions"""
        try:
            subscriptions = {}
            async for sub in self.subscriptions_collection.find({"enabled": True}):
                subscriptions[sub["guild_id"]] = sub
            return subscriptions
        except Exception as e:
            print(f"Error getting all subscriptions: {e}")
            return {}
    
    def is_on_cooldown(self, member_id: int, guild_id: str) -> bool:
        """Check if a member is on cooldown for notifications in a specific guild"""
        if member_id not in self.notification_cooldowns:
            return False
        
        if guild_id not in self.notification_cooldowns[member_id]:
            return False
        
        last_notification = self.notification_cooldowns[member_id][guild_id]
        current_time = time.time()
        
        return (current_time - last_notification) < self.cooldown_duration
    
    def update_cooldown(self, member_id: int, guild_id: str):
        """Update the cooldown for a member in a specific guild"""
        if member_id not in self.notification_cooldowns:
            self.notification_cooldowns[member_id] = {}
        
        self.notification_cooldowns[member_id][guild_id] = time.time()
    
    def get_cooldown_remaining(self, member_id: int, guild_id: str) -> int:
        """Get remaining cooldown time in seconds"""
        if not self.is_on_cooldown(member_id, guild_id):
            return 0
        
        last_notification = self.notification_cooldowns[member_id][guild_id]
        current_time = time.time()
        remaining = self.cooldown_duration - (current_time - last_notification)
        
        return max(0, int(remaining))
    
    @commands.command(name='subscribe')
    @commands.has_permissions(manage_guild=True)
    async def subscribe_command(self, ctx, channel: Optional[discord.TextChannel] = None):
        """
        Subscribe this server to Sea of Thieves notifications
        Usage: !subscribe [#channel]
        """
        target_channel = channel if channel else ctx.channel
        
        # Ensure we have a TextChannel
        if not isinstance(target_channel, discord.TextChannel):
            await ctx.send("❌ Please specify a valid text channel or use this command in a text channel.")
            return
        
        guild_id = str(ctx.guild.id)
        
        # Create subscription data
        subscription_data = {
            "guild_id": guild_id,
            "guild_name": ctx.guild.name,
            "channel_id": target_channel.id,
            "channel_name": target_channel.name,
            "enabled": True,
            "notify_start": True
        }
        
        # Save to MongoDB
        await self.save_subscription(guild_id, subscription_data)
        
        embed = discord.Embed(
            title="🏴‍☠️ Sea of Thieves Notifications",
            description=f"Successfully subscribed to Sea of Thieves notifications!",
            color=discord.Color.green()
        )
        embed.add_field(name="Notification Channel", value=target_channel.mention, inline=True)
        embed.add_field(name="Server", value=ctx.guild.name, inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='unsubscribe')
    @commands.has_permissions(manage_guild=True)
    async def unsubscribe_command(self, ctx):
        """Unsubscribe this server from Sea of Thieves notifications"""
        guild_id = str(ctx.guild.id)
        
        # Check if subscription exists
        subscription = await self.get_subscription(guild_id)
        
        if subscription and subscription.get("enabled", False):
            # Disable the subscription
            subscription["enabled"] = False
            await self.save_subscription(guild_id, subscription)
            
            embed = discord.Embed(
                title="🏴‍☠️ Sea of Thieves Notifications",
                description="Successfully unsubscribed from Sea of Thieves notifications.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ This server is not currently subscribed to notifications.")
    
    @commands.command(name='subscription_status')
    @commands.has_permissions(manage_guild=True)
    async def subscription_status_command(self, ctx):
        """Check the current subscription status"""
        guild_id = str(ctx.guild.id)
        
        # Get subscription from MongoDB
        subscription = await self.get_subscription(guild_id)
        
        if subscription and subscription.get("enabled", False):
            channel = self.bot.get_channel(subscription["channel_id"])
            
            embed = discord.Embed(
                title="🏴‍☠️ Subscription Status",
                description="This server is subscribed to Sea of Thieves notifications.",
                color=discord.Color.blue()
            )
            embed.add_field(name="Channel", value=channel.mention if channel else "Channel not found", inline=True)
            embed.add_field(name="Start Notifications", value="✅" if subscription.get("notify_start", True) else "❌", inline=True)
            
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="🏴‍☠️ Subscription Status",
                description="This server is not subscribed to notifications.\nUse `!subscribe` to enable notifications.",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
    
    async def notify_sea_of_thieves_activity(self, member: discord.Member, activity_type: str):
        """Send notification to subscribed servers with cooldown protection"""
        # Get all active subscriptions from MongoDB
        subscriptions = await self.get_all_subscriptions()
        
        for guild_id, sub in subscriptions.items():
            if not sub.get("enabled", False):
                continue
            
            # Check if member is in this guild
            guild = self.bot.get_guild(int(guild_id))
            if not guild or member not in guild.members:
                continue
            
            # Check notification preferences - only check for start notifications
            if activity_type == "start" and not sub.get("notify_start", True):
                continue
            
            # Check cooldown - prevent spam notifications
            if self.is_on_cooldown(member.id, guild_id):
                remaining = self.get_cooldown_remaining(member.id, guild_id)
                print(f"🕒 Cooldown active for {member.name} in {guild.name} - {remaining}s remaining")
                continue
            
            # Get notification channel
            channel = self.bot.get_channel(sub["channel_id"])
            if not channel:
                continue
            
            # Create and send notification (only for game start)
            try:
                if activity_type == "start":
                    embed = discord.Embed(
                        title="⚓ Ahoy you fucks!",
                        description=f"🏴‍☠️ **{member.display_name}** has set sail in **Sea of Thieves**!",
                        color=discord.Color.blue(),
                        timestamp=discord.utils.utcnow()
                    )
                    embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
                    embed.add_field(name="Player", value=member.mention, inline=True)
                    embed.add_field(name="Status", value="🚢 Setting Sail", inline=True)
                    
                    print(f"Sending Sea of Thieves notification to {guild.name} in {channel.name}")
                    await channel.send(embed=embed)
                    
                    # Update cooldown after successful notification
                    self.update_cooldown(member.id, guild_id)
                
            except Exception as e:
                print(f"Error sending notification to {guild.name}: {e}")
    
    @commands.command(name='cooldown_status')
    @commands.has_permissions(manage_guild=True)
    async def cooldown_status_command(self, ctx, member: Optional[discord.Member] = None):
        """Check the cooldown status for a specific member or all members"""
        guild_id = str(ctx.guild.id)
        
        if member:
            # Check specific member
            if self.is_on_cooldown(member.id, guild_id):
                remaining = self.get_cooldown_remaining(member.id, guild_id)
                embed = discord.Embed(
                    title="🕒 Cooldown Status",
                    description=f"**{member.display_name}** is on cooldown.",
                    color=discord.Color.orange()
                )
                embed.add_field(name="Remaining Time", value=f"{remaining} seconds", inline=True)
            else:
                embed = discord.Embed(
                    title="🕒 Cooldown Status",
                    description=f"**{member.display_name}** is not on cooldown.",
                    color=discord.Color.green()
                )
        else:
            # Show all members on cooldown in this guild
            cooldown_members = []
            for member_id, guild_cooldowns in self.notification_cooldowns.items():
                if guild_id in guild_cooldowns:
                    remaining = self.get_cooldown_remaining(member_id, guild_id)
                    if remaining > 0:
                        guild_member = ctx.guild.get_member(member_id)
                        if guild_member:
                            cooldown_members.append(f"**{guild_member.display_name}**: {remaining}s")
            
            if cooldown_members:
                embed = discord.Embed(
                    title="🕒 Active Cooldowns",
                    description="\n".join(cooldown_members),
                    color=discord.Color.orange()
                )
            else:
                embed = discord.Embed(
                    title="🕒 Cooldown Status",
                    description="No members are currently on cooldown.",
                    color=discord.Color.green()
                )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='reset_cooldown')
    @commands.has_permissions(manage_guild=True)
    async def reset_cooldown_command(self, ctx, member: discord.Member):
        """Reset the cooldown for a specific member"""
        guild_id = str(ctx.guild.id)
        
        if member.id in self.notification_cooldowns and guild_id in self.notification_cooldowns[member.id]:
            del self.notification_cooldowns[member.id][guild_id]
            embed = discord.Embed(
                title="🔄 Cooldown Reset",
                description=f"Cooldown reset for **{member.display_name}**.",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="🔄 Cooldown Reset",
                description=f"**{member.display_name}** was not on cooldown.",
                color=discord.Color.blue()
            )
        
        await ctx.send(embed=embed)

# Setup function
async def setup(bot):
    await bot.add_cog(SubscriptionManager(bot))
