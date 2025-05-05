import os
import base64
import pickle
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
import pdfplumber
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ----------------------
# Configuration Section
# ----------------------

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME")
GMAIL_CREDENTIALS_JSON_PATH = os.getenv("GMAIL_CREDENTIALS_JSON_PATH", "credentials/gmail_token.json")
GMAIL_CLIENT_SECRET_JSON_PATH = os.getenv("GMAIL_CLIENT_SECRET_JSON_PATH", "credentials/gmail_client_secret.json")

# ---------------------
# Data Model Definition
# ---------------------

class ResumeAnalysis(BaseModel):
    name: str = Field(description="Full name of the candidate")
    email: str = Field(description="Email address")
    linkedin: str = Field(description="LinkedIn profile URL")
    score: str = Field(description="Resume score out of 100")
    skills: str = Field(description="List of skills")
    standouts: List[str] = Field(description="Top 5 standout points")
    summary: str = Field(description="Short summary under 250 characters")

# ---------------------
# Helper Functions
# ---------------------

def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

def get_gmail_service():
    creds = None
    if os.path.exists(GMAIL_CREDENTIALS_JSON_PATH):
        creds = Credentials.from_authorized_user_file(GMAIL_CREDENTIALS_JSON_PATH)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(GMAIL_CLIENT_SECRET_JSON_PATH, ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send'])
            creds = flow.run_local_server(port=0)
        with open(GMAIL_CREDENTIALS_JSON_PATH, 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def get_sheets_service():
    creds = Credentials.from_authorized_user_file(GMAIL_CREDENTIALS_JSON_PATH)
    return build('sheets', 'v4', credentials=creds)

def analyze_resume_with_openai(resume_text):
    parser = PydanticOutputParser(pydantic_model=ResumeAnalysis)
    prompt_template = """
Here is the resume:
{resume_text}

Evaluate this resume thoroughly and respond strictly in the following format:
{format_instructions}
"""

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["resume_text"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    model = ChatOpenAI(model_name="gpt-4o-mini", openai_api_key=OPENAI_API_KEY)
    _input = prompt.format_prompt(resume_text=resume_text)
    output = model(_input.to_messages())
    return parser.parse(output.content)

def append_to_google_sheet(data: ResumeAnalysis):
    service = get_sheets_service()
    sheet = service.spreadsheets()
    values = [
        data.name,
        data.email,
        data.linkedin,
        data.score,
        data.summary,
        data.standouts[0],
        data.standouts[1],
        data.standouts[2],
        data.standouts[3],
        data.standouts[4],
        data.skills
    ]
    body = {"values": [values]}
    result = sheet.values().append(
        spreadsheetId=GOOGLE_SHEET_ID,
        range=GOOGLE_SHEET_NAME,
        valueInputOption="RAW",
        body=body
    ).execute()
    print(f"{result.get('updates').get('updatedCells')} cells appended.")

def send_email_summary(data: ResumeAnalysis):
    service = get_gmail_service()
    message = MIMEText(f"""
    <h2>Resume Summary</h2>
    <p><strong>Name:</strong> {data.name}</p>
    <p><strong>Email:</strong> {data.email}</p>
    <p><strong>Score:</strong> {data.score}/100</p>
    <p><strong>Summary:</strong> {data.summary}</p>
    """, "html")
    message["to"] = "surajanand.work@gmail.com"
    message["subject"] = f"Resume Summary of {data.name} - Score: {data.score}"
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(userId='me', body={'raw': raw}).execute()
    print("Summary email sent.")

# ---------------------
# Main Execution Flow
# ---------------------

def main():
    # 1. Get unread emails
    gmail = get_gmail_service()
    results = gmail.users().messages().list(userId='me', labelIds=['UNREAD']).execute()
    messages = results.get('messages', [])

    for msg_ref in messages[:1]:  # process one for now
        msg = gmail.users().messages().get(userId='me', id=msg_ref['id']).execute()

        # 2. Find PDF attachment
        for part in msg.get("payload", {}).get("parts", []):
            if part.get("filename") and part["filename"].endswith(".pdf"):
                attachment_id = part["body"].get("attachmentId")
                att = gmail.users().messages().attachments().get(
                    userId='me', messageId=msg_ref['id'], id=attachment_id
                ).execute()
                data = att.get("data")
                pdf_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                with open("temp_resume.pdf", "wb") as f:
                    f.write(pdf_data)
                break

        # 3. Extract text from PDF
        resume_text = extract_text_from_pdf("temp_resume.pdf")

        # 4. Analyze with OpenAI
        analysis = analyze_resume_with_openai(resume_text)
        print("Analysis:", analysis.dict())

        # 5. Save to Google Sheet
        append_to_google_sheet(analysis)

        # 6. Send Email Summary
        send_email_summary(analysis)

if __name__ == "__main__":
    main()