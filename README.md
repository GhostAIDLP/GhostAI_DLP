# GhostAI_DLP

Got it 👍 — here’s the full documentation in one complete README.md file (all in Markdown, nothing skipped):

# Python Virtual Environment Setup & Running Flask

This guide explains how to set up a Python virtual environment, activate it, install Flask, run a Flask application, and use CLI tools inside the environment.

---

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