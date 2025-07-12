
---

## 10. `admin_dashboard.py`

```python
import yaml
import os
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

SCHEDULE_FILE = 'volunteer_input.yaml'


def load_schedule():
    if os.path.exists(SCHEDULE_FILE):
        with open(SCHEDULE_FILE, 'r') as f:
            return yaml.safe_load(f) or []
    return []


def save_schedule(schedule):
    with open(SCHEDULE_FILE, 'w') as f:
        yaml.safe_dump(schedule, f)


@app.route('/')
def index():
    schedule = load_schedule()
    return render_template_string('''
    <html>
    <head><title>Volunteer Admin Dashboard</title></head>
    <body>
      <h1>Volunteer Admin Dashboard</h1>
      <table border="1" cellpadding="8" cellspacing="0">
        <thead>
          <tr>
            <th>Name</th><th>Phone</th><th>Shifts</th><th>Actions</th>
          </tr>
        </thead>
        <tbody>
        {% for vol in schedule %}
          <tr>
            <td>{{ vol.name }}</td>
            <td>{{ vol.phone }}</td>
            <td>
              <ul>
                {% for shift in vol.shifts %}
                <li>{{ shift.date }} {{ shift.time }} - {{ shift.role }}</li>
                {% endfor %}
              </ul>
            </td>
            <td>
              <form method="post" action="{{ url_for('delete_volunteer') }}">
                <input type="hidden" name="name" value="{{ vol.name }}">
                <input type="hidden" name="phone" value="{{ vol.phone }}">
                <button type="submit" onclick="return confirm('Delete volunteer {{ vol.name }}?')">Delete</button>
              </form>
            </td>
          </tr>
        {% endfor %}
        </tbody>
      </table>
    </body>
    </html>
    ''', schedule=schedule)


@app.route('/delete', methods=['POST'])
def delete_volunteer():
    name = request.form.get('name')
    phone = request.form.get('phone')

    schedule = load_schedule()
    schedule = [v for v in schedule if not (v.get('name') == name and v.get('phone') == phone)]
    save_schedule(schedule)

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, port=8080)
