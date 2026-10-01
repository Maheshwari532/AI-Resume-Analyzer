document.addEventListener("DOMContentLoaded", function () {

    // =========================================
    // Get Analysis Data
    // =========================================

    const resultData = sessionStorage.getItem("resumeAnalysis");

    if (!resultData) {
        window.location.href = "/";
        return;
    }

    let data;

    try {
        data = JSON.parse(resultData);
    } catch (error) {
        console.error("Invalid resume analysis data:", error);
        window.location.href = "/";
        return;
    }


    // =========================================
    // Resume Score
    // =========================================

    const resumeScoreElement =
        document.getElementById("resumeScore");

    if (resumeScoreElement) {
        resumeScoreElement.textContent =
            (data.resume_score ?? 0) + "/100";
    }


    // =========================================
    // AI Job Match
    // =========================================

    const jobMatchElement =
        document.getElementById("jobMatch");

    const jobMatch =
        data.job_match?.match_percentage;

    if (jobMatchElement) {

        if (jobMatch !== null && jobMatch !== undefined) {
            jobMatchElement.textContent =
                jobMatch + "%";
        } else {
            jobMatchElement.textContent =
                "N/A";
        }
    }


    // =========================================
    // Resume Statistics
    // =========================================

    const wordCountElement =
        document.getElementById("wordCount");

    const bulletCountElement =
        document.getElementById("bulletCount");

    const actionVerbsElement =
        document.getElementById("actionVerbs");


    if (wordCountElement) {
        wordCountElement.textContent =
            data.analysis?.word_count ?? 0;
    }

    if (bulletCountElement) {
        bulletCountElement.textContent =
            data.analysis?.bullet_count ?? 0;
    }

    if (actionVerbsElement) {
        actionVerbsElement.textContent =
            data.analysis?.action_verbs ?? 0;
    }


    // =========================================
    // Contact Information
    // =========================================

    const contactContainer =
        document.getElementById("contactInfo");

    const contact =
        data.analysis?.contact || {};


    if (contactContainer) {

        contactContainer.innerHTML = "";

        const contactFields = [
            ["Email", contact.email],
            ["Phone", contact.phone],
            ["LinkedIn", contact.linkedin],
            ["GitHub", contact.github]
        ];


        contactFields.forEach(function ([label, value]) {

            const item =
                document.createElement("div");

            item.className =
                "contact-item";


            const labelElement =
                document.createElement("strong");

            labelElement.textContent =
                label + ": ";


            const valueElement =
                document.createElement("span");


            if (value) {
                valueElement.textContent = value;
            } else {
                valueElement.textContent =
                    "Not detected";
            }


            item.appendChild(labelElement);
            item.appendChild(valueElement);

            contactContainer.appendChild(item);
        });
    }


    // =========================================
    // Resume Sections
    // =========================================

    const sectionsContainer =
        document.getElementById("sectionsList");

    const sections =
        data.analysis?.sections || {};


    if (sectionsContainer) {

        sectionsContainer.innerHTML = "";

        Object.entries(sections).forEach(
            function ([section, detected]) {

                const item =
                    document.createElement("div");

                item.className =
                    detected
                        ? "section-item detected"
                        : "section-item missing";


                item.textContent =
                    `${section}: ${
                        detected
                            ? "Detected ✓"
                            : "Missing ✗"
                    }`;


                sectionsContainer.appendChild(item);
            }
        );
    }


    // =========================================
    // Skill Name Formatter
    // =========================================

    function formatSkill(skill) {

        const specialCases = {

            "nlp": "NLP",
            "sql": "SQL",
            "mysql": "MySQL",

            "html": "HTML",
            "css": "CSS",

            "javascript": "JavaScript",
            "typescript": "TypeScript",

            "github": "GitHub",
            "git": "Git",

            "tensorflow": "TensorFlow",
            "pytorch": "PyTorch",
            "keras": "Keras",

            "flask": "Flask",
            "django": "Django",
            "fastapi": "FastAPI",

            "rest api": "REST API",
            "rest apis": "REST APIs",

            "machine learning": "Machine Learning",
            "deep learning": "Deep Learning",
            "artificial intelligence": "Artificial Intelligence",

            "computer vision": "Computer Vision",
            "natural language processing": "Natural Language Processing",

            "problem solving": "Problem Solving",
            "problem-solving": "Problem Solving",

            "time management": "Time Management",

            "google cloud": "Google Cloud",
            "google cloud platform": "Google Cloud Platform",

            "node.js": "Node.js",
            "node": "Node.js",

            "react": "React",
            "react native": "React Native",

            "spring boot": "Spring Boot",

            "scikit-learn": "Scikit-learn",

            "visual studio code": "Visual Studio Code"
        };


        const normalizedSkill =
            String(skill)
                .trim()
                .toLowerCase();


        if (specialCases[normalizedSkill]) {
            return specialCases[normalizedSkill];
        }


        // Generic capitalization for unknown skills
        return String(skill)
            .trim()
            .split(" ")
            .map(function (word) {

                if (!word) {
                    return word;
                }

                return (
                    word.charAt(0).toUpperCase() +
                    word.slice(1)
                );
            })
            .join(" ");
    }


    // =========================================
    // Create Skill Tag
    // =========================================

    function createSkillTag(skill, type = "normal") {

        const tag =
            document.createElement("span");

        tag.className =
            "skill-tag";


        const displaySkill =
            formatSkill(skill);


        if (type === "matched") {

            tag.classList.add("matched-skill");

            tag.textContent =
                "✓ " + displaySkill;

        } else if (type === "missing") {

            tag.classList.add("missing-skill");

            tag.textContent =
                "✗ " + displaySkill;

        } else {

            tag.textContent =
                displaySkill;
        }


        return tag;
    }


    // =========================================
    // Detected Skills
    // =========================================

    const skillsContainer =
        document.getElementById("skillsList");

    const skills =
        data.analysis?.skills || {};


    if (skillsContainer) {

        skillsContainer.innerHTML = "";


        if (Object.keys(skills).length === 0) {

            skillsContainer.textContent =
                "No predefined skills detected.";

        } else {

            Object.entries(skills).forEach(
                function ([category, skillList]) {

                    const categoryDiv =
                        document.createElement("div");

                    categoryDiv.className =
                        "skill-category";


                    // Category heading
                    const heading =
                        document.createElement("h3");

                    heading.textContent =
                        category;


                    categoryDiv.appendChild(
                        heading
                    );


                    // Skill tags container
                    const tags =
                        document.createElement("div");

                    tags.className =
                        "skill-tags";


                    // Create individual tags
                    skillList.forEach(
                        function (skill) {

                            const tag =
                                createSkillTag(skill);

                            tags.appendChild(tag);
                        }
                    );


                    categoryDiv.appendChild(tags);

                    skillsContainer.appendChild(
                        categoryDiv
                    );
                }
            );
        }
    }


    // =========================================
    // Matched Skills
    // =========================================

    const matchedSkillsContainer =
        document.getElementById("matchedSkills");

    const matchedSkills =
        data.job_match?.matched_skills || [];


    if (matchedSkillsContainer) {

        matchedSkillsContainer.innerHTML = "";


        if (matchedSkills.length === 0) {

            matchedSkillsContainer.textContent =
                "No matching predefined skills detected.";

        } else {

            matchedSkills.forEach(
                function (skill) {

                    const tag =
                        createSkillTag(
                            skill,
                            "matched"
                        );


                    matchedSkillsContainer.appendChild(
                        tag
                    );
                }
            );
        }
    }


    // =========================================
    // Missing Skills
    // =========================================

    const missingSkillsContainer =
        document.getElementById("missingSkills");

    const missingSkills =
        data.job_match?.missing_skills || [];


    if (missingSkillsContainer) {

        missingSkillsContainer.innerHTML = "";


        if (missingSkills.length === 0) {

            missingSkillsContainer.textContent =
                "No missing predefined skills detected.";

        } else {

            missingSkills.forEach(
                function (skill) {

                    const tag =
                        createSkillTag(
                            skill,
                            "missing"
                        );


                    missingSkillsContainer.appendChild(
                        tag
                    );
                }
            );
        }
    }


    // =========================================
    // AI Resume Improvement Suggestions
    // =========================================

    const suggestionsContainer =
        document.getElementById("aiSuggestions");


    if (suggestionsContainer) {

        const suggestions =
            data.ai_suggestions || [];


        suggestionsContainer.innerHTML = "";


        // -----------------------------------------
        // Array of suggestions
        // -----------------------------------------

        if (
            Array.isArray(suggestions) &&
            suggestions.length > 0
        ) {

            const list =
                document.createElement("ol");

            list.className =
                "suggestions-list";


            suggestions.forEach(
                function (suggestion) {

                    const item =
                        document.createElement("li");

                    item.textContent =
                        suggestion;

                    list.appendChild(item);
                }
            );


            suggestionsContainer.appendChild(list);
        }


        // -----------------------------------------
        // Single string suggestion
        // -----------------------------------------

        else if (
            typeof suggestions === "string" &&
            suggestions.trim() !== ""
        ) {

            suggestionsContainer.textContent =
                suggestions;
        }


        // -----------------------------------------
        // No suggestions
        // -----------------------------------------

        else {

            suggestionsContainer.textContent =
                "No resume improvement suggestions were generated.";
        }
    }


    // =========================================
    // Debug Message
    // =========================================

    console.log(
        "Resume analysis results loaded successfully."
    );

});