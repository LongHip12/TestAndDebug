from flask import Flask, request, jsonify
import discord
from discord.ext import commands
import asyncio
import json
import os
import threading
from datetime import datetime

# ===== Cấu hình =====
TOKEN = os.environ.get("DISCORD_BOT_TOKEN")  # Discord Bot Token
CHANNEL_ID = int(os.environ.get("DISCORD_CHANNEL_ID", 0))  # Discord channel ID
counter_file = "counter.json"
print("Load")

# ===== Load counter =====
if os.path.exists(counter_file):
    with open(counter_file, "r") as f:
        counter = json.load(f).get("count", 0)
else:
    counter = 0

# ===== Discord Bot =====
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ===== Flask App =====
app = Flask(__name__)

# ----- Route / : hiển thị server running -----
@app.route("/", methods=["GET"])
def index():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"<h2>🚀 LonelyHub API is running! ({now}) Flask + Discord Bot active.</h2>", 200

# ----- Route /execute : nhận POST từ Roblox -----
@app.route("/execute", methods=["POST"])
def execute():
    global counter
    try:
        data = request.json
        user = data.get("user", "Unknown")
        counter += 1

        # Lưu counter
        with open(counter_file, "w") as f:
            json.dump({"count": counter}, f)

        # Log POST request
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{now}] POST received from '{user}'. Total executed: {counter}")

        # Đổi tên channel Discord async
        async def edit_channel():
            await bot.wait_until_ready()
            channel = bot.get_channel(CHANNEL_ID)
            if channel:
                await channel.edit(name=f"Executed: {counter}")
                print(f"[{now}] Discord channel name updated to 'Executed: {counter}'")

        asyncio.run_coroutine_threadsafe(edit_channel(), bot.loop)

        return jsonify({"status": "success", "executed_count": counter})

    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# ===== Chạy bot Discord trong thread =====
def run_bot():
    asyncio.run(bot.start(TOKEN))

threading.Thread(target=run_bot, daemon=True).start()

# ===== Run Flask =====
if __name__ == "__main__":
    print("🚀 Flask server is running... Listening for POST requests on port 8000")
    app.run(host="0.0.0.0", port=8000)
