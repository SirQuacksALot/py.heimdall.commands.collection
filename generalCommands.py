import discord
from discord import app_commands
from discord.ext import commands

class GeneralCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Zeigt 'Pong!' an.")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("Pong!", ephemeral=True)

    @commands.Cog.listener()
    async def on_ready(self):
        # Wenn du global registrierst:
        try:
            synced = await self.bot.tree.sync()
            print(f"Slash-Commands registriert: {len(synced)}")
        except Exception as e:
            print(f"Fehler beim Registrieren der Slash-Commands: {e}")

async def setup(bot):
    await bot.add_cog(GeneralCommands(bot))