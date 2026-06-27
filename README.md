# AI-Powered Technical Resume Score Checker using Python, NLP and Streamlit

An intelligent **ATS (Applicant Tracking System) Resume Analyzer** that compares a candidate's resume against a job description and provides an ATS compatibility score, skill analysis, personalized improvement suggestions, and application recommendations.

## 🚀 Features

* 📄 **PDF Resume Parsing**

  * Extracts text directly from PDF resumes using `PyPDF2`.

* 🎯 **ATS Resume Scoring**

  * Calculates an overall ATS score based on:

    * Technical skill matching
    * Keyword matching
    * Contextual phrase matching
    * Semantic similarity analysis

* 🛠️ **Technical Skill Detection**

  * Detects programming languages, frameworks, databases, cloud platforms, DevOps tools, and data technologies from both resumes and job descriptions.

* ✅ **Matched Skills Analysis**

  * Displays all technical skills that match the job description.

* ⚠️ **Missing Skills Identification**

  * Highlights important skills present in the job description but missing from the resume.

* 💡 **Resume Improvement Suggestions**

  * Provides actionable recommendations to improve resume quality and ATS compatibility.

* 🎯 **Application Recommendation**

  * Advises candidates whether they should apply for the role based on resume-job alignment.

* 🤖 **NLP-Powered Analysis**

  * Uses `spaCy` for:

    * Lemmatization
    * Semantic similarity
    * Contextual phrase extraction

* 🌐 **Interactive Web Interface**

  * Built using `Streamlit` for a clean and user-friendly experience.

---

## 🛠️ Tech Stack

* **Python**
* **Streamlit**
* **spaCy**
* **PyPDF2**
* **Regular Expressions (re)**

---

## 📊 Scoring Methodology

The ATS score is calculated using multiple weighted metrics:

| Metric                  | Weight |
| ----------------------- | ------ |
| Technical Skills Match  | 40%    |
| Semantic Similarity     | 25%    |
| Contextual Phrase Match | 20%    |
| Keyword/Lemma Match     | 15%    |

The final score is normalized to a maximum of **100%**.

---

## 📂 Supported Skills Categories

The application currently detects skills from the following categories:

* Programming Languages
* Frameworks and Libraries
* Databases
* Cloud Technologies
* DevOps Tools
* Data Science and Machine Learning Technologies

---

## 📷 Workflow

1. Upload your resume in PDF format.
2. Paste the target job description.
3. Click **Calculate Resume Score**.
4. View:

   * ATS Score
   * Matched Skills
   * Missing Skills
   * Resume Improvement Suggestions
   * Application Recommendation

---

## ▶️ Installation

Clone the repository:

```bash
git clone <repository-url>
cd <repository-folder>
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Download the spaCy model:

```bash
python -m spacy download en_core_web_md
```

Run the application:

```bash
streamlit run app.py
```

---

## 📁 Project Structure

```text
Resume-Score-Checker/
│
├── app.py
├── requirements.txt
├── logo.png
├── README.md
└── sample_resume.pdf
```

---

## 🔮 Future Improvements

* Support for DOCX resumes.
* Resume section detection (Education, Projects, Experience, Skills).
* Experience-level matching.
* Industry-specific resume scoring.
* Report Generation
* Integration with Large Language Models for deeper resume analysis.

---


## 📜 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

**Madhu**

Built using **Python, NLP, and Streamlit** to help candidates optimize their resumes and improve their chances of passing ATS screening systems.
