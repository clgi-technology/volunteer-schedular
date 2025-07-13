#!/usr/bin/env python3
import os
import sys
import json
import yaml
import argparse
import re
from datetime import datetime
from clicksend_client import SMSApi, SmsMessage, SmsMessageCollection, Configuration, ApiClient
from ics import Calendar, Event

SCHEDULE_FILE = 'volunteer_input.yaml'
DOCS_JSON = 'docs/volunteer_schedule.json'

def load_schedule():
    if os.path.exists(SCHEDULE_FILE):
        with open(SCHEDULE_FILE) as f:
            return yaml.safe_load(f) or []
    return []

def save_schedule(schedule):
    with open(SCHEDULE_FILE, 'w') as f:
        yaml.safe_dump(schedule, f)

def export_json(schedule):
    flat = []
    for entry in schedule:
        for sh in entry.get('shifts', []):
            flat.append({
                'date': sh['date'],
                'time': sh['time'],
                'volunteer': entry['name'],
                'role': sh['role']
            })
    os.makedirs(os.path.dirname(DOCS_JSON), exist_ok=True)
    with open(DOCS_JSON, 'w') as f:
        json.dump(flat, f, indent=2)

def parse_shifts(lines):
    out = []
    for line in lines:
        parts = re.split(r'\s+[-–—]\s+', line.strip())
        if len(parts) != 2:
            continue
        try:
            dt = datetime.strptime(parts[0].strip(), '%A %B %d, %Y, %I:%M %p')
        except ValueError:
            continue
        out.append({
            'date': dt.strftime('%Y-%m-%d'),
            'time': dt.strftime('%H:%M'),
            'role': parts[1].strip()
        })
    if not out:
        sys.exit('❌ No valid shifts parsed.')
    return out

def parse_issue_body(body):
    lines = body.splitlines()
    name = phone = ""
    notify_sms = False
    shifts = []
    mode = None
    for l in lines:
        l = l.strip()
        if l.startswith("###"):
            if "Full Name" in l: mode = 'name'
            elif "Phone Number" in l: mode = 'phone'
            elif "notify via sms" in l.lower(): mode = 'notify_sms'
            elif "shifts" in l.lower(): mode = 'shifts'
            else: mode = None
            continue
        if mode == 'name' and l and not name:
            name = l
        elif mode == 'phone' and l and not phone:
            phone = l
        elif mode == 'notify_sms' and l:
            if l.lower() in ("yes", "true", "1"):
                notify_sms = True
        elif mode == 'shifts' and l:
            shifts.append(l.lstrip('- ').strip())
    if not name or not shifts:
        sys.exit('❌ Missing name or shifts in issue body.')
    return name, phone, shifts, notify_sms

def send_sms(name, phone, shifts):
    user = os.getenv('CLICKSEND_USERNAME')
    key = os.getenv('CLICKSEND_API_KEY')
    if not user or not key or not phone:
        return
    cfg = Configuration(); cfg.username = user; cfg.password = key
    api = SMSApi(ApiClient(cfg))
    msgs = []
    for s in shifts:
        dt = datetime.strptime(s['date'], '%Y-%m-%d').strftime('%A, %B %d, %Y')
        msgs.append(SmsMessage(
            source="python",
            body=f"Hi {name}, you have a {s['role']} shift on {dt} at {s['time']}.",
            to=phone
        ))
    api.sms_send_post(SmsMessageCollection(messages=msgs))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--issue-body', help='Full issue text')
    ap.add_argument('--name', help='Volunteer name')
    ap.add_argument('--phone', help='Optional phone')
    ap.add_argument('--shifts', nargs='*', help='One or more "Day Month DD, YYYY, HH:MM AM/PM – Role" entries')
    ap.add_argument('--notify-sms', action='store_true')
    args = ap.parse_args()

    if args.issue_body:
        name, phone, raw, notify_sms = parse_issue_body(args.issue_body)
    else:
        if not args.name or not args.shifts:
            sys.exit('❌ Missing required --name or --shifts')
        name = args.name.strip()
        phone = (args.phone or "").strip()
        raw = args.shifts
        notify_sms = args.notify_sms

    shifts = parse_shifts(raw)

    sched = load_schedule()

    entry = {
        'name': name,
        'phone': phone,
        'shifts': shifts
    }
    if notify_sms:
        entry['notify_sms'] = True

    sched.append(entry)
    save_schedule(sched)
    export_json(sched)

    if notify_sms:
        send_sms(name, phone, shifts)

    print(f"✅ Recorded {name} with {len(shifts)} shift(s).")

if __name__ == '__main__':
    main()
