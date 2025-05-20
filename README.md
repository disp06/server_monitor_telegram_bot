# Server Monitoring Telegram Bot

A Telegram bot for monitoring server status (HTTP/IP + port) with user-specific tracking and notifications.

## Features

- 🕒 **15-minute Interval Checks**: Automatic server status monitoring
- 🔔 **Instant Notifications**: Get alerts when server status changes (Online/Offline)
- 👤 **User Isolation**: Each user maintains their own server list
- ➕ **Easy Management**: Add/remove servers via Telegram commands
- 📊 **Status Logging**: Persistent storage in SQLite database

## Installation

1. **Clone Repository**
   ```bash
   git clone https://github.com/yourusername/server-monitoring-bot.git
   cd server-monitoring-bot

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt

3. **Configure Bot Token**
   Get token from @BotFather
   Edit server_monitor_bot.py with your bot token, save:
   ```bash
   BOT_TOKEN=your_bot_token_here

4. Run
   ```bash
   python server_monitor_bot.py

 ## Usage
 Available Commands:
  - **/start** - Show welcome message
  - **/add_server <server:port>** - Add server to monitoring
  - **/remove_server <server:port>** - Remove server from monitoring
  - **/list_servers** - Show all monitored servers

## Example:
  - **/add_server example.com:80**
  - **/add_server 192.168.1.1:443**
  - **/remove_server example.com:80**

## Requirements:
- **Python 3.8+**
- **python-telegram-bot==20.6**
- **python-dotenv==0.19.0**
