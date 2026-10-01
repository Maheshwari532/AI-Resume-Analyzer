def calculate_resume_score(analysis):
    """
    Calculate a basic resume quality score out of 100.

    This is our own Resume Score.
    It is NOT an official ATS score.
    """

    score = 0

    contact = analysis["contact"]
    sections = analysis["sections"]
    word_count = analysis["word_count"]
    bullet_count = analysis["bullet_count"]
    action_verbs = analysis["action_verbs"]
    skills = analysis["skills"]

    # -------------------------
    # Contact information: 20
    # -------------------------

    if contact["email"]:
        score += 5

    if contact["phone"]:
        score += 5

    if contact["linkedin"]:
        score += 5

    if contact["github"]:
        score += 5

    # -------------------------
    # Resume sections: 25
    # -------------------------

    important_sections = [
        "Summary",
        "Education",
        "Skills",
        "Projects",
        "Experience"
    ]

    section_points = 25 / len(important_sections)

    for section in important_sections:

        if sections.get(section):
            score += section_points

    # -------------------------
    # Resume length: 15
    # -------------------------

    if 300 <= word_count <= 800:
        score += 15

    elif 200 <= word_count < 300:
        score += 10

    elif 800 < word_count <= 1000:
        score += 10

    elif word_count >= 150:
        score += 5

    # -------------------------
    # Bullet points: 15
    # -------------------------

    score += min(bullet_count, 15)

    # -------------------------
    # Action verbs: 10
    # -------------------------

    score += min(action_verbs, 10)

    # -------------------------
    # Skills: 15
    # -------------------------

    total_skills = sum(
        len(skill_list)
        for skill_list in skills.values()
    )

    score += min(total_skills, 15)

    return min(round(score), 100)