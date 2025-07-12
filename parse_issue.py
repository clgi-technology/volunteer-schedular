import argparse
import json
import sys
import re
from datetime import datetime
from ics import Calendar, Event
import yaml
import os

SCHEDULE_FILE = 'volunteer_input.yaml'

def load_schedule():
    if os.path.exists(SCHEDULE_FILE):
        with open(SCHEDULE_FILE, 'r') as f:
            return yaml.safe_load(f) or []
    return []

def save_schedule(schedule):
    def convert_dates(obj):
        if isinstance(obj, list):
            return [convert_dates(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: convert_dates(value) for key, value in obj.items()}
        elif isinstance(obj, (datetime,)):
            return obj.isoformat()
        else:
            return obj

    schedule_serializable = convert_dates(schedule)
    with open(SCHEDULE_FILE, 'w') as f:
        yaml.safe_dump(schedule_serializable, f)

def parse_shifts(shifts_str):
    shift_lines = [line.strip() for line in shifts_str.split('\n') if line.strip()]

    # If only one line, fallback to comma-based split
    if len(shift_lines) == 1 and all(sep not in shift_lines[0] for sep in [' – ', ' - ', ' — ']):
        shift_lines = [line.strip() for line in shifts_str.split(',') if line.strip()]

    parsed_shifts = []
    for line in shift_lines:
        # Accept any dash format surrounded by spaces
        parts = re.split(r'\s+[-–—]\s+', line)
        if len(parts) != 2:
            print(f"⚠️ Failed to parse shift line: '{line}': expected exactly 2 parts split by dash")
            continue

        date_time_str, role = parts
        try:
            dt = datetime.strptime(date_time_str.strip(), '%A %B %d, %Y, %I:%M %p')
        except ValueError as e:
            print(f"⚠️ Failed to parse date/time in shift line: '{line}': {e}")
            continue

        parsed_shifts.append({
            'date': dt.strftime('%Y-%m-%d'),
            'time': dt.strftime('%H:%M'),
            'role': role.strip()
        })

    if not parsed_shifts:
        print("❌ No valid shifts parsed.")
        sys.exit(1)

    return parsed_shifts

def main():
    parser = argparse.ArgumentParser(description='Process volunteer shifts.')
    parser.add_argument('--name', required=True, help='Volunteer full name')
    parser.add_argument('--phone', help='Volunteer phone number (optional)')
    parser.add_argument('--shifts', required=True, help='Shifts string')
    parser.add_argument('--notify_sms', action='store_true', help='Send SMS notification if set')

    args = parser.parse_args()

    name = args.name.strip()
    if not name:
        print("❌ Name is empty.")
        sys.exit(1)

    shifts = parse_shifts(args.shifts)

    schedule = load_schedule()
    schedule.append({
        'name': name,
        'phone': args.phone,
        'shifts': shifts,
        'notify_sms': args.notify_sms
    })
    save_schedule(schedule)

    print(f"✅ Successfully processed submission for {name} with {len(shifts)} shifts.")

if __name__ == '__main__':
    main()
