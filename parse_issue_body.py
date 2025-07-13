import sys
import re
import json

def extract_sections(issue_body: str):
    name = ""
    phone = ""
    shifts = []

    current_section = None
    for line in issue_body.splitlines():
        stripped = line.strip()

        if stripped.startswith("### "):
            heading = stripped[4:].strip().lower()
            if "full name" in heading:
                current_section = "name"
            elif "phone" in heading:
                current_section = "phone"
            elif "shifts" in heading:
                current_section = "shifts"
            else:
                current_section = None
            continue

        if current_section == "name" and not name and stripped:
            name = stripped

        elif current_section == "phone" and not phone and stripped:
            phone = stripped

        elif current_section == "shifts" and stripped:
            if stripped.startswith("- "):  # e.g. "- Monday July 22..."
                shifts.append(stripped[2:].strip())
            else:
                shifts.append(stripped)

    return {
        "name": name.strip(),
        "phone": phone.strip(),
        "raw_shifts": shifts
    }


if __name__ == "__main__":
    issue_body = sys.stdin.read()
    result = extract_sections(issue_body)

    if not result["name"] or not result["raw_shifts"]:
        print("❌ Error: Missing required 'name' or 'shifts'", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, indent=2))
