import sqlite3
import discord
import traceback
# import logging
from discord import app_commands
from discord.ext import commands

DB_PATH = "data/channels.db"

# logging.basicConfig(level=logging.DEBUG)

class AutoChannelManager(commands.Cog):

    """
    |
    | Initialisation
    |
    """

    def __init__(self, bot):
        self.bot = bot
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS auto_voice_channels (
                guild_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                PRIMARY KEY (guild_id, channel_id)
            )
        ''')
        conn.commit()
        conn.close()

    """
    |
    | Commands
    |
    """

    @app_commands.command(name="add_channel_listener", description="Fügt einen neuen Auto Voice Channel Listener hinzu.")
    @app_commands.describe(channel="Voice Channel ID")
    @app_commands.default_permissions()
    async def add_channel_listener(self, interaction: discord.Interaction, channel: discord.VoiceChannel):
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()

            c.execute("SELECT 1 FROM auto_voice_channels WHERE guild_id = ? AND channel_id = ?", (interaction.guild.id, channel.id))
            if c.fetchone():
                await interaction.response.send_message("⚠️ Dieser Channel ist bereits als Auto-Voice-Channel gespeichert.", ephemeral=True)
                conn.close()
                print(f"⚠️ **{channel.name}** Channel ist bereits als Auto-Voice-Channel gespeichert.")
                return

            c.execute('INSERT OR IGNORE INTO auto_voice_channels (guild_id, channel_id) VALUES (?, ?)', (interaction.guild.id, channel.id))
            conn.commit()
            conn.close()
            await interaction.response.send_message(f"✅ Listener für channel **{channel.name}** hinzugefügt", ephemeral=True)
            print(f"✅ Listener für channel **{channel.name}** hinzugefügt")
        
        except Exception as e:
            print("❌ Fehler beim Entfernen des Join-Channels:")
            traceback.print_exc()
            try:
                await interaction.followup.send("❌ Es ist ein Fehler aufgetreten beim Entfernen.", ephemeral=True)
            except Exception as e:
                print("Unknown exception occurred in add_channel_listener")
    
    @app_commands.command(name="remove_channel_listener", description="Entfernt einen gespeicherten Join-Voice-Channel.")
    @app_commands.describe(channel="Der Channel, der entfernt werden soll")
    @app_commands.default_permissions()
    async def remove_channel_listener(self, interaction: discord.Interaction, channel: discord.VoiceChannel):
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()

            c.execute("SELECT 1 FROM auto_voice_channels WHERE guild_id = ? AND channel_id = ?", (interaction.guild.id, channel.id))
            if not c.fetchone():
                await interaction.response.send_message("⚠️ Dieser Channel ist nicht als Auto-Voice-Channel gespeichert.", ephemeral=True)
                conn.close()
                print(f"⚠️ **{channel.name}** Channel ist nicht als Auto-Voice-Channel gespeichert.")
                return
            
            c.execute("DELETE FROM auto_voice_channels WHERE guild_id = ? AND channel_id = ?", (interaction.guild.id, channel.id))
            conn.commit()
            conn.close()

            await interaction.response.send_message(f"✅ Auto-Voice-Channel **{channel.name}** wurde entfernt.", ephemeral=True)
            print(f"✅ Auto-Voice-Channel **{channel.name}** wurde entfernt.")

        except Exception as e:
            print("❌ Fehler beim Entfernen des Join-Channels:")
            traceback.print_exc()
            try:
                await interaction.response.send_message("❌ Es ist ein Fehler aufgetreten beim Entfernen.", ephemeral=True)
            except Exception as e:
                print("Unknown exception occurred in remove_channel_listener")

    """
    |
    | Listeners
    |
    """

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        print(f"🔥 on_voice_state_update event fired!")
        if before.channel == after.channel:
            return

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT channel_id FROM auto_voice_channels WHERE guild_id = ?', (member.guild.id,))
        results = c.fetchall()
        conn.close()

        auto_channel_ids = [row[0] for row in results]

        
        # Wenn User in den Join-Channel joint → temporären Channel erstel:
        if after.channel and after.channel.id in auto_channel_ids:
            auto_channel = after.channel
            category = after.channel.category

            new_channel = await member.guild.create_voice_channel(
                name=f"︱🎙️ of {member.display_name}",
                category=category,
                position=auto_channel.position
            )
            await member.move_to(new_channel)

        # Prüfen, ob vorheriger temporärer Channel leer ist → löschen
        if before.channel and len(before.channel.members) == 0 and before.channel.name.startswith("︱🎙️ of"):
            try:
                await before.channel.delete()
            except Exception as e:
                print(f"❌ Fehler beim Löschen des Channels: {e}")

async def setup(bot):
    await bot.add_cog(AutoChannelManager(bot))