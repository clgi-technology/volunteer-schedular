import yaml
import os
import sys

body = os.environ.get("ISSUE_BODY", "")

def extract_field(label):
    marker = f"**{label}**:"
    if marker not in body:
        # For phone (optional), return empty string if missing
        if label == "Phone Number":
            return ""
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
    shifts = []
    for line in shifts_text.splitlines():
        line = line.strip()
        if not line:
            continue
        if '–' in line:
            date_time_part, role = line.split('–', 1)
            shifts.append({"datetime": date_time_part.strip(), "role": role.strip()})
        else:
            print(f"❌ Invalid shift format: {line}")
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

print(f"✅ Added {name} with {len(shifts)} shift(s). Phone: {'provided' if phone else 'not provided'}")

# Print GitHub Actions step outputs
print(f"::set-output name=name::{name}")
print(f"::set-output name=phone::{phone}")
