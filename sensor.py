import RPi.GPIO as GPIO
from time import sleep, strftime
from datetime import datetime
import pyrebase


config = {
    "apiKey": "AIzaSyCs7mxtAmpeXgH5SS-qKBBzu0VLLWTJFF0",
    "authDomain": "alarm-clock-app-537c6.firebaseapp.com",
    "databaseURL": "https://alarm-clock-app-537c6-default-rtdb.firebaseio.com",
    "storageBucket": "alarm-clock-app-537c6.appspot.com"
}

GPIO.setmode(GPIO.BCM)
PIR_PIN = 21
GPIO.setup(PIR_PIN, GPIO.IN)

firebase = pyrebase.initialize_app(config)

db = firebase.database()



def update_trigger_alarm(alarm_id, current_state, utc_current_time):
    db.child("alarms").child(alarm_id).update({"triggered": current_state, "current_time": utc_current_time})


def match_time(alarms):
    utc_current_time = datetime.utcnow().strftime("%H:%M")
    current_time_hour = utc_current_time.split(":")[0]
    current_time_minute = utc_current_time.split(":")[1]

    for alarm_value in alarms.values():
        alarm_hour = alarm_value["time"].split(":")[0]
        alarm_minute = alarm_value["time"].split(":")[1]

        if alarm_hour == current_time_hour:
            if alarm_minute == current_time_minute:
                if not alarm_value["triggered"]:
                    update_trigger_alarm(alarm_value["id"], True, utc_current_time)
                    
            if (int(current_time_minute) >= int(alarm_minute)):
                return [True, alarm_value]
        
    return [False, None]


def check_alarm_match_and_update_data(alarm):
    current_utc_time = datetime.utcnow().strftime("%H:%M")
    current_minute = current_utc_time.split(":")[1]
    alarm_minute = alarm["time"].split(":")[1]
    
    if alarm["triggered"]:
        print("Alarm is triggered so person must be a wake and out of room")
        update_trigger_alarm(alarm["id"], False, current_utc_time)
        return

    if (int(current_minute) - int(alarm_minute)) > 10:
        print("Alarm is past 10 mins wait period so it will be turned off")
        update_trigger_alarm(alarm["id"], False, current_utc_time)
        return
    
    print("Alarm is not triggered and its under 10mins wait period so person must have come back in room")
    update_trigger_alarm(alarm["id"], True, current_utc_time)
    return

def motion_detector():
    print("Motion Detected")
    alarms = db.child("alarms").get()
    is_alarm_triggered, alarm  = match_time(alarms.val())
    if is_alarm_triggered:
        check_alarm_match_and_update_data(alarm)
    return


print("App starting...")
sleep(2)
print("App started")

try:
    GPIO.add_event_detect(PIR_PIN, GPIO.RISING, callback=motion_detector)
    while True:
        sleep(100)
        # print("App running")
        
        # if is_alarm_triggered:
        #     if GPIO.input(PIR_PIN):
        #         print("Motion Detected")
                
        # sleep(1)
except KeyboardInterrupt:
    print("Exiting...")
    GPIO.cleanup()
