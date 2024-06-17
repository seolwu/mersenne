from datetime import datetime, timedelta
import holidays

kr_holidays = holidays.KR()

def ms_to_hms(ms):
    seconds = (ms // 1000) % 60
    minutes = (ms // (1000 * 60)) % 60
    hours = (ms // (1000 * 60 * 60)) % 24
    days = ms // (1000 * 60 * 60 * 24)
    return days, hours, minutes, seconds

def format_activity_time(ms):
    days, hours, minutes, seconds = ms_to_hms(ms)
    if days > 0:
        return f"{days}일 {hours}시간 {minutes}분 {seconds}초"
    elif hours > 0:
        return f"{hours}시간 {minutes}분 {seconds}초"
    elif minutes > 0:
        return f"{minutes}분 {seconds}초"
    else:
        return f"{seconds}초"

def ms_to_time_remaining(ms):
    minutes = ms // (1000 * 60)
    if minutes < 60:
        return f"{minutes}분 남았습니다."
    hours = minutes // 60
    return f"{hours}시간 남았습니다."

def calculate_workdays(year, month):
    total_days = (datetime(year, month + 1, 1) - timedelta(days=1)).day
    workdays = 0
    for day in range(1, total_days + 1):
        date = datetime(year, month, day)
        if date.weekday() < 5 and date not in kr_holidays:
            workdays += 1
    return workdays