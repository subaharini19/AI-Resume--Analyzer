from flask import Flask, render_template, request, send_file
from PyPDF2 import PdfReader
from reportlab.pdfgen import canvas
import matplotlib
matplotlib.use("Agg")   # non-GUI backend, needed for server-side chart saving
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs("static", exist_ok=True)

domains = {
    "Data Analytics": [
        "python", "sql", "excel",
        "power bi", "tableau",
        "pandas", "numpy"
    ],
    "Web Development": [
        "html", "css", "javascript",
        "react", "flask", "bootstrap"
    ],
    "Software Development": [
        "java", "python", "c++",
        "oop", "database", "api"
    ],
    "Cyber Security": [
        "linux", "networking",
        "wireshark", "nmap"
    ],
    "AI / ML": [
        "python", "machine learning",
        "deep learning",
        "tensorflow",
        "pytorch"
    ]
}

job_roles = {
    "Data Analytics": [
        "Data Analyst",
        "Business Analyst",
        "BI Developer"
    ],
    "Web Development": [
        "Frontend Developer",
        "Backend Developer",
        "Full Stack Developer"
    ],
    "Software Development": [
        "Software Engineer",
        "Application Developer",
        "Programmer"
    ],
    "Cyber Security": [
        "Security Analyst",
        "SOC Analyst",
        "Penetration Tester"
    ],
    "AI / ML": [
        "Machine Learning Engineer",
        "AI Engineer",
        "Data Scientist"
    ]
}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    file = request.files["resume"]

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        file.filename
    )
    file.save(filepath)

    reader = PdfReader(filepath)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    text = text.lower()

    best_domain = ""
    best_score = 0
    found_skills = []

    for domain, skills in domains.items():
        matched = []
        for skill in skills:
            if skill in text:
                matched.append(skill)

        if len(matched) > best_score:
            best_score = len(matched)
            best_domain = domain
            found_skills = matched

    if best_domain:
        total_skills = len(domains[best_domain])
        score = int((len(found_skills) / total_skills) * 100)

        missing_skills = [
            skill for skill in domains[best_domain]
            if skill not in found_skills
        ]

        roles = job_roles[best_domain]
        suggestions = []

        for skill in missing_skills:
            suggestions.append(f"Learn {skill}")

        if score < 40:
            suggestions.append("Add more technical skills")
            suggestions.append("Include projects")
        elif score < 70:
            suggestions.append("Add certifications")
            suggestions.append("Add internships")
        else:
            suggestions.append("Resume is ATS Friendly")

        suggestions.append("Add GitHub Profile")
        suggestions.append("Add Projects Section")
    else:
        score = 0
        missing_skills = []
        roles = []
        suggestions = []

    plt.figure(figsize=(4, 4))
    plt.pie(
        [score, 100 - score],
        labels=["Matched", "Missing"],
        autopct="%1.1f%%"
    )
    plt.title("Resume Analysis")
    plt.savefig("static/chart.png")
    plt.close()

    return render_template(
        "index.html",
        score=score,
        domain=best_domain,
        found=found_skills,
        missing=missing_skills,
        roles=roles,
        suggestions=suggestions,
        chart="chart.png"
    )


@app.route("/download-report")
def download_report():
    pdf_path = "resume_report.pdf"
    pdf = canvas.Canvas(pdf_path)
    pdf.drawString(100, 800, "AI Resume Analyzer Report")
    pdf.drawString(100, 770, "Generated Successfully")
    pdf.save()
    return send_file(pdf_path, as_attachment=True)


if __name__ == "__main__":

    app.run(debug=True)
    