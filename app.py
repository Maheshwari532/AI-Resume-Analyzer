"""
AI Resume Analyser
-------------------
A Flask backend that accepts a resume (PDF, DOCX, or TXT), extracts its text,
and runs a rule-based analysis engine that mimics what an ATS (Applicant
Tracking System) and a human recruiter would look for:

  * Contact info detection (email, phone, LinkedIn)
  * Section detection (summary, experience, education, skills, projects...)
  * Skill extraction against a curated skills taxonomy
  * Readability / length checks
  * Bullet-point / action-verb usage
  * Optional Job Description keyword match + gap analysis
  * A composite 0-100 "Resume Score" with actionable suggestions

No external AI API key is required -- the "AI" here is a transparent,
explainable scoring engine, which is actually preferable for resume tooling
since candidates can see exactly *why* they got a given score.
"""

import os
import re
import io
import uuid

from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename

import pdfplumber
import docx  # python-docx

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024  # 8 MB upload cap
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}


# --------------------------------------------------------------------------
# Text extraction
# --------------------------------------------------------------------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_pdf(path):
    text_parts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
    return "\n".join(text_parts)


def extract_text_from_docx(path):
    document = docx.Document(path)
    return "\n".join(p.text for p in document.paragraphs)


def extract_text_from_txt(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def extract_text(path, ext):
    if ext == "pdf":
        return extract_text_from_pdf(path)
    if ext == "docx":
        return extract_text_from_docx(path)
    if ext == "txt":
        return extract_text_from_txt(path)
    return ""


# --------------------------------------------------------------------------
# Analysis knowledge base
# --------------------------------------------------------------------------
SKILL_TAXONOMY = {
    "Programming": [
        "python", "java", "c++", "c#", "javascript", "typescript", "go", "rust",
        "ruby", "php", "kotlin", "swift", "scala", "r", "matlab", "sql"
    ],
    "Web & Frameworks": [
        "react", "angular", "vue", "django", "flask", "node.js", "node", "express",
        "next.js", "spring", "spring boot", ".net", "html", "css", "tailwind",
        "bootstrap", "graphql", "rest api", "fastapi"
    ],
    "Data & AI": [
        "machine learning", "deep learning", "nlp", "computer vision", "pandas",
        "numpy", "tensorflow", "pytorch", "scikit-learn", "keras", "data analysis",
        "data visualization", "power bi", "tableau", "etl", "spark", "hadoop",
        "llm", "generative ai"
    ],
    "Cloud & DevOps": [
        "aws", "azure", "gcp", "docker", "kubernetes", "ci/cd", "jenkins",
        "terraform", "ansible", "linux", "git", "github actions", "cloudformation"
    ],
    "Database": [
        "mysql", "postgresql", "mongodb", "redis", "oracle", "sqlite",
        "elasticsearch", "dynamodb", "firebase"
    ],
    "Soft Skills": [
        "leadership", "communication", "teamwork", "problem solving",
        "project management", "collaboration", "adaptability", "critical thinking",
        "time management", "mentoring", "stakeholder management"
    ],
}

SECTION_PATTERNS = {
    "Contact Info": r"(email|phone|linkedin|github|address)",
    "Summary/Objective": r"(summary|objective|profile)\b",
    "Experience": r"(experience|employment history|work history)\b",
    "Education": r"\beducation\b",
    "Skills": r"\bskills\b",
    "Projects": r"\bprojects?\b",
    "Certifications": r"(certifications?|licenses?)\b",
}

ACTION_VERBS = [
    "led", "built", "designed", "developed", "created", "managed", "improved",
    "increased", "reduced", "launched", "implemented", "optimized", "automated",
    "delivered", "achieved", "drove", "spearheaded", "streamlined", "architected",
    "mentored", "negotiated", "analyzed"
]

STOPWORDS = set("""
a an the and or but if in on at for with to of is are was were be been being
this that these those from as it its by an your you we our they their he she
his her i my me us job role position responsibilities requirements preferred
years experience will must have has having such into about over under
""".split())


# --------------------------------------------------------------------------
# Analysis helpers
# --------------------------------------------------------------------------
def find_contact_info(text):
    email = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)
    phone = re.search(r"(\(?\+?\d{1,3}\)?[\d\-.\s()]{7,}\d)", text)
    linkedin = re.search(r"(linkedin\.com/[^\s,;]+)", text, re.IGNORECASE)
    return {
        "email": email.group(0) if email else None,
        "phone": phone.group(0).strip() if phone else None,
        "linkedin": linkedin.group(0) if linkedin else None,
    }


def find_sections(text_lower):
    found = {}
    for section, pattern in SECTION_PATTERNS.items():
        found[section] = bool(re.search(pattern, text_lower))
    return found


def _skill_pattern(skill):
    # Word-boundary match so short/substring-prone tokens ("r", "go", "java")
    # don't false-positive inside longer words ("javascript", "algorithm").
    escaped = re.escape(skill)
    return re.compile(r"(?<![a-z0-9+#.])" + escaped + r"(?![a-z0-9+#-])")


_SKILL_REGEXES = {
    category: [(skill, _skill_pattern(skill)) for skill in skills]
    for category, skills in SKILL_TAXONOMY.items()
}


def find_skills(text_lower):
    matched = {}
    for category, skill_patterns in _SKILL_REGEXES.items():
        hits = sorted({skill for skill, pattern in skill_patterns if pattern.search(text_lower)})
        if hits:
            matched[category] = hits
    return matched



def count_bullets(text):
    lines = text.split("\n")
    bullet_lines = [l for l in lines if re.match(r"^\s*([•\-\*\u2022]|[0-9]+[\.\)])\s+", l)]
    return len(bullet_lines)


def count_action_verbs(text_lower):
    return sum(len(re.findall(r"\b" + re.escape(v) + r"\b", text_lower)) for v in ACTION_VERBS)


def extract_keywords(text_lower, top_n=40):
    words = re.findall(r"[a-zA-Z][a-zA-Z+.#-]{1,}", text_lower)
    freq = {}
    for w in words:
        if w in STOPWORDS or len(w) < 3:
            continue
        freq[w] = freq.get(w, 0) + 1
    ranked = sorted(freq.items(), key=lambda kv: kv[1], reverse=True)
    return [w for w, _ in ranked[:top_n]]


def compare_with_job_description(resume_text_lower, jd_text_lower):
    jd_keywords = extract_keywords(jd_text_lower, top_n=30)
    matched = [kw for kw in jd_keywords if kw in resume_text_lower]
    missing = [kw for kw in jd_keywords if kw not in resume_text_lower]
    match_pct = round((len(matched) / len(jd_keywords)) * 100) if jd_keywords else None
    return {
        "match_percentage": match_pct,
        "matched_keywords": matched,
        "missing_keywords": missing[:15],
    }


def build_suggestions(word_count, sections, contact, bullets, action_verbs, skills, jd_result):
    tips = []

    if not contact["email"]:
        tips.append("Add a professional email address near the top of your resume.")
    if not contact["phone"]:
        tips.append("Include a phone number so recruiters can reach you directly.")
    if not contact["linkedin"]:
        tips.append("Add your LinkedIn profile URL to strengthen credibility.")

    for section in ["Experience", "Education", "Skills"]:
        if not sections.get(section):
            tips.append(f"Add a clearly labeled '{section}' section — ATS systems look for these headers explicitly.")

    if word_count < 250:
        tips.append("Your resume looks light on content (under 250 words). Add more detail on impact and results.")
    elif word_count > 900:
        tips.append("Your resume is quite long. Aim for 1 page (400–700 words) unless you have 10+ years of experience.")

    if bullets < 5:
        tips.append("Use more bullet points to describe achievements — they're easier for both ATS and recruiters to scan.")

    if action_verbs < 5:
        tips.append("Start bullet points with strong action verbs like 'led', 'built', or 'improved' instead of passive phrases.")

    if not skills:
        tips.append("List specific technical or professional skills — ATS keyword matching relies heavily on this.")

    if jd_result and jd_result["match_percentage"] is not None:
        if jd_result["match_percentage"] < 50:
            tips.append("Your resume matches fewer than half the key terms in the job description. Consider weaving in the missing keywords where genuinely true.")

    if not tips:
        tips.append("Strong resume! Consider tailoring keywords per job application for the best ATS match.")

    return tips


def compute_score(word_count, sections, contact, bullets, action_verbs, skills, jd_result):
    score = 0

    # Contact info: 15 pts
    score += 5 if contact["email"] else 0
    score += 5 if contact["phone"] else 0
    score += 5 if contact["linkedin"] else 0

    # Sections: 25 pts
    key_sections = ["Experience", "Education", "Skills", "Summary/Objective"]
    score += sum(6.25 for s in key_sections if sections.get(s))

    # Length: 15 pts
    if 250 <= word_count <= 900:
        score += 15
    elif 150 <= word_count < 250 or 900 < word_count <= 1100:
        score += 8

    # Bullets & action verbs: 20 pts
    score += min(bullets, 10) * 1.0
    score += min(action_verbs, 10) * 1.0

    # Skills breadth: 15 pts
    total_skills = sum(len(v) for v in skills.values())
    score += min(total_skills, 15)

    # JD match: 10 pts (only if JD provided, otherwise redistribute to skills/length already counted)
    if jd_result and jd_result["match_percentage"] is not None:
        score += round(jd_result["match_percentage"] / 100 * 10)
    else:
        score += 10  # neutral credit when no JD supplied

    return max(0, min(100, round(score)))


# --------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    if "resume" not in request.files:
        return jsonify({"error": "No resume file uploaded."}), 400

    file = request.files["resume"]
    job_description = request.form.get("job_description", "").strip()

    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Unsupported file type. Please upload PDF, DOCX, or TXT."}), 400

    ext = file.filename.rsplit(".", 1)[1].lower()
    filename = secure_filename(f"{uuid.uuid4().hex}.{ext}")
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(save_path)

    try:
        text = extract_text(save_path, ext)
    except Exception as e:
        return jsonify({"error": f"Could not read file: {str(e)}"}), 400
    finally:
        if os.path.exists(save_path):
            os.remove(save_path)

    if not text or not text.strip():
        return jsonify({"error": "We couldn't extract any text from that file. If it's a scanned/image PDF, try a text-based export instead."}), 400

    text_lower = text.lower()
    word_count = len(re.findall(r"\b\w+\b", text))

    contact = find_contact_info(text)
    sections = find_sections(text_lower)
    skills = find_skills(text_lower)
    bullets = count_bullets(text)
    action_verbs = count_action_verbs(text_lower)

    jd_result = None
    if job_description:
        jd_result = compare_with_job_description(text_lower, job_description.lower())

    suggestions = build_suggestions(word_count, sections, contact, bullets, action_verbs, skills, jd_result)
    score = compute_score(word_count, sections, contact, bullets, action_verbs, skills, jd_result)

    return jsonify({
        "score": score,
        "word_count": word_count,
        "contact": contact,
        "sections": sections,
        "skills": skills,
        "bullets": bullets,
        "action_verbs": action_verbs,
        "job_match": jd_result,
        "suggestions": suggestions,
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
