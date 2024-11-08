from datetime import datetime, timezone
from ics import Calendar

def get_today_events():
    with open("calendar.ics", "r") as f:
        calendar = Calendar(f.read())
    today = datetime.now(timezone.utc).date()
    today_events = [event for event in calendar.events if event.begin.datetime.date() == today]
    return today_events, today
