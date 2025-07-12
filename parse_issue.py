import os
import sys
import json
import yaml
from datetime import datetime
from clicksend_client import SMSApi, SmsMessage, SmsMessageCollection, Configuration, ApiClient
from clicksend_client.rest import ApiException
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

def parse_shift_line(line):
    # Expected format: "Friday July 25, 2025, 7:00 PM - Usher"
    try:
        date_part, role = line.rsplit(' - ', 1)
        # Remove weekday: split at first space and join back without weekday
        parts = date_part.split(' ', 1)
        date_time_str = parts[1] if len(parts) > 1 else parts[0]
        dt = datetime.strptime(date_time_str.strip(), '%B %d, %Y, %I:%M %p')
        return {
            'date': dt.strftime('%Y-%m-%d'),
            'time': dt.strftime('%H:%M'),
            'role': role.strip()
        }
    except Exception as e:
        print(f"⚠️ Failed to parse shift line: '{line}': {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Process volunteer shifts and send SMS.')
    parser.add_argument('--name', required=True, help='Volunteer full name')
    parser.add_argument('--phone', help='Volunteer phone number (optional, required if SMS reminder is enabled)')
    parser.add_argument('--shifts', required=True, help='Multiline string of shifts')
    parser.add_argument('--notify_sms', action='store_true', help='Send SMS notification if set')

    args = parser.parse_args()

    name = args.name
    phone = args.phone
    raw_shifts_str = args.shifts.strip()
    lines = [line.strip() for line in raw_shifts_str.split('\n') if line.strip()]

    parsed_shifts = []
    for line in lines:
        shift = parse_shift_line(line)
        if shift:
            parsed_shifts.append(shift)

    if not parsed_shifts:
        print("❌ No valid shifts parsed.")
        sys.exit(1)

    schedule = load_schedule()

    # Append new entry
    schedule.append({
        'name': name,
        'phone': phone,
        'shifts': parsed_shifts,
        'notify_sms': args.notify_sms
    })

    save_schedule(schedule)
    print(f"✅ Added {len(parsed_shifts)} shifts for {name} to {SCHEDULE_FILE}")

    if args.notify_sms:
        if phone:
            send_sms(name, phone, parsed_shifts)
        else:
            print("SMS notification requested but no phone number provided.")

    generate_ics(name, parsed_shifts)

if __name__ == '__main__':
    main()
