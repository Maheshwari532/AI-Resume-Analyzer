from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re

from utils.skills import SKILL_TAXONOMY


# =========================================
# Hugging Face BGE Model
# =========================================

MODEL_NAME = "BAAI/bge-small-en-v1.5"

model = SentenceTransformer(MODEL_NAME)


# =========================================
# Semantic Embedding
# =========================================

def get_embedding(text):
    """
    Convert text into a numerical embedding
    using the Hugging Face BGE model.
    """

    if not text or not text.strip():
        return None

    embedding = model.encode(
        text,
        normalize_embeddings=True
    )

    return embedding


# =========================================
# Semantic Similarity
# =========================================

def calculate_similarity(resume_text, job_description):
    """
    Calculate semantic similarity between
    resume and job description.
    """

    if not resume_text or not job_description:
        return 0.0

    resume_embedding = get_embedding(resume_text)
    job_embedding = get_embedding(job_description)

    similarity = cosine_similarity(
        [resume_embedding],
        [job_embedding]
    )[0][0]

    percentage = similarity * 100

    return round(float(percentage), 2)


# =========================================
# Normalize Text
# =========================================

def normalize_text(text):
    """
    Normalize text for reliable skill matching.
    """

    text = text.lower()

    # Convert different dash characters to normal hyphen
    text = text.replace("–", "-")
    text = text.replace("—", "-")

    # Replace multiple spaces
    text = re.sub(r"\s+", " ", text)

    return text


# =========================================
# Extract Skills
# =========================================

def normalize_skill(skill):
    """
    Convert skill variations into one canonical form.
    """

    skill = skill.lower().strip()

    # Convert hyphen to space
    skill = skill.replace("-", " ")

    # REST API variations
    if skill in [
        "rest api",
        "rest apis",
        "restful api",
        "restful apis"
    ]:
        return "rest api"

    # Problem-solving variations
    if skill in [
        "problem solving",
        "problem-solving"
    ]:
        return "problem solving"

    return skill


def extract_skills_from_text(text):
    """
    Detect predefined skills from text
    and return normalized skill names.
    """

    if not text:
        return []

    normalized_text = normalize_text(text)

    detected_skills = set()

    for category, skills in SKILL_TAXONOMY.items():

        for skill in skills:

            normalized_skill = normalize_text(skill)

            # Escape special regex characters
            pattern = re.escape(normalized_skill)

            # Detect skill in text
            if re.search(
                r"(?<!\w)" + pattern + r"(?!\w)",
                normalized_text
            ):

                canonical_skill = normalize_skill(skill)

                detected_skills.add(
                    canonical_skill
                )

    return sorted(detected_skills)


# =========================================
# Analyze Job Match
# =========================================

def analyze_job_match(resume_text, job_description):
    """
    Return semantic match percentage,
    matched skills and missing skills.
    """

    if not job_description or not job_description.strip():

        return {
            "match_percentage": None,
            "message": "Job description was not provided.",
            "matched_skills": [],
            "missing_skills": []
        }


    # -----------------------------------------
    # Semantic similarity
    # -----------------------------------------

    match_percentage = calculate_similarity(
        resume_text,
        job_description
    )


    # -----------------------------------------
    # Extract skills
    # -----------------------------------------

    resume_skills = set(
        extract_skills_from_text(resume_text)
    )

    job_skills = set(
        extract_skills_from_text(job_description)
    )


    # -----------------------------------------
    # Compare skills
    # -----------------------------------------

    matched_skills = sorted(
        resume_skills.intersection(job_skills)
    )

    missing_skills = sorted(
        job_skills - resume_skills
    )


    # -----------------------------------------
    # Return result
    # -----------------------------------------

    return {

        "match_percentage": match_percentage,

        "message":
            "AI-based semantic matching completed.",

        "matched_skills":
            matched_skills,

        "missing_skills":
            missing_skills
    }


# =========================================
# Temporary Test
# =========================================

if __name__ == "__main__":

    resume = """
    Python developer with experience in Flask,
    MySQL, machine learning, Git, GitHub
    and JavaScript.
    """

    job_description = """
    We are looking for a Software Engineer.

    Requirements:
    Strong knowledge of Python.
    Experience with Flask.
    Knowledge of MySQL.
    Git and GitHub.
    Understanding of REST APIs.
    Knowledge of JavaScript.
    Good problem-solving skills.
    """


    result = analyze_job_match(
        resume,
        job_description
    )


    print("\n===== JOB MATCH RESULT =====")

    print(
        "Match Percentage:",
        result["match_percentage"]
    )

    print(
        "\nMatched Skills:"
    )

    for skill in result["matched_skills"]:
        print("✓", skill)

    print(
        "\nMissing Skills:"
    )

    for skill in result["missing_skills"]:
        print("✗", skill)