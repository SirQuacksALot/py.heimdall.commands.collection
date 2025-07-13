import discord
from discord import app_commands
from discord.ext import commands

class DebugTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="delete_message", description="Löscht eine nachricht anhand einer Message ID.")
    @app_commands.describe(message_id="Die ID der Nachricht, die gelöscht werden soll")
    @app_commands.default_permissions()
    async def delete_message(self, interaction: discord.Interaction, message_id: str):
        channel = interaction.channel

        try:
            message = await channel.fetch_message(int(message_id))
        except discord.NotFound:
            await interaction.response.send_message("❌ Nachricht nicht gefunden.", ephemeral=True)
            return
        except discord.Forbidden:
            await interaction.response.send_message("❌ Ich habe keine Berechtigung, Nachrichten zu lesen.", ephemeral=True)
            return
        except discord.HTTPException:
            await interaction.response.send_message("❌ Ungültige Nachricht oder andere Fehler.", ephemeral=True)
            return

        if message.author.id != self.bot.user.id:
            await interaction.response.send_message("❌ Diese Nachricht wurde nicht von mir erstellt.", ephemeral=True)
            return

        try:
            await message.delete()
            await interaction.response.send_message("✅ Nachricht wurde gelöscht.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ Ich habe keine Berechtigung, die Nachricht zu löschen.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(DebugTools(bot))