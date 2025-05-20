import logging
import sqlite3
import socket
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Settings
TOKEN = "INSERT_YOUR_BOT_TOKEN_HERE"
CHECK_INTERVAL = 900  # 15 minutes in seconds

# Config log
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Init data
conn = sqlite3.connect("servers.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute(
    """CREATE TABLE IF NOT EXISTS servers
                  (user_id INTEGER, server TEXT, status BOOLEAN)"""
)
conn.commit()

def check_server(server: str) -> bool:
    """Checking avalible of server"""
    try:
        if ":" in server:
            host, port = server.split(":")
            port = int(port)
        else:
            host = server
            port = 80

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10)
            s.connect((host, port))
        return True
    except Exception as e:
        return False

async def monitor_servers(context: ContextTypes.DEFAULT_TYPE):
    """Periodical checking servers"""
    cursor.execute("SELECT DISTINCT user_id FROM servers")
    users = cursor.fetchall()

    for (user_id,) in users:
        cursor.execute("SELECT server, status FROM servers WHERE user_id=?", (user_id,))
        servers = cursor.fetchall()

        for server, old_status in servers:
            new_status = check_server(server)
            if new_status != old_status:
                cursor.execute(
                    "UPDATE servers SET status=? WHERE user_id=? AND server=?",
                    (new_status, user_id, server),
                )
                conn.commit()

                status_text = "ONLINE" if new_status else "OFFLINE"
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"🚨 Status of server {server} changed: {status_text}",
                )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    await update.message.reply_text(
        f"Hello {user.first_name}! I'm monitor server status bot.\n"
        "Доступные команды:\n"
        "/add_server <сервер:порт> - Add server\n"
        "/remove_server <сервер:порт> - Del server\n"
        "/list_servers - List of servers"
    )

async def add_server(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add server"""
    user_id = update.effective_user.id
    args = context.args

    if not args:
        await update.message.reply_text("Enter a server in format example.com:80")
        return

    server = args[0].lower()
    if not validate_server(server):
        await update.message.reply_text("Incorrect format. Use example.com:80")
        return

    cursor.execute("SELECT * FROM servers WHERE user_id=? AND server=?", (user_id, server))
    if cursor.fetchone():
        await update.message.reply_text("This server already added")
        return

    status = check_server(server)
    cursor.execute("INSERT INTO servers VALUES (?, ?, ?)", (user_id, server, status))
    conn.commit()

    await update.message.reply_text(
        f"Server {server} added. Current status: {'ONLINE' if status else 'OFFLINE'}"
    )

async def remove_server(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Del server"""
    user_id = update.effective_user.id
    args = context.args

    if not args:
        await update.message.reply_text("Choose server for delete")
        return

    server = args[0].lower()
    cursor.execute("DELETE FROM servers WHERE user_id=? AND server=?", (user_id, server))
    conn.commit()

    if cursor.rowcount > 0:
        await update.message.reply_text(f"Server {server} deleted")
    else:
        await update.message.reply_text("Server not found")

async def list_servers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show list of servers"""
    user_id = update.effective_user.id
    cursor.execute("SELECT server, status FROM servers WHERE user_id=?", (user_id,))
    servers = cursor.fetchall()

    if not servers:
        await update.message.reply_text("You don't have added servers")
        return

    message = "List of your servers:\n" + "\n".join(
        [f"{server} - {'ONLINE' if status else 'OFFLINE'}" for server, status in servers]
    )
    await update.message.reply_text(message)

def validate_server(server: str) -> bool:
    """Validation of server format"""
    parts = server.split(":")
    if len(parts) != 2 or not parts[1].isdigit():
        return False
    return True

def main():
    # Init bot
    application = Application.builder().token(TOKEN).build()

    # Registering command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add_server", add_server))
    application.add_handler(CommandHandler("remove_server", remove_server))
    application.add_handler(CommandHandler("list_servers", list_servers))

    # Config timing check
    application.job_queue.run_repeating(
        monitor_servers,
        interval=CHECK_INTERVAL,
        first=0,
    )

    # Run Bot
    application.run_polling()

if __name__ == "__main__":
    main()