import yaml
import os
import sys
from datetime import datetime

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
    if "**What shifts are you available for?**:" not in body:
        print("❌ Missing field: What shifts are you available for?")
        sys.exit(1)
    shifts_text = body.split("**What shifts are you available for?**:")[1].strip()
    # Each shift on its own line:
    lines = [line.strip() for line in shifts_text.splitlines() if line.strip()]

    shifts = []
    for line in lines:
        # Example line: Monday July 22, 2025, 6:00 PM – Usher
        try:
            # Split on the "–" dash character (note: this is an en dash, not a hyphen)
            date_time_part, role = line.split("–")
            role = role.strip()

            # date_time_part = "Monday July 22, 2025, 6:00 PM"
            # Remove weekday by splitting on first space:
            # Or just parse entire date_time_part with datetime.strptime (ignore weekday)
            
            # Remove weekday (first word)
            parts = date_time_part.strip().split(' ', 1)
            if len(parts) < 2:
                raise ValueError("Date/time format incorrect")
            date_time_str = parts[1].strip()

            # Parse date_time_str like "July 22, 2025, 6:00 PM"
            dt = datetime.strptime(date_time_str, "%B %d, %Y, %I:%M %p")

            # Format date/time as ISO strings
            iso_date = dt.strftime("%Y-%m-%d")
            iso_time = dt.strftime("%H:%M")

            shifts.append({
                "date": iso_date,
                "time": iso_time,
                "role": role
            })
        except Exception as e:
            print(f"❌ Failed to parse shift line: '{line}' - {e}")
            sys.exit(1)
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
