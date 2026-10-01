import os
import json

from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

from services.resume_parser import extract_text
from services.resume_analyzer import analyze_resume
from services.scoring import calculate_resume_score
from services.ai_matcher import analyze_job_match
from services.suggestions import generate_rule_based_suggestions


app = Flask(__name__)

# =========================================
# Upload Configuration
# =========================================

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Create uploads folder automatically
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =========================================
# Allowed File Check
# =========================================

def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


# =========================================
# Home Page
# =========================================

@app.route("/")
def home():
    return render_template("index.html")


# =========================================
# Results Page
# =========================================

@app.route("/results")
def results():
    return render_template("results.html")


# =========================================
# Resume Analysis
# =========================================

@app.route("/analyze", methods=["POST"])
def analyze():

    # -----------------------------------------
    # Check whether resume was uploaded
    # -----------------------------------------

    if "resume" not in request.files:
        return jsonify({
            "success": False,
            "error": "Please upload a resume."
        }), 400

    file = request.files["resume"]

    # -----------------------------------------
    # Check filename
    # -----------------------------------------

    if file.filename == "":
        return jsonify({
            "success": False,
            "error": "Please select a resume file."
        }), 400

    # -----------------------------------------
    # Check file extension
    # -----------------------------------------

    if not allowed_file(file.filename):
        return jsonify({
            "success": False,
            "error": "Only PDF, DOCX, and TXT files are supported."
        }), 400

    # -----------------------------------------
    # Get Job Description
    # -----------------------------------------

    job_description = request.form.get(
        "job_description",
        ""
    ).strip()

    # -----------------------------------------
    # Secure Filename
    # -----------------------------------------

    filename = secure_filename(file.filename)

    # -----------------------------------------
    # Create File Path
    # -----------------------------------------

    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    # -----------------------------------------
    # Save Uploaded Resume
    # -----------------------------------------

    file.save(file_path)

    print("Resume saved at:", file_path)

    try:

        # =====================================
        # 1. Extract Resume Text
        # =====================================

        resume_text = extract_text(file_path)

        if not resume_text.strip():
            return jsonify({
                "success": False,
                "error": "Could not extract text from the resume."
            }), 400

        # =====================================
        # 2. Analyze Resume
        # =====================================

        resume_analysis = analyze_resume(
            resume_text
        )

        # =====================================
        # 3. Calculate Resume Score
        # =====================================

        resume_score = calculate_resume_score(
            resume_analysis
        )

        # =====================================
        # 4. AI Job Matching
        # =====================================

        job_match = analyze_job_match(
            resume_text,
            job_description
        )

        matched_skills = job_match.get(
            "matched_skills",
            []
        )

        missing_skills = job_match.get(
            "missing_skills",
            []
        )

        # =====================================
        # 5. AI Resume Suggestions
        # =====================================

        ai_suggestions = generate_rule_based_suggestions(
            resume_text,
            job_description,
            matched_skills,
            missing_skills
        )

        # =====================================
        # 6. Return Complete Result
        # =====================================

        return jsonify({
            "success": True,
            "resume_score": resume_score,
            "job_match": job_match,
            "analysis": resume_analysis,
            "ai_suggestions": ai_suggestions
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =========================================
# Run Application
# =========================================

if __name__ == "__main__":
    app.run(debug=True)