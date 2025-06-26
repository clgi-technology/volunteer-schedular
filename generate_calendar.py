import yaml
import json
from collections import defaultdict

SCHEDULE_FILE = 'volunteer_input.yaml'
CALENDAR_HTML = 'calendar.html'
JSON_FILE = 'volunteer_schedule.json'


def load_schedule():
    with open(SCHEDULE_FILE, 'r') as f:
        return yaml.safe_load(f) or []


def generate_json(schedule):
    """Flattens the schedule for JSON output."""
    entries = []
    for volunteer in schedule:
        name = volunteer['name']
        for shift in volunteer['shifts']:
            entries.append({
                'date': shift['date'],
                'time': shift['time'],
                'volunteer': name,
                'role': shift['role']
            })
    return entries


def generate_html(entries):
    roles = sorted(set(e['role'] for e in entries))
    roles_options = '\n'.join(f'<option value="{r}">{r}</option>' for r in roles)

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Volunteer Schedule Calendar</title>
<style>
  body {{ font-family: Arial, sans-serif; padding: 1em; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
  th {{ background-color: #f2f2f2; }}
  select {{ margin-bottom: 1em; padding: 0.5em; font-size: 1em; }}
</style>
</head>
<body>

<h1>Volunteer Schedule Calendar</h1>

<label for="role-filter">Filter by Role:</label>
<select id="role-filter" onchange="filterCalendar()">
  <option value="All">All</option>
  {roles_options}
</select>

<table>
  <thead>
    <tr>
      <th>Date</th>
      <th>Time</th>
      <th>Volunteer</th>
      <th>Role</th>
    </tr>
  </thead>
  <tbody id="calendar-body"></tbody>
</table>

<script>
let volunteerData = {json.dumps(entries)};

function renderCalendar(data) {{
  const tableBody = document.getElementById('calendar-body');
  tableBody.innerHTML = '';
  data.forEach(entry => {{
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${{entry.date}}</td>
      <td>${{entry.time}}</td>
      <td>${{entry.volunteer}}</td>
      <td>${{entry.role}}</td>
    `;
    tableBody.appendChild(row);
  }});
}}

function filterCalendar() {{
  const selectedRole = document.getElementById('role-filter').value;
  if (selectedRole === 'All') {{
    renderCalendar(volunteerData);
  }} else {{
    const filtered = volunteerData.filter(e => e.role === selectedRole);
    renderCalendar(filtered);
  }}
}}

window.onload = () => renderCalendar(volunteerData);
</script>

</body>
</html>
"""
    return html


def main():
    schedule = load_schedule()
    entries = generate_json(schedule)

    # Write JSON data file
    with open(JSON_FILE, 'w') as jf:
        json.dump(entries, jf, indent=2)

    # Write HTML file
    with open(CALENDAR_HTML, 'w') as hf:
        hf.write(generate_html(entries))


if __name__ == '__main__':
    main()
