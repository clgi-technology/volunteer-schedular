# parse_issue.py

import yaml
import os
import sys
import re

def exit_with_error(message):
    print(f"❌ {message}")
    sys.exit(1)

# Step 1: Extract issue form values from GitHub Actions environment
name = os.environ.get("INPUT_NAME", "").strip()
phone = os.environ.get("INPUT_PHONE", "").strip()
shifts_text = os.environ.get("INPUT_SHIFTS", "").strip()

if not name:
    exit_with_error("Missing Full Name")
if not phone:
    exit_with_error("Missing Phone Number")
if not shifts_text:
    exit_with_error("Missing Shifts")

# Step 2: Parse each shift line into a dictionary
shifts = []
for line in shifts_text.splitlines():
    line = line.strip()
    if not line:
        continue
    match = re.match(r"(.+?),\s*(\d{1,2}:\d{2}\s*[APMapm]{2})\s*[–-]\s*(.+)", line)
    if not match:
        print(f"⚠️ Could not parse line: {line}")
        continue
    date_str, time_str, role = match.groups()
    shifts.append({
        "date": date_str.strip(),
        "time": time_str.strip(),
        "role": role.strip()
    })

if not shifts:
    exit_with_error("No valid shifts parsed.")

# Step 3: Load existing YAML and append
yaml_file = "volunteer_input.yaml"
try:
    with open(yaml_file, "r") as f:
        data = yaml.safe_load(f) or []
except FileNotFoundError:
    data = []

data.append({
    "name": name,
    "phone": phone,
    "shifts": shifts
})

# Step 4: Save back to YAML
with open(yaml_file, "w") as f:
    yaml.safe_dump(data, f, sort_keys=False)

print(f"✅ Added {name} with {len(shifts)} shift(s).")
