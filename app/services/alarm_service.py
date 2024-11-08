import threading
from datetime import datetime
import time

alarm_time = None

def set_alarm(time_string):
    global alarm_time
    alarm_time = time_string
    threading.Thread(target=_check_alarm).start()

def _check_alarm():
    global alarm_time
    while alarm_time:
        if datetime.now().strftime("%H:%M") == alarm_time:
            emit('trigger_alarm', {'message': "Time's up! Your alarm is ringing!"})
            alarm_time = None
            break
        time.sleep(1)

def clear_alarm():
    global alarm_time
    alarm_time = None
