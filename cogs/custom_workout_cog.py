import nextcord
from nextcord.ext import commands
from nextcord.ui import View, Modal, TextInput, Select, Button
import motor.motor_asyncio
import os

class CreateScheduleModal(Modal):
    def __init__(self, cog, view_ref):
        super().__init__("Forge New Schedule")
        self.cog = cog
        self.view_ref = view_ref
        self.name = TextInput(
            label="Schedule Name", 
            placeholder="e.g. Calisthenics, Boxing, or PPL",
            min_length=1,
            max_length=20
        )
        self.add_item(self.name)

    async def callback(self, interaction: nextcord.Interaction):
        new_schedule = {
            "name": self.name.value.strip(),
            "days": {day: [] for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}
        }
        
        try:
            await self.cog.collection.update_one(
                {"_id": str(interaction.user.id)},
                {"$push": {"schedules": new_schedule}},
                upsert=True
            )
            user_data = await self.cog.collection.find_one({"_id": str(interaction.user.id)})
            current_schedules = user_data.get("schedules", []) if user_data else []
        except Exception as e:
            print(f"MongoDB error in CreateScheduleModal: {e}")
            current_schedules = []

        self.view_ref.current_sched_idx = max(0, len(current_schedules) - 1)
        await self.view_ref.refresh_data(interaction)

class AddExerciseModal(Modal):
    def __init__(self, cog, view_ref, schedule_idx, day):
        super().__init__(f"Add to {day}")
        self.cog, self.view_ref, self.sched_idx, self.day = cog, view_ref, schedule_idx, day
        self.ex = TextInput(label="Exercise Name", placeholder="e.g. Weighted Pullups")
        self.reps = TextInput(label="Sets/Reps or Time", placeholder="e.g. 4x10 or 30s")
        self.add_item(self.ex)
        self.add_item(self.reps)

    async def callback(self, interaction: nextcord.Interaction):
        try:
            user_data = await self.cog.collection.find_one({"_id": str(interaction.user.id)})
            schedules = user_data.get("schedules", []) if user_data else []
            
            if 0 <= self.sched_idx < len(schedules):
                entry = {"exercise": f"🧩 {self.ex.value.strip()}", "reps": self.reps.value.strip()}
                if "days" not in schedules[self.sched_idx]:
                    schedules[self.sched_idx]["days"] = {day: [] for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}
                schedules[self.sched_idx]["days"][self.day].append(entry)
                
                await self.cog.collection.update_one(
                    {"_id": str(interaction.user.id)},
                    {"$set": {"schedules": schedules}}
                )
        except Exception as e:
            print(f"MongoDB error in AddExerciseModal: {e}")
            
        await self.view_ref.refresh_data(interaction)

class WorkoutView(View):
    def __init__(self, user_name, schedules, cog):
        super().__init__(timeout=300)
        self.user_name = user_name
        self.schedules = schedules
        self.cog = cog
        self.current_sched_idx = 0
        self.current_day = "Monday"
        self.setup_selectors()

    def setup_selectors(self):
        self.clear_items()
        has_schedules = len(self.schedules) > 0
        if self.current_sched_idx >= len(self.schedules):
            self.current_sched_idx = max(0, len(self.schedules) - 1)
        
        sched_options = []
        if not has_schedules:
            sched_options.append(nextcord.SelectOption(label="No Schedules Created", value="none"))
        else:
            for i, s in enumerate(self.schedules):
                sched_options.append(nextcord.SelectOption(
                    label=s.get("name", f"Schedule {i+1}"), 
                    value=str(i), 
                    default=(i == self.current_sched_idx)
                ))
        
        sched_select = Select(
            custom_id="workout_schedule_select",
            placeholder="Select a Workout Schedule...", 
            options=sched_options, 
            disabled=not has_schedules,
            row=0
        )
        sched_select.callback = self.change_schedule
        self.add_item(sched_select)
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day_options = [nextcord.SelectOption(label=d, value=d, default=(d == self.current_day)) for d in days]
        
        day_select = Select(
            custom_id="workout_day_select",
            placeholder="Choose Day of the Week...", 
            options=day_options, 
            disabled=not has_schedules,
            row=1
        )
        day_select.callback = self.change_day
        self.add_item(day_select)
        
        add_sched_btn = Button(label="New Schedule", style=nextcord.ButtonStyle.blurple, row=2, custom_id="new_schedule_btn")
        add_sched_btn.callback = self.add_schedule_modal
        self.add_item(add_sched_btn)
        
        add_ex_btn = Button(
            label="Add Exercise", 
            style=nextcord.ButtonStyle.success, 
            row=2, 
            disabled=not has_schedules,
            custom_id="add_exercise_btn"
        )
        add_ex_btn.callback = self.add_exercise_modal
        self.add_item(add_ex_btn)
        
        clear_btn = Button(
            label="Clear All", 
            style=nextcord.ButtonStyle.danger, 
            row=2,
            disabled=not has_schedules,
            custom_id="clear_all_btn"
        )
        clear_btn.callback = self.clear_all_data
        self.add_item(clear_btn)

    def get_file(self):
        paths = ["assets/armor.jpg", os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "armor.jpg")]
        for p in paths:
            if os.path.exists(p):
                return nextcord.File(p, filename="armor.jpg")
        return None

    async def refresh_data(self, interaction: nextcord.Interaction):
        try:
            user_data = await self.cog.collection.find_one({"_id": str(interaction.user.id)})
            self.schedules = user_data.get("schedules", []) if user_data else []
        except Exception as e:
            print(f"MongoDB error in refresh_data: {e}")
            
        self.setup_selectors()
        
        kwargs = {"embed": self.create_embed(), "view": self}
        file = self.get_file()
        if file:
            kwargs["file"] = file
            
        if interaction.response.is_done():
            await interaction.followup.send(**kwargs, ephemeral=True)
        else:
            await interaction.response.edit_message(**kwargs)

    async def change_schedule(self, interaction: nextcord.Interaction):
        if not interaction.data.get('values') or interaction.data['values'][0] == "none": return
        self.current_sched_idx = int(interaction.data['values'][0])
        await self.refresh_data(interaction)

    async def change_day(self, interaction: nextcord.Interaction):
        if not interaction.data.get('values'): return
        self.current_day = interaction.data['values'][0]
        await self.refresh_data(interaction)

    async def add_schedule_modal(self, interaction: nextcord.Interaction):
        await interaction.response.send_modal(CreateScheduleModal(self.cog, self))

    async def add_exercise_modal(self, interaction: nextcord.Interaction):
        await interaction.response.send_modal(AddExerciseModal(self.cog, self, self.current_sched_idx, self.current_day))

    async def clear_all_data(self, interaction: nextcord.Interaction):
        try:
            await self.cog.collection.update_one({"_id": str(interaction.user.id)}, {"$set": {"schedules": []}})
        except Exception as e:
            print(f"MongoDB error in clear_all_data: {e}")
        self.schedules = []
        self.current_sched_idx = 0
        self.setup_selectors()
        
        kwargs = {"content": "🧹 **All workout schedules have been cleared.**", "embed": self.create_embed(), "view": self}
        file = self.get_file()
        if file:
            kwargs["file"] = file
            
        if interaction.response.is_done():
            await interaction.followup.send(**kwargs, ephemeral=True)
        else:
            await interaction.response.edit_message(**kwargs)

    def create_embed(self):
        embed = nextcord.Embed(
            title=f"🛡️ {self.user_name}'s Private Armory", 
            color=0x3498db
        )
        if os.path.exists("assets/armor.jpg") or os.path.exists(os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "armor.jpg")):
            embed.set_thumbnail(url="attachment://armor.jpg")
        
        if not self.schedules:
            embed.description = "❌ **No schedules found.**\n\nClick the **New Schedule** button below to create your first plan."
            return embed

        if self.current_sched_idx >= len(self.schedules):
            self.current_sched_idx = max(0, len(self.schedules) - 1)

        sched = self.schedules[self.current_sched_idx]
        day_data = sched.get("days", {}).get(self.current_day, [])
        
        embed.description = f"**Current Plan:** `{sched.get('name', 'Schedule')}`\n**Day:** `{self.current_day}`"
        
        if not day_data:
            embed.add_field(name="Rest Day", value="No exercises recorded for today.", inline=False)
        else:
            for i, ex in enumerate(day_data, 1):
                embed.add_field(name=f"{i}. {ex.get('exercise', 'Exercise')}", value=f"└ {ex.get('reps', '-')}", inline=False)
        
        embed.set_footer(text="Switch schedules or days using the menus above.")
        return embed

class CustomWorkoutCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if hasattr(bot, "mongo_client") and bot.mongo_client is not None:
            self.cluster = bot.mongo_client
        else:
            self.cluster = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGO_URI"), serverSelectionTimeoutMS=5000)
        self.collection = self.cluster["GymBotDB"]["custom_workouts_v2"]

    @nextcord.slash_command(name="myworkout", description="Create your custom workout plans")
    async def myworkout(self, interaction: nextcord.Interaction):
        if not interaction.response.is_done():
            try:
                await interaction.response.defer(ephemeral=True)
            except Exception:
                pass

        try:
            user_data = await self.collection.find_one({"_id": str(interaction.user.id)})
            schedules = user_data.get("schedules", []) if user_data else []
        except Exception as e:
            print(f"MongoDB error in /myworkout: {e}")
            schedules = []

        view = WorkoutView(interaction.user.display_name, schedules, self)
        
        kwargs = {
            "embed": view.create_embed(), 
            "view": view,
            "ephemeral": True
        }
        
        file = view.get_file()
        if file:
            kwargs["file"] = file
            
        await interaction.followup.send(**kwargs)

def setup(bot):
    bot.add_cog(CustomWorkoutCog(bot))