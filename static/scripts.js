let generatedSubject = "";

const statusBox = document.getElementById("statusMessage");
const emailDraft = document.getElementById("emailDraft");
const recipientDropdown = document.getElementById("recipientDropdown");

// Helper to display status messages
function showStatus(message, isError = false) {
    statusBox.style.color = isError ? "red" : "green";
    statusBox.innerText = message;
}

// Handle form submission
document.getElementById("emailForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    showStatus("Generating draft, please wait...", false);

    const company = document.getElementById("company").value.trim();
    const role = document.getElementById("role").value.trim();
    const resumeFile = document.getElementById("resume").files[0];

    if (!company || !role) {
        showStatus("Company and Role are required fields.", true);
        return;
    }

    if (resumeFile && resumeFile.type !== "application/pdf") {
        showStatus("Please upload a valid PDF file.", true);
        return;
    }

    const formData = new FormData();
    formData.append("company", company);
    formData.append("role", role);
    if (resumeFile) formData.append("resume", resumeFile);

    try {
        const response = await fetch("/generate", { method: "POST", body: formData });
        const result = await response.json();

        if (result.error) {
            showStatus("Error: " + result.error, true);
            return;
        }

        generatedSubject = result.subject || `Application for ${role} at ${company}`;
        emailDraft.value = result.draft || "No draft generated.";
        
        // Populate recipient dropdown
        recipientDropdown.innerHTML = "<option value=''>--Select Email--</option>";
        if (result.emails && result.emails.length > 0) {
            result.emails.forEach(email => {
                const option = document.createElement("option");
                option.value = email;
                option.text = email;
                recipientDropdown.appendChild(option);
            });
        } else {
            showStatus("No recipient emails found, using default suggestions.", true);
        }

        showStatus("Draft generated successfully!", false);

    } catch (err) {
        console.error(err);
        showStatus("Failed to generate draft. Please try again.", true);
    }
});

// Handle sending email
document.getElementById("sendBtn").addEventListener("click", async () => {
    const body = emailDraft.value.trim();
    const recipient_email = recipientDropdown.value;

    if (!recipient_email) {
        showStatus("Please select a recipient email.", true);
        return;
    }
    if (!body) {
        showStatus("Email body is empty. Generate draft first.", true);
        return;
    }

    const formData = new FormData();
    formData.append("subject", generatedSubject);
    formData.append("body", body);
    formData.append("recipient", recipient_email);

    showStatus("Sending email, please wait...", false);

    try {
        const response = await fetch("/send", { method: "POST", body: formData });
        const result = await response.json();

        if (result.status) {
            showStatus(result.status, false);
        } else {
            showStatus("Failed to send email. Please try again.", true);
        }
    } catch (err) {
        console.error(err);
        showStatus("Error occurred while sending email.", true);
    }
});
