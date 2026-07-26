import nextcord
from nextcord.ext import commands, tasks
import datetime
import motor.motor_asyncio
import os

class WorkoutReminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGO_URI"))
        self.db = self.client["gladiator_db"]
        self.reminders = self.db["workout_reminders"]
        
        self.check_reminders.start()

    def cog_unload(self):
        self.check_reminders.cancel()

    @nextcord.slash_command(name="remind_workout", description="Set your daily workout time and enable Discord reminders.")
    async def remind_workout(
        self, 
        interaction: nextcord.Interaction, 
        time_range: str = nextcord.SlashOption(description="e.g., 6:00 AM to 7:00 AM or 06:00 AM"),
        channel: nextcord.TextChannel = nextcord.SlashOption(description="Channel to receive the reminder ping", required=False)
    ):
        await interaction.response.defer(ephemeral=True)

        existing_reminder = await self.reminders.find_one({"user_id": interaction.user.id})
        
        if existing_reminder:
            existing_time = existing_reminder.get("time_range_text", "Unknown Time")
            
            view = ManageExistingReminderView(self, interaction.user.id, time_range, channel)
            await interaction.followup.send(
                f"❌ **You can't set a time because it is already set at `{existing_time}`!**\n\n"
                f"Would you like to **Update** your current schedule to `{time_range}` or **Delete** your existing reminder entirely?",
                view=view,
                ephemeral=True
            )
            return

        await self._process_reminder_setup(interaction, time_range, channel)

    async def _process_reminder_setup(self, interaction: nextcord.Interaction, time_range: str, channel: nextcord.TextChannel = None, is_update: bool = False):
        target_channel = channel or interaction.channel

        try:
            start_time_str = time_range.split("to")[0].strip()
            parsed_time = datetime.datetime.strptime(start_time_str, "%I:%M %p").time()
        except ValueError:
            await interaction.followup.send(
                "⚠️ **Invalid time format!** Please use format like `6:00 AM to 7:00 AM` or `06:30 PM`.", 
                ephemeral=True
            )
            return

        view = ConfirmReminderView()
        await interaction.followup.send(
            f"⚔️ **Workout Reminder Agreement**\n\n"
            f"• **Scheduled Time:** `{time_range}`\n"
            f"• **Reminder Channel:** {target_channel.mention}\n"
            f"• **Notice:** You will be pinged **5 minutes before** your start time.\n\n"
            f"Do you agree to receive workout reminder pings in this server?",
            view=view,
            ephemeral=True
        )

        await view.wait()

        if view.value is None:
            await interaction.followup.send("⏰ Timed out. Operation cancelled.", ephemeral=True)
            return
        elif not view.value:
            await interaction.followup.send("❌ Setup cancelled. No changes were made.", ephemeral=True)
            return

        reminder_data = {
            "user_id": interaction.user.id,
            "guild_id": interaction.guild_id,
            "channel_id": target_channel.id,
            "start_hour": parsed_time.hour,
            "start_minute": parsed_time.minute,
            "time_range_text": time_range,
            "enabled": True
        }

        await self.reminders.update_one(
            {"user_id": interaction.user.id},
            {"$set": reminder_data},
            upsert=True
        )

        status_msg = "Updated!" if is_update else "Set!"
        await interaction.followup.send(
            f"✅ **Reminder {status_msg}** I will ping you in {target_channel.mention} 5 minutes before `{start_time_str}` every day. Get ready to train! 🥊",
            ephemeral=True
        )

    @tasks.loop(minutes=1)
    async def check_reminders(self):
        now = datetime.datetime.now()
        target_dt = now + datetime.timedelta(minutes=5)
        
        target_hour = target_dt.hour
        target_minute = target_dt.minute

        cursor = self.reminders.find({
            "enabled": True,
            "start_hour": target_hour,
            "start_minute": target_minute
        })

        async for doc in cursor:
            channel = self.bot.get_channel(doc["channel_id"])
            if channel:
                user_id = doc["user_id"]
                time_str = doc["time_range_text"]
                
                view = ReminderPingView(self.reminders, user_id)
                try:
                    await channel.send(
                        f"🚨 <@{user_id}> **WORKOUT REMINDER!** 🚨\n"
                        f"Your workout slot (`{time_str}`) starts in **5 minutes**! Time to suit up and gear up! ⚔️",
                        view=view
                    )
                except Exception as e:
                    print(f"Failed to send reminder to user {user_id}: {e}")

    @check_reminders.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()


class ManageExistingReminderView(nextcord.ui.View):
    def __init__(self, cog, user_id, new_time_range, new_channel):
        super().__init__(timeout=60)
        self.cog = cog
        self.user_id = user_id
        self.new_time_range = new_time_range
        self.new_channel = new_channel

    @nextcord.ui.button(label="Update Time", style=nextcord.ButtonStyle.primary)
    async def update_time(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("This menu isn't for you!", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        await self.cog._process_reminder_setup(interaction, self.new_time_range, self.new_channel, is_update=True)

    @nextcord.ui.button(label="Delete Reminder", style=nextcord.ButtonStyle.danger)
    async def delete_reminder(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("This menu isn't for you!", ephemeral=True)

        await interaction.response.defer(ephemeral=True)
        await self.cog.reminders.delete_one({"user_id": self.user_id})
        await interaction.followup.send("🗑️ **Your workout reminder has been deleted successfully.**", ephemeral=True)


class ConfirmReminderView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.value = None

    @nextcord.ui.button(label="I Agree (Enable Reminders)", style=nextcord.ButtonStyle.green)
    async def confirm(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = True
        self.stop()

    @nextcord.ui.button(label="Cancel / Opt Out", style=nextcord.ButtonStyle.red)
    async def cancel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.value = False
        self.stop()


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
        await self.reminders_collection.delete_one({"user_id": self.target_user_id})
        await interaction.followup.send("🗑️ **Reminder deleted.** You will no longer receive pings.", ephemeral=True)

    @nextcord.ui.button(label="How to Update Time", style=nextcord.ButtonStyle.secondary)
    async def update_help(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user.id != self.target_user_id:
            return await interaction.response.send_message("This button is for the scheduled user.", ephemeral=True)

        await interaction.response.send_message(
            "⚙️ To change your workout slot, simply run the `/remind_workout` command again with your new time! You will be given the option to overwrite your existing time.",
            ephemeral=True
        )


def setup(bot):
    bot.add_cog(WorkoutReminder(bot))