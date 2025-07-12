import os
import yaml
from datetime import datetime, timedelta
import clicksend_client
from clicksend_client import SMSApi, SmsMessage, SmsMessageCollection
from clicksend_client.rest import ApiException

# Load volunteer data
with open("volunteer_input.yaml", "r") as f:
    volunteers = yaml.safe_load(f) or []

# Current UTC time rounded to minute + 1 hour (the reminder time)
now = datetime.utcnow().replace(second=0, microsecond=0)
reminder_time = now + timedelta(hours=1)

# Initialize ClickSend API client
configuration = clicksend_client.Configuration()
configuration.username = os.getenv('CLICKSEND_USERNAME')
configuration.password = os.getenv('CLICKSEND_API_KEY')
sms_api = SMSApi(clicksend_client.ApiClient(configuration))

def send_sms(to_phone, message_body):
    sms = SmsMessage(source="python", body=message_body, to=to_phone)
    sms_collection = SmsMessageCollection(messages=[sms])
    try:
        response = sms_api.sms_send_post(sms_collection)
        print(f"✅ SMS sent to {to_phone}: {response}")
    except ApiException as e:
        print(f"❌ Failed to send SMS to {to_phone}: {e}")

for volunteer in volunteers:
    name = volunteer.get("name", "Volunteer")
    phone = volunteer.get("phone", "").strip()
    shifts = volunteer.get("shifts", [])

    if not phone:
        print(f"ℹ️ Skipping {name} — no phone number provided.")
        continue  # skip volunteers without phone

    for shift in shifts:
        # Expecting dict with keys: date (YYYY-MM-DD), time (HH:MM 24h), role
        try:
            shift_datetime = datetime.strptime(f"{shift['date']} {shift['time']}", "%Y-%m-%d %H:%M")
        except Exception as e:
            print(f"⚠️ Skipping shift with bad format: {shift} ({e})")
            continue

        # Send SMS reminder if the shift time matches the reminder time exactly
        if shift_datetime == reminder_time:
            message = f"Hi {name}, reminder: your volunteer shift as {shift['role']} starts at {shift['time']} on {shift['date']}."
            send_sms(phone, message)
