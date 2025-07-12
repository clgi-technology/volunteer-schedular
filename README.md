# 🙌 Volunteer Scheduler (Fully Scripted Version)

This project enables volunteers to submit their availability for multiple roles, dates, and times using a **static HTML form** hosted on GitHub Pages. Submissions are processed via **GitHub Actions**, stored in a YAML file, and rendered in an interactive calendar.

---

## ✨ Features

- 📋 Accepts structured input for multiple shifts per volunteer
- 🔁 Fully automated using GitHub Actions
- 📅 Builds a filterable, interactive calendar from schedule data
- 🌐 Publishes calendar and JSON data to GitHub Pages
- 📧 Optional email notifications via SMTP
- 🔐 Credentials managed securely with GitHub Secrets

---

## 📁 Project Structure

```

.
├── .github/
│   ├── workflows/
│       ├── deploy-dashboard.yml
│       ├── process-all-volunteers.yml
│       ├── process_submission.yml
│       └── quality-gate.yml
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
├── templates/                     # optional but useful for Flask templates
│   └── calendar_template.html
├── admin_dashboard.py
├── volunteer_input.yaml
├── volunteer_schedule.py
├── generate_calendar.py
├── requirements.txt
├── requirements-dev.txt           # optional
├── .env                          # optional for local environment variables
└── README.md




```
---

## 🧠 How It Works

1. Volunteer fills out the static HTML form.
2. JavaScript sends a POST request to GitHub API to trigger a workflow.
3. GitHub Action:
   - Appends shifts to `volunteer_input.yaml`
   - Sends optional email reminders
   - Generates interactive calendar HTML + JSON
   - Publishes calendar files to GitHub Pages

---

## 🛠️ Setup Instructions

### 1. Create GitHub Repository

Create a new public or private repository named `volunteer-scheduler`.

### 2. Add GitHub Secrets

Go to **Repo → Settings → Secrets → Actions → New repository secret**, and add:

| Secret Name       | Description                        |
|-------------------|------------------------------------|
| EMAIL_SENDER      | Your SMTP email address            |
| EMAIL_PASSWORD    | Your SMTP email password or app key|
| GH_PAT            | GitHub Personal Access Token       |

### 3. Enable GitHub Pages

- Go to: **Repo Settings → Pages**
- Source: `docs/` folder
- URL: `https://your-username.github.io/volunteer-scheduler`

---

## 🌐 Static HTML Form

- Located at `form/index.html`
- Collects name, phone, and shifts
- Sends data to GitHub API using `fetch()`

---

## 🧪 Local Testing

```
bash
# Set environment variables for testing
export EMAIL_SENDER="your_email@example.com"
export EMAIL_PASSWORD="your_email_password"

# Run scripts manually
python volunteer_schedule.py --name "Alice" --phone "+1234567890" --shifts '[{"date": "2025-07-15", "time": "10:00", "role": "Greeter"}]'
python generate_calendar.py

```
⸻
## 🛠️ Optional Enhancements
• Send calendar invites (ICS) via email
• Web dashboard to manage volunteers directly
• Export or sync calendar to Google Calendar or Outlook
⸻
## 📘 License
MIT License
⸻
## 🙏 Acknowledgments
• GitHub Actions
• GitHub Pages
• All our amazing volunteers

