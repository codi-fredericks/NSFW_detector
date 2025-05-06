import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
import dotenv
import url_detect
import json
from typing import Union
import time

dotenv.load_dotenv()
LOG_FILE = "log_channels.json"

def init_log_file():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            json.dump({}, f)

# Load all log channels
def load_log_channels():
    with open(LOG_FILE, "r") as f:
        return json.load(f)

# Save all log channels
def save_log_channels(data):
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Get a log channel for a guild
def get_log_channel(guild_id):
    channels = load_log_channels()
    return channels.get(str(guild_id))

# Set a log channel for a guild
def set_log_channel(guild_id, channel_id):
    channels = load_log_channels()
    channels[str(guild_id)] = channel_id
    save_log_channels(channels)

class bot(commands.Bot): # define the bot
    
    async def on_ready(self):
        await bot.wait_until_ready()

        await sync_commands()
        


async def sync_commands():
    # Syncing global commands
    global_commands = await bot.tree.sync()

    # Optionally, clean up any commands that no longer exist
    commands_to_remove = []
    for command in bot.tree.get_commands():
        if not any(command.name == c.name for c in bot.tree.get_commands()):
            commands_to_remove.append(command)

    if commands_to_remove:
        for command in commands_to_remove:
            await bot.tree.remove_command(command.name)



intents = discord.Intents.default()
intents.message_content = True

bot = bot(
        command_prefix='!',
        intents=intents
        )
bt = bot.tree
labels = [
        "FEMALE_BREAST_EXPOSED",
        "FEMALE_GENITALIA_EXPOSED",
        "ANUS_EXPOSED",
        "MALE_GENITALIA_EXPOSED",
    ]

async def log_embed(message:discord.message, values, url):
    embed = discord.Embed(title="NSFW image Detected")
    embed.add_field(name="Person:", value=f'<@{message.author.id}>', inline=False)
    embed.add_field(name="Image:", value=f"||{url}||", inline=False)
    embed.add_field(name="Values:", value="\n".join(f"- __**{item['class']}**__: {item['score'] * 100:.1f}%" for item in values))
    embed.timestamp = message.created_at
    return embed

async def check(message):
    if message.author == bot.user:
        return
    if message.channel.nsfw:
        return
    channel_id = get_log_channel(message.guild.id)
    logs = await bot.fetch_channel(channel_id)
    if message.attachments:
        for attachment in message.attachments:
            if attachment.content_type.startswith("image"):
                value = await url_detect.detect_from_url(attachment.proxy_url, labels)
                if value == False:
                    pass
                else:
                    await logs.send(embed=(await log_embed(message, value, attachment.proxy_url)))
                    await message.delete()
            if attachment.content_type.startswith("video"):
                value = await url_detect.process_video_from_url(attachment.proxy_url , labels)
                if value == False:
                    pass
                else:
                    await logs.send(embed=(await log_embed(message, value, attachment.proxy_url)))
                    await message.delete()
    if message.embeds:
        for embed in message.embeds:
            if embed.video.proxy_url:
                value = await url_detect.process_video_from_url(embed.video.proxy_url , labels)
                if value == False:
                    pass
                else:
                    await logs.send(embed=(await log_embed(message, value, embed.video.proxy_url)))
                    await message.delete()
            if embed.image.url:
                value = await url_detect.detect_from_url(embed.image.proxy_url , labels)
                if value == False:
                    pass
                else:
                    await logs.send(embed=(await log_embed(message, value, embed.image.proxy_url)))
                    await message.delete()
                    return
            if embed.thumbnail.url:
                value = await url_detect.detect_from_url(embed.thumbnail.proxy_url , labels)
                if value == False:
                    pass
                else:
                    await logs.send(embed=(await log_embed(message, value, embed.thumbnail.proxy_url)))
                    await message.delete()
@bot.event
async def on_message(message):
    await check(message)

@bot.event
async def on_message_edit(before, message):
    await check(message)


@bt.command()
@app_commands.default_permissions(administrator=True)
async def setlog(interaction:discord.Interaction, channel: Union[discord.TextChannel, discord.Thread] ):
    set_log_channel(interaction.guild.id, channel.id)
    try:
        ok = await bot.fetch_channel(channel.id)
        await interaction.response.send_message(f"Log channel set to {channel.mention}", ephemeral=True)
    except:
        
        await interaction.response.send_message(f"I can not access {channel.mention}", ephemeral=True)

bot.run(os.getenv('TOKEN'))