import nextcord
from nextcord.ext import commands, tasks
import datetime
import motor.motor_asyncio
import os
import re
from bson import ObjectId

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

# Default training days if the user doesn't specify their own. Monday=0 ... Sunday=6.
DEFAULT_TRAINING_DAYS = [0, 1, 3, 4, 5]  # Mon, Tue, Thu, Fri, Sat

DAY_NAME_TO_INT = {
    "mon": 0, "monday": 0,
    "tue": 1, "tues": 1, "tuesday": 1,
    "wed": 2, "weds": 2, "wednesday": 2,
    "thu": 3, "thur": 3, "thurs": 3, "thursday": 3,
    "fri": 4, "friday": 4,
    "sat": 5, "saturday": 5,
    "sun": 6, "sunday": 6,
}

DAY_DISPLAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _guild_id_filter(guild_id):
    if guild_id is None:
        return None
    try:
        g_int = int(guild_id)
        return {"$in": [g_int, str(g_int)]}
    except (ValueError, TypeError):
        return str(guild_id)


def parse_days_input(days_str: str):
    """
    Parses a free-text list of days like 'Mon, Wed, Fri' or 'monday tuesday'.
    Returns a sorted list of unique weekday ints (0=Mon..6=Sun).
    Returns an empty list if nothing valid could be parsed.
    """
    tokens = re.split(r"[,\s/]+", days_str.strip().lower())
    result = set()
    for tok in tokens:
        tok = tok.strip(".")
        if tok in DAY_NAME_TO_INT:
            result.add(DAY_NAME_TO_INT[tok])
    return sorted(result)


def format_days(day_ints):
    if not day_ints or not isinstance(day_ints, (list, tuple, set)):
        day_ints = DEFAULT_TRAINING_DAYS
    valid_days = [d for d in sorted(day_ints) if isinstance(d, int) and 0 <= d <= 6]
    if not valid_days:
        valid_days = DEFAULT_TRAINING_DAYS
    return ", ".join(DAY_DISPLAY_NAMES[d] for d in valid_days)


def parse_time_input(time_str: str):
    """
    Parses flexible human time inputs like '3:11 PM', '3:11PM', '03:11 PM', '3:11 pm', '15:11', '3:11 AM'.
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
        self.bot.loop.create_task(self._ensure_indexes())

    async def _ensure_indexes(self):
        try:
            # Enforce 1 reminder per user per server at DB level to prevent spam & race conditions
            await self.reminders.create_index(
                [("user_id", 1), ("guild_id", 1)],
                unique=True
            )
        except Exception as e:
            print(f"[WorkoutReminder] Index check warning: {e}")

    def cog_unload(self):
        self.check_reminders.cancel()

    def _bot_can_send(self, guild, channel):
        if not guild or not channel:
            return False
        bot_member = guild.me
        if not bot_member:
            return True
        perms = channel.permissions_for(bot_member)
        return perms.view_channel and perms.send_messages

    @nextcord.slash_command(name="remindworkout", description="Set your daily workout time and enable Discord reminders.")
    async def remind_workout(
        self, 
        interaction: nextcord.Interaction, 
        time: str = nextcord.SlashOption(description="e.g., 6:00 AM or 3:11 PM"),
        timezone_choice: str = nextcord.SlashOption(
            name="timezone",
            description="Your local timezone (default is GMT, UTC+0)",
            required=False,
            choices={
                "GMT / UTC (UTC+0)": "UTC",
                "IST (UTC+5:30)": "IST",
                "EST (UTC-5)": "EST",
                "CST (UTC-6)": "CST",
                "MST (UTC-7)": "MST",
                "PST (UTC-8)": "PST",
                "BST (UTC+1)": "BST",
                "AEST (UTC+10)": "AEST"
            },
            default="UTC"
        ),
        channel: nextcord.TextChannel = nextcord.SlashOption(description="Channel to receive the reminder ping", required=False),
        days: str = nextcord.SlashOption(
            description="Days to be pinged, e.g. 'Mon, Wed, Fri'. Defaults to Mon, Tue, Thu, Fri, Sat.",
            required=False,
            default=None
        )
    ):
        await interaction.response.defer(ephemeral=True)

        if interaction.guild is None:
            await interaction.followup.send("⚠️ This command only works inside a server channel, not in DMs.", ephemeral=True)
            return

        target_channel = channel or interaction.channel

        if not self._bot_can_send(interaction.guild, target_channel):
            await interaction.followup.send(
                f"⚠️ **Permission Error!** I do not have permission to view and send messages in {target_channel.mention}. "
                f"Please choose a channel where I have permissions.",
                ephemeral=True
            )
            return

        try:
            existing_reminder = await self.reminders.find_one({
                "user_id": str(interaction.user.id),
                "guild_id": _guild_id_filter(interaction.guild_id)
            })
        except Exception as db_err:
            print(f"MongoDB error: {db_err}")
            await interaction.followup.send("⚠️ Database error occurred. Please try again.", ephemeral=True)
            return
        
        if existing_reminder:
            existing_time = existing_reminder.get("time_range_text", "Unknown Time")
            existing_ch_id = existing_reminder.get("channel_id")
            existing_ch_str = f"<#{existing_ch_id}>" if existing_ch_id else "a channel"
            
            view = ManageExistingReminderView(self, interaction.user.id, interaction.guild_id, time, timezone_choice, target_channel, days)
            await interaction.followup.send(
                f"❌ **You already have a reminder set in this server ({existing_ch_str} at `{existing_time}`)!**\n"
                f"To prevent spam, only one reminder is allowed per server, though you can set one in as many different servers as you like.\n\n"
                f"Would you like to **Update** this server's reminder to `{time}` in {target_channel.mention} (`{timezone_choice}`) or **Delete** it entirely? Use `/myreminders` any time to see and manage all your reminders.",
                view=view,
                ephemeral=True
            )
            return

        await self._process_reminder_setup(interaction, time, timezone_choice, target_channel, days_str=days)

    @nextcord.slash_command(name="myreminders", description="View and manage every workout reminder you've set across all servers.")
    async def my_reminders(self, interaction: nextcord.Interaction):
        await interaction.response.defer(ephemeral=True)

        try:
            cursor = self.reminders.find({
                "user_id": {"$in": [str(interaction.user.id), int(interaction.user.id)]}
            })
            all_reminders = await cursor.to_list(length=25)
        except Exception as e:
            print(f"MongoDB error in /myreminders: {e}")
            await interaction.followup.send("⚠️ Database error occurred. Please try again.", ephemeral=True)
            return

        if not all_reminders:
            await interaction.followup.send(
                "You don't have any workout reminders set yet.\n"
                "-# Use `/remindworkout` in a server channel to set one.",
                ephemeral=True
            )
            return

        embed = nextcord.Embed(
            title="🔔 Your Workout Reminders",
            description="Every server you've set a reminder in. Select one below to delete it.",
            color=0x3498db
        )
        for r in all_reminders:
            guild_name = str(r.get("guild_name") or "Unknown Server")
            ch_id = r.get("channel_id")
            channel_mention = f"<#{ch_id}>" if ch_id else "Unknown Channel"
            time_text = str(r.get("time_range_text") or "Unknown time")
            tz = str(r.get("timezone") or "UTC")
            days_text = format_days(r.get("training_days"))
            embed.add_field(
                name=f"🏟️ {guild_name}",
                value=f"📍 {channel_mention}\n⏰ `{time_text}` ({tz})\n📅 {days_text}",
                inline=False
            )

        view = ReminderManageView(self, all_reminders)
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    async def _process_reminder_setup(
        self, 
        interaction: nextcord.Interaction, 
        time: str, 
        timezone_str: str = "UTC",
        channel: nextcord.TextChannel = None, 
        is_update: bool = False,
        days_str: str = None
    ):
        target_channel = channel or interaction.channel

        parsed_time = parse_time_input(time)
        if not parsed_time:
            await interaction.followup.send(
                "⚠️ **Invalid time format!** Please use formats like `6:00 AM` or `3:11 PM`.", 
                ephemeral=True
            )
            return

        if days_str and days_str.strip():
            training_days = parse_days_input(days_str)
            if not training_days:
                await interaction.followup.send(
                    "⚠️ **Invalid days!** Use day names or short forms separated by commas, e.g. `Mon, Wed, Fri`.",
                    ephemeral=True
                )
                return
        else:
            training_days = DEFAULT_TRAINING_DAYS.copy()

        # Calculate exact ping time (Workout Time minus 5 minutes) in user's local timezone
        workout_dt_naive = datetime.datetime.combine(datetime.date.today(), parsed_time)
        ping_dt_naive = workout_dt_naive - datetime.timedelta(minutes=5)

        tz_offset = TIMEZONE_OFFSETS.get(timezone_str, TIMEZONE_OFFSETS["UTC"])
        tz_info = datetime.timezone(tz_offset)
        local_ping_dt = ping_dt_naive.replace(tzinfo=tz_info)
        utc_ping_dt = local_ping_dt.astimezone(datetime.timezone.utc)

        reminder_data = {
            "user_id": str(interaction.user.id),
            "guild_id": interaction.guild_id,
            "guild_name": interaction.guild.name if interaction.guild else "Unknown Server",
            "guild_icon_url": str(interaction.guild.icon.url) if interaction.guild and interaction.guild.icon else None,
            "channel_id": target_channel.id,
            "channel_name": target_channel.name,
            "timezone": timezone_str,
            "utc_ping_hour": utc_ping_dt.hour,
            "utc_ping_minute": utc_ping_dt.minute,
            "ping_hour": ping_dt_naive.hour,
            "ping_minute": ping_dt_naive.minute,
            "start_hour": parsed_time.hour,
            "start_minute": parsed_time.minute,
            "time_range_text": time,
            "training_days": training_days,
            "enabled": True
        }

        # Use upsert with _guild_id_filter to update or insert strictly 1 document per server
        await self.reminders.update_one(
            {"user_id": str(interaction.user.id), "guild_id": _guild_id_filter(interaction.guild_id)},
            {"$set": reminder_data},
            upsert=True
        )

        status_msg = "Updated!" if is_update else "Set!"
        start_time_formatted = parsed_time.strftime("%I:%M %p").lstrip("0")
        await interaction.followup.send(
            f"✅ **Reminder {status_msg}** I will ping you in {target_channel.mention} 5 minutes before `{start_time_formatted}` ({timezone_str}) on **{format_days(training_days)}**. Get ready to train! 🥊\n"
            f"-# Use `/myreminders` any time to view or manage every reminder you've set.",
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
            if self.is_training_day(doc, now_utc):
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
            if self.is_training_day(doc, now_utc):
                await self._send_reminder_ping(doc)

    def is_training_day(self, doc, now_utc):
        tz_offset = TIMEZONE_OFFSETS.get(doc.get("timezone", "UTC"), TIMEZONE_OFFSETS["UTC"])
        local_now = now_utc + tz_offset
        training_days = doc.get("training_days", DEFAULT_TRAINING_DAYS)
        return local_now.weekday() in training_days

    async def _send_reminder_ping(self, doc):
        channel = self.bot.get_channel(doc["channel_id"])
        if not channel:
            try:
                channel = await self.bot.fetch_channel(doc["channel_id"])
            except Exception:
                channel = None

        if channel:
            user_id = doc["user_id"]

            view = ReminderPingView(self.reminders, int(user_id), doc["guild_id"])
            try:
                await channel.send(
                    f"🚨 <@{user_id}> **WORKOUT REMINDER!** 🚨\n"
                    f"Your workout slot begins in 5 minutes! Time to gear up ⚔️",
                    view=view
                )
            except Exception as e:
                print(f"Failed to send reminder to user {user_id}: {e}")

    @check_reminders.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()


class ManageExistingReminderView(nextcord.ui.View):
    def __init__(self, cog, user_id, guild_id, new_time, new_timezone, new_channel, new_days=None):
        super().__init__(timeout=60)
        self.cog = cog
        self.user_id = user_id
        self.guild_id = guild_id
        self.new_time = new_time
        self.new_timezone = new_timezone
        self.new_channel = new_channel
        self.new_days = new_days

    @nextcord.ui.button(label="Update Reminder", style=nextcord.ButtonStyle.primary)
    async def update_time(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("This menu isn't for you!", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        await self.cog._process_reminder_setup(interaction, self.new_time, self.new_timezone, self.new_channel, is_update=True, days_str=self.new_days)

    @nextcord.ui.button(label="Delete Reminder", style=nextcord.ButtonStyle.danger)
    async def delete_reminder(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("This menu isn't for you!", ephemeral=True)

        await interaction.response.defer(ephemeral=True)
        await self.cog.reminders.delete_one({
            "user_id": str(self.user_id),
            "guild_id": _guild_id_filter(self.guild_id)
        })
        await interaction.followup.send("🗑️ **Your reminder for this server has been deleted successfully.**", ephemeral=True)


class ReminderPingView(nextcord.ui.View):
    def __init__(self, reminders_collection, target_user_id, guild_id):
        super().__init__(timeout=None)
        self.reminders_collection = reminders_collection
        self.target_user_id = target_user_id
        self.guild_id = guild_id

    @nextcord.ui.button(label="Delete Reminder", style=nextcord.ButtonStyle.danger)
    async def delete_from_ping(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user.id != self.target_user_id:
            return await interaction.response.send_message("Only the scheduled athlete can delete this reminder!", ephemeral=True)

        await interaction.response.defer(ephemeral=True)
        await self.reminders_collection.delete_one({
            "user_id": str(self.target_user_id),
            "guild_id": _guild_id_filter(self.guild_id)
        })
        await interaction.followup.send("🗑️ **Reminder deleted.** You will no longer receive pings in this server.", ephemeral=True)

    @nextcord.ui.button(label="How to Update Time", style=nextcord.ButtonStyle.secondary)
    async def update_help(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user.id != self.target_user_id:
            return await interaction.response.send_message("This button is for the scheduled user.", ephemeral=True)

        await interaction.response.send_message(
            "⚙️ To change your workout slot, simply run the `/remindworkout` command again with your new time! You will be given the option to overwrite your existing time.",
            ephemeral=True
        )

    @nextcord.ui.button(label="Mod: Delete", style=nextcord.ButtonStyle.danger, emoji="🛡️")
    async def mod_delete(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.guild is None or not isinstance(interaction.user, nextcord.Member):
            return await interaction.response.send_message("This button only works inside a server.", ephemeral=True)

        perms = interaction.user.guild_permissions
        if not (perms.manage_guild or perms.administrator):
            return await interaction.response.send_message("❌ Only moderators and admins can use this button.", ephemeral=True)

        view = ModDeleteWarningView(self.reminders_collection, self.target_user_id, self.guild_id, interaction.user.id)
        await interaction.response.send_message(
            f"⚠️ **You are about to delete workout reminder data set by <@{self.target_user_id}>.**\n\n"
            f"Only do this for a valid reason, such as the wrong channel, spam, or abuse. "
            f"Misusing this without good reason isn't appropriate, and users are within their rights "
            f"to raise a complaint about moderator actions taken against them.\n\n"
            f"Click **Continue** to provide a reason and proceed, or **Cancel** to back out.",
            view=view,
            ephemeral=True
        )


class ModDeleteWarningView(nextcord.ui.View):
    def __init__(self, reminders_collection, target_user_id, guild_id, moderator_id):
        super().__init__(timeout=60)
        self.reminders_collection = reminders_collection
        self.target_user_id = target_user_id
        self.guild_id = guild_id
        self.moderator_id = moderator_id

    @nextcord.ui.button(label="Continue", style=nextcord.ButtonStyle.danger, emoji="⚠️")
    async def proceed(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user.id != self.moderator_id:
            return await interaction.response.send_message("This confirmation isn't for you!", ephemeral=True)
        await interaction.response.send_modal(ModReasonModal(self.reminders_collection, self.target_user_id, self.guild_id))

    @nextcord.ui.button(label="Cancel", style=nextcord.ButtonStyle.secondary)
    async def cancel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user.id != self.moderator_id:
            return await interaction.response.send_message("This confirmation isn't for you!", ephemeral=True)
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(content="❌ Cancelled. No changes made.", view=self)


class ModReasonModal(nextcord.ui.Modal):
    def __init__(self, reminders_collection, target_user_id, guild_id):
        super().__init__("Delete Workout Reminder")
        self.reminders_collection = reminders_collection
        self.target_user_id = target_user_id
        self.guild_id = guild_id
        self.reason = nextcord.ui.TextInput(
            label="Reason for deleting this reminder",
            placeholder="e.g. wrong channel, spam, requested by the user",
            min_length=3,
            max_length=300
        )
        self.add_item(self.reason)

    async def callback(self, interaction: nextcord.Interaction):
        await self.reminders_collection.delete_one({
            "user_id": str(self.target_user_id),
            "guild_id": _guild_id_filter(self.guild_id)
        })
        print(f"[ModAction] {interaction.user} ({interaction.user.id}) deleted the workout reminder for user {self.target_user_id} in guild {self.guild_id}. Reason: {self.reason.value}")

        await interaction.response.send_message(
            f"🛡️ <@{self.target_user_id}>, your workout reminder in this server was removed by a moderator.\n"
            f"**Reason:** {self.reason.value}"
        )


class ReminderManageView(nextcord.ui.View):
    def __init__(self, cog, reminders):
        super().__init__(timeout=120)
        self.add_item(ReminderManageSelect(cog, reminders))


class ReminderManageSelect(nextcord.ui.Select):
    def __init__(self, cog, reminders):
        self.cog = cog
        options = []
        for r in reminders:
            doc_id = str(r["_id"])
            guild_name = str(r.get("guild_name") or "Unknown Server")[:100]
            time_text = str(r.get("time_range_text") or "Unknown time")
            tz = str(r.get("timezone") or "UTC")
            ch_name = str(r.get("channel_name") or "channel")
            options.append(nextcord.SelectOption(
                label=guild_name,
                description=f"{time_text} ({tz}) • #{ch_name}"[:100],
                value=doc_id
            ))
        super().__init__(custom_id="reminder_manage_select", placeholder="Select a reminder to delete...", options=options)

    async def callback(self, interaction: nextcord.Interaction):
        doc_id_str = self.values[0]
        try:
            reminder = await self.cog.reminders.find_one({"_id": ObjectId(doc_id_str)})
        except Exception:
            reminder = await self.cog.reminders.find_one({"_id": doc_id_str})

        if not reminder:
            return await interaction.response.send_message("That reminder no longer exists.", ephemeral=True)

        guild_name = reminder.get("guild_name") or "Unknown Server"
        view = ConfirmDeleteReminderView(self.cog, interaction.user.id, reminder)
        await interaction.response.send_message(
            f"⚠️ Delete your reminder for **{guild_name}**? This cannot be undone.",
            view=view,
            ephemeral=True
        )


class ConfirmDeleteReminderView(nextcord.ui.View):
    def __init__(self, cog, user_id, reminder_doc):
        super().__init__(timeout=60)
        self.cog = cog
        self.user_id = user_id
        self.reminder_doc = reminder_doc

    @nextcord.ui.button(label="Yes, Delete", style=nextcord.ButtonStyle.danger)
    async def confirm(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("This confirmation isn't for you!", ephemeral=True)

        doc_id = self.reminder_doc["_id"]
        await self.cog.reminders.delete_one({"_id": doc_id})
        for child in self.children:
            child.disabled = True
        guild_name = self.reminder_doc.get("guild_name") or "Server"
        await interaction.response.edit_message(content=f"🗑️ **Deleted your reminder for {guild_name}.**", view=self)

    @nextcord.ui.button(label="Cancel", style=nextcord.ButtonStyle.secondary)
    async def cancel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("This confirmation isn't for you!", ephemeral=True)

        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(content="❌ Cancelled. No changes made.", view=self)


def setup(bot):
    bot.add_cog(WorkoutReminder(bot))