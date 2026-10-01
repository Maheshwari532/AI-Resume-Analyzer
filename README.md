# 🤖 AI Resume Analyzer

An AI-powered web application that analyzes resumes against a given job
description and provides resume quality insights, job-skill matching,
semantic similarity, and AI-generated improvement suggestions.

The application combines **rule-based resume analysis**, **Hugging Face
semantic embeddings**, and a lightweight **Hugging Face language model**
to provide practical feedback without requiring a paid API key.

------------------------------------------------------------------------

## 📌 Features

### 📄 Resume Analysis

Upload your resume and automatically extract useful information such as:

-   Word count
-   Bullet-point count
-   Action-verb count
-   Email
-   Phone number
-   LinkedIn profile
-   GitHub profile
-   Resume sections
-   Technical skills

Supported resume formats:

-   PDF
-   DOCX

------------------------------------------------------------------------

### 🎯 Resume Section Detection

The analyzer detects common resume sections including:

-   Summary
-   Education
-   Experience
-   Skills
-   Projects
-   Certifications

The section detector checks for actual section headings rather than
simply searching for words anywhere in the resume.

------------------------------------------------------------------------

### 🛠️ Skill Detection

The application uses a predefined skill taxonomy to detect skills from
the resume.

Current categories include:

-   Programming Languages
-   Web Development
-   Databases
-   AI & Machine Learning
-   Cloud & DevOps
-   Tools & Technologies
-   Soft Skills

Example detected skills:

``` text
Python
Java
C
JavaScript
Flask
HTML
CSS
MySQL
Git
GitHub
TensorFlow
PyTorch
Machine Learning
Deep Learning
Communication
Problem Solving
```

------------------------------------------------------------------------

### 🎯 Job Description Skill Matching

Users can provide a job description together with their resume.

The system compares the predefined skills detected in the resume with
the skills detected in the job description and separates them into:

-   Matched Skills
-   Missing Skills

Example:

``` text
Matched Skills

✓ Python
✓ Flask
✓ MySQL
✓ Git
✓ GitHub
✓ JavaScript
✓ Problem Solving

Missing Skills

✗ REST API
✗ Communication
✗ Teamwork
```

This helps identify skills that may need to be added to the resume
**only when the candidate genuinely has those skills**.

------------------------------------------------------------------------

### 🤖 AI Job Matching

The application calculates semantic similarity between the resume and
job description using a Hugging Face sentence-transformer model.

Model:

``` text
BAAI/bge-small-en-v1.5
```

The similarity result is displayed as an AI Job Match percentage.

Example:

``` text
AI Job Match
59.6%
```

This semantic score is different from predefined skill matching. A
resume can have several matched skills while still receiving a lower
semantic similarity score if the overall wording and content differ from
the job description.

------------------------------------------------------------------------

### 💡 AI Resume Improvement Suggestions

The application generates practical resume improvement suggestions based
on the uploaded resume and job description.

The lightweight language model used for suggestions is:

``` text
HuggingFaceTB/SmolLM2-360M-Instruct
```

The model is instructed to:

-   Give practical suggestions
-   Avoid inventing experience
-   Avoid inventing skills
-   Avoid inventing projects
-   Avoid inventing achievements
-   Focus on the supplied resume and job description
-   Highlight relevant missing skills
-   Improve project descriptions
-   Improve job-specific keywords
-   Improve resume clarity

Example:

``` text
1. REST API is mentioned in the job description but was not detected
   in your resume. If you genuinely have experience with REST API,
   consider adding it to your Technical Skills or a relevant project.

2. Communication is mentioned in the job description but was not
   detected in your resume. If you genuinely demonstrate this skill,
   show it through projects, presentations, or actual teamwork.

3. Review your project descriptions and clearly show how you used
   Python, Flask, MySQL, JavaScript, Git, and GitHub.
```

------------------------------------------------------------------------

### 📊 Resume Score

The application generates an overall resume-quality score based on the
information extracted from the resume.

Example:

``` text
Resume Score
80/100
```

The resume score and AI Job Match percentage represent different
measurements.

------------------------------------------------------------------------

### 📈 Resume Statistics

The results page displays:

``` text
Words
308

Bullet Points
6

Action Verbs
4
```

These statistics provide a quick overview of resume content and
structure.

------------------------------------------------------------------------

### 📇 Contact Information Detection

The application detects common contact information:

-   Email
-   Phone
-   LinkedIn
-   GitHub

Example:

``` text
Email: example@gmail.com
Phone: +91-XXXXXXXXXX
LinkedIn: LinkedIn profile detected
GitHub: GitHub profile detected
```

------------------------------------------------------------------------

## 🧠 Analysis Approach

The project combines three main approaches.

### 1. Rule-Based Resume Analysis

Regular expressions and predefined rules are used for:

-   Contact information detection
-   Resume section detection
-   Skill detection
-   Bullet-point counting
-   Action-verb counting
-   Word counting

### 2. Semantic Similarity

A sentence-transformer model converts the resume and job description
into numerical embeddings.

Cosine similarity is then used to calculate semantic similarity.

``` text
Resume
   ↓
BGE Embedding
   ↓
Numerical Vector
   ↓
Cosine Similarity
   ↑
Numerical Vector
   ↑
BGE Embedding
   ↑
Job Description
```

### 3. Generative AI Suggestions

SmolLM2 is used to generate practical resume improvement suggestions
based on the resume and job description.

``` text
Resume + Job Description
          ↓
     Prompt Creation
          ↓
     SmolLM2 Model
          ↓
AI Resume Suggestions
```

------------------------------------------------------------------------

## 🏗️ Project Structure

``` text
AI Resume Analyzer/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── services/
│   ├── __init__.py
│   ├── resume_parser.py
│   ├── resume_analyzer.py
│   ├── job_matcher.py
│   └── ai_suggestions.py
│
├── utils/
│   ├── __init__.py
│   └── skills.py
│
├── templates/
│   ├── index.html
│   └── results.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   └── js/
│       ├── script.js
│       └── results.js
│
└── uploads/
```

> The exact files may vary slightly depending on the current version of
> the project.

------------------------------------------------------------------------

## ⚙️ Technologies Used

### Frontend

``` text
HTML5
CSS3
JavaScript
```

### Backend

``` text
Python
Flask
```

### Resume Processing

``` text
pdfplumber
python-docx
Regular Expressions
```

### Machine Learning / NLP

``` text
PyTorch
Transformers
Sentence Transformers
Scikit-learn
NumPy
```

### Hugging Face Models

``` text
BAAI/bge-small-en-v1.5
HuggingFaceTB/SmolLM2-360M-Instruct
```

------------------------------------------------------------------------

## 📦 Installation

### 1. Clone the repository

``` bash
git clone https://github.com/your-username/ai-resume-analyzer.git
```

Move into the project directory:

``` bash
cd ai-resume-analyzer
```

------------------------------------------------------------------------

### 2. Create a virtual environment

Windows:

``` bash
python -m venv venv
```

Activate it:

``` bash
venv\Scripts\activate
```

For macOS/Linux:

``` bash
python3 -m venv venv
source venv/bin/activate
```

------------------------------------------------------------------------

### 3. Install dependencies

``` bash
pip install -r requirements.txt
```

------------------------------------------------------------------------

### 4. Run the application

``` bash
python app.py
```

Open the local Flask URL shown in the terminal, commonly:

``` text
http://127.0.0.1:5000
```

------------------------------------------------------------------------

## 🔄 Application Workflow

``` text
              Upload Resume
                    │
                    ▼
            Extract Resume Text
                    │
                    ▼
          Rule-Based Resume Analysis
                    │
       ┌────────────┼─────────────┐
       ▼            ▼             ▼
   Sections      Skills       Statistics
       │            │             │
       └────────────┼─────────────┘
                    ▼
             Enter Job Description
                    │
                    ▼
            Extract JD Skills
                    │
                    ▼
       Compare Resume & JD Skills
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
    Matched Skills       Missing Skills
          │                   │
          └─────────┬─────────┘
                    ▼
          Semantic Job Matching
                    │
                    ▼
             AI Job Match %
                    │
                    ▼
          SmolLM2 AI Suggestions
                    │
                    ▼
             Results Dashboard
```

------------------------------------------------------------------------

## 🖥️ Results Dashboard

The results page presents the analysis in separate sections.

### Main Scores

``` text
Resume Score
80/100

AI Job Match
59.6%
```

### Resume Statistics

``` text
Words
Bullet Points
Action Verbs
```

### Contact Information

``` text
Email
Phone
LinkedIn
GitHub
```

### Resume Sections

``` text
Certifications: Detected ✓
Education: Detected ✓
Experience: Missing ✗
Projects: Detected ✓
Skills: Detected ✓
Summary: Detected ✓
```

### Detected Skills

Skills are grouped into their respective categories.

### Job Description Skill Analysis

``` text
Matched Skills
Missing Skills
```

### AI Resume Improvement Suggestions

The generated suggestions are displayed at the bottom of the analysis
page.

------------------------------------------------------------------------

## 📝 Example Job Description

The application can be tested with a job description such as:

``` text
We are looking for a Software Engineer.

Requirements:
- Strong knowledge of Python
- Experience with Flask
- Knowledge of MySQL
- Git and GitHub
- Understanding of REST APIs
- Knowledge of JavaScript
- Good problem-solving skills
- Good communication skills
- Ability to work effectively in a team
```

The analyzer can then compare the job requirements with the uploaded
resume.

------------------------------------------------------------------------

## 🔍 Example Analysis

For a resume containing:

``` text
Python
Flask
MySQL
JavaScript
Git
GitHub
Problem Solving
```

and a job description requiring:

``` text
Python
Flask
MySQL
Git
GitHub
JavaScript
REST API
Problem Solving
Communication
Teamwork
```

the skill analysis can produce:

``` text
Matched Skills

✓ Python
✓ Flask
✓ MySQL
✓ Git
✓ GitHub
✓ JavaScript
✓ Problem Solving

Missing Skills

✗ REST API
✗ Communication
✗ Teamwork
```

The AI suggestions can then explain how to address those gaps without
automatically claiming that the candidate has skills they do not
actually possess.

------------------------------------------------------------------------

## 🔐 No Paid API Key Required

The project is designed to use Hugging Face models locally.

It does not require a paid OpenAI, Gemini, or other commercial LLM API
key for the implemented analysis and suggestion-generation
functionality.

The first execution may download model files from Hugging Face, so
internet access is required when the models are not already available
locally.

------------------------------------------------------------------------

## ⚠️ Important Limitations

### Skill Taxonomy

Skill matching is based on the predefined skill taxonomy in the project.

Therefore, a skill may not be detected if:

-   It is not included in the taxonomy.
-   It is written using an unsupported variation.
-   The resume uses a different synonym or abbreviation.

The taxonomy can be extended as the project evolves.

### Semantic Matching

The BGE model measures semantic similarity between the resume and job
description. The percentage should be treated as a similarity indicator,
not as a guaranteed probability of getting an interview or job.

### AI Suggestions

The generated suggestions are AI-generated recommendations. They should
be reviewed before applying them to a real resume.

Users should only add skills, experience, projects, certifications, or
achievements that are genuinely applicable to them.

------------------------------------------------------------------------

## 🛡️ Responsible Resume Improvement

The application is designed to help improve the presentation of genuine
qualifications rather than fabricate qualifications.

For example, if the job description requires REST APIs but the resume
does not mention REST APIs, the system should suggest adding it **only
if the candidate actually has REST API experience**.

It should not recommend falsely claiming:

``` text
"Experienced REST API Developer"
```

when no such experience exists.

------------------------------------------------------------------------

## 🚀 Future Enhancements

Potential future improvements include:

-   ATS keyword analysis
-   Skill synonym detection
-   Better REST API / API terminology matching
-   Resume formatting analysis
-   Job-specific resume recommendations
-   Multiple job-description comparison
-   Resume version comparison
-   Resume PDF report generation
-   Analysis history
-   Resume improvement tracking
-   Improved AI suggestion formatting
-   Experience-level detection
-   More comprehensive skill taxonomy
-   Better multilingual resume support

------------------------------------------------------------------------

## 🎓 Project Purpose

The **AI Resume Analyzer** demonstrates the practical integration of
traditional software development with modern AI/NLP techniques.

The project demonstrates:

-   Python programming
-   Flask web development
-   HTML/CSS/JavaScript
-   PDF and DOCX processing
-   Regular-expression-based text analysis
-   Natural Language Processing
-   Semantic embeddings
-   Cosine similarity
-   Machine Learning
-   Generative AI
-   Hugging Face models
-   Resume analysis
-   Job-description matching

------------------------------------------------------------------------

## 📚 Key Learning Outcomes

Through this project, the following concepts are demonstrated:

1.  Building a full-stack Flask application.
2.  Extracting and processing text from PDF and DOCX files.
3.  Designing rule-based NLP features.
4.  Creating a reusable skill taxonomy.
5.  Comparing resume skills with job requirements.
6.  Generating semantic embeddings.
7.  Calculating cosine similarity.
8.  Integrating Hugging Face models into a Python application.
9.  Generating AI-based resume suggestions.
10. Building a user-friendly results dashboard.

------------------------------------------------------------------------

## 👩‍💻 Author

**Maheshwari Inamadar**

Computer Science and Engineering Student

------------------------------------------------------------------------

## 📄 License

This project is intended for educational and portfolio purposes.

If you choose to publish the project publicly, add an appropriate
license file such as `MIT`, `Apache-2.0`, or another license that
matches your intended usage.
