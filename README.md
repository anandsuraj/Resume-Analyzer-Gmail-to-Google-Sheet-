# Resume Analyzer: Gmail to Google Sheet (Python Version)

Automatically extract, analyze, and organize candidate resumes from Gmail into a structured Google Sheet using Python.

resume-analyzer-n8n-to-python/
├── .env.example
├── requirements.txt
├── resume_analyzer.py
├── credentials/
│   ├── gmail_client_secret.json     # You add this
│   └── gmail_token.json             # Will be generated
├── README.md
└── .gitignore

## 🔧 Features

- Triggers on unread emails with PDF attachments (resumes)
- Extracts text from PDFs
- Uses OpenAI (GPT) to evaluate and summarize resumes
- Stores structured data in Google Sheets
- Sends formatted summary email to recruiter

## 🛠️ Setup Instructions

### 1. Clone the repo
```bash
git clone https://github.com/anandsuraj/Resume-Analyzer-Gmail-to-Google-Sheet.git
cd resume-analyzer-n8n-to-python
