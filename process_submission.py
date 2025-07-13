import os
import sys
import re
import json
import yaml
import argparse
from datetime import datetime, date
from ics import Calendar, Event
from clicksend_client import SMSApi, SmsMessage, SmsMessageCollection, Configuration, ApiClient
from clicksend_client.rest import ApiException

SCHEDULE_FILE = 'volunteer_input.yaml'

def extract_fields(issue_body):
    def find_section(label):
        pattern = rf"### {re.escape(label)}\n(.*?)(\n### |\Z)"
        match = re.search(pattern, issue_body, re.DOTALL)
        return match.group(1).strip() if match else ""

    return {
        'name': find_section("Full Name"),
        'phone': find_section("Phone Number"),
        'shifts_raw': find_section("What shifts are you available for?")
    }

def parse_shifts(shifts_str):
    lines = [l.strip() for l in shifts_str.splitlines() if l.strip()]
    parsed = []

    for line in lines:
        try:
            parts = re.split(r"\s+[-–—]\s+", line)
            if len(parts) != 2:
                raise ValueError("Invalid format")
            dt = datetime.strptime(parts[0].strip(), "%A %B %d, %Y, %I:%M %p")
            parsed.append({
                'date': dt.strftime("%Y-%m-%d"),
                'time': dt.strftime("%H:%M"),
                'role': parts[1].strip()
            })
        except Exception as e:
            print(f"⚠️ Could not parse shift: '{line}' ({e})", file=sys.stderr)
    return parsed

def load_schedule():
    if os.path.exists(SCHEDULE_FILE):
        with open(SCHEDULE_FILE, 'r') as f:
            return yaml.safe_load(f) or []
    return []

def save_schedule(schedule):
    def convert(obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, list):
            return [convert(i) for i in obj]
        elif isinstance(obj, dict):
            return {k: convert(v) for k, v in obj.items()}
        return obj

    with open(SCHEDULE_FILE, 'w') as f:
        yaml.safe_dump(convert(schedule), f)

def export_to_json(schedule):
    flat = []
    for person in schedule:
        for shift in person.get('shifts', []):
            flat.append({
                'date': shift['date'],
                'time': shift['time'],
                'volunteer': person['name'],
                'role': shift['role']
            })
    os.makedirs('docs', exist_ok=True)
    with open('docs/volunteer_schedule.json', 'w') as f:
        json.dump(flat, f, indent=2)

def send_sms(name, phone, shifts):
    username = os.getenv("CLICKSEND_USERNAME")
    api_key = os.getenv("CLICKSEND_API_KEY")

    if not (username and api_key):
        print("❌ Missing ClickSend credentials.")
        return

    configuration = Configuration()
    configuration.username = username
    configuration.password = api_key

    sms_api = SMSApi(ApiClient(configuration))

    messages = []
    for shift in shifts:
        text = (
            f"Hi {name}! You're scheduled to {shift['role']} on "
            f"{datetime.strptime(shift['date'], '%Y-%m-%d').strftime('%A, %B %d, %Y')} at {shift['time']}."
        )
        messages.append(SmsMessage(source="python", body=text, to=phone, _from="Volunteers"))

    try:
        response = sms_api.sms_send_post(SmsMessageCollection(messages=messages))
        print("✅ SMS sent:", response)
    except ApiException as e:
        print("❌ ClickSend API error:", e)

def generate_ics(name, shifts):
    cal = Calendar()
    for shift in shifts:
        dt = datetime.strptime(f"{shift['date']} {shift['time']}", "%Y-%m-%d %H:%M")
        event = Event(name=f"{shift['role']} shift", begin=dt, duration={"hours": 1}, description=f"Volunteer: {name}")
        cal.events.add(event)
    filename = f"{name.replace(' ', '_')}_shifts.ics"
    with open(filename, 'w') as f:
        f.writelines(cal)
    print(f"📆 ICS calendar saved: {filename}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--issue-body', required=True, help="Raw GitHub issue body text")
    parser.add_argument('--notify_sms', action='store_true')
    args = parser.parse_args()

    data = extract_fields(args.issue_body)

    if not data['name'] or not data['shifts_raw']:
        print("❌ Missing name or shifts")
        sys.exit(1)

    shifts = parse_shifts(data['shifts_raw'])
    if not shifts:
        print("❌ No valid shifts parsed")
        sys.exit(1)

    entry = {
        'name': data['name'],
        'phone': data['phone'],
        'shifts': shifts,
        'notify_sms': args.notify_sms
    }

    schedule = load_schedule()
    schedule.append(entry)
    save_schedule(schedule)
    export_to_json(schedule)

    if args.notify_sms and data['phone']:
        send_sms(data['name'], data['phone'], shifts)

    generate_ics(data['name'], shifts)

    print(f"✅ Processed submission for {data['name']} with {len(shifts)} shifts.")

if __name__ == '__main__':
    main()
