"""
A simple tool to tell the current time.
Usage: 'time:' or 'what time is it?'
"""
from datetime import datetime

def tell_time_tool() -> str:
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return f"[TOOL] The current time is: {now}"
