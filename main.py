import nextcord
from nextcord.ext import commands
import os
import sys
import motor.motor_asyncio
from dotenv import load_dotenv

# Ensure stdout supports UTF-8 on Windows consoles
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv()

intents = nextcord.Intents.default()
intents.members = True  
intents.message_content = True 

activity = nextcord.Game(name="❄️ Winter is coming... /startworkout")

bot = commands.Bot(
    intents=intents, 
    activity=activity
)

# Single shared MongoDB client connection pool
mongo_uri = os.getenv("MONGO_URI")
if mongo_uri:
    bot.mongo_client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri, serverSelectionTimeoutMS=5000)
else:
    bot.mongo_client = None
    print("⚠️ MONGO_URI environment variable not found!")

ALLOWED_COGS = [
    "cogs.workout_cog",
    "cogs.flex_cog",
    "cogs.reminder_cog",
    "cogs.hype_cog",
    "cogs.diet_cog",
    "cogs.custom_workout_cog",
    "cogs.help_cog"
]

if __name__ == "__main__":
    for cog in ALLOWED_COGS:
        try:
            bot.load_extension(cog)
            print(f"✅ Loaded: {cog}")
        except Exception as e:
            print(f"❌ Failed to load {cog}: {e}")

@bot.event
async def on_ready():
    print("---")
    print(f"🛡️ Gladiator V is Online")
    print(f"Logged in as: {bot.user.name}")
    print(f"Status: Playing {bot.activity.name}")
    print("---")

bot.run(os.getenv("DISCORD_TOKEN"))