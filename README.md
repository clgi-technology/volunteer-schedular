# 🙌 Volunteer Schedule Automation

(with Tally + Zapier + GitHub Actions + ClickSend + GitHub Pages)

This project lets volunteers submit their availability for multiple roles, dates, and times using a form (via Tally.so).

Submissions are automatically:

Sent via Zapier to GitHub Actions

Added to the volunteer schedule (volunteer_input.yaml)

Used to send SMS reminders via ClickSend

Rendered in an interactive HTML calendar with role filtering and published on GitHub Pages

# ✨ Features
📋 Accepts structured input for multiple shifts per volunteer

🔁 Fully automated using GitHub Actions

💬 Sends personalized SMS reminders using ClickSend API

📅 Builds a filterable, interactive calendar from schedule data

🌐 Publishes calendar and JSON data to GitHub Pages

🔐 Credentials managed securely with GitHub Secrets

# 📁 Project Structure

```
.
├── .github/
│   └── workflows/
│       └── send_schedule.yml       # GitHub Action workflow
├── docs/
│   ├── calendar.html               # Auto-generated interactive calendar
│   └── volunteer_schedule.json    # JSON data for calendar filtering
├── volunteer_schedule.py           # Processes inputs + sends SMS
├── generate_calendar.py            # Builds calendar.html + JSON from YAML
├── volunteer_input.yaml            # Full volunteer schedule (append-only)
├── requirements.txt                # Python dependencies
└── README.md
```

# 🧾 How the System Works
Volunteer fills out a Tally form

Name, phone number

Multiple shifts: date, time, role

Zapier receives submission

Parses shifts into JSON

Sends GitHub API request to trigger the workflow

GitHub Action:

Accepts data via workflow_dispatch

Appends shifts to volunteer_input.yaml

Sends SMS reminders via ClickSend

Generates interactive calendar HTML + JSON

Publishes calendar files to GitHub Pages

# 📤 Example Tally Input (via Form)

```
Name: Alice Johnson  
Phone: +1234567890  
Shifts:  
2025-07-07 18:00 Usher  
2025-07-09 09:00 Greeter
```

Zapier converts this to:

```
"shifts": [
  { "date": "2025-07-07", "time": "18:00", "role": "Usher" },
  { "date": "2025-07-09", "time": "09:00", "role": "Greeter" }
]

```

💬 Example SMS
```
Hi Alice Johnson! You're scheduled to Usher on Monday, July 7 at 6:00 PM. Thank you for serving!
```

# 🗓️ Interactive Calendar Output
Published at:
👉 https://your-username.github.io/volunteer-scheduler

Features:

Displays all upcoming volunteer shifts

Dropdown filter to view shifts by Role/Position (e.g., Usher, Greeter)

Dynamic updates without page reload

Mobile-friendly and accessible layout

Date	Time	Volunteer	Role
2025-07-07	18:00	Alice Johnson	Usher
2025-07-09	09:00	Alice Johnson	Greeter

# 🔧 Setup Instructions
1. ☁️ Create Your GitHub Repository
Create a new public or private repository named volunteer-scheduler.

2. 🔐 Add GitHub Secrets
Go to Repo → Settings → Secrets → Actions → New repository secret, and add:

Secret Name	Description
```
CLICKSEND_USERNAME	Your ClickSend email login
CLICKSEND_API_KEY	Your ClickSend API key
```
3. 📄 Define the GitHub Action
```
File: .github/workflows/send_schedule.yml
```
```
name: Process Volunteer Submission

on:
  workflow_dispatch:
    inputs:
      name:
        required: true
      phone:
        required: true
      shifts:
        required: true  # JSON string

jobs:
  handle_submission:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run SMS Scheduler
        env:
          CLICKSEND_USERNAME: ${{ secrets.CLICKSEND_USERNAME }}
          CLICKSEND_API_KEY: ${{ secrets.CLICKSEND_API_KEY }}
        run: |
          python volunteer_schedule.py \
            --name "${{ github.event.inputs.name }}" \
            --phone "${{ github.event.inputs.phone }}" \
            --shifts '${{ github.event.inputs.shifts }}'

      - name: Generate Calendar
        run: python generate_calendar.py

      - name: Publish Calendar
        run: |
          mkdir -p docs
          cp calendar.html docs/
          cp volunteer_schedule.json docs/
```

4. 🧠 Zapier Setup
Trigger: New Tally form submission

Zapier Step: Code or Formatter to convert shifts text into JSON list

Action: POST to GitHub REST API

Zapier Webhook POST:
```
URL:
https://api.github.com/repos/your-username/volunteer-scheduler/actions/workflows/send_schedule.yml/dispatches
```
Headers:
```
{
  "Authorization": "Bearer YOUR_GITHUB_PAT",
  "Accept": "application/vnd.github.v3+json"
}
Body:

```
```
{
  "ref": "main",
  "inputs": {
    "name": "Alice Johnson",
    "phone": "+1234567890",
    "shifts": "[{\"date\":\"2025-07-07\", \"time\":\"18:00\", \"role\":\"Usher\"}, {\"date\":\"2025-07-09\", \"time\":\"09:00\", \"role\":\"Greeter\"}]"
  }
}
```

🔐 Use a GitHub PAT with workflow scope and store it securely in Zapier.

5. 🌐 Enable GitHub Pages
Go to: Repo Settings → Pages

Source: docs/ folder
```
URL: https://your-username.github.io/volunteer-scheduler
```

# 🧪 Local Testing
```
# Set environment variables for testing
export CLICKSEND_USERNAME="your_email@example.com"
export CLICKSEND_API_KEY="your_api_key"

# Run scripts manually
python volunteer_schedule.py --name "Alice" --phone "+1234567890" --shifts '[{"date": "2025-07-07", "time": "18:00", "role": "Usher"}]'
python generate_calendar.py
```

# ✅ Requirements (requirements.txt)
```
clicksend-client
PyYAML
```

# 🛠️ Future Improvements
Send calendar invites (ICS) via email

Web dashboard to manage volunteers directly

Export or sync calendar to Google Calendar or Outlook

📘 License
MIT License

# 🙏 Acknowledgments
ClickSend API

Tally.so

Zapier

All our amazing volunteers Awesome! Here's how we'll proceed with Option 1: a fully GitHub-native volunteer scheduler using a static HTML form, GitHub Actions, and GitHub Secrets.
⸻
✅ Step-by-Step Build Plan
1. 🔐 GitHub Secrets Setup
You'll need to add the following secrets to your repository:
Secret NameDescription
CLICKSEND_USERNAMEYour ClickSend email login
CLICKSEND_API_KEYYour ClickSend API key
GH_PATGitHub Personal Access Token (for form submission)
⸻
2. 🧾 GitHub Action: process_submission.yml
This action will:
Accept manual or API-triggered submissions
Append to volunteer_input.yaml
Send SMS via ClickSend
Generate and publish the calendar
✅ I’ll generate this file for you shortly.
⸻
3. 🌐 Static HTML Form (form/index.html)
This form will:
Collect name, phone, and shifts
Use JavaScript to call the GitHub API and trigger the workflow
Require the GH_PAT to be injected securely (e.g., via Netlify environment variable or GitHub Pages JS obfuscation)
✅ I’ll generate this file for you too.
⸻
4. 🐍 Python Scripts
volunteer_schedule.py: Appends to YAML and sends SMS
generate_calendar.py: Builds calendar HTML + JSON
✅ You already have these, but I can help refactor them to support this new flow if needed.
⸻
✅ Next Step
I’ll now generate the following files:
.github/workflows/process_submission.yml
form/index.html
Let’s start with that.

✅ The following files have been generated for your GitHub-native volunteer scheduler:
⸻
📄 .github/workflows/process_submission.yml
This GitHub Action:
Triggers manually or via API
Uses secrets for ClickSend
Runs your Python scripts to append data, send SMS, and regenerate the calendar
⸻
🌐 form/index.html
A static HTML form that:
Collects volunteer name, phone, and shifts
Sends a POST request to the GitHub API to trigger the workflow
Requires a GitHub PAT (to be injected securely)
⸻
🔐 Next Steps
Replace placeholders:
In form/index.html, update:
"your-username" → your GitHub username
"YOUR_GITHUB_PAT" → inject securely via environment variable or obfuscation
Add GitHub Secrets:
CLICKSEND_USERNAME
CLICKSEND_API_KEY
GH_PAT (optional if not using from frontend)
Deploy the form:
Place form/index.html in your docs/ folder to serve it via GitHub Pages
Or host it on Netlify/Vercel with environment variable injec


