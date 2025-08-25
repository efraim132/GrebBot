# GrebBot

A Discord bot designed to track Sea of Thieves gaming activity and provide server management utilities.

## Features

### Sea of Thieves Activity Tracking

- Monitors when members start playing Sea of Thieves
- Sends notifications to subscribed Discord channels
- Anti-spam protection with 2-minute cooldown per member per server
- MongoDB database for persistent subscription storage
- Individual DM notifications for users who want personal alerts

### Basic Commands

- `!hello` - Greets the user
- `!ping` - Shows bot latency
- `!info` - Displays bot information
- `!say <message>` - Makes the bot repeat a message
- `!echo <message>` - Echoes the message back
- `!help_commands` - Shows all available commands

### Subscription Management (Admin Only)

- `!subscribe [#channel]` - Subscribe server to Sea of Thieves notifications
- `!unsubscribe` - Disable notifications for the server
- `!subscription_status` - Check current subscription status
- `!cooldown_status [@member]` - Check cooldown status for members
- `!reset_cooldown @member` - Reset cooldown for a specific member

### DM Subscriptions (Any User)

- `!dm_subscribe` - Subscribe to receive DMs when notifications are sent in the current server
- `!dm_unsubscribe` - Unsubscribe from DMs for the current server
- `!dm_status` - Check your DM subscription status for the current server

### Advanced Commands

- `!serverinfo` - Shows detailed server information

## Requirements

- Python 3.8+
- MongoDB database
- Discord bot token

## Installation

1. Clone the repository
2. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file with the following variables:

   ```
   DISCORD_TOKEN=your_discord_bot_token
   MONGODB_URL=mongodb://localhost:27017
   DEBUG_MODE=False
   VERSION=0.1.0
   bot_status=playing with <code>
   ```

4. Set up MongoDB:
   - Install MongoDB locally or use MongoDB Atlas
   - The bot will create a database named `grebbot_db_test`
   - Subscription data is stored in the `sea_of_thieves_subscriptions` collection
   - DM subscription data is stored in the `dm_subscriptions` collection

## Usage

1. Invite the bot to your Discord server with the following permissions:

   - Send Messages
   - Read Messages/View Channels
   - Read Message History
   - Embed Links
   - Manage Messages (optional, for !say command)

2. Use `!subscribe` in a channel to enable Sea of Thieves notifications

3. When members start playing Sea of Thieves, the bot will send notifications to the subscribed channel

## Web interface

This bot has a running web interface that can be used to administrate the functions of this bot. Simply address the IP address of where the bot is running and you can use the bot this way.

## Docker

The bot can be run in a Docker container:

```bash
docker build -t grebbot .
docker run -d --name grebbot grebbot
```

Ensure your `.env` file is properly configured for your Docker environment.

## Database Schema

### Subscriptions Collection

```json
{
  "guild_id": "string",
  "guild_name": "string",
  "channel_id": "number",
  "channel_name": "string",
  "enabled": "boolean",
  "notify_start": "boolean"
}
```

### DM Subscriptions Collection

```json
{
  "user_id": "number",
  "guild_id": "string",
  "enabled": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## Configuration

The bot uses environment variables for configuration:

- `DISCORD_TOKEN` - Your Discord bot token
- `MONGODB_URL` - MongoDB connection string
- `DEBUG_MODE` - Enable debug logging (True/False)
- `VERSION` - Bot version number
- `bot_status` - Custom status message for the bot

## Architecture

The bot is organized into cogs (modules):

- `basic_commands.py` - Basic utility commands
- `advanced_commands.py` - Advanced server information commands
- `presenceChanges.py` - Monitors member presence changes
- `subscription_manager.py` - Handles subscription management and notifications

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.
