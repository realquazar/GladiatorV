import nextcord
from nextcord.ext import commands

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="help", description="Learn how Gladiator V works and view all commands.")
    async def help_command(self, interaction: nextcord.Interaction):
        embed = nextcord.Embed(
            title="⚔️ GLADIATOR V",
            description=(
                "Want to begin working out but can't figure out where to begin?\n"
                "**Gladiator V has got you covered.**\n\n"
                "🚀 **How to start**\n"
                "Follow the steps below to set up your routine, lock in your schedule, and track your progress.\n\n"
                "───\n\n"
                "📜 **COMMANDS**\n\n"
                "• **`/schedule`** — Set up or customize your personal workout schedule and routine.\n\n"
                "• **`/startworkout`** — Begin your active workout session for the day and follow guided exercises.\n\n"
                "• **`/myworkout`** — View your workout history, current streak, and personal progression stats.\n\n"
                "• **`/resetworkout`** — Wipe your workout count and rank back to zero and restart your climb from Level 1: Novice / Beginner. ⚠️ This cannot be undone.\n\n"
                "• **`/remindworkout`** — Set custom reminders so you never miss a scheduled training session.\n\n"
                "• **`/levels`** — View the grueling path of discipline, ranks, and workout milestones.\n\n"
                "• **`/flex`** — Flex your achievements, new PRs, and workout streaks directly in the server.\n\n"
                "• **`/diet`** — Log and track your daily nutrition, calories, and macros to stay on target.\n\n"
                "• **`/hype`** — Play hype workout music to get locked in for your session.\n\n"
                "• **`/help`** — Pull up this menu any time you need a refresher on how Gladiator V works.\n\n"
                "───\n\n"
                "🌐 **WEB DASHBOARD**\n"
                "Prefer a visual interface? Sign in with Discord on the official web dashboard to seamlessly view your stats, customize your schedules, and manage your workout logs in real time!\n\n"
                "───\n\n"
                "⚙️ **PROGRESSIVE DIFFICULTY**\n"
                "workouts and exercises dynamically scale—the more you complete them and progress, the harder they get to keep challenging your limits!\n\n"
                "💪 **Grow Stronger. Keep pushing forward.** 🛡️"
            ),
            color=nextcord.Color.dark_gray()
        )

        # Interactive Link Buttons for Dashboard, Top.gg, and Support Server
        view = nextcord.ui.View()
        
        dashboard_button = nextcord.ui.Button(
            label="Open Dashboard",
            url="https://gladiator-v.up.railway.app/",
            style=nextcord.ButtonStyle.link,
            emoji="🌐"
        )

        topgg_button = nextcord.ui.Button(
            label="Vote on Top.gg",
            url="https://top.gg/bot/1016363661444534452",
            style=nextcord.ButtonStyle.link,
            emoji="⭐"
        )
        
        support_button = nextcord.ui.Button(
            label="Support Server",
            url="https://discord.gg/KBtTsr9ub",
            style=nextcord.ButtonStyle.link,
            emoji="💬"
        )

        view.add_item(dashboard_button)
        view.add_item(topgg_button)
        view.add_item(support_button)

        # Force try/except fallback to guarantee it sends regardless of prior acknowledgment state
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(embed=embed, view=view)
            else:
                await interaction.followup.send(embed=embed, view=view)
        except Exception:
            await interaction.followup.send(embed=embed, view=view)

def setup(bot):
    bot.add_cog(HelpCog(bot))