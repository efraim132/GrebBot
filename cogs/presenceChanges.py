import discord
from discord.ext import commands
import os
from typing import Optional

DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() in ['true', '1', 'yes']

class PresenceChanges(commands.Cog):
    """Handles presence change events for members"""
    
    def __init__(self, bot):
        self.bot = bot

    def check_if_sea_of_thieves(activity_name: Optional[str] = None):
        """Check if the activity is Sea of Thieves"""
        if not activity_name:
            return False
            
        right_game = "sea of thieves"

        # Debugging output
        if DEBUG_MODE:
            print(f"[DEBUG] Checking if activity '{activity_name}' is Sea of Thieves")

        if activity_name.lower() == right_game:
            return True
        return False

    async def check_sea_of_thieves_activity(self, before, after):
        """Check for Sea of Thieves activity changes and notify subscribers"""
        before_activity = before.activity.name if before.activity else None
        after_activity = after.activity.name if after.activity else None

        # Only check if Sea of Thieves started (removed stop notifications)
        if (not self.check_if_sea_of_thieves(before_activity) and
                self.check_if_sea_of_thieves(after_activity)):

            # Get subscription manager and notify
            subscription_manager = self.bot.get_cog('SubscriptionManager')
            if subscription_manager:
                await subscription_manager.notify_sea_of_thieves_activity(after, "start")

    async def on_tracked_game_activity(self, member, activity_name: str, activity_type: str):
        """Check if the activity is a tracked game"""
        if self.check_if_sea_of_thieves(activity_name):
            print(f"🏴‍☠️ {member.name} {activity_type}ed Sea of Thieves!")


    @commands.Cog.listener()
    async def on_presence_update(self, before, after):
        """Event triggered when a member's presence changes"""
        # Always check for Sea of Thieves activity for notifications
        await self.check_sea_of_thieves_activity(before, after)
        
        if not DEBUG_MODE:
            return
            
        # Check if activity changed
        before_activity = before.activity.name if before.activity else None
        after_activity = after.activity.name if after.activity else None
        
        if before_activity != after_activity:
            if after_activity:
                if before_activity:
                    print(f"🎮 {after.name} switched from '{before_activity}' to '{after_activity}'")
                else:
                    print(f"🎮 {after.name} started playing: {after_activity}")
                
                # Check if the activity is a tracked game
                await self.on_tracked_game_activity(after, after_activity, "start")
            else:
                if before_activity:
                    print(f"🎮 {after.name} stopped playing: {before_activity}")
                    # Removed stop activity tracking since we don't notify for stops



                    







    

# Setup function to add the cog to the bot
async def setup(bot):
    await bot.add_cog(PresenceChanges(bot))