from flask import Blueprint, render_template
from ..services.calendar_service import get_today_events

calendar_routes = Blueprint('calendar_routes', __name__)

@calendar_routes.route('/calendar')
def daily_calendar():
    today_events, current_date = get_today_events()
    return render_template("calendar.html", today_events=today_events, current_date=current_date)
