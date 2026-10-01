import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


# =========================================
# Hugging Face Model
# =========================================

MODEL_NAME = "HuggingFaceTB/SmolLM2-360M-Instruct"


# =========================================
# Device
# =========================================

device = "cuda" if torch.cuda.is_available() else "cpu"

print(f"AI Suggestions Model: {MODEL_NAME}")
print(f"AI Suggestions Device: {device}")


# =========================================
# Load Tokenizer
# =========================================

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME
)


# =========================================
# Load Model
# =========================================

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME
).to(device)

model.eval()


# =========================================
# Generate Suggestions
# =========================================

def generate_suggestions(
    resume_text,
    job_description,
    matched_skills,
    missing_skills
):
    """
    Generate concise resume improvement suggestions.

    The skill analysis is performed by Python.
    SmolLM2 is used only to convert the verified
    information into natural-language suggestions.
    """

    # -----------------------------------------
    # Validate input
    # -----------------------------------------

    if not resume_text or not resume_text.strip():
        return "Resume text was not available."

    if not job_description or not job_description.strip():
        return "Please provide a job description."

    # -----------------------------------------
    # Prepare verified skills
    # -----------------------------------------

    matched_skills = matched_skills or []
    missing_skills = missing_skills or []

    matched_text = ", ".join(
        str(skill) for skill in matched_skills
    )

    missing_text = ", ".join(
        str(skill) for skill in missing_skills
    )

    if not matched_text:
        matched_text = "None"

    if not missing_text:
        missing_text = "None"

    # -----------------------------------------
    # Limit input size
    # -----------------------------------------

    resume_text = resume_text[:3000]

    # -----------------------------------------
    # Strict prompt
    # -----------------------------------------

    prompt = f"""
You are a resume improvement assistant.

Give exactly 5 short and practical suggestions.

Use ONLY the verified information below.

MATCHED SKILLS:
{matched_text}

MISSING SKILLS:
{missing_text}

RULES:

- Do not invent skills.
- Do not invent technologies.
- Do not invent projects.
- Do not invent experience.
- Do not invent achievements.
- Do not mention technologies that are not listed above.
- Do not suggest unrelated technologies.
- Do not claim the candidate has a missing skill.
- If a skill is missing, say:
  "If you genuinely have this skill, consider adding it."
- Focus on improving the resume, not judging the candidate.
- Keep each suggestion to one or two sentences.
- Return exactly 5 numbered suggestions.
- Do not repeat the job description.

RESUME:
{resume_text}

Return only:

1. Suggestion
2. Suggestion
3. Suggestion
4. Suggestion
5. Suggestion
"""

    # -----------------------------------------
    # Chat format
    # -----------------------------------------

    messages = [
        {
            "role": "user",
            "content": prompt
        }
    ]

    # -----------------------------------------
    # Tokenize using chat template
    # -----------------------------------------

    inputs = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt"
    )

    # -----------------------------------------
    # Move inputs to device
    # -----------------------------------------

    inputs = {
        key: value.to(device)
        for key, value in inputs.items()
    }

    # -----------------------------------------
    # Generate
    # -----------------------------------------

    with torch.no_grad():

        outputs = model.generate(
            **inputs,

            # Enough for 5 short suggestions
            max_new_tokens=220,

            # Deterministic output
            do_sample=False,

            # Reduce repetition
            repetition_penalty=1.15,

            # Prevent repeated phrases
            no_repeat_ngram_size=3,

            # End generation correctly
            pad_token_id=tokenizer.eos_token_id
        )

    # -----------------------------------------
    # Remove prompt tokens
    # -----------------------------------------

    generated_tokens = outputs[
        0
    ][
        inputs["input_ids"].shape[-1]:
    ]

    # -----------------------------------------
    # Decode
    # -----------------------------------------

    result = tokenizer.decode(
        generated_tokens,
        skip_special_tokens=True
    )

    result = result.strip()

    # -----------------------------------------
    # Clean common unwanted prefixes
    # -----------------------------------------

    unwanted_prefixes = [
        "Resume Improvement Suggestions:",
        "Resume Improvement Suggestions",
        "Here are five suggestions:",
        "Here are 5 suggestions:"
    ]

    for prefix in unwanted_prefixes:

        if result.startswith(prefix):

            result = result[
                len(prefix):
            ].strip()

    return result


# =========================================
# Test
# =========================================

if __name__ == "__main__":

    resume = """
    Python developer with experience in Flask,
    MySQL, JavaScript, Git and GitHub.

    Developed an AI Resume Analyzer using Python
    and Flask.
    """

    job_description = """
    We are looking for a Software Engineer.

    Requirements:
    - Strong knowledge of Python
    - Experience with Flask
    - Knowledge of MySQL
    - Git and GitHub
    - Understanding of REST APIs
    - Knowledge of JavaScript
    - Good problem-solving skills
    """

    matched = [
        "flask",
        "git",
        "github",
        "javascript",
        "mysql",
        "problem solving",
        "python"
    ]

    missing = [
        "rest api"
    ]

    result = generate_suggestions(
        resume,
        job_description,
        matched,
        missing
    )

    print("\n")
    print("AI Resume Improvement Suggestions")
    print("=" * 50)
    print(result)