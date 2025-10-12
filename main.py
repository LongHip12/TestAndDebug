from flask import Flask, request, jsonify
import discord
from discord.ext import commands
import asyncio
import json
import os
import threading

TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(os.environ.get("DISCORD_CHANNEL_ID", 0))

counter_file = "counter.json"
if os.path.exists(counter_file):
    with open(counter_file, "r") as f:
        counter = json.load(f).get("count", 0)
else:
    counter = 0

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
app = Flask(__name__)

# Endpoint Roblox gửi request
@app.route("/execute", methods=["POST"])
def execute():
    global counter
    data = request.json
    user = data.get("user", "Unknown")

    counter += 1
    # Lưu counter
    with open(counter_file, "w") as f:
        json.dump({"count": counter}, f)

    print(f"[LOG] Script executed by: {user}, total executed: {counter}")

    # Đổi tên kênh Discord (chạy trong event loop bot)
    async def edit_channel():
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            await channel.edit(name=f"Executed: {counter}")
            print(f"[LOG] Discord channel updated to: Executed: {counter}")
        else:
            print("[WARN] Channel not found or bot missing permissions")
    asyncio.run_coroutine_threadsafe(edit_channel(), bot.loop)

    return jsonify({"status": "success", "executed_count": counter})

# Chạy bot Discord trong thread riêng
def run_bot():
    asyncio.run(bot.start(TOKEN))

threading.Thread(target=run_bot).start()

# Chạy Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
