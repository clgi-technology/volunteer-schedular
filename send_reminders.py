import os
import yaml
from datetime import datetime, timedelta
import pytz
import clicksend_client
from clicksend_client import SMSApi, SmsMessage, SmsMessageCollection
from clicksend_client.rest import ApiException

# Load volunteer data
with open("volunteer_input.yaml", "r") as f:
    volunteers = yaml.safe_load(f) or []

# Current UTC time + 1 hour (the reminder time)
now = datetime.utcnow().replace(second=0, microsecond=0)
reminder_time = now + timedelta(hours=1)

configuration = clicksend_client.Configuration()
configuration.username = os.getenv('CLICKSEND_USERNAME')
configuration.password = os.getenv('CLICKSEND_API_KEY')
sms_api = SMSApi(clicksend_client.ApiClient(configuration))

def send_sms(to_phone, message_body):
    sms = SmsMessage(source="python", body=message_body, to=to_phone)
    sms_collection = SmsMessageCollection(messages=[sms])
    try:
        response = sms_api.sms_send_post(sms_collection)
        print(f"SMS sent to {to_phone}: {response}")
    except ApiException as e:
        print(f"Failed to send SMS to {to_phone}: {e}")

for volunteer in volunteers:
    name = volunteer.get("name")
    phone = volunteer.get("phone")
    shifts = volunteer.get("shifts", [])

    for shift in shifts:
        # shift should be dict with keys: date, time, role
        try:
            shift_datetime = datetime.strptime(f"{shift['date']} {shift['time']}", "%Y-%m-%d %H:%M")
        except Exception as e:
            print(f"Skipping shift with bad format: {shift} ({e})")
            continue

        # Compare times ignoring timezone (assume all UTC)
        if shift_datetime == reminder_time:
            message = f"Hi {name}, reminder: your volunteer shift as {shift['role']} is at {shift['time']} on {shift['date']}."
            if phone:
                send_sms(phone, message)
