import os
import sys
import json
import yaml
from datetime import datetime
from clicksend_client import ClickSendClient
from clicksend_client.models.sms_message import SmsMessage
from clicksend_client.models.sms_message_collection import SmsMessageCollection
import argparse
from ics import Calendar, Event

SCHEDULE_FILE = 'volunteer_input.yaml'

def load_schedule():
    if os.path.exists(SCHEDULE_FILE):
        with open(SCHEDULE_FILE, 'r') as f:
            return yaml.safe_load(f) or []
    return []

def save_schedule(schedule):
    with open(SCHEDULE_FILE, 'w') as f:
        yaml.safe_dump(schedule, f)

def send_sms(name, phone, shifts):
    username = os.getenv('CLICKSEND_USERNAME')
    api_key = os.getenv('CLICKSEND_API_KEY')

    if not username or not api_key:
        print("Missing ClickSend credentials")
        return

    client = ClickSendClient(username=username, api_key=api_key)
    sms_api = client.sms_api

    messages = []
    for shift in shifts:
        date_obj = datetime.strptime(shift['date'], '%Y-%m-%d')
        date_str = date_obj.strftime('%A, %B %d, %Y')
        time_str = shift['time']
        role = shift['role']

        text = (
            f"Hi {name}! You're scheduled to {role} on {date_str} at {time_str}. Thank you for volunteering!"
        )
        messages.append(
            SmsMessage(
                source="python",
                body=text,
                to=phone,
                from_="Volunteers"  # Adjust sender ID if allowed
            )
        )

    sms_collection = SmsMessageCollection(messages=messages)
    try:
        response = sms_api.sms_send_post(sms_collection)
        print(f"SMS sent successfully: {response}")
    except Exception as e:
        print(f"Error sending SMS: {e}")

def generate_ics(name, shifts):
    cal = Calendar()
    for shift in shifts:
        event = Event()
        dt = datetime.strptime(f"{shift['date']} {shift['time']}", '%Y-%m-%d %H:%M')
        event.name = f"{shift['role']} shift"
        event.begin = dt
        event.duration = {"hours": 1}  # Assume 1 hour shifts; adjust as needed
        event.description = f"Volunteer: {name}"
        cal.events.add(event)
    ics_path = f"{name.replace(' ', '_')}_shifts.ics"
    with open(ics_path, 'w') as f:
        f.writelines(cal)
    print(f"ICS calendar invite saved to {ics_path}")

def main():
    parser = argparse.ArgumentParser(description='Process volunteer shifts and send SMS.')
    parser.add_argument('--name', required=True, help='Volunteer full name')
    parser.add_argument('--phone', required=True, help='Volunteer phone number')
    parser.add_argument('--shifts', required=True, help='JSON string of shifts')
    parser.add_argument('--notify_sms', action='store_true', help='Send SMS notification if set')

    args = parser.parse_args()

    name = args.name
    phone = args.phone
    try:
        shifts = json.loads(args.shifts)
    except json.JSONDecodeError:
        print("Error parsing shifts JSON")
        sys.exit(1)

    schedule = load_schedule()
    schedule.append({
        'name': name,
        'phone': phone,
        'shifts': shifts
    })
    save_schedule(schedule)

    if args.notify_sms:
        send_sms(name, phone, shifts)

    generate_ics(name, shifts)

if __name__ == '__main__':
    main()
