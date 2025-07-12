# parse_issue.py

import yaml
import json
import os
import sys

body = os.environ.get("ISSUE_BODY", "")

def extract_field(label):
    marker = f"**{label}**:"
    if marker not in body:
        print(f"❌ Missing field: {label}")
        sys.exit(1)
    start = body.find(marker) + len(marker)
    end = body.find('\n', start)
    if end == -1:
        end = len(body)
    return body[start:end].strip()

try:
    name = extract_field("Full Name")
    phone = extract_field("Phone Number")
    if "**Shift Availability**:" not in body:
        print("❌ Missing field: Shift Availability")
        sys.exit(1)
    shifts_json = body.split("**Shift Availability**:")[1].strip()
    shifts = json.loads(shifts_json)
except Exception as e:
    print(f"❌ Error parsing issue body: {e}")
    sys.exit(1)

try:
    with open("volunteer_input.yaml", "r") as f:
        data = yaml.safe_load(f) or []
except FileNotFoundError:
    data = []

data.append({"name": name, "phone": phone, "shifts": shifts})

with open("volunteer_input.yaml", "w") as f:
    yaml.dump(data, f, sort_keys=False)

print(f"✅ Added {name} with {len(shifts)} shift(s).")
