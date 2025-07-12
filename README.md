🙌 Volunteer Scheduler (Fully Scripted Version)
This project enables volunteers to submit their availability for multiple roles, dates, and times using a static HTML form hosted on GitHub Pages. Submissions are processed automatically via GitHub Actions, stored in a YAML file, and rendered in an interactive calendar.

✨ Features
📋 Accepts structured input for multiple shifts per volunteer

🔁 Fully automated processing with GitHub Actions workflows

📅 Builds a filterable, interactive calendar from schedule data

🌐 Publishes calendar HTML and JSON data to GitHub Pages (docs/)

📧 Optional email notifications via SMTP using GitHub Secrets

🔐 Credentials managed securely with GitHub Secrets

📁 Project Structure
pgsql
Copy
Edit
.
├── .github/
│   ├── workflows/
│   │   ├── deploy-dashboard.yml
│   │   ├── process-all-volunteers.yml
│   │   ├── process_submission.yml
│   │   └── quality-gate.yml
│   └── ISSUE_TEMPLATE/
│       └── volunteer_submission.yml
├── admin_dashboard/
│   └── Dockerfile
├── docs/
│   ├── calendar.html
│   ├── index.html
│   └── volunteer_schedule.json
├── form/
│   └── index.html
├── templates/                     
│   └── calendar_template.html
├── admin_dashboard.py
├── volunteer_input.yaml
├── volunteer_schedule.py
├── generate_calendar.py
├── requirements.txt
├── requirements-dev.txt           
├── .env                          
└── README.md
🧠 How It Works
Volunteer fills out the static HTML form (form/index.html).

JavaScript sends a POST request to GitHub API to trigger the process_submission.yml workflow.

GitHub Actions workflows:

Append volunteer submission to volunteer_input.yaml

Send optional email reminders (if configured)

Generate interactive calendar HTML + JSON (docs/)

Publish calendar files to GitHub Pages via deploy-dashboard.yml

🛠️ Setup Instructions
1. Create GitHub Repository
Create a new public or private repository named volunteer-scheduler.

2. Add GitHub Secrets
Go to Settings > Secrets and variables > Actions > New repository secret and add:

Secret Name	Description
EMAIL_SENDER	Your SMTP email address
EMAIL_PASSWORD	Your SMTP email password or app key
GH_PAT	GitHub Personal Access Token

3. Enable GitHub Pages
Go to Settings > Pages and set the source to the docs/ folder.
Your site will be available at:

arduino
Copy
Edit
https://your-username.github.io/volunteer-scheduler
🌐 Static HTML Form
Location: form/index.html

Collects: name, phone number, and multiple shift availabilities

Sends data to GitHub API via JavaScript fetch() call to trigger workflows

🧪 Local Testing
bash
Copy
Edit
# Set environment variables for testing
export EMAIL_SENDER="your_email@example.com"
export EMAIL_PASSWORD="your_email_password"

# Run volunteer scheduling script manually
python volunteer_schedule.py --name "Alice" --phone "+1234567890" --shifts '[{"date": "2025-07-15", "time": "10:00", "role": "Greeter"}]'

# Generate calendar HTML and JSON files
python generate_calendar.py
🛠️ Optional Enhancements
Send calendar invites (ICS) via email

Web dashboard to manage volunteers directly

Export or sync calendar to Google Calendar or Outlook

📘 License
This project is licensed under the MIT License.

🙏 Acknowledgments
GitHub Actions

GitHub Pages

All our amazing volunteers
