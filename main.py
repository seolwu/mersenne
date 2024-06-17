import os
import discord
import asyncio
from datetime import datetime
from discord.ext import commands, tasks
from discord.ui import View, Button
from utils.map_utils import open_map, save_map, initialize_map_file
from utils.activity_utils import create_activity_embed, create_previous_month_embed, start_recording
from utils.config import TOKEN, LOUNGE_ID, LOUNGE_LOG_ID, PROMPT_ID

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(intents=intents)

initialize_map_file()  # Initialize map file if it doesn't exist
map_data = open_map()

@bot.event
async def on_ready():
    print(f"+ ready: {bot.user}")

    activity = discord.Activity(
        type=discord.ActivityType.watching,
        name="라운지 쓸쩍"
    )
    await bot.change_presence(
        status=discord.Status.streaming,
        activity=activity
    )

    # Check if the im message exists, create if not
    await check_im_message()

    # Wait until the bot is fully ready
    await bot.wait_until_ready()

    # Start updating im message
    update_im_message.start()

    # Initialize user data in map
    await initialize_user_data()

    # Check if any users are streaming in the lounge channel when the bot starts
    lounge_log_channel = bot.get_channel(LOUNGE_LOG_ID)
    for guild in bot.guilds:
        for voice_channel in guild.voice_channels:
            if voice_channel.id == LOUNGE_ID:
                for member in voice_channel.members:
                    if member.voice and member.voice.self_stream:
                        user_id = str(member.id)
                        if start_recording(user_id):
                            await lounge_log_channel.send(f"{member.mention}이(가) 라운지에서 방송 중입니다.", allowed_mentions=discord.AllowedMentions(users=False))
                            print(f"봇 시작 시 {member}의 방송을 감지했습니다: 라운지")

class ActivityDetailsButton(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(label="이번달 활동 내역", custom_id="current_month_activity_details_button", style=discord.ButtonStyle.primary))
        self.add_item(Button(label="지난달 활동 내역", custom_id="previous_month_activity_details_button", style=discord.ButtonStyle.secondary))

async def check_im_message():
    prompt_channel = bot.get_channel(PROMPT_ID)
    if "system" not in map_data:
        map_data["system"] = {}
    if "im" in map_data["system"]:
        try:
            msg_id = int(map_data["system"]["im"])
            msg = await prompt_channel.fetch_message(msg_id)
            if msg:
                await msg.edit(view=ActivityDetailsButton())
                return
        except discord.NotFound:
            pass
    
    # Create the im message
    message = await prompt_channel.send(view=ActivityDetailsButton())
    map_data["system"]["im"] = message.id
    save_map(map_data)

@tasks.loop(seconds=60.0)
async def update_im_message():
    await check_im_message()

@bot.event
async def on_voice_state_update(member, before, after):
    from cogs.activity_tracker import ActivityTracker
    await ActivityTracker.handle_voice_state_update(bot, member, before, after)

@bot.event
async def on_member_update(before, after):
    if before.display_name != after.display_name:
        user_id = str(after.id)
        map_data = open_map()
        if user_id in map_data:
            map_data[user_id]['name'] = after.display_name
            save_map(map_data)
        print(f"{before.display_name}의 이름이 {after.display_name}로 변경되었습니다.")

@bot.event
async def on_interaction(interaction):
    if interaction.custom_id == "current_month_activity_details_button":
        embed = await create_activity_embed(bot, interaction.user)
        if embed is not None:
            await interaction.response.send_message(embed=embed, ephemeral=True)
            # Set a timer to delete the ephemeral message after 3 minutes
            await asyncio.sleep(180)
            await interaction.delete_original_response()
        else:
            await interaction.response.send_message("데이터가 없기 때문에 활동 내역을 불러올 수 없습니다.\n스트림을 시작하고 활동해 보세요.", ephemeral=True)
    elif interaction.custom_id == "previous_month_activity_details_button":
        embed = await create_previous_month_embed(bot, interaction.user)
        if embed is not None:
            await interaction.response.send_message(embed=embed, ephemeral=True)
            # Set a timer to delete the ephemeral message after 3 minutes
            await asyncio.sleep(180)
            await interaction.delete_original_response()
        else:
            await interaction.response.send_message("데이터가 없기 때문에 활동 내역을 불러올 수 없습니다.", ephemeral=True)

async def initialize_user_data():
    today = datetime.today()
    year = today.strftime('%Y')
    month = today.strftime('%m')
    
    for guild in bot.guilds:
        for member in guild.members:
            if member.bot:
                continue
            user_id = str(member.id)
            display_name = member.display_name
            if user_id not in map_data:
                map_data[user_id] = {"name": display_name}
            else:
                map_data[user_id]["name"] = display_name
            if year not in map_data[user_id]:
                map_data[user_id][year] = {}
            if month not in map_data[user_id][year]:
                map_data[user_id][year][month] = {}
            if 'number_of_vacations_taken' not in map_data[user_id][year][month]:
                map_data[user_id][year][month]['number_of_vacations_taken'] = 0
    
    save_map(map_data)

bot.run(TOKEN)
