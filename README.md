

# 🧾 Resume Analyzer — AI-Powered Resume Parser

Automatically extract, analyze, and organize candidate resumes from Gmail into a structured **Google Sheet** using **AI-powered insights** (powered by OpenAI).

It uses **Gmail API**, **OpenAI**, and **Google Sheets API** to automate resume screening for HR teams.

---

<img width="521" alt="Screenshot 2025-05-05 at 6 14 32 PM" src="https://github.com/user-attachments/assets/39db765d-d9e6-4d4b-8754-5ba90aba75e3" />

## Features

- Triggers on **new unread emails** in Gmail
- Automatically downloads **PDF attachments** (resumes)
- Uses **OpenAI GPT** models to:
  - Extract personal info (name, email, LinkedIn)
  - Identify key skills
  - Generate a concise summary (under 250 characters)
  - Score the resume out of 100
  - Highlight top 5 standout achievements
-  Saves all data into a **Google Sheet**
-  *(Optional)* Sends a formatted **HTML summary email** to recruiters

Perfect for HR teams looking to **screen applicants faster and smarter** using automation.

---

##  Requirements

Before running this script, make sure you have:

| Tool | Description |
|------|-------------|
| Python 3.9+ | Required to run the script |
| OpenAI API Key | Get one at [platform.openai.com/api-keys](https://platform.openai.com/api-keys) |
| Google Cloud Project | With enabled APIs:  
&nbsp; &nbsp; - [Google Sheets API](https://console.cloud.google.com/apis/api/sheets.googleapis.com/overview)  
&nbsp; &nbsp; - [Gmail API](https://console.cloud.google.com/apis/api/gmail.googleapis.com/overview) |
| OAuth Credentials | Create credentials in [Google Cloud Console](https://console.cloud.google.com/apis/credentials) |
| Google Sheet | With the following columns:<br>`Name`, `Email`, `LinkedIn`, `Score (Out of 100)`, `Summary (250 chars)`, `Standout 1`, `Standout 2`, `Standout 3`, `Standout 4`, `Standout 5`, `Skills` |

---

## Dependencies

Install with:

```bash
pip install -r requirements.txt
```

### `requirements.txt`
```txt
langchain==0.1.20
openai==1.35.1
google-api-python-client==2.146.0
google-auth-httplib2==0.1.0
google-auth-oauthlib==1.0.0
pdfplumber==0.10.3
python-dotenv==1.0.1
email-validator==2.1.0
beautifulsoup4==4.12.3
pydantic==2.9.2
```

---

## Folder Structure

```
resume-analyzer/
├── main.py
├── .env
├── requirements.txt
└── credentials/
    ├── gmail_client_secret.json   # From Google Cloud Console
    └── gmail_token.json           # Generated automatically
```

---

## How It Works

1. **Triggers on new unread email**: The script checks your Gmail inbox for unread messages.
2. **Downloads PDF attachment**: If an email contains a PDF resume, it gets downloaded locally.
3. **Extracts text from PDF**: Uses `pdfplumber` to extract readable content.
4. **Analyzes with OpenAI**: Sends the extracted text to OpenAI's GPT model (`gpt-4o-mini`) to parse and score the resume.
5. **Saves to Google Sheet**: Stores structured data like name, email, score, and standout points.
6. **Sends summary email**: (Optional) Sends a formatted HTML email with key insights to a recruiter.

---

## Sample Output

```json
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "linkedin": "https://www.linkedin.com/in/johndoe",
  "score": "87",
  "skills": "Project Management, Python, Data Analysis, Leadership",
  "standouts": [
    "Led a team of 10 engineers",
    "Built AI-driven analytics pipeline",
    "Published research paper on ML",
    "Won hackathon award",
    "Mentored 20+ junior developers"
  ],
  "summary": "Experienced project manager with strong technical background in Python and machine learning."
}
```

---

## Environment Variables

Create a `.env` file with the following:

```env
# Gmail Credentials
GMAIL_CREDENTIALS_JSON_PATH="credentials/gmail_token.json"
GMAIL_CLIENT_SECRET_JSON_PATH="credentials/gmail_client_secret.json"

# Google Sheets
GOOGLE_SHEET_ID="xxxxxxxxxx"
GOOGLE_SHEET_NAME="Resume-Summary"

# OpenAI
OPENAI_API_KEY="your-openai-api-key-here"
```

---

## How to Run

1. Set up Google API access:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create OAuth client ID (Desktop app), download JSON, rename to `credentials/gmail_client_secret.json`
2. Run the script:

```bash
python main.py
```

It will:
- Authenticate with Gmail
- Download the latest unread email with a PDF
- Extract text
- Analyze it with OpenAI
- Append to Google Sheet
- Send a formatted email summary
  


