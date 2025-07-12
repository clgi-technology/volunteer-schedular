import os
import sys
import json
import yaml
import logging
from datetime import datetime
import argparse

try:
    from clicksend_client import ClickSendClient
    from clicksend_client.models.sms_message import SmsMessage
    from clicksend_client.models.sms_message_collection import SmsMessageCollection
except ImportError:
    # ClickSend client not installed or not needed for local testing without notification
    ClickSendClient = None

SCHEDULE_FILE = 'volunteer_input.yaml'

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')


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
        logging.error("Missing ClickSend credentials in environment variables.")
        sys.exit(1)

    if ClickSendClient is None:
        logging.error("clicksend-client package is not installed.")
        sys.exit(1)

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
        logging.info(f"SMS sent successfully: {response}")
    except Exception as e:
        logging.error(f"Error sending SMS: {e}")
        sys.exit(1)


def deduplicate_and_update(schedule, name, phone, new_shifts):
    """
    Check if a volunteer with the same name and phone exists.
    If yes, update shifts (merge without duplicates).
    If no, append new volunteer.
    """
    for vol in schedule:
        if vol.get('name') == name and vol.get('phone') == phone:
            # Merge shifts, avoiding duplicates
            existing = vol.get('shifts', [])
            combined = existing.copy()

            # Create a set of tuples for existing shifts
            existing_set = {(s['date'], s['time'], s['role']) for s in existing}
            for ns in new_shifts:
                key = (ns['date'], ns['time'], ns['role'])
                if key not in existing_set:
                    combined.append(ns)
                    existing_set.add(key)

            vol['shifts'] = combined
            return schedule

    # Not found, append
    schedule.append({
        'name': name,
        'phone': phone,
        'shifts': new_shifts
    })
    return schedule


def generate_ics(name, shifts, filename=None):
    """
    Generate a simple ICS file with all shifts as events.
    Returns ICS string if filename is None, else writes to file.
    """
    from datetime import timedelta

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Volunteer Schedule//EN",
        "CALSCALE:GREGORIAN"
    ]

    for i, shift in enumerate(shifts, 1):
        start_dt = datetime.strptime(f"{shift['date']} {shift['time']}", "%Y-%m-%d %H:%M")
        end_dt = start_dt + timedelta(hours=1)  # Assume 1-hour shift; adjust if needed
        uid = f"{name}-{i}@volunteers.example.com"

        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
            f"DTSTART;TZID=UTC:{start_dt.strftime('%Y%m%dT%H%M%SZ')}",
            f"DTEND;TZID=UTC:{end_dt.strftime('%Y%m%dT%H%M%SZ')}",
            f"SUMMARY:{shift['role']} shift for {name}",
            f"DESCRIPTION:Volunteer {name} scheduled for {shift['role']} on {shift['date']} at {shift['time']}",
            "END:VEVENT"
        ])

    lines.append("END:VCALENDAR")
    ics_content = "\n".join(lines)

    if filename:
        with open(filename, 'w') as f:
            f.write(ics_content)
        logging.info(f"ICS calendar file written to {filename}")

    return ics_content


def main():
    parser = argparse.ArgumentParser(description='Process volunteer shifts and optionally send SMS reminders.')
    parser.add_argument('--name', required=True, help='Volunteer full name')
    parser.add_argument('--phone', required=True, help='Volunteer phone number')
    parser.add_argument('--shifts', required=True, help='JSON string of shifts')
    parser.add_argument('--notify', action='store_true', help='Send SMS notification via ClickSend')
    parser.add_argument('--generate-ics', help='Optional output filename for ICS calendar')

    args = parser.parse_args()

    name = args.name
    phone = args.phone
    try:
        shifts = json.loads(args.shifts)
    except json.JSONDecodeError:
        logging.error("Error parsing shifts JSON")
        sys.exit(1)

    schedule = load_schedule()
    schedule = deduplicate_and_update(schedule, name, phone, shifts)
    save_schedule(schedule)

    if args.notify:
        send_sms(name, phone, shifts)

    if args.generate_ics:
        generate_ics(name, shifts, args.generate_ics)


if __name__ == '__main__':
    main()
