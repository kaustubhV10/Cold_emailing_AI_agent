import os, re, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage

load_dotenv()

# ----------------------------
# Environment variables
# ----------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SENDER_NAME = os.getenv("SENDER_NAME")
SENDER_PHONE = os.getenv("SENDER_PHONE")
LINKEDIN_URL = os.getenv("LINKEDIN_URL")

RESUME_PATH = "saved_resume.pdf"

# ----------------------------
# LLM and Search setup
# ----------------------------
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, openai_api_key=OPENAI_API_KEY)
search = DuckDuckGoSearchRun()

# ----------------------------
# Prompt template for draft
# ----------------------------
email_prompt = PromptTemplate(
    input_variables=["company", "role", "research"],
    template="""
You are an AI assistant writing a human-tailored cold email for a job application.
The applicant is early in their career, enthusiastic, and highly motivated. Do NOT use "fresher".

Include:
- Professional salutation (e.g., "Dear Hiring Manager," or "Dear {company} Team,")
- Personalized body using the research points provided
Do NOT include any closing or signature; that will be added separately

Company: {company}
Role: {role}
Research (key points for this role): {research}

Write under 150 words.
"""
)

# ----------------------------
# Helper functions
# ----------------------------
def _signature() -> str:
    parts = [f"Best regards,\n{SENDER_NAME}"]
    if SENDER_PHONE: parts.append(SENDER_PHONE)
    if LINKEDIN_URL: parts.append(LINKEDIN_URL)
    return "\n".join(parts)

def _closing_line() -> str:
    return ("I would be delighted to discuss how my background and skills align with this role.\n"
            "I look forward to the possibility of connecting with you.")

# ----------------------------
# AI functions with error handling
# ----------------------------
def research_company(company: str) -> str:
    """Perform company research safely."""
    try:
        query = f"{company} company profile mission values recent news"
        return search.run(query)
    except Exception as e:
        return f"Research failed: {str(e)}"

def summarize_research(research_text: str, role: str) -> str:
    """Summarize research safely for email draft."""
    prompt = f"""
Summarize the following company research into 3–5 key points relevant to the role of {role}.
Focus on achievements, projects, values, products, or initiatives a candidate for {role} could mention.
Research:
{research_text}
"""
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip()
    except Exception as e:
        return f"Summary failed: {str(e)}"

def draft_email(company: str, role: str, research_text: str) -> str:
    """Generate a draft email safely."""
    try:
        relevant_points = summarize_research(research_text, role)
        prompt_text = email_prompt.format(company=company, role=role, research=relevant_points)
        response = llm.invoke([HumanMessage(content=prompt_text)])
        body = response.content.strip()
        return f"{body}\n\n{_closing_line()}\n\n{_signature()}"
    except Exception as e:
        return f"Draft generation failed: {str(e)}"

def find_emails(company: str) -> list:
    """Find possible emails, fallback to default."""
    try:
        query = f"{company} careers HR recruiter email contact"
        results_text = search.run(query)
        emails = set(re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", results_text))
    except Exception:
        emails = set()

    if not emails:
        domain = company.lower().replace(" ", "") + ".com"
        emails = {f"hr@{domain}", f"careers@{domain}"}
    return list(emails)

# ----------------------------
# Email sending function
# ----------------------------
def send_email(to_email: str, subject: str, body: str, resume_path: str = None) -> str:
    """Send email with optional PDF attachment safely."""
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        if resume_path and os.path.exists(resume_path):
            with open(resume_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f'attachment; filename="{os.path.basename(resume_path)}"')
            msg.attach(part)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        return "Email sent successfully."
    except Exception as e:
        return f"Failed to send email: {str(e)}"
