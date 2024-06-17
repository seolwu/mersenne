import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
LOUNGE_ID = int(os.getenv("LOUNGE_ID"))
LOUNGE_LOG_ID = int(os.getenv("LOUNGE_LOG_ID"))
PROMPT_ID = int(os.getenv("PROMPT_ID"))
MAP_FILE_PATH = os.getenv("MAP")
PLANETS_FILE_PATH = os.getenv("PLANETS")
GOAL_MINIMUM = int(os.getenv("GOAL_MINIMUM"))
GOAL_RECOMMEND = int(os.getenv("GOAL_RECOMMEND"))
GOAL_MAXIMUM = int(os.getenv("GOAL_MAXIMUM"))

# Monthly colors
MONTHLY_COLORS = {
    "01": int(os.getenv("JANUARY_COLOR").lstrip("#"), 16),
    "02": int(os.getenv("FEBRUARY_COLOR").lstrip("#"), 16),
    "03": int(os.getenv("MARCH_COLOR").lstrip("#"), 16),
    "04": int(os.getenv("APRIL_COLOR").lstrip("#"), 16),
    "05": int(os.getenv("MAY_COLOR").lstrip("#"), 16),
    "06": int(os.getenv("JUNE_COLOR").lstrip("#"), 16),
    "07": int(os.getenv("JULY_COLOR").lstrip("#"), 16),
    "08": int(os.getenv("AUGUST_COLOR").lstrip("#"), 16),
    "09": int(os.getenv("SEPTEMBER_COLOR").lstrip("#"), 16),
    "10": int(os.getenv("OCTOBER_COLOR").lstrip("#"), 16),
    "11": int(os.getenv("NOVEMBER_COLOR").lstrip("#"), 16),
    "12": int(os.getenv("DECEMBER_COLOR").lstrip("#"), 16),
}
