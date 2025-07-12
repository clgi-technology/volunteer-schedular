# parse_issue.py

import yaml
import os
import sys
import re

def exit_with_error(msg):
    print(f"❌ {msg}")
    sys.exit(1)

body = os.environ.get("ISSUE_BODY", "")
if not body:
    exit_with_error("ISSUE_BODY environment variable is empty")

# Extract YAML frontmatter from issue body (between --- and ---)
if body.startswith("---"):
    try:
        end = body.find("\n---", 3)
        if end == -1:
            exit_with_error("Could not find end of YAML frontmatter")
        yaml_block = body[3:end]
        form_data = yaml.safe_load(yaml_block)
    except Exception as e:
        exit_with_error(f"Failed to parse YAML frontmatter: {e}")
else:
    exit_with_error("Issue body does not start with YAML frontmatter")

name = form_data.get("name")
phone = form_data.get("phone")
shifts_raw = form_data.get("shifts")

if not name or not phone or not shifts_raw:
    exit_with_error("Missing required fields in form submission")

# Parse freeform shifts (textarea), one per line
shifts = []
for line in shifts_raw.splitlines():
    line = line.strip()
    if not line:
        continue
    match = re.match(r"(.+?),\s*(\d{1,2}:\d{2}\s*[APMapm]{2})\s*[–-]\s*(.+)", line)
    if not match:
        print(f"⚠️ Could not parse shift line: {line}")
        continue
    date_str, time_str, role = match.groups()
    shifts.append({
        "date": date_str.strip(),
        "time": time_str.strip(),
        "role": role.strip()
    })

if not shifts:
    exit_with_error("No valid shifts parsed")

# Append to volunteer_input.yaml
yaml_file = "volunteer_input.yaml"
try:
    with open(yaml_file, "r") as f:
        existing = yaml.safe_load(f) or []
except FileNotFoundError:
    existing = []

existing.append({
    "name": name,
    "phone": phone,
    "shifts": shifts
})

with open(yaml_file, "w") as f:
    yaml.safe_dump(existing, f, sort_keys=False)

print(f"✅ Submission parsed: {name} ({len(shifts)} shifts)")
