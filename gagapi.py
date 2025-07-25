import asyncio
import json
from collections import defaultdict
from datetime import datetime
import websockets
import httpx
import discord
from discord.ext import commands
from datetime import datetime, timedelta



DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/......"
MENTION_USER_ID = []
TARGET_USER_ID = []
DISCORD_TOKEN = ""
TOKEN = ""

ITEM_SPESIAL = {
    "gear": {"Master Sprinkler", "Godly Sprinkler", "Level Up Lollipop", "Medium Treat", "Medium Toy"},
    "eggs": {"Paradise Egg", "Bug Egg", "Bee Egg"},
    "event": {"Zen Egg", "Koi"}
}

latest_seed = []
latest_gear = []
latest_eggs = []
lastest_event = []
current_ws_data = {}
last_sent_special_time_egg = None
last_sent_special_time_event = None
last_sent_egg_names = set()
last_sent_event_names = set()
last_special_eggs = set()
last_special_event = set()

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents)

def format_item_name(name):
    if name == "Master Sprinkler":
        return f"<:mastersprinkler:1398133364376080465> {name}"
    elif name == "Godly Sprinkler":
        return f"<:godlysprinkler:1398133605556817930> {name}"
    elif name == "Paradise Egg":
        return f"<:paradiseegg:1398134367297208340> {name}"
    elif name == "Bug Egg":
        return f"<:bugegg:1398134619500445841> {name}"
    elif name == "Bee Egg":
        return f"<:beeegg:1398134908949364736> {name}"
    elif name == "Zen Egg":
        return f"<:zenegg:1398180049534062714> {name}"
    elif name == "Koi":
        return f"<:koipet:1398180073315766354> {name}"
    elif name == "Level Up Lollipop":
        return f"<:lolipopgear:1398254993202745445> {name}"
    elif name == "Medium Treat":
        return f"<:mediumtreatgear:1398255916499075082> {name}"
    elif name == "Medium Toy":
        return f"<:mediumtoygear:1398255931124355092> {name}"
    return f"- {name}"

def combine_items_by_name(items):
    combined = defaultdict(int)
    for item in items:
        combined[item["name"]] += item.get("quantity", 0)
    return [{"name": name, "quantity": qty} for name, qty in combined.items()]

def clean_items(items):
    return [{"name": item["name"], "quantity": item.get("quantity", 0)} for item in items]

def format_data(seed, gear, eggs, event, tag_user=False):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    lines = [f"-------- {now} ---------"]

    if seed:
        lines.append("\n🌱 Seed:")
        for item in seed:
            lines.append(f"{format_item_name(item['name'])} x{item['quantity']}")

    if gear:
        lines.append("\n📦 Gear:")
        for item in gear:
            lines.append(f"{format_item_name(item['name'])} x{item['quantity']}")

    if eggs:
        lines.append("\n🥚 Eggs:")
        for item in eggs:
            lines.append(f"{format_item_name(item['name'])} x{item['quantity']}")
    if event:
        lines.append("\n🎉 Event:")
        for item in event:
            lines.append(f"{format_item_name(item['name'])} x{item['quantity']}")
            
    if tag_user:
        mentions = " ".join([f"<@{user_id}>" for user_id in MENTION_USER_ID])
        lines.append(f"\n🔔 {mentions} Ada item spesial!")

    return "\n".join(lines)

async def send_discord_webhook(content: str):
    async with httpx.AsyncClient() as client:
        await client.post(DISCORD_WEBHOOK_URL, json={"content": content})

async def send_dm_if_needed(gear_items, egg_items, event_items):
    global last_special_eggs, last_special_event, last_sent_special_time_egg, last_sent_special_time_event

    now = datetime.now()

    # Reset otomatis setelah 20 menit
    if last_sent_special_time_egg and now - last_sent_special_time_egg >= timedelta(minutes=20):
        print("🕒 20 menit telah lewat — reset last_special_eggs dan event")
        last_special_eggs = set()
        last_sent_special_time_egg = None

    # Reset otomatis setelah 60 menit
    if last_sent_special_time_event and now - last_sent_special_time_event >= timedelta(minutes=60):
        print("🕒 60 menit telah lewat — reset last_special_eggs dan event")
        last_special_event = set()
        last_sent_special_time_event = None

    gear_names = [item["name"] for item in gear_items if item["name"] in ITEM_SPESIAL["gear"]]
    egg_names = [item["name"] for item in egg_items if item["name"] in ITEM_SPESIAL["eggs"]]
    event_names = [item["name"] for item in event_items if item["name"] in ITEM_SPESIAL["event"]]

    current_special_eggs = set(egg_names)
    current_special_event = set(event_names)

    if (
        not gear_names and
        current_special_eggs == last_special_eggs and
        current_special_event == last_special_event
    ):
        print("✅ Tidak ada perubahan spesial, tidak kirim DM.")
        return


    last_special_eggs = current_special_eggs
    last_special_event = current_special_event
    

    message_lines = ["🔔 **Item spesial tersedia!**"]
    if gear_names:
        message_lines.append(f"🛠️ Gear: {', '.join(gear_names)}")
    if egg_names:
        message_lines.append(f"🥚 Eggs: {', '.join(egg_names)}")
    if event_names:
        message_lines.append(f"🎉 Event: {', '.join(event_names)}")

    full_message = "\n".join(message_lines)

    for user_id in TARGET_USER_ID:
        try:
            user = await client.fetch_user(user_id)
            dm_channel = await user.create_dm()
            deleted_count = 0

            async for msg in dm_channel.history(limit=100):
                if msg.author.id == client.user.id:
                    try:
                        await msg.delete()
                        deleted_count += 1
                        await asyncio.sleep(0.3)
                    except Exception as e:
                        print(f"⚠️ Gagal hapus pesan: {e}")

            await dm_channel.send(full_message)
            print(f"✅ DM berhasil dikirim ke {user.name} ({user.id}), hapus {deleted_count} pesan lama")
            if egg_names:
                last_sent_special_time_egg = now
            if event_names:
                last_sent_special_time_event = now
        except Exception as e:
            print(f"❌ Gagal mengirim DM ke {user_id}: {e}")



async def validate_every_10s():
    global latest_seed, latest_gear, latest_eggs, latest_event, current_ws_data, last_special_eggs, last_special_event
    while True:
        await asyncio.sleep(10)
        if current_ws_data:

            new_seeds = clean_items(current_ws_data.get("seeds", []))
            new_gear = clean_items(current_ws_data.get("gear", []))
            new_eggs = combine_items_by_name(current_ws_data.get("eggs", []))
            new_event = clean_items(current_ws_data.get("honey", []))

            if new_gear != latest_gear or new_eggs != latest_eggs or new_event != latest_event:
                print("🔁 Validasi mendeteksi perubahan data! Mengirim ulang ke Discord.")
                latest_seed = new_seeds
                latest_gear = new_gear
                latest_eggs = new_eggs
                latest_event = new_event
                
                new_special_eggs = {item["name"] for item in new_eggs if item["name"] in ITEM_SPESIAL["eggs"]}
                new_special_event = {item["name"] for item in new_event if item["name"] in ITEM_SPESIAL["event"]}

                tag_required = (
                    any(item["name"] in ITEM_SPESIAL["gear"] for item in new_gear) or
                    new_special_eggs != last_special_eggs or
                    new_special_event != last_special_event
                )
                    
                content = format_data(new_seeds, new_gear, new_eggs, new_event, tag_user=tag_required)

                await send_discord_webhook(content)
                await send_dm_if_needed(new_gear, new_eggs, new_event)

async def websocket_listener():
    uri = "wss://ws.growagardenpro.com/"
    global current_ws_data
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                print("✅ Terhubung ke WebSocket...")
                async for message in websocket:
                    data = json.loads(message)
                    # print(data)
                    if data.get("type") and "data" in data:
                        current_ws_data = data["data"]
        except Exception as e:
            print(f"⚠️ WebSocket error: {e}. Reconnect dalam 5 detik...")
            await asyncio.sleep(5)

@client.event
async def on_ready():
    print(f"✅ Bot Discord {client.user} sudah online.")
    asyncio.create_task(websocket_listener())
    asyncio.create_task(validate_every_10s())
    asyncio.create_task(reset_egg_tag_cache())
    asyncio.create_task(reset_event_tag_cache())
    try:
        await client.wait_until_ready()
        synced = await client.tree.sync()
        print(f"✅ Slash command berhasil disinkronisasi: {len(synced)} command")
        print(f"Daftar command: {[cmd.name for cmd in synced]}")
    except Exception as e:
        print(f"❌ Gagal sync slash command: {e}")

async def reset_egg_tag_cache():
    global last_sent_egg_names
    while True:
        await asyncio.sleep(20 * 60)  # 20 menit
        print("🔄 Reset cache Egg spesial.")
        last_sent_egg_names.clear()
        
async def reset_event_tag_cache():
    global last_sent_event_names
    while True:
        await asyncio.sleep(60 * 60)  # 60 menit
        print("🔄 Reset cache Egg spesial.")
        last_sent_event_names.clear()
        
@client.tree.command(name="hello", description="Sapa pengguna.")
async def hello_command(interaction: discord.Interaction):
    print(f"📥 Diterima request dari: {interaction.user.name}")
    await interaction.response.defer()
    await asyncio.sleep(2)
    await interaction.followup.send(f"Halo, {interaction.user.name}!")

@client.tree.command(name="clear_dm", description="Hapus semua pesan yang dikirim bot di DM kamu.")
async def clear_dm(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    try:
        dm_channel = await interaction.user.create_dm()
        deleted_count = 0

        async for msg in dm_channel.history(limit=100):
            if msg.author.id == client.user.id:
                try:
                    await msg.delete()
                    deleted_count += 1
                    await asyncio.sleep(0.3)
                except Exception as e:
                    print(f"Gagal hapus pesan: {e}")
        await interaction.followup.send(f"✅ Berhasil menghapus {deleted_count} pesan yang dikirim bot di DM kamu.", ephemeral=True)

    except Exception as e:
        await interaction.followup.send(f"❌ Terjadi kesalahan: {e}", ephemeral=True)

# async def main():
#     await client.start(DISCORD_TOKEN)

if __name__ == "__main__":
    # asyncio.run(main())
    client.run(DISCORD_TOKEN)
