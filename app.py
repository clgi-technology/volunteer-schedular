import yaml
import os
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)
SCHEDULE_FILE = 'volunteer_input.yaml'

def load_schedule():
    if os.path.exists(SCHEDULE_FILE):
        try:
            with open(SCHEDULE_FILE, 'r') as f:
                return yaml.safe_load(f) or []
        except yaml.YAMLError:
            return []
    return []

def save_schedule(schedule):
    with open(SCHEDULE_FILE, 'w') as f:
        yaml.safe_dump(schedule, f, sort_keys=False)

@app.route('/')
def index():
    schedule = load_schedule()
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Volunteer Admin Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 2em; background-color: #f9f9f9; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ccc; padding: 10px; text-align: left; }
            th { background-color: #28a745; color: white; }
            tr:nth-child(even) { background-color: #f2f2f2; }
            h1 { color: #333; }
            form { display: inline; }
        </style>
    </head>
    <body>
        <h1>Volunteer Admin Dashboard</h1>
        <table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Phone</th>
                    <th>Notify SMS</th>
                    <th>Shifts</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for vol in schedule %}
                <tr>
                    <td>{{ vol.get('name', '') }}</td>
                    <td>{{ vol.get('phone', '') }}</td>
                    <td>{{ vol.get('notify_sms', False) }}</td>
                    <td>
                        <ul>
                        {% for shift in vol.get('shifts', []) %}
                            <li>{{ shift.date }} {{ shift.time }} - {{ shift.role }}</li>
                        {% endfor %}
                        </ul>
                    </td>
                    <td>
                        <form method="post" action="{{ url_for('delete_volunteer') }}">
                            <input type="hidden" name="name" value="{{ vol.get('name', '') }}">
                            <input type="hidden" name="phone" value="{{ vol.get('phone', '') }}">
                            <button type="submit" onclick="return confirm('Are you sure you want to delete {{ vol.get('name', '') }}?')">
                                Delete
                            </button>
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

    updated = [v for v in schedule if not (v.get('name') == name and v.get('phone') == phone)]
    save_schedule(updated)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=8080)
