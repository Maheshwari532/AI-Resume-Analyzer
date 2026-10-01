# =========================================
# Resume Improvement Suggestions
# =========================================


def generate_rule_based_suggestions(
    resume_text,
    job_description,
    matched_skills,
    missing_skills
):
    """
    Generate factual resume improvement suggestions.

    Suggestions are generated from the verified
    matched and missing skills detected by the
    resume analyzer.

    No LLM is used here, so the system does not
    invent technologies, projects, or experience.
    """

    suggestions = []

    matched = {
        str(skill).lower().strip()
        for skill in (matched_skills or [])
    }

    missing = {
        str(skill).lower().strip()
        for skill in (missing_skills or [])
    }

    # =========================================
    # 1. Missing Skills
    # =========================================

    if missing:

        for skill in sorted(missing):

            display_skill = skill.title()

            # Special handling for soft skills
            if skill in [
                "communication",
                "teamwork",
                "leadership",
                "collaboration",
                "time management",
                "adaptability",
                "critical thinking",
                "problem solving"
            ]:

                suggestion = (
                    f"{display_skill} is mentioned in the job "
                    f"description but was not detected in your resume. "
                    f"If you genuinely demonstrate this skill, consider "
                    f"showing it through relevant projects, teamwork, "
                    f"presentations, or other actual experiences."
                )

            else:

                suggestion = (
                    f"{display_skill} is mentioned in the job "
                    f"description but was not detected in your resume. "
                    f"If you genuinely have experience with "
                    f"{display_skill}, consider adding it to your "
                    f"Technical Skills or a relevant project."
                )

            suggestions.append(suggestion)

    else:

        suggestions.append(
            "All predefined job-description skills detected by the "
            "analyzer were also found in the resume. Keep these skills "
            "clearly visible in the relevant sections."
        )

    # =========================================
    # 2. Matched Skills
    # =========================================

    if matched:

        important_skills = [
            skill for skill in [
                "python",
                "flask",
                "mysql",
                "git",
                "github",
                "javascript",
                "problem solving"
            ]
            if skill in matched
        ]

        if not important_skills:
            important_skills = sorted(matched)[:7]

        formatted_skills = ", ".join(
            skill.title()
            for skill in important_skills
        )

        suggestions.append(
            f"Your resume already matches several job requirements, "
            f"including {formatted_skills}. Keep these skills clearly "
            f"connected to the projects or experience where you actually "
            f"used them."
        )

    # =========================================
    # 3. Project Description
    # =========================================

    project_skills = [
        skill for skill in [
            "python",
            "flask",
            "mysql",
            "javascript",
            "git",
            "github"
        ]
        if skill in matched
    ]

    if project_skills:

        formatted_project_skills = ", ".join(
            skill.title()
            for skill in project_skills
        )

        suggestions.append(
            f"Review your project descriptions and clearly show how "
            f"you used {formatted_project_skills}. Mention the specific "
            f"functionality you implemented rather than only listing "
            f"the technologies."
        )

    else:

        suggestions.append(
            "Make your project descriptions more specific by clearly "
            "stating what you built, which technologies you used, and "
            "what your contribution was."
        )

    # =========================================
    # 4. Job-specific Keywords
    # =========================================

    if matched:

        keyword_skills = sorted(matched)[:7]

        formatted_keywords = ", ".join(
            skill.title()
            for skill in keyword_skills
        )

        suggestions.append(
            f"Keep relevant keywords such as {formatted_keywords} "
            f"visible in appropriate sections of your resume. Only "
            f"use keywords that accurately represent your experience."
        )

    # =========================================
    # 5. Resume Clarity
    # =========================================

    suggestions.append(
        "Keep resume bullets concise and action-oriented. Clearly "
        "describe what you built or accomplished, the technologies "
        "you actually used, and your specific contribution."
    )

    # =========================================
    # Return maximum 5 suggestions
    # =========================================

    return suggestions[:5]