import os
from discord.ext import commands
import discord
from utils.activity_utils import start_recording, stop_recording, pause_recording, resume_recording, create_activity_embed

class ActivityTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def handle_voice_state_update(bot, member, before, after):
        user_id = str(member.id)
        lounge_id = int(os.getenv("LOUNGE_ID"))
        lounge_log_id = int(os.getenv("LOUNGE_LOG_ID"))

        lounge_log_channel = bot.get_channel(lounge_log_id)

        # Check if the event is in the lounge channel
        if (before.channel and before.channel.id != lounge_id) and (after.channel and after.channel.id != lounge_id):
            return

        # Check if the user started streaming in the lounge channel
        if not before.self_stream and after.self_stream and after.channel and after.channel.id == lounge_id:
            if start_recording(user_id):
                await lounge_log_channel.send(f"{member.mention}이(가) 라운지에서 방송을 시작했습니다.", allowed_mentions=discord.AllowedMentions(users=False))
                print(f"{member}의 라운지 방송 기록 시작")

        # Check if the user stopped streaming in the lounge channel
        if before.self_stream and not after.self_stream and before.channel and before.channel.id == lounge_id:
            stop_recording(user_id)
            await lounge_log_channel.send(f"{member.mention}이(가) 라운지에서 방송을 종료했습니다.", allowed_mentions=discord.AllowedMentions(users=False))
            await create_activity_embed(bot, member)
            print(f"{member}의 라운지 방송 기록 중지")

        # Check if the user went idle in the lounge channel
        if after.afk and after.channel and after.channel.id == lounge_id:
            pause_recording(user_id)
            await lounge_log_channel.send(f"{member.mention}이(가) 라운지에서 자리를 비웠습니다.", allowed_mentions=discord.AllowedMentions(users=False))
            print(f"{member}의 라운지 방송 기록 일시 중지 (자리 비움)")

        # Check if the user came back from idle in the lounge channel
        if before.afk and not after.afk and after.channel and after.channel.id == lounge_id:
            resume_recording(user_id)
            await lounge_log_channel.send(f"{member.mention}이(가) 라운지에서 돌아왔습니다.", allowed_mentions=discord.AllowedMentions(users=False))
            print(f"{member}의 라운지 방송 기록 재개 (온라인)")

        # Check if the user left the lounge channel while streaming
        if before.channel is not None and after.channel is None and before.self_stream and before.channel.id == lounge_id:
            stop_recording(user_id)
            await lounge_log_channel.send(f"{member.mention}이(가) 라운지를 떠났습니다 (방송 중).", allowed_mentions=discord.AllowedMentions(users=False))
            await create_activity_embed(bot, member)
            print(f"{member}의 라운지 방송 기록 중지 (채널 떠남)")

        # Send a message when a user joins the lounge channel
        if after.channel and after.channel.id == lounge_id and (before.channel is None or before.channel.id != lounge_id):
            await lounge_log_channel.send(f"{member.mention}이(가) 라운지에 입장했습니다.", allowed_mentions=discord.AllowedMentions(users=False))
            print(f"{member}이(가) 라운지에 입장했습니다")

        # Send a message when a user leaves the lounge channel
        if before.channel and before.channel.id == lounge_id and (after.channel is None or after.channel.id != lounge_id):
            await lounge_log_channel.send(f"{member.mention}이(가) 라운지를 떠났습니다.", allowed_mentions=discord.AllowedMentions(users=False))
            print(f"{member}이(가) 라운지를 떠났습니다")

def setup(bot):
    bot.add_cog(ActivityTracker(bot))
