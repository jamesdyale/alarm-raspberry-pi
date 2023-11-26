import RPi.GPIO as GPIO
from time import sleep, strftime
from datetime import datetime
import pyrebase

is_alarm_allowed_to_trigger = False

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


def match_time(alarms, is_alarm_allowed_to_trigger):
    print("Checking if time matches")
    utc_current_time = datetime.utcnow().strftime("%H:%M")
    current_time_hour = utc_current_time.split(":")[0]
    current_time_minute = utc_current_time.split(":")[1]

    for alarm_value in alarms.values():
        alarm_hour = alarm_value["time"].split(":")[0]
        alarm_minute = alarm_value["time"].split(":")[1]

        if alarm_hour == current_time_hour:
            if alarm_minute == current_time_minute:
                if not alarm_value["triggered"]:
                    print("Time matched")
                    is_alarm_allowed_to_trigger = True
                    update_trigger_alarm(alarm_value["id"], True, utc_current_time)
            
            if is_alarm_allowed_to_trigger:
                print("Alarm is allowed to trigger")
                return [True, alarm_value]
        
    is_alarm_allowed_to_trigger = False
    return [False, None]


def check_motion_and_update_data(alarm):
    print("Checking motion and updating data")
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



try:
    while True:
        print("App running")
        alarms = db.child("alarms").get()
        print("PIR_PIN: ")
        print(GPIO.input(PIR_PIN))
        if GPIO.input(PIR_PIN):
            print("Motion Detected")
        # isTimeMatched, alarm = match_time(alarms.val(), is_alarm_allowed_to_trigger)

        # if isTimeMatched:
        #     print("Time matched")
        #     if GPIO.input(PIR_PIN):
        #         print("Motion Detected")
        #         check_motion_and_update_data(alarm)
        sleep(1)
except KeyboardInterrupt:
    print("Exiting...")
    GPIO.cleanup()
