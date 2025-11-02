# ⚡ Green Signal - Phishing Intelligence Agent

Welcome to the Green Signal challenge! Your mission is to build an agent that can analyze a batch of emails, correctly identify all phishing attempts, and submit your findings to the API to capture the flag.

This project consists of two main parts:

FastAPI Backend (main.py): A Python server that provides the challenge data (emails) and validates your agent's answers.

n8n Workflow (green-signal_workflow.json): A starter template for your agent. You will need to modify this workflow to solve the challenge.

### 🚀 Quick Start Guide

Get your agent running in 5 steps!

Step 1: Set Up Project & Dependencies

You'll need Python 3.12+ and the project dependencies.

# Clone the repository (if you have one) or just navigate to the folder
# cd green-signal

# Make sure you are using Python 3.12
python --version 
# [cite: .python-version]

# Install all required Python dependencies
pip install "fastapi[standard]>=0.120.0" "google-genai>=1.46.0" python-dotenv uvicorn
# [cite: pyproject.toml]


Step 2: Generate Challenge Data

The backend server needs a data file (data/emails.json) to serve the challenge. You can generate this using the provided script.

Create an environment file called .env in the same directory.

Add your Google AI API key to it (for the Gemini model):

GEMINI_API_KEY="YOUR_API_KEY_HERE"


Run the data generation script [cite: generate_messages_with_labels.py]:

# This script will call the Gemini API to create 20 sample emails
python generate_messages_with_labels.py


Move the data file to where the server expects it:

# Create the data directory
mkdir data

# Move the generated emails.json into the data/ folder
# (On Windows, use: move emails.json data\emails.json)
mv emails.json data/emails.json


Step 3: Start the Backend Server

Now you can run the FastAPI server, which will serve the challenge at http://localhost:3000.

# Run the server using uvicorn
uvicorn main:app --host 0.0.0.0 --port 3000


✅ You should see: Uvicorn running on http://0.0.0.0:3000

You can test it by visiting http://localhost:3000/health or http://localhost:3000/api/challenges/green-signal in your browser.

Step 4: Set Up n8n

Open your n8n instance (Cloud or local).

Create a new, blank workflow.

Click "Import from File" and select the green-signal_workflow.json file you have [cite: green-signal_workflow.json].

The starter workflow will load.

Step 5: Build Your Agent (The Core Challenge)

The starter workflow is intentionally incomplete. It fetches the emails but doesn't process them correctly.

Your Goal: Modify the workflow to correctly submit to the API.

The Problem: The "Fetch Emails Data" node gets a single item containing a list of emails. The "Submit to Validation API" node expects you to send a single list containing your classifications for all emails.

Your Solution:

You must loop or iterate over each email in the list.

For each email, use an LLM node (the default is OpenAI, but you can use any) to get a classification. The classification must be either "PHISHING" or "LEGITIMATE".

You also need to provide a reasoning_summary (a short string) for your choice.

After looping, you must aggregate all the individual results back into a single JSON list that matches the required format (see Submission Format below).

Finally, configure the "Submit to Validation API" node to send this single aggregated list in the body of a POST request.

📖 API & Submission Details

API Endpoints (main.py)

GET /health: Check if the API server is online.

GET /api/challenges/green-signal: Fetches the challenge data (a list of email objects).

POST /api/challenges/green-signal/submit: Submit your agent's answers. This is where you get the flag.

Submission Format

To get the flag, you must POST a single JSON list to the /api/challenges/green-signal/submit endpoint. The list must contain an object for every email from the challenge, in the following exact format [cite: main.py]:

[
  {
    "email": {
      "sender": "user@example.com",
      "subject": "Subject line 1",
      "body": "Email body text 1..."
    },
    "classification": "PHISHING",
    "reasoning_summary": "This contains a suspicious link and urgent language."
  },
  {
    "email": {
      "sender": "internal@company.com",
      "subject": "Subject line 2",
      "body": "Email body text 2..."
    },
    "classification": "LEGITIMATE",
    "reasoning_summary": "Looks like a standard internal memo."
  }
]


If your submission is correct (you've identified all phishing emails and the list length matches), the API will respond with the flag: FLAG{green_signal_secured} [cite: main.py].

Project Files

main.py: The FastAPI server.

generate_messages_with_labels.py: Helper script to create the data/emails.json challenge file using the Gemini API. This is for setup/organizers.

green-signal_workflow.json: The n8n starter workflow you need to edit.

pyproject.toml: Defines project dependencies.

.python-version: Specifies the required Python version.

.gitignore.txt: Standard gitignore file.