# GhostAI_DLP 🕵️‍♂️🔐

A developer-first **Data Loss Prevention (DLP)** tool for detecting risky patterns in code.  
Built with Flask + Python CLI.

---

## 📌 Roadmap
- ✅ CLI-based detection engine (secrets, blobs, entropy)
- ⏳ Pre-commit + GitHub CI integration
- ⏳ AI post-processing filter to reduce false positives
- ⏳ SaaS dashboard for org-wide reporting

---

## ⚡ CLI Usage (Important!)

The CLI lives under `src/cli/`.  
Because this project uses packages (`src/`), you must run the CLI with Python’s **module flag** (`-m`) from the **project root**.

### 🔹 Interactive Mode
Run:

```bash
python3 -m src.cli.cli
Example session:

java
Copy code
Enter a code prompt (or type 'exit' to quit): // detector test: obvious AWS creds (FAKE ONLY)
Enter the next line (or press Enter to submit): const AWS = require('aws-sdk');
...

{
    "score": 0.98,
    "severity": "high",
    "breakdown": [
        { "name": "secrets", "score": 0.9, "reasons": ["aws_access_key detected"] },
        { "name": "keywords", "score": 0.6, "reasons": ["keyword_secret detected"] }
    ]
}
The CLI sends the snippet to the Flask API and prints a JSON result with:

score

severity

breakdown of detectors triggered

🛠️ Setup & Running Flask
1. Prerequisites
Make sure you have Python 3.x installed:

bash
Copy code
python3 --version
If you don’t have Python installed, download it from python.org/downloads.

Also ensure pip (Python’s package manager) is installed:

bash
Copy code
pip --version
2. Install Virtual Environment
bash
Copy code
pip install virtualenv
3. Create a Virtual Environment
bash
Copy code
python3 -m venv .venv
This will create a folder named .venv/ that contains your isolated environment.

4. Activate the Virtual Environment
macOS / Linux

bash
Copy code
source .venv/bin/activate
Windows (PowerShell)

powershell
Copy code
.venv\Scripts\activate
When activated, you’ll see (.venv) in your terminal prompt.
To deactivate at any time:

bash
Copy code
deactivate
5. Install Dependencies
With the environment activated, install dependencies:

bash
Copy code
pip install -r requirements.txt
6. Run the Flask API
From the project root:

bash
Copy code
flask --app src/api/routers/risk run
Flask will run at:

👉 http://127.0.0.1:5000

7. Deactivate the Virtual Environment
When finished:

bash
Copy code
deactivate
🐛 Troubleshooting
Error: ModuleNotFoundError: No module named 'src'
✅ Fix: Always run with -m:

bash
Copy code
python3 -m src.cli.cli
Warning: NotOpenSSLWarning from urllib3
⚠️ This is non-blocking — safe to ignore in development.

