import os
import sys
import json
import yaml
import argparse
from datetime import datetime, date
from ics import Calendar, Event
from clicksend_client import SMSApi, SmsMessage, SmsMessageCollection, Configuration, ApiClient
from clicksend_client.rest import ApiException

SCHEDULE_FILE = 'volunteer_input.yaml'

def load_schedule():
    if os.path.exists(SCHEDULE_FILE):
        with open(SCHEDULE_FILE, 'r') as f:
            return yaml.safe_load(f) or []
    return []

def save_schedule(schedule):
    # Convert any date objects to strings before saving
    def convert_dates(obj):
        if isinstance(obj, list):
            return [convert_dates(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: convert_dates(value) for key, value in obj.items()}
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()
        else:
            return obj

    schedule_serializable = convert_dates(schedule)
    with open(SCHEDULE_FILE, 'w') as f:
        yaml.safe_dump(schedule_serializable, f)

def export_to_json(schedule):
    flat_list = []
    for entry in schedule:
        name = entry.get('name')
        shifts = entry.get('shifts', [])
        for shift in shifts:
            flat_list.append({
                'date': shift.get('date'),
                'time': shift.get('time'),
                'volunteer': name,
                'role': shift.get('role')
            })

    # Write to docs/volunteer_schedule.json
    os.makedirs('docs', exist_ok=True)
    with open('docs/volunteer_schedule.json', 'w') as f:
        json.dump(flat_list, f, indent=2)

def send_sms(name, phone, shifts):
    username = os.getenv('CLICKSEND_USERNAME')
    api_key = os.getenv('CLICKSEND_API_KEY')

    if not username or not api_key:
        print("Missing ClickSend credentials")
        return

    configuration = Configuration()
    configuration.username = username
    configuration.password = api_key

    sms_api = SMSApi(ApiClient(configuration))

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
                _from="Volunteers"
            )
        )

    sms_collection = SmsMessageCollection(messages=messages)
    try:
        response = sms_api.sms_send_post(sms_collection)
        print(f"SMS sent successfully: {response}")
    except ApiException as e:
        print(f"ClickSend API error: {e}")
    except Exception as e:
        print(f"Unexpected error while sending SMS: {e}")

def generate_ics(name, shifts):
    cal = Calendar()
    for shift in shifts:
        event = Event()
        dt = datetime.strptime(f"{shift['date']} {shift['time']}", '%Y-%m-%d %H:%M')
        event.name = f"{shift['role']} shift"
        event.begin = dt
        event.duration = {"hours": 1}
        event.description = f"Volunteer: {name}"
        cal.events.add(event)
    ics_path = f"{name.replace(' ', '_')}_shifts.ics"
    with open(ics_path, 'w') as f:
        f.writelines(cal)
    print(f"ICS calendar invite saved to {ics_path}")

def main():
    parser = argparse.ArgumentParser(description='Process volunteer shifts and send SMS.')
    parser.add_argument('--name', required=True, help='Volunteer full name')
    parser.add_argument('--phone', help='Volunteer phone number (optional, required if SMS reminder is enabled)')
    parser.add_argument('--shifts', required=True, help='JSON string of shifts or a Python list')
    parser.add_argument('--notify_sms', action='store_true', help='Send SMS notification if set')

    args = parser.parse_args()

    name = args.name
    phone = args.phone
    try:
        if isinstance(args.shifts, str):
            shifts = json.loads(args.shifts)
        else:
            shifts = args.shifts
    except Exception as e:
        print(f"Error parsing shifts: {e}")
        sys.exit(1)

    schedule = load_schedule()
    schedule.append({
        'name': name,
        'phone': phone,
        'shifts': shifts,
        'notify_sms': args.notify_sms
    })
    save_schedule(schedule)

    # Export updated flat schedule to JSON for the calendar
    export_to_json(schedule)

    if args.notify_sms:
        if phone:
            send_sms(name, phone, shifts)
        else:
            print("SMS notification requested but no phone number provided.")

    generate_ics(name, shifts)

if __name__ == '__main__':
    main()
