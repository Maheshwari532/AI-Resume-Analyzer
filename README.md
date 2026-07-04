# AI Resume Analyser

A Flask + HTML/CSS/JS web app that analyses resumes (PDF, DOCX, TXT) the way an ATS would: it checks contact info, section structure, skills coverage, bullet/action-verb usage, and — if you paste a job description — keyword match against that specific role.

## Features
- Drag-and-drop upload (PDF / DOCX / TXT, up to 8MB)
- Contact info detection (email, phone, LinkedIn)
- Section detection (Summary, Experience, Education, Skills, Projects, Certifications)
- Skill extraction across Programming, Web, Data/AI, Cloud/DevOps, Database, and Soft Skills
- Bullet point & action-verb usage check
- Optional job description keyword match with a missing-keywords list
- Composite 0–100 Resume Score with a prioritized "Fix List" of suggestions
- All analysis logic is transparent/rule-based — no external API key needed

## Setup

```bash
cd resume-analyzer
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Then open **http://127.0.0.1:5000** in your browser.

## Project structure

```
resume-analyzer/
├── app.py                  # Flask backend + analysis engine
├── requirements.txt
├── templates/
│   └── index.html          # UI markup
├── static/
│   ├── css/style.css       # "Scanline" visual design
│   └── js/script.js        # Upload handling + result rendering
└── uploads/                # Temp storage (files deleted right after parsing)
```

## Extending it with a real LLM

The current engine is fully rule-based so it works offline with no API key.
If you want deeper, more nuanced feedback (e.g. rewriting bullet points,
judging tone, or scoring against a specific company's culture), you can add
a call to the Anthropic API inside `analyze()` in `app.py`, sending the
extracted resume text and job description to Claude and merging its
response into the JSON returned to the frontend.

## Notes
- Scanned/image-only PDFs won't extract text (no OCR is included). Use a text-based PDF or DOCX export instead.
- Uploaded files are deleted immediately after text extraction — nothing is stored long-term.
