name: Process Submission

on:
  workflow_dispatch:
  repository_dispatch:
  issues:
    types: [opened]

permissions:
  contents: write

jobs:
  process:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pyyaml clicksend-client

      - name: Run parser
        id: parse
        env:
          ISSUE_BODY: ${{ github.event.issue.body }}
        run: python parse_issue.py

      - name: Commit updated volunteer_input.yaml
        run: |
          git config user.name "github-actions"
          git config user.email "actions@github.com"
          git add volunteer_input.yaml
          git commit -m "Append new volunteer submission" || echo "No changes to commit"
          git push

      - name: Send SMS Notification
        if: steps.parse.outputs.phone != ''
        env:
          CLICKSEND_USERNAME: ${{ secrets.CLICKSEND_USERNAME }}
          CLICKSEND_API_KEY: ${{ secrets.CLICKSEND_API_KEY }}
        run: |
          python send_sms.py "${{ steps.parse.outputs.phone }}" "${{ steps.parse.outputs.name }}"

      - name: Trigger Process All Volunteers workflow
        uses: peter-evans/repository-dispatch@v3
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          repository: clgi-technology/volunteer-schedular
          event-type: process-all-volunteers
