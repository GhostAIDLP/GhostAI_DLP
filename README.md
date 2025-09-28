# GhostAI_DLP

Got it 👍 — here’s the full documentation in one complete README.md file (all in Markdown, nothing skipped):

## Roadmap
- ✅ CLI-based detection engine (secrets, blobs, entropy)
- ⏳ Pre-commit + GitHub CI integration
- ⏳ AI post-processing filter to reduce false positives
- ⏳ SaaS dashboard for org-wide reporting


# Python Virtual Environment Setup & Running Flask

This guide explains how to set up a Python virtual environment, activate it, install Flask, run a Flask application, and use CLI tools inside the environment.

---
CLI Usage (important!)

The CLI lives under src/cli/.
Because this project uses packages (src/), you must run the CLI with Python’s module flag (-m) from the project root.

Interactive Mode

For pasting multiline code and analyzing it:

python3 -m src.cli.cli


Example:

Enter a code prompt (or type 'exit' to quit): // detector test: obvious AWS creds (FAKE ONLY)
Enter the next line (or press Enter to submit): const AWS = require('aws-sdk');
...


This will send the snippet to the Flask API and print the JSON result (score, severity, breakdown, etc.).

Automation Mode (coming soon)

Automation tooling (src/cli/automate.py) is being added, but for now interactive CLI is the primary entrypoint.
## 1. Prerequisites

Make sure you have **Python 3.x** installed. Check with:

```bash
python3 --version

If you don’t have Python installed, download it from python.org/downloads
.

Also ensure pip (Python’s package manager) is installed:

pip --version

2. Install Virtual Environment

Install virtualenv if it’s not already available:

pip install virtualenv

3. Create a Virtual Environment

Navigate to your project directory and run:

python3 -m venv venv

This will create a folder named venv/ that contains your isolated environment.

4. Activate the Virtual Environment

Linux / macOS:

source .venv/bin/activate

Windows (PowerShell):

.venv\Scripts\activate

When activated, you’ll see (venv) in your terminal prompt.

To deactivate at any time:

deactivate

5. Install Flask

With the environment activated, install Flask:

- pip install flask

Confirm installation:

- pip show flask

Install all the needed dependencies using requirements.txt:

- pip install -r requirements.txt

Run the application from root folder:

- flask --app src/api/routers/risk run 

Flask will run on:

- http://127.0.0.1:5000

Visit this URL in your browser to see your app.

7. Using Flask CLI

Flask comes with a built-in command-line tool. With your virtual environment activated, you can access it directly.

Check available commands:

flask --help

To run your app with the CLI, set the FLASK_APP environment variable:

Linux / macOS:

export FLASK_APP=app.py
flask run

Windows (PowerShell):

$env:FLASK_APP = "app.py"
flask run

This will start the Flask server the same way as running python app.py.

8. Deactivate the Virtual Environment

When finished, deactivate the environment:

deactivate
