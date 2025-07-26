from flask import Flask
from threading import Thread
import discord
from discord.ext import commands
import asyncio
import re

app = Flask('')

@app.route('/')
def home():
    return "✅ The Nexus is awake and watching..."

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='-', intents=intents, description="The Nexus - Guardian of the Server")

banned_words = ["badword1", "badword2", "stupid", "idiot"]
user_warnings = {}
spam_tracker = {}

@bot.event
async def on_ready():
    game = discord.Game("GTA VI")
    await bot.change_presence(status=discord.Status.online, activity=game)
    print(f'✅ The Nexus is now online as {bot.user}')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    msg = message.content.lower()
    author_id = message.author.id

    # Anti-swear filter
    for word in banned_words:
        if re.search(rf"\b{re.escape(word)}\b", msg):
            await message.delete()

            # Add warning
            if author_id not in user_warnings:
                user_warnings[author_id] = 1
            else:
                user_warnings[author_id] += 1

            warning_count = user_warnings[author_id]
            await message.channel.send(
                f"🚫 {message.author.mention}, watch your language! Warning {warning_count}/3",
                delete_after=5
            )

            # Mute after 3 warnings
            if warning_count >= 3:
                muted_role = discord.utils.get(message.guild.roles, name="Muted")
                if muted_role:
                    await message.author.add_roles(muted_role)
                    await message.channel.send(
                        f"🔇 {message.author.mention} has been muted for repeated cursing."
                    )
            return

    # Anti-spam: more than 5 messages in 10 seconds
    now = asyncio.get_event_loop().time()
    spam_tracker.setdefault(author_id, [])
    spam_tracker[author_id] = [t for t in spam_tracker[author_id] if now - t < 10]
    spam_tracker[author_id].append(now)
    if len(spam_tracker[author_id]) > 5:
        await message.channel.send(f"⚠️ {message.author.mention}, stop spamming!", delete_after=5)
        return

    await bot.process_commands(message)

@bot.command()
@commands.has_permissions(manage_channels=True)
async def announce(ctx, channel: discord.TextChannel, *, msg):
    await channel.send(f"📢 {msg}")
    await ctx.send(f"✅ Sent your message to {channel.mention}")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.kick(reason=reason)
    await ctx.send(f"👢 {member.mention} has been kicked | Reason: {reason}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 {member.mention} has been banned | Reason: {reason}")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 5):
    await ctx.channel.purge(limit=amount)
    await ctx.send(f"🧹 Cleared {amount} messages", delete_after=3)

@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, *, reason="No reason provided"):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not muted_role:
        return await ctx.send("❌ No 'Muted' role found. Please create one first.")
    await member.add_roles(muted_role, reason=reason)
    await ctx.send(f"🔇 {member.mention} has been muted. Reason: {reason}")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not muted_role:
        return await ctx.send("❌ No 'Muted' role found.")
    await member.remove_roles(muted_role)
    await ctx.send(f"🔊 {member.mention} has been unmuted.")

@bot.command()
async def hello(ctx):
    await ctx.send("Greetings. I am **The Nexus** — your server's protector. 🛡️🤖")

keep_alive()
bot.run("YOUR_BOT_TOKEN_HERE")  # Replace with your actual bot token