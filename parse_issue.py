import os
import json
import yaml
from datetime import datetime
from pathlib import Path

ISSUE_BODY = os.environ.get("ISSUE_BODY", "")
YAML_FILE = "volunteer_input.yaml"
JSON_FILE = "docs/volunteer_schedule.json"

# --- Robust Markdown Field Parser ---
def parse_fields_from_issue(body):
    fields = {}
    current_field = None
    for line in body.splitlines():
        line = line.strip()
        if line.startswith("### "):
            current_field = line[4:].strip()
            fields[current_field] = ""
        elif current_field and line and not line.startswith("_"):
            if fields[current_field]:
                fields[current_field] += " " + line
            else:
                fields[current_field] = line
    return fields

# --- Parse Shifts from Natural Text ---
def parse_shifts(text):
    shifts = []
    lines = text.splitlines()
    for line in lines:
        if not line.strip():
            continue
        try:
            # Basic example: "Friday August 12, 2025, 8:00 PM"
            dt = datetime.strptime(line.strip(), "%A %B %d, %Y, %I:%M %p")
            shift = {
                "date": dt.strftime("%Y-%m-%d"),
                "time": dt.strftime("%H:%M"),
                "role": "Volunteer"  # Default role
            }
            shifts.append(shift)
        except Exception as e:
            print(f"⚠️ Failed to parse shift line: '{line}': {e}")
    return shifts

# --- Main Execution ---
def main():
    fields = parse_fields_from_issue(ISSUE_BODY)

    required_fields = ["Full Name", "What shifts are you available for?"]
    for field in required_fields:
        if not fields.get(field):
            print(f"❌ Missing field: {field}")
            exit(1)

    name = fields["Full Name"]
    phone = fields.get("Phone Number", "")
    shift_text = fields["What shifts are you available for?"]
    shifts = parse_shifts(shift_text)

    if not shifts:
        print("❌ No valid shifts parsed.")
        exit(1)

    # Append to volunteer_input.yaml
    yaml_entry = {
        "name": name,
        "phone": phone,
        "shifts": shifts
    }

    if Path(YAML_FILE).exists():
        with open(YAML_FILE, "r") as f:
            yaml_data = yaml.safe_load(f) or []
    else:
        yaml_data = []

    yaml_data.append(yaml_entry)

    with open(YAML_FILE, "w") as f:
        yaml.safe_dump(yaml_data, f, sort_keys=False)

    print(f"✅ Saved to {YAML_FILE}")

    # Build docs/volunteer_schedule.json
    flat_list = []
    for entry in yaml_data:
        for shift in entry["shifts"]:
            flat_list.append({
                "date": shift["date"],
                "time": shift["time"],
                "volunteer": entry["name"],
                "role": shift.get("role", "Volunteer")
            })

    os.makedirs(os.path.dirname(JSON_FILE), exist_ok=True)
    with open(JSON_FILE, "w") as f:
        json.dump(flat_list, f, indent=2)

    print(f"✅ Updated {JSON_FILE} with {len(flat_list)} entries.")

if __name__ == "__main__":
    main()
