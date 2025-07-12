import yaml
import json
import os
from datetime import datetime

SCHEDULE_FILE = 'volunteer_input.yaml'
CALENDAR_HTML = 'docs/calendar.html'
JSON_FILE = 'docs/volunteer_schedule.json'


def load_schedule():
    if not os.path.exists(SCHEDULE_FILE):
        return []
    with open(SCHEDULE_FILE, 'r') as f:
        return yaml.safe_load(f) or []


def generate_json(schedule):
    """Flattens the schedule for JSON output and sorts entries chronologically."""
    entries = []
    for volunteer in schedule:
        name = volunteer.get('name', 'Unknown')
        for shift in volunteer.get('shifts', []):
            entries.append({
                'date': shift['date'],
                'time': shift['time'],
                'volunteer': name,
                'role': shift['role']
            })
    # Sort by date and time
    entries.sort(key=lambda e: (e['date'], e['time']))
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
  body {{ font-family: Arial, sans-serif; margin: 2rem; background: #f9f9f9; color: #333; }}
  h1 {{ text-align: center; margin-bottom: 1rem; }}
  label {{ font-weight: bold; }}
  select {{ margin: 1rem 0 2rem 0; padding: 0.5rem; font-size: 1rem; }}
  table {{ border-collapse: collapse; width: 100%; background: white; box-shadow: 0 2px 6px rgba(0,0,0,0.1); }}
  th, td {{ border: 1px solid #ddd; padding: 0.75rem 1rem; text-align: left; }}
  th {{ background-color: #4CAF50; color: white; }}
  tbody tr:hover {{ background-color: #f1f1f1; }}
  @media (max-width: 600px) {{
    table, thead, tbody, th, td, tr {{ display: block; }}
    thead tr {{ display: none; }}
    tbody tr {{ margin-bottom: 1rem; border: 1px solid #ddd; border-radius: 4px; padding: 0.5rem; }}
    tbody td {{ border: none; padding: 0.5rem 0; position: relative; padding-left: 50%; }}
    tbody td::before {{
      position: absolute;
      top: 50%;
      left: 10px;
      width: 45%;
      padding-right: 10px;
      white-space: nowrap;
      font-weight: bold;
      transform: translateY(-50%);
    }}
    tbody td:nth-of-type(1)::before {{ content: "Date"; }}
    tbody td:nth-of-type(2)::before {{ content: "Time"; }}
    tbody td:nth-of-type(3)::before {{ content: "Volunteer"; }}
    tbody td:nth-of-type(4)::before {{ content: "Role"; }}
  }}
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
  let volunteerData = {json.dumps(entries, indent=2)};

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

  window.onload = () => {{
    renderCalendar(volunteerData);
  }};
</script>

</body>
</html>
"""
    return html


def main():
    schedule = load_schedule()
    entries = generate_json(schedule)

    # Ensure docs folder exists
    os.makedirs('docs', exist_ok=True)

    with open(JSON_FILE, 'w') as jf:
        json.dump(entries, jf, indent=2)

    with open(CALENDAR_HTML, 'w') as hf:
        hf.write(generate_html(entries))


if __name__ == '__main__':
    main()
