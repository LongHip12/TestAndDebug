# Chatgpt:)

# embed_counter_bot.py
# Yêu cầu: pip install -U discord.py pytz
import os
import json
import asyncio
from pathlib import Path
import discord
from discord.ext import tasks
from dotenv import load_dotenv

# --------- CẤU HÌNH - sửa các giá trị sau ----------
load_dotenv()
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")            # <-- thay token bot của bạn
GUILD_ID = 1409783780217983029                 # <-- ID server (guild) chứa kênh
EXECUTED_CHECK_CHANNEL = 1426831461247488060  # <-- ID kênh để quét embed
EXECUTED_CHANNEL = 1426798908146843719        # <-- ID kênh sẽ đổi tên
DATA_DIR = Path("Bot_Data")
DATA_DIR.mkdir(exist_ok=True)
STATE_FILE = DATA_DIR / "executed_state.json"
# ---------------------------------------------------

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.messages = True

client = discord.Client(intents=intents)

def load_state():
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"count": 0}
    return {"count": 0}

def save_state(state: dict):
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"[ERROR] Lưu state thất bại: {e}")

@client.event
async def on_ready():
    print(f"[READY] Bot đăng nhập với: {client.user} (id={client.user.id})")
    # Bắt đầu vòng lặp nếu chưa chạy
    if not check_embeds.is_running():
        check_embeds.start()

@tasks.loop(seconds=5.0)
async def check_embeds():
    """Quét recent messages và đếm tổng số embed trong channel,
       sau đó đổi tên target channel thành 'Executed: X'"""
    try:
        guild = client.get_guild(GUILD_ID)
        if not guild:
            print(f"[WARN] Không tìm thấy guild với ID {GUILD_ID}")
            return

        check_channel = guild.get_channel(EXECUTED_CHECK_CHANNEL)
        target_channel = guild.get_channel(EXECUTED_CHANNEL)

        if check_channel is None:
            print(f"[WARN] Không tìm thấy kênh check (ID {EXECUTED_CHECK_CHANNEL})")
            return
        if target_channel is None:
            print(f"[WARN] Không tìm thấy kênh đổi tên (ID {EXECUTED_CHANNEL})")
            return

        # Lấy tối đa 200 tin nhắn gần nhất (api limit), nếu cần tăng thì loop nhiều lần
        # nhưng 200 thường đủ. Bạn có thể chỉnh limit.
        messages = [msg async for msg in check_channel.history(limit=200)]
        embed_count = sum(len(m.embeds) for m in messages)

        # Cập nhật tên kênh nếu khác
        new_name = f"Executed: {embed_count}"
        if target_channel.name != new_name:
            try:
                await target_channel.edit(name=new_name)
                print(f"[OK] Đã đổi tên kênh {target_channel.id} -> {new_name}")
            except discord.Forbidden:
                print("[ERROR] Thiếu quyền Manage Channels để đổi tên kênh.")
            except Exception as e:
                print(f"[ERROR] Lỗi khi đổi tên kênh: {e}")
        else:
            print(f"[INFO] Tên kênh đã đúng: {new_name}")

        # Lưu trạng thái
        save_state({"count": embed_count})

    except Exception as e:
        print(f"[ERROR] Exception trong check_embeds: {e}")

@client.event
async def on_message(message):
    # Chỉ in debug, không làm gì khác ở đây
    # Bỏ qua tin nhắn bot hoặc DM
    if message.author.bot or message.guild is None:
        return
    # (Không cần xử lý gì thêm vì ta dùng tasks.loop để đếm)
    # Nhưng vẫn có thể debug
    # print(f"[MSG] {message.author} → channel {message.channel.id} (embeds={len(message.embeds)})")
    return

if __name__ == "__main__":
    # Tạo file trạng thái nếu chưa có
    if not STATE_FILE.exists():
        save_state({"count": 0})
    try:
        client.run(BOT_TOKEN)
    except Exception as e:
        print(f"[FATAL] Bot không thể khởi động: {e}")
