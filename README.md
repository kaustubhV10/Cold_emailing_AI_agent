# AI Cold Email Generator

An AI-powered tool that helps job seekers **generate personalized cold emails** to companies.  
The app can:
- Research a company,
- Draft a tailored email for a specific role,
- Suggest possible recipient emails,
- Send the email with your attached resume.

Built with **FastAPI + Jinja2 + Vanilla JS**.

---

## Features
- Upload your resume (PDF) and auto-attach it to emails.
- AI-generated personalized email drafts for any company & role.
- Suggests possible recipient emails.
- One-click **Send Email** functionality.
- Fail-safe backend and frontend (handles most common errors gracefully).

---

## Tech Stack
- **Backend:** FastAPI
- **Frontend:** HTML, JavaScript (Vanilla)
- **Templating:** Jinja2
- **Email Sending:** `smtplib`
- **Research & Drafting Logic:** Custom AI functions (`agent.py`)
- **Environment:** Python 3.9+ recommended
