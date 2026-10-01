import re

from utils.skills import SKILL_TAXONOMY


# =========================================
# Resume Section Detection
# =========================================

SECTION_PATTERNS = {
    "Summary": [
        r"^summary$",
        r"^professional summary$",
        r"^career summary$",
        r"^profile$",
        r"^professional profile$",
        r"^objective$",
        r"^career objective$",
        r"^about me$"
    ],

    "Education": [
        r"^education$",
        r"^educational background$",
        r"^academic background$",
        r"^academic qualifications?$",
        r"^qualifications?$"
    ],

    "Experience": [
        r"^experience$",
        r"^work experience$",
        r"^professional experience$",
        r"^employment experience$",
        r"^internship experience$",
        r"^work history$",
        r"^employment history$"
    ],

    "Skills": [
        r"^skills$",
        r"^technical skills$",
        r"^technical skillset$",
        r"^technical skills and technologies$",
        r"^skills & technologies$",
        r"^technologies$"
    ],

    "Projects": [
        r"^projects$",
        r"^academic projects$",
        r"^personal projects$",
        r"^project experience$",
        r"^key projects$"
    ],

    "Certifications": [
        r"^certifications?$",
        r"^certificates?$",
        r"^professional certifications?$",
        r"^licenses?$",
        r"^certifications & courses$",
        r"^certificates & training$",
        r"^certifications & training$",
        r"^certificates and training$",
        r"^certifications and training$"
    ]
}


# =========================================
# Action Verbs
# =========================================

ACTION_VERBS = [
    "built",
    "developed",
    "designed",
    "created",
    "implemented",
    "managed",
    "improved",
    "optimized",
    "automated",
    "analyzed",
    "tested",
    "deployed",
    "integrated",
    "configured",
    "maintained"
]


# =========================================
# Normalize Text
# =========================================

def normalize_text(text):
    """
    Clean extracted resume text while preserving
    line breaks for bullet and section detection.
    """

    if not text:
        return ""

    # Remove null characters
    text = text.replace("\x00", " ")

    # Normalize spaces and tabs
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n\s*\n+", "\n", text)

    return text.strip()


# =========================================
# Count Words
# =========================================

def count_words(text):
    """
    Count words in the resume.
    """

    if not text:
        return 0

    words = re.findall(r"\b\w+\b", text)

    return len(words)


# =========================================
# Contact Information
# =========================================

def find_contact_information(text):
    """
    Detect:
    - Email
    - Phone
    - LinkedIn
    - GitHub

    Supports full URLs and labeled profile information.
    """

    if not text:
        return {
            "email": None,
            "phone": None,
            "linkedin": None,
            "github": None
        }

    # -----------------------------------------
    # Email
    # -----------------------------------------

    email_match = re.search(
        r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+",
        text,
        re.IGNORECASE
    )

    # -----------------------------------------
    # Phone
    # -----------------------------------------

    phone_match = re.search(
        r"(?:\+91[\s.-]?)?[6-9]\d{9}",
        text
    )

    # -----------------------------------------
    # LinkedIn URL
    # -----------------------------------------

    linkedin_url = re.search(
        r"(?:https?://)?(?:www\.)?linkedin\.com/"
        r"(?:in|pub)/[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]+",
        text,
        re.IGNORECASE
    )

    # -----------------------------------------
    # GitHub URL
    # -----------------------------------------

    github_url = re.search(
        r"(?:https?://)?(?:www\.)?github\.com/"
        r"[A-Za-z0-9][A-Za-z0-9-]*",
        text,
        re.IGNORECASE
    )

    # -----------------------------------------
    # LinkedIn Label
    # -----------------------------------------

    linkedin_label = re.search(
        r"\blinkedin\b\s*[:\-]?\s*(.+)",
        text,
        re.IGNORECASE
    )

    # -----------------------------------------
    # GitHub Label
    # -----------------------------------------

    github_label = re.search(
        r"\bgithub\b\s*[:\-]?\s*(.+)",
        text,
        re.IGNORECASE
    )

    # -----------------------------------------
    # Determine LinkedIn
    # -----------------------------------------

    if linkedin_url:

        linkedin = linkedin_url.group(0).rstrip(
            ".,;:)]"
        )

    elif linkedin_label:

        linkedin = "LinkedIn profile detected"

    else:

        linkedin = None

    # -----------------------------------------
    # Determine GitHub
    # -----------------------------------------

    if github_url:

        github = github_url.group(0).rstrip(
            ".,;:)]"
        )

    elif github_label:

        github = "GitHub profile detected"

    else:

        github = None

    # -----------------------------------------
    # Return Contact Information
    # -----------------------------------------

    return {
        "email": email_match.group(0)
        if email_match
        else None,

        "phone": phone_match.group(0)
        if phone_match
        else None,

        "linkedin": linkedin,

        "github": github
    }


# =========================================
# Detect Resume Sections
# =========================================

def detect_sections(text):
    """
    Detect actual resume section headings.

    IMPORTANT:
    This checks individual lines instead of searching
    for words throughout the entire resume.

    Therefore a sentence such as:

        Experience with Python and Flask

    will NOT be detected as an Experience section.

    Only headings such as:

        Experience
        Work Experience
        Professional Experience

    will be detected.
    """

    detected = {
        "Certifications": False,
        "Education": False,
        "Experience": False,
        "Projects": False,
        "Skills": False,
        "Summary": False
    }

    if not text:
        return detected

    lines = text.splitlines()

    for line in lines:

        # -----------------------------------------
        # Remove surrounding whitespace
        # -----------------------------------------

        line = line.strip()

        if not line:
            continue

        # -----------------------------------------
        # Remove common heading symbols
        # -----------------------------------------

        line = re.sub(
            r"^[\W_]+|[\W_]+$",
            "",
            line
        ).strip()

        # -----------------------------------------
        # Normalize spaces
        # -----------------------------------------

        line = re.sub(
            r"\s+",
            " ",
            line
        )

        # -----------------------------------------
        # Compare with section headings
        # -----------------------------------------

        for section, patterns in SECTION_PATTERNS.items():

            for pattern in patterns:

                if re.fullmatch(
                    pattern,
                    line,
                    re.IGNORECASE
                ):

                    detected[section] = True

                    break

    return detected


# =========================================
# Extract Skills
# =========================================

def extract_skills(text):
    """
    Detect skills from the predefined skill taxonomy.
    """

    if not text:
        return {}

    text_lower = text.lower()

    detected_skills = {}

    for category, skills in SKILL_TAXONOMY.items():

        found = []

        for skill in skills:

            normalized_skill = skill.lower()

            # -----------------------------------------
            # Handle special characters safely
            # -----------------------------------------

            pattern = (
                r"(?<![a-zA-Z0-9])"
                + re.escape(normalized_skill)
                + r"(?![a-zA-Z0-9])"
            )

            if re.search(
                pattern,
                text_lower
            ):

                found.append(skill)

        if found:

            detected_skills[category] = sorted(
                set(found),
                key=str.lower
            )

    return detected_skills


# =========================================
# Count Bullet Points
# =========================================

def count_bullets(text):
    """
    Count bullet points in extracted resume text.

    Handles:
    1. Explicit bullet characters
    2. Numbered bullets
    3. Project description lines when the document
       extractor has removed the bullet characters
    """

    if not text:
        return 0

    lines = text.splitlines()

    bullet_count = 0
    inside_projects = False

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # Remove invisible characters
        line = line.replace("\u200b", "")
        line = line.replace("\ufeff", "")

        # =========================================
        # Detect PROJECTS heading
        # =========================================

        if re.fullmatch(
            r"projects?|academic projects?|personal projects?|project experience",
            line,
            re.IGNORECASE
        ):
            inside_projects = True
            continue

        # =========================================
        # Detect next major section
        # =========================================

        if re.fullmatch(
            r"certificates? & training|"
            r"certifications?|"
            r"education|"
            r"technical skills|"
            r"skills|"
            r"experience|"
            r"professional summary|"
            r"summary",
            line,
            re.IGNORECASE
        ):
            inside_projects = False

        # =========================================
        # Explicit bullet characters
        # =========================================

        if re.match(
            r"^[•●▪◦○◉➢➤►■◆★‣⁃∙·]\s*",
            line
        ):
            bullet_count += 1
            continue

        # =========================================
        # Hyphen / asterisk bullets
        # =========================================

        if re.match(
            r"^[-*]\s+",
            line
        ):
            bullet_count += 1
            continue

        # =========================================
        # Numbered bullets
        # =========================================

        if re.match(
            r"^\d+[.)]\s+",
            line
        ):
            bullet_count += 1
            continue

        # =========================================
        # Project description detection
        # =========================================

        if inside_projects:

            project_description_verbs = (
                r"developed|implemented|integrated|"
                r"designed|built|created|"
                r"configured|automated|"
                r"deployed|optimized|"
                r"analyzed|tested|maintained"
            )

            if re.match(
                r"^(?:" + project_description_verbs + r")\b",
                line,
                re.IGNORECASE
            ):
                bullet_count += 1

    return bullet_count

# =========================================
# Count Action Verbs
# =========================================

def count_action_verbs(text):
    """
    Count action verbs used in the resume.
    """

    if not text:
        return 0

    text_lower = text.lower()

    count = 0

    for verb in ACTION_VERBS:

        matches = re.findall(
            r"\b" + re.escape(verb) + r"\b",
            text_lower
        )

        count += len(matches)

    return count


# =========================================
# Complete Resume Analysis
# =========================================

def analyze_resume(text):
    """
    Perform complete resume analysis.
    """

    # -----------------------------------------
    # Normalize resume text
    # -----------------------------------------

    text = normalize_text(text)

    # -----------------------------------------
    # Contact information
    # -----------------------------------------

    contact = find_contact_information(text)

    # -----------------------------------------
    # Resume sections
    # -----------------------------------------

    sections = detect_sections(text)

    # -----------------------------------------
    # Skills
    # -----------------------------------------

    skills = extract_skills(text)

    # -----------------------------------------
    # Word count
    # -----------------------------------------

    word_count = count_words(text)

    # -----------------------------------------
    # Bullet count
    # -----------------------------------------

    bullet_count = count_bullets(text)

    # -----------------------------------------
    # Action verbs
    # -----------------------------------------

    action_verbs = count_action_verbs(text)

    # -----------------------------------------
    # Return complete analysis
    # -----------------------------------------

    return {
        "word_count": word_count,
        "contact": contact,
        "sections": sections,
        "skills": skills,
        "bullet_count": bullet_count,
        "action_verbs": action_verbs
    }