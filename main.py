import os, shutil
from fastapi import FastAPI, Form, UploadFile, File, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from agent import draft_email, send_email, research_company, find_emails, RESUME_PATH

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = FastAPI()

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": f"An error occurred: {str(exc)}"}
    )

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "resume_path": RESUME_PATH if os.path.exists(RESUME_PATH) else None})

@app.post("/generate")
async def generate_email(
    company: str = Form(...),
    role: str = Form(...),
    resume: UploadFile = File(None)
):
    # Save resume if uploaded
    if resume:
        try:
            with open(RESUME_PATH, "wb") as f:
                shutil.copyfileobj(resume.file, f)
        except Exception as e:
            return {"error": f"Resume upload failed: {str(e)}"}

    attach_path = RESUME_PATH if os.path.exists(RESUME_PATH) else None
    research_text = research_company(company)
    email_body = draft_email(company, role, research_text)
    subject = f"Application for {role} at {company}"

    possible_emails = find_emails(company)

    return {
        "draft": email_body,
        "subject": subject,
        "attach": attach_path,
        "emails": possible_emails
    }

@app.post("/send")
async def send_generated_email(recipient: str = Form(...), subject: str = Form(...), body: str = Form(...)):
    result = send_email(recipient, subject, body, RESUME_PATH)
    return {"status": result}
