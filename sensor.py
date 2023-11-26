import RPi.GPIO as GPIO
from time import sleep, strftime
from datetime import datetime
import pyrebase

config = {
    "apiKey":"",
    "authDomain": "",
    "databaseURL": "",
    "storageBucket": ""
}


GPIO.setmode(GPIO.BCM)

PIR_PIN = 21

GPIO.setup(PIR_PIN, GPIO.IN)

firebase = pyrebase.initialize_app(config)

db = firebase.database()

current_ringing_alarm = None

def updateTriggerAlarm(alarm_id, current_state, current_time):
    db.child("alarms").child(alarm_id).update({"triggered": current_state, "current_time": current_time})

def matchTime(alarms):
    utc_time = datetime.utcnow()
    current_time = utc_time.strftime("%H:%M") 
    
    time_hit = []

    for alarm in alarms.values():
        alarm_hour = alarm["time"].split(":")[0]
        current_time_hour = current_time.split(":")[0]
        alarm_minute = alarm["time"].split(":")[1]
        current_time_minute = current_time.split(":")[1]
        
        if (alarm_hour == current_time_hour and alarm_minute == current_time_minute):
            if (!alarm["triggered"] and current_ringing_alarm == None):
                updateTriggerAlarm(alarm["id"], True, current_time)
            return [True, alarm]

    return [False, None]


def checkMotionAndUpdateData(alarm):
    current_time_here = datetime.utcnow().strftime("%H:%M")
    if (alarm["triggered"]):
        updateTriggerAlarm(alarm["id"], False, current_time_here)

    # check if it is less than 10mins and then fire if false or set to true    
    

    


try: 
    while True:
        utc_time = datetime.utcnow()
        current_time = utc_time.strftime("%H:%M")
        alarms = db.child("alarms").get()
        
        #isTimeMatched, alarm  = matchTime(alarms.val())

        #if isTimeMatched:
         #   if GPIO.input(PIR_PIN):
          #      checkMotionAndUpdateData(alarm)
           #     print("Motion Detected")
        sleep(60)
except KeyboardInterrupt:
    print("Exiting...")
    GPIO.cleanup()


