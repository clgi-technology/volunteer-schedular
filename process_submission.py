import sys
import argparse
import yaml
import json
import re
from datetime import datetime

SCHEDULE_YAML = 'volunteer_input.yaml'
SCHEDULE_JSON = 'docs/volunteer_schedule.json'

def load_schedule():
    try:
        with open(SCHEDULE_YAML, 'r') as f:
            data = yaml.safe_load(f)
            return data if data else []
    except FileNotFoundError:
        return []

def save_schedule(schedule):
    with open(SCHEDULE_YAML, 'w') as f:
        yaml.safe_dump(schedule, f, sort_keys=False)

def export_json(schedule):
    # Convert shifts time to int if string is numeric (like '1380' -> 1380)
    json_data = []
    for vol in schedule:
        for shift in vol.get('shifts', []):
            time_val = shift.get('time')
            if isinstance(time_val, str) and time_val.isdigit():
                shift['time'] = int(time_val)
        json_data.extend([
            {
                "date": shift.get('date'),
                "time": shift.get('time'),
                "volunteer": vol.get('name'),
                "role": shift.get('role')
            }
            for shift in vol.get('shifts', [])
        ])
    with open(SCHEDULE_JSON, 'w') as f:
        json.dump(json_data, f, indent=2)

def parse_shifts(shift_lines):
    shifts = []
    # Example line: "Saturday July 12, 2025, 11:15 PM – Livestream"
    pattern = re.compile(r"^(.*?),\s*(\d{1,2}:\d{2}\s*[APMapm\.]{2,4})\s*[-–—]\s*(.*)$")
    for line in shift_lines:
        m = pattern.match(line)
        if not m:
            continue
        date_str, time_str, role = m.groups()
        # Parse date to ISO YYYY-MM-DD
        try:
            dt_date = datetime.strptime(date_str.strip(), "%A %B %d, %Y")
            date_fmt = dt_date.strftime("%Y-%m-%d")
        except ValueError:
            # fallback, skip if bad date
            continue
        # Parse time to 24h HH:MM
        try:
            dt_time = datetime.strptime(time_str.strip().replace('.', ''), "%I:%M %p")
            time_fmt = dt_time.strftime("%H:%M")
        except ValueError:
            # fallback, skip if bad time
            continue
        shifts.append({
            'date': date_fmt,
            'time': time_fmt,
            'role': role.strip()
        })
    if not shifts:
        sys.exit("❌ No valid shifts parsed.")
    return shifts

def parse_issue_body(body):
    lines = body.splitlines()
    name = ""
    phone = ""
    notify_sms = False
    shifts = []
    mode = None
    for l in lines:
        l = l.strip()
        if l.startswith("###"):
            if "Full Name" in l:
                mode = 'name'
            elif "Phone Number" in l:
                mode = 'phone'
            elif "Notify me via SMS" in l:
                mode = 'notify_sms'
            elif "shifts" in l.lower():
                mode = 'shifts'
            else:
                mode = None
            continue

        if mode == 'name' and l and not name:
            name = l
        elif mode == 'phone' and l and not phone:
            phone = l
        elif mode == 'notify_sms' and l:
            notify_sms = l.lower() in ('yes', 'true', '1')
        elif mode == 'shifts' and l:
            # ignore any numeric-only lines (like '1s' etc)
            if not re.match(r'^\d+s$', l):
                shifts.append(l.lstrip('- ').strip())

    if not name:
        sys.exit("❌ Missing Full Name in issue body.")
    if not shifts:
        sys.exit("❌ No shifts specified in issue body.")
    return name, phone, notify_sms, shifts

def main():
    parser = argparse.ArgumentParser(description="Process volunteer submission")
    parser.add_argument('--issue-body', type=str, help="Full issue body text")
    parser.add_argument('--name', type=str, help="Volunteer name (if no issue body)")
    parser.add_argument('--phone', type=str, help="Phone number (if no issue body)")
    parser.add_argument('--shifts', type=str, nargs='*', help="Shifts (if no issue body)")
    parser.add_argument('--notify-sms', action='store_true', help="Send SMS notification")
    args = parser.parse_args()

    if args.issue_body:
        name, phone, notify_sms, raw_shifts = parse_issue_body(args.issue_body)
    else:
        if not args.name or not args.shifts:
            sys.exit("❌ Missing required --name or --shifts")
        name = args.name.strip()
        phone = (args.phone or "").strip()
        notify_sms = args.notify_sms
        raw_shifts = args.shifts

    shifts = parse_shifts(raw_shifts)

    schedule = load_schedule()
    # Remove existing entry for same name and phone (optional)
    schedule = [v for v in schedule if not (v.get('name') == name and v.get('phone') == phone)]

    new_volunteer = {
        'name': name,
        'phone': phone,
        'shifts': shifts
    }
    if notify_sms:
        new_volunteer['notify_sms'] = True

    schedule.append(new_volunteer)
    save_schedule(schedule)
    export_json(schedule)
    print(f"✅ Recorded {name} with {len(shifts)} shift(s).")

if __name__ == "__main__":
    main()
