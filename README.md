# Scanline — AI Resume Analyser

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

## Deploying to Vercel

This repo includes a `vercel.json` that routes all traffic to the Flask app. Steps:

```bash
npm i -g vercel      # if you don't have the CLI
cd resume-analyzer
vercel
```

Things that are already handled for you, because they're the most common causes of a 500 on Vercel:

- **Read-only filesystem**: Vercel's serverless functions can only write to `/tmp`. Uploaded files are now saved via `tempfile.gettempdir()` instead of a local `uploads/` folder.
- **Request body size limit**: Vercel's Hobby tier caps request bodies around 4.5MB. The upload cap is set to 4MB so you get a clean error instead of a platform-level rejection.
- **Unhandled exceptions**: a global error handler returns a JSON error message and logs the real exception (visible in your Vercel deployment's **Logs** tab) instead of a bare crash.

If you still see a 500 after deploying, check **Vercel dashboard → your project → Deployments → (latest) → Functions/Logs** for the actual Python traceback — that will tell you exactly what failed. Common remaining causes:
- A missing dependency in `requirements.txt` (redeploy after any changes there)
- The function timing out on a large PDF (Hobby tier has a 10s execution limit)
- Cold-start install size — `pdfplumber` pulls in Pillow/pdfminer.six; if the bundle exceeds Vercel's size limit, switching to a lighter PDF library (e.g. `pypdf`) can help

## Notes
- Scanned/image-only PDFs won't extract text (no OCR is included). Use a text-based PDF or DOCX export instead.
- Uploaded files are deleted immediately after text extraction — nothing is stored long-term.
