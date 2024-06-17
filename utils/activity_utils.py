import time
from datetime import datetime, timedelta
import discord
from .map_utils import open_map, save_map
from .time_utils import format_activity_time, ms_to_time_remaining, calculate_workdays
from .config import GOAL_MINIMUM, GOAL_RECOMMEND, GOAL_MAXIMUM, MONTHLY_COLORS

timer_cache = {}

async def create_activity_embed(bot, member, previous_month=False):
    user_id = str(member.id)
    today = datetime.today()
    year = today.strftime('%Y')

    if previous_month:
        month = (today - timedelta(days=today.day)).strftime('%m')
    else:
        month = today.strftime('%m')

    map_data = open_map()

    if user_id not in map_data or year not in map_data[user_id] or month not in map_data[user_id][year]:
        return None

    user_data = map_data[user_id][year][month]

    if 'list_of_dates' not in user_data:
        return None

    if 'total_record' not in user_data:
        user_data['total_record'] = sum(day['record'] for day in user_data['list_of_dates'].values())

    day_record = user_data['list_of_dates'].get(today.strftime('%d'), {}).get('record', 0)
    total_record = user_data.get('total_record', 0)

    workdays = calculate_workdays(int(year), int(month))
    monthly_goal_minimum = workdays * GOAL_MINIMUM
    monthly_goal_recommend = workdays * GOAL_RECOMMEND
    monthly_goal_maximum = workdays * GOAL_MAXIMUM
    time_remaining = monthly_goal_minimum - total_record
    time_remaining_str = ms_to_time_remaining(time_remaining)

    last_activity_time = "N/A"
    if 'list_of_dates' in user_data:
        for day, records in user_data['list_of_dates'].items():
            for period, duration in records['at_record'].items():
                _, end_time = period.split('~')
                last_activity_time = end_time

    embed_color = MONTHLY_COLORS.get(month, 0x000000)  # Default to black if not found

    embed = discord.Embed(
        title=f"{month}월 활동 내역",
        color=embed_color,
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="마지막 활동 시간", value=last_activity_time, inline=False)
    embed.add_field(name="오늘 활동", value=format_activity_time(day_record), inline=False)
    embed.add_field(name="이번달 활동", value=format_activity_time(total_record), inline=False)
    embed.add_field(name="이번달 남은 시간", value=time_remaining_str, inline=False)
    embed.set_footer(text="해당 메시지는 3분 후에 사라집니다.")

    return embed

async def create_previous_month_embed(bot, member):
    user_id = str(member.id)
    today = datetime.today()
    previous_month_date = today.replace(day=1) - timedelta(days=1)
    year = previous_month_date.strftime('%Y')
    month = previous_month_date.strftime('%m')

    map_data = open_map()

    if user_id not in map_data or year not in map_data[user_id] or month not in map_data[user_id][year]:
        return None

    user_data = map_data[user_id][year][month]

    if 'list_of_dates' not in user_data:
        return None

    if 'total_record' not in user_data:
        user_data['total_record'] = sum(day['record'] for day in user_data['list_of_dates'].values())

    total_record = user_data.get('total_record', 0)

    workdays = calculate_workdays(int(year), int(month))
    monthly_goal_minimum = workdays * GOAL_MINIMUM
    monthly_goal_recommend = workdays * GOAL_RECOMMEND
    monthly_goal_maximum = workdays * GOAL_MAXIMUM

    if total_record < monthly_goal_minimum:
        result = "좀 더 분발해야 할 것 같아요."
    elif total_record < monthly_goal_recommend:
        result = "목표치를 달성했습니다."
    elif total_record < monthly_goal_maximum:
        result = "목표치를 충분히 달성했습니다."
    else:
        result = "목표치를 완전히 달성했습니다."

    embed_color = MONTHLY_COLORS.get(month, 0x000000)  # Default to black if not found

    embed = discord.Embed(
        title=f"{month}월 활동 내역",
        color=embed_color,
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="총 스트림 시간", value=format_activity_time(total_record), inline=False)
    embed.add_field(name="스트림 결과", value=result, inline=False)
    embed.set_footer(text="해당 메시지는 3분 후에 사라집니다.")

    return embed

def start_recording(user_id):
    today = datetime.today().strftime('%d')
    year = datetime.today().strftime('%Y')
    month = datetime.today().strftime('%m')

    map_data = open_map()

    if user_id in map_data and year in map_data[user_id] and month in map_data[user_id][year]:
        user_data = map_data[user_id][year][month]
        if today in user_data['list_of_dates']:
            if user_data['list_of_dates'][today]['record'] >= GOAL_MAXIMUM:
                print(f"{user_id}는 오늘 최대 방송 시간에 도달했습니다.")
                return False

    timer_cache[user_id] = int(time.time() * 1000)
    return True

def stop_recording(user_id):
    map_data = open_map()

    if user_id in timer_cache:
        start_time_ms = timer_cache.pop(user_id)
        end_time_ms = int(time.time() * 1000)
        elapsed_time = end_time_ms - start_time_ms

        start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time_ms / 1000))
        end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time_ms / 1000))
        time_period = f"{start_time}~{end_time}"

        today = datetime.today().strftime('%d')
        year = datetime.today().strftime('%Y')
        month = datetime.today().strftime('%m')

        if user_id not in map_data:
            map_data[user_id] = {}

        if year not in map_data[user_id]:
            map_data[user_id][year] = {}

        if month not in map_data[user_id][year]:
            map_data[user_id][year][month] = {
                'total_record': 0,
                'list_of_dates': {}
            }

        user_data = map_data[user_id][year][month]

        if today not in user_data['list_of_dates']:
            user_data['list_of_dates'][today] = {
                'record': 0,
                'at_record': {}
            }

        day_record = user_data['list_of_dates'][today]
        day_record['at_record'][time_period] = elapsed_time

        day_record['record'] = sum(day_record['at_record'].values())

        user_data['total_record'] = sum(day['record'] for day in user_data['list_of_dates'].values())

        save_map(map_data)

def pause_recording(user_id):
    if user_id in timer_cache:
        start_time_ms = timer_cache[user_id]
        pause_time_ms = int(time.time() * 1000)
        elapsed_time = pause_time_ms - start_time_ms

        timer_cache[user_id] = (start_time_ms, elapsed_time)

def resume_recording(user_id):
    if user_id in timer_cache and isinstance(timer_cache[user_id], tuple):
        start_time_ms, elapsed_time = timer_cache[user_id]
        resume_time_ms = int(time.time() * 1000) - elapsed_time

        timer_cache[user_id] = resume_time_ms
