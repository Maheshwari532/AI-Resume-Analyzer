const form = document.getElementById("resumeForm");
const message = document.getElementById("message");
const loading = document.getElementById("loading");

form.addEventListener("submit", async function (event) {

    event.preventDefault();

    const resumeFile =
        document.getElementById("resume").files[0];

    const jobDescription =
        document.getElementById("job_description").value.trim();


    // -----------------------------
    // Validate Resume
    // -----------------------------

    if (!resumeFile) {

        message.textContent =
            "Please upload your resume.";

        return;
    }


    // -----------------------------
    // Show Loading
    // -----------------------------

    loading.style.display = "block";

    message.textContent =
        "Analyzing your resume. Please wait...";


    // -----------------------------
    // Prepare Form Data
    // -----------------------------

    const formData = new FormData();

    formData.append(
        "resume",
        resumeFile
    );

    formData.append(
        "job_description",
        jobDescription
    );


    try {

        // -----------------------------
        // Send to Flask
        // -----------------------------

        const response = await fetch(
            "/analyze",
            {
                method: "POST",
                body: formData
            }
        );


        const data = await response.json();


        // -----------------------------
        // Hide Loading
        // -----------------------------

        loading.style.display = "none";


        // -----------------------------
        // Handle Error
        // -----------------------------

        if (!data.success) {

            message.textContent =
                data.error || "Something went wrong.";

            return;
        }


        // -----------------------------
        // Save Results
        // -----------------------------

        sessionStorage.setItem(
            "resumeAnalysis",
            JSON.stringify(data)
        );


        // -----------------------------
        // Go to Results Page
        // -----------------------------

        window.location.href = "/results";

    } catch (error) {

        loading.style.display = "none";

        message.textContent =
            "Could not connect to the server.";

        console.error(error);
    }

});