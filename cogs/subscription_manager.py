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
    
    database: AsyncIOMotorDatabase

    def __init__(self, bot):
        self.bot = bot
        # MongoDB connection
        self.mongo_url = os.getenv('MONGODB_URL', 'mongodb://localhost:27017')
        self.client: AsyncIOMotorClient = AsyncIOMotorClient(self.mongo_url)

        # Dev Mode uses grebbot_db_test, production uses grebbot_db
        if os.getenv('DEBUG_MODE', 'False').lower() in ['true', '1', 'yes']:
            self.database: AsyncIOMotorDatabase = self.client.grebbot_db_test
            print("Using test database: grebbot_db_test")
        else:
            self.database: AsyncIOMotorDatabase = self.client.grebbot_db


        self.database: AsyncIOMotorDatabase = self.client.grebbot_db_test
        self.subscriptions_collection: AsyncIOMotorCollection = self.database.sea_of_thieves_subscriptions
        self.dm_subscriptions_collection: AsyncIOMotorCollection = self.database.dm_subscriptions
        
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
    
    async def get_dm_subscription(self, user_id: int, guild_id: str) -> Optional[Dict]:
        """Get DM subscription for a specific user in a specific guild"""
        try:
            dm_sub = await self.dm_subscriptions_collection.find_one({
                "user_id": user_id,
                "guild_id": guild_id
            })
            return dm_sub
        except Exception as e:
            print(f"Error getting DM subscription for user {user_id} in guild {guild_id}: {e}")
            return None
    
    async def save_dm_subscription(self, user_id: int, guild_id: str, enabled: bool):
        """Save or update DM subscription for a user"""
        try:
            dm_data = {
                "user_id": user_id,
                "guild_id": guild_id,
                "enabled": enabled
            }
            await self.dm_subscriptions_collection.update_one(
                {"user_id": user_id, "guild_id": guild_id},
                {"$set": dm_data},
                upsert=True
            )
            print(f"Saved DM subscription for user {user_id} in guild {guild_id}: {enabled}")
        except Exception as e:
            print(f"Error saving DM subscription: {e}")
    
    async def get_dm_subscribers_for_guild(self, guild_id: str) -> list:
        """Get all users subscribed to DMs for a specific guild"""
        try:
            subscribers = []
            async for sub in self.dm_subscriptions_collection.find({
                "guild_id": guild_id,
                "enabled": True
            }):
                subscribers.append(sub["user_id"])
            return subscribers
        except Exception as e:
            print(f"Error getting DM subscribers for guild {guild_id}: {e}")
            return []
    
    async def get_all_dm_subscriptions_for_user(self, user_id: int) -> list:
        """Get all DM subscriptions for a specific user across all guilds"""
        try:
            subscriptions = []
            async for sub in self.dm_subscriptions_collection.find({
                "user_id": user_id,
                "enabled": True
            }):
                subscriptions.append(sub)
            return subscriptions
        except Exception as e:
            print(f"Error getting all DM subscriptions for user {user_id}: {e}")
            return []
    
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
                    
                    # Send DMs to subscribed users in this guild
                    dm_subscribers = await self.get_dm_subscribers_for_guild(guild_id)
                    for user_id in dm_subscribers:
                        try:
                            user = self.bot.get_user(user_id)
                            if user and user != member:  # Don't DM the player themselves
                                dm_embed = discord.Embed(
                                    title="⚓ Ahoy you fucks!",
                                    description=f"🏴‍☠️ **{member.display_name}** has set sail in **Sea of Thieves** in **{guild.name}**!",
                                    color=discord.Color.blue(),
                                    timestamp=discord.utils.utcnow()
                                )
                                dm_embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
                                dm_embed.add_field(name="Player", value=member.display_name, inline=True)
                                dm_embed.add_field(name="Server", value=guild.name, inline=True)
                                dm_embed.add_field(name="Status", value="🚢 Setting Sail", inline=True)
                                
                                await user.send(embed=dm_embed)
                                print(f"Sent DM notification to {user.name} for {member.display_name} in {guild.name}")
                        except discord.Forbidden:
                            print(f"Could not send DM to user {user_id} - DMs might be disabled")
                        except Exception as e:
                            print(f"Error sending DM to user {user_id}: {e}")
                    
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
    
    @commands.command(name='dm_subscribe')
    async def dm_subscribe_command(self, ctx):
        """Subscribe to receive DMs when Sea of Thieves notifications are sent in this server"""
        if ctx.guild is None:
            await ctx.send("❌ This command can only be used in a server  in which we both exist!, not in DMs.")
            return
        
        user_id = ctx.author.id
        guild_id = str(ctx.guild.id)
        
        # Check if the server has notifications enabled
        subscription = await self.get_subscription(guild_id)
        if not subscription or not subscription.get("enabled", False):
            await ctx.send("❌ This server is not subscribed to Sea of Thieves notifications. Ask a server admin to use `!subscribe` first.")
            return
        
        # Save DM subscription
        await self.save_dm_subscription(user_id, guild_id, True)
        
        embed = discord.Embed(
            title="📬 DM Subscription",
            description=f"You will now receive DMs when Sea of Thieves notifications are sent in **{ctx.guild.name}**.",
            color=discord.Color.green()
        )
        embed.add_field(name="Server", value=ctx.guild.name, inline=True)
        embed.add_field(name="Status", value="✅ Enabled", inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='dm_unsubscribe')
    async def dm_unsubscribe_command(self, ctx):
        """Unsubscribe from DMs for this server"""
        if ctx.guild is None:
            await ctx.send("❌ This command can only be used in a server  in which we both exist!, not in DMs.")
            return
        
        user_id = ctx.author.id
        guild_id = str(ctx.guild.id)
        
        # Check if user has a DM subscription
        dm_sub = await self.get_dm_subscription(user_id, guild_id)
        if not dm_sub or not dm_sub.get("enabled", False):
            await ctx.send("❌ You are not subscribed to DMs for this server.")
            return
        
        # Disable DM subscription
        await self.save_dm_subscription(user_id, guild_id, False)
        
        embed = discord.Embed(
            title="📬 DM Subscription",
            description=f"You will no longer receive DMs for **{ctx.guild.name}**.",
            color=discord.Color.red()
        )
        embed.add_field(name="Server", value=ctx.guild.name, inline=True)
        embed.add_field(name="Status", value="❌ Disabled", inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='dm_status')
    async def dm_status_command(self, ctx):
        """Check your DM subscription status - works in servers or DMs"""
        user_id = ctx.author.id
        
        # If used in DMs, show all subscriptions across all servers
        if ctx.guild is None:
            # Get all DM subscriptions for this user
            user_subscriptions = await self.get_all_dm_subscriptions_for_user(user_id)
            
            if not user_subscriptions:
                embed = discord.Embed(
                    title="📬 DM Subscription Status",
                    description="You are not subscribed to DM notifications for any servers.",
                    color=discord.Color.orange()
                )
                embed.add_field(
                    name="How to Subscribe",
                    value="Use `!dm_subscribe` in any server where you want to receive notifications.",
                    inline=False
                )
                await ctx.send(embed=embed)
                return
            
            # Build status for all subscribed servers
            embed = discord.Embed(
                title="📬 Your DM Subscriptions",
                description=f"You are subscribed to DM notifications for {len(user_subscriptions)} server(s):",
                color=discord.Color.blue()
            )
            
            for sub in user_subscriptions:
                guild_id = sub["guild_id"]
                guild = self.bot.get_guild(int(guild_id))
                
                if guild:
                    # Check if server still has notifications enabled
                    server_sub = await self.get_subscription(guild_id)
                    server_enabled = server_sub and server_sub.get("enabled", False)
                    
                    status_emoji = "✅" if server_enabled else "⚠️"
                    status_text = "Active" if server_enabled else "Server notifications disabled"
                    
                    embed.add_field(
                        name=f"{status_emoji} {guild.name}",
                        value=status_text,
                        inline=True
                    )
                else:
                    # Guild not found (bot might have left)
                    embed.add_field(
                        name=f"❌ Unknown Server",
                        value=f"Guild ID: {guild_id}\n(Bot no longer in server)",
                        inline=True
                    )
            
            embed.set_footer(text="Use `!dm_unsubscribe` in a server to remove DM notifications for that server.")
            await ctx.send(embed=embed)
            return
        
        # If used in a server, show status for that specific server
        guild_id = str(ctx.guild.id)
        
        # Check DM subscription status
        dm_sub = await self.get_dm_subscription(user_id, guild_id)
        is_subscribed = dm_sub and dm_sub.get("enabled", False)
        
        # Check if server has notifications enabled
        subscription = await self.get_subscription(guild_id)
        server_enabled = subscription and subscription.get("enabled", False)
        
        embed = discord.Embed(
            title="📬 DM Subscription Status",
            color=discord.Color.blue() if is_subscribed else discord.Color.orange()
        )
        
        embed.add_field(name="Server", value=ctx.guild.name, inline=True)
        embed.add_field(name="Server Notifications", value="✅ Enabled" if server_enabled else "❌ Disabled", inline=True)
        embed.add_field(name="Your DM Subscription", value="✅ Enabled" if is_subscribed else "❌ Disabled", inline=True)
        
        if not server_enabled:
            embed.description = "This server doesn't have Sea of Thieves notifications enabled."
        elif is_subscribed:
            embed.description = "You will receive DMs when Sea of Thieves notifications are sent in this server."
        else:
            embed.description = "Use `!dm_subscribe` to receive DMs for this server's notifications."
        
        embed.set_footer(text="💡 Tip: DM me `!dm_status` to see all your subscriptions!")
        await ctx.send(embed=embed)

# Setup function
async def setup(bot):
    await bot.add_cog(SubscriptionManager(bot))
