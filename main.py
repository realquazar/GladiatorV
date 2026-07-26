import nextcord
from nextcord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

intents = nextcord.Intents.default()
intents.members = True  
intents.message_content = True 

activity = nextcord.Game(name="❄️ Winter is coming... /startworkout")

bot = commands.Bot(
    intents=intents, 
    activity=activity
)

ALLOWED_COGS = [
    "cogs.workout_cog",
    "cogs.flex_cog",
    "cogs.reminder_cog",
    "cogs.hype_cog",
    "cogs.diet_cog",
    "cogs.custom_workout_cog"
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
    
    await bot.sync_all_application_commands()
    print("⚔️ Application command tree synced and cleaned!")
    print("---")

bot.run(os.getenv("DISCORD_TOKEN"))