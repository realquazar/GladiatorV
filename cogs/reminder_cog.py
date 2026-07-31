import nextcord
from nextcord.ext import commands, tasks
import datetime
import motor.motor_asyncio
import os
import re

TIMEZONE_OFFSETS = {
    "IST": datetime.timedelta(hours=5, minutes=30),
    "UTC": datetime.timedelta(hours=0),
    "EST": datetime.timedelta(hours=-5),
    "CST": datetime.timedelta(hours=-6),
    "MST": datetime.timedelta(hours=-7),
    "PST": datetime.timedelta(hours=-8),
    "BST": datetime.timedelta(hours=1),
    "AEST": datetime.timedelta(hours=10)
}

def parse_time_input(time_str: str):
    """
    Parses flexible human time inputs like '3:11 PM', '3:11PM', '03:11 PM', '3:11 pm', '15:11', '3:11 AM', '6:00 AM to 7:00 AM'
    Returns datetime.time object or None if invalid.
    """
    clean = time_str.split("to")[0].strip()
    match = re.search(r"(\d{1,2}):(\d{2})\s*([ap]\.?m\.?)?", clean, re.IGNORECASE)
    if not match:
        return None
    
    hr, mn, period = int(match.group(1)), int(match.group(2)), match.group(3)
    if hr < 0 or hr > 23 or mn < 0 or mn > 59:
        return None

    if period:
        p = period.replace(".", "").upper()
        if p == "PM" and hr < 12:
            hr += 12
        elif p == "AM" and hr == 12:
            hr = 0

    return datetime.time(hr, mn)


class WorkoutReminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if hasattr(bot, "mongo_client") and bot.mongo_client is not None:
            self.client = bot.mongo_client
        else:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGO_URI"), serverSelectionTimeoutMS=5000)
        self.db = self.client["gladiator_db"]
        self.reminders = self.db["workout_reminders"]
        
        self.check_reminders.start()

    def cog_unload(self):
        self.check_reminders.cancel()

    @nextcord.slash_command(name="remindworkout", description="Set your daily workout time and enable Discord reminders.")
    async def remind_workout(
        self, 
        interaction: nextcord.Interaction, 
        time_range: str = nextcord.SlashOption(description="e.g., 3:11 PM or 6:00 AM to 7:00 AM"),
        timezone_choice: str = nextcord.SlashOption(
            name="timezone",
            description="Your local timezone (default is IST UTC+5:30)",
            required=False,
            choices={
                "IST (UTC+5:30)": "IST",
                "UTC (UTC+0)": "UTC",
                "EST (UTC-5)": "EST",
                "CST (UTC-6)": "CST",
                "MST (UTC-7)": "MST",
                "PST (UTC-8)": "PST",
                "GMT / BST (UTC+1)": "BST",
                "AEST (UTC+10)": "AEST"
            },
            default="IST"
        ),
        channel: nextcord.TextChannel = nextcord.SlashOption(description="Channel to receive the reminder ping", required=False)
    ):
        await interaction.response.defer(ephemeral=True)

        try:
            existing_reminder = await self.reminders.find_one({"user_id": str(interaction.user.id)})
        except Exception as db_err:
            print(f"MongoDB error: {db_err}")
            await interaction.followup.send("⚠️ Database error occurred. Please try again.", ephemeral=True)
            return
        
        if existing_reminder:
            existing_time = existing_reminder.get("time_range_text", "Unknown Time")
            
            view = ManageExistingReminderView(self, interaction.user.id, time_range, timezone_choice, channel)
            await interaction.followup.send(
                f"❌ **You can't set a new time directly because it is already set at `{existing_time}`!**\n\n"
                f"Would you like to **Update** your current schedule to `{time_range}` (`{timezone_choice}`) or **Delete** your existing reminder entirely?",
                view=view,
                ephemeral=True
            )
            return

        await self._process_reminder_setup(interaction, time_range, timezone_choice, channel)

    async def _process_reminder_setup(
        self, 
        interaction: nextcord.Interaction, 
        time_range: str, 
        timezone_str: str = "IST",
        channel: nextcord.TextChannel = None, 
        is_update: bool = False
    ):
        target_channel = channel or interaction.channel

        parsed_time = parse_time_input(time_range)
        if not parsed_time:
            await interaction.followup.send(
                "⚠️ **Invalid time format!** Please use formats like `3:11 PM`, `15:11`, or `6:00 AM to 7:00 AM`.", 
                ephemeral=True
            )
            return

        # Calculate exact ping time (Workout Time minus 5 minutes) in user's local timezone
        workout_dt_naive = datetime.datetime.combine(datetime.date.today(), parsed_time)
        ping_dt_naive = workout_dt_naive - datetime.timedelta(minutes=5)

        tz_offset = TIMEZONE_OFFSETS.get(timezone_str, TIMEZONE_OFFSETS["IST"])
        tz_info = datetime.timezone(tz_offset)
        local_ping_dt = ping_dt_naive.replace(tzinfo=tz_info)
        utc_ping_dt = local_ping_dt.astimezone(datetime.timezone.utc)

        reminder_data = {
            "user_id": str(interaction.user.id),
            "guild_id": interaction.guild_id,
            "channel_id": target_channel.id,
            "timezone": timezone_str,
            "utc_ping_hour": utc_ping_dt.hour,
            "utc_ping_minute": utc_ping_dt.minute,
            "ping_hour": ping_dt_naive.hour,
            "ping_minute": ping_dt_naive.minute,
            "start_hour": parsed_time.hour,
            "start_minute": parsed_time.minute,
            "time_range_text": time_range,
            "enabled": True
        }

        await self.reminders.update_one(
            {"user_id": str(interaction.user.id)},
            {"$set": reminder_data},
            upsert=True
        )

        status_msg = "Updated!" if is_update else "Set!"
        start_time_formatted = parsed_time.strftime("%I:%M %p").lstrip("0")
        await interaction.followup.send(
            f"✅ **Reminder {status_msg}** I will ping you in {target_channel.mention} 5 minutes before `{start_time_formatted}` ({timezone_str}) every day. Get ready to train! 🥊",
            ephemeral=True
        )

    @tasks.loop(minutes=1)
    async def check_reminders(self):
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        utc_hour = now_utc.hour
        utc_minute = now_utc.minute

        # Query UTC-based reminders first
        cursor = self.reminders.find({
            "enabled": True,
            "utc_ping_hour": utc_hour,
            "utc_ping_minute": utc_minute
        })

        async for doc in cursor:
            await self._send_reminder_ping(doc)

        # Fallback for legacy documents without utc_ping_hour
        now_local = datetime.datetime.now()
        legacy_cursor = self.reminders.find({
            "enabled": True,
            "utc_ping_hour": {"$exists": False},
            "$or": [
                {"ping_hour": now_local.hour, "ping_minute": now_local.minute},
                {"start_hour": now_local.hour, "start_minute": now_local.minute}
            ]
        })

        async for doc in legacy_cursor:
            await self._send_reminder_ping(doc)

    async def _send_reminder_ping(self, doc):
        channel = self.bot.get_channel(doc["channel_id"])
        if not channel:
            try:
                channel = await self.bot.fetch_channel(doc["channel_id"])
            except Exception:
                channel = None

        if channel:
            user_id = doc["user_id"]
            time_str = doc["time_range_text"]
            tz_str = doc.get("timezone", "IST")
            
            view = ReminderPingView(self.reminders, int(user_id))
            try:
                await channel.send(
                    f"🚨 <@{user_id}> **WORKOUT REMINDER!** 🚨\n"
                    f"Your workout slot (`{time_str}` {tz_str}) starts in **5 minutes**! Time to suit up and gear up! ⚔️",
                    view=view
                )
            except Exception as e:
                print(f"Failed to send reminder to user {user_id}: {e}")

    @check_reminders.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()


class ManageExistingReminderView(nextcord.ui.View):
    def __init__(self, cog, user_id, new_time_range, new_timezone, new_channel):
        super().__init__(timeout=60)
        self.cog = cog
        self.user_id = user_id
        self.new_time_range = new_time_range
        self.new_timezone = new_timezone
        self.new_channel = new_channel

    @nextcord.ui.button(label="Update Time", style=nextcord.ButtonStyle.primary)
    async def update_time(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("This menu isn't for you!", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        await self.cog._process_reminder_setup(interaction, self.new_time_range, self.new_timezone, self.new_channel, is_update=True)

    @nextcord.ui.button(label="Delete Reminder", style=nextcord.ButtonStyle.danger)
    async def delete_reminder(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("This menu isn't for you!", ephemeral=True)

        await interaction.response.defer(ephemeral=True)
        await self.cog.reminders.delete_one({"user_id": str(self.user_id)})
        await interaction.followup.send("🗑️ **Your workout reminder has been deleted successfully.**", ephemeral=True)


class ReminderPingView(nextcord.ui.View):
    def __init__(self, reminders_collection, target_user_id):
        super().__init__(timeout=None)
        self.reminders_collection = reminders_collection
        self.target_user_id = target_user_id

    @nextcord.ui.button(label="Delete Reminder", style=nextcord.ButtonStyle.danger)
    async def delete_from_ping(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user.id != self.target_user_id:
            return await interaction.response.send_message("Only the scheduled athlete can delete this reminder!", ephemeral=True)

        await interaction.response.defer(ephemeral=True)
        await self.reminders_collection.delete_one({"user_id": str(self.target_user_id)})
        await interaction.followup.send("🗑️ **Reminder deleted.** You will no longer receive pings.", ephemeral=True)

    @nextcord.ui.button(label="How to Update Time", style=nextcord.ButtonStyle.secondary)
    async def update_help(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user.id != self.target_user_id:
            return await interaction.response.send_message("This button is for the scheduled user.", ephemeral=True)

        await interaction.response.send_message(
            "⚙️ To change your workout slot, simply run the `/remindworkout` command again with your new time! You will be given the option to overwrite your existing time.",
            ephemeral=True
        )


def setup(bot):
    bot.add_cog(WorkoutReminder(bot))