import streamlit as st
from PyPDF2 import PdfReader
import spacy
import re

# Initialize session state
if 'nlp_model' not in st.session_state:
    try:
        # Medium model with word vectors
        st.session_state.nlp_model = spacy.load("en_core_web_md")
        st.session_state.has_vectors = True

    except:
        try:
            # Small model without vectors
            st.session_state.nlp_model = spacy.load("en_core_web_sm")
            st.session_state.has_vectors = False

        except:
            # Final fallback
            st.session_state.nlp_model = spacy.blank("en")
            st.session_state.has_vectors = False

st.set_page_config(
    page_title="Resume Score Checker",
    page_icon="logo.png",
    layout=None,
    initial_sidebar_state=None,
    menu_items=None
)

with st.container(horizontal=True):
    st.space("stretch")
    st.image("logo.png", width=100)
    st.space("stretch")

st.title("Resume Score Checker", text_alignment="center")
st.text(
    "Upload your resume and paste the JD of the job and see how your "
    "resume matches with the job you are applying for by checking your ATS score"
)

resume_file = st.file_uploader(
    "Upload your Resume:",
    type="pdf",
    accept_multiple_files=False
)

job_description = st.text_area(
    "Paste the Job Description:",
    height=300
)

with st.container(horizontal=True):
    st.space("stretch")
    analyze_resume = st.button("Calculate Resume Score")
    st.space("stretch")


# ==================== NLP FUNCTIONS ====================

def extract_entities(doc):
    """Extract skills, tools, and domain-specific entities"""
    entities = {
        'skills': set(),
        'organizations': set(),
        'products': set(),
        'technologies': set()
    }

    for ent in doc.ents:
        if ent.label_ == "ORG":
            entities['organizations'].add(ent.text.lower())
        elif ent.label_ == "PRODUCT":
            entities['products'].add(ent.text.lower())

    return entities


def extract_technical_skills(text):
    """Extract technical skills using keyword matching"""

    tech_keywords = {
        'languages': [
            'python', 'java', 'javascript', 'c++', 'c#', 'ruby',
            'go', 'rust', 'php', 'swift', 'kotlin', 'typescript',
            'scala', 'r', 'matlab', 'sql', 'html', 'css'
        ],

        'frameworks': [
            'django', 'flask', 'fastapi', 'react', 'angular',
            'vue', 'spring', 'hibernate', 'nodejs', 'express',
            'rails', 'laravel', 'asp.net'
        ],

        'databases': [
            'mysql', 'postgresql', 'mongodb', 'oracle',
            'sql server', 'cassandra', 'redis',
            'elasticsearch', 'dynamodb'
        ],

        'tools': [
            'git', 'docker', 'kubernetes', 'jenkins',
            'aws', 'azure', 'gcp', 'linux',
            'bash', 'jira', 'confluence'
        ],

        'data': [
            'machine learning', 'deep learning', 'nlp', 'cv',
            'tensorflow', 'pytorch', 'scikit-learn',
            'pandas', 'numpy', 'spark', 'hadoop'
        ]
    }

    text_lower = text.lower()

    found_skills = {
        'languages': set(),
        'frameworks': set(),
        'databases': set(),
        'tools': set(),
        'data': set()
    }

    for category, skills in tech_keywords.items():
        for skill in skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                found_skills[category].add(skill)

    return found_skills


def lemmatize_tokens(doc):
    """Extract lemmatized tokens"""

    return set(
        token.lemma_.lower()
        for token in doc
        if not token.is_stop
        and not token.is_punct
        and len(token.text.strip()) > 2
    )


def calculate_semantic_similarity(resume_doc, job_doc):
    """Calculate semantic similarity only if vectors exist"""

    try:
        if (
            st.session_state.has_vectors and
            st.session_state.nlp_model.vocab.vectors_length > 0
        ):
            similarity = resume_doc.similarity(job_doc)
            return similarity * 100

    except Exception:
        pass

    return None


def calculate_contextual_match(resume_text, job_text):
    """Calculate contextual match without penalizing missing JD phrases"""

    nlp = st.session_state.nlp_model

    resume_doc = nlp(resume_text)
    job_doc = nlp(job_text)

    resume_chunks = set(
        chunk.text.lower()
        for chunk in resume_doc.noun_chunks
    )

    job_chunks = set(
        chunk.text.lower()
        for chunk in job_doc.noun_chunks
    )

    matching_chunks = resume_chunks.intersection(job_chunks)

    if resume_chunks:
        return (len(matching_chunks) / len(resume_chunks)) * 100

    return 0

def calculate_resume_score(pdf_text, job_description):
    """Main scoring function"""

    nlp = st.session_state.nlp_model

    resume_doc = nlp(pdf_text[:1000000])
    job_doc = nlp(job_description)

    scores = {}

    # --------------------------
    # Lemma Match
    # --------------------------
    resume_lemmas = lemmatize_tokens(resume_doc)
    job_lemmas = lemmatize_tokens(job_doc)

    matching_lemmas = resume_lemmas.intersection(job_lemmas)

    if resume_lemmas:
        scores['lemma_match'] = (
            len(matching_lemmas) / len(resume_lemmas)
        ) * 100
    else:
        scores['lemma_match'] = 0

    # --------------------------
    # Technical Skills Match
    # --------------------------
    resume_tech = extract_technical_skills(pdf_text)
    job_tech = extract_technical_skills(job_description)

    all_resume_tech = set()
    all_job_tech = set()

    for category in resume_tech.values():
        all_resume_tech.update(category)

    for category in job_tech.values():
        all_job_tech.update(category)

    matched_tech = all_resume_tech.intersection(all_job_tech)

    # Missing skills do not reduce score
    if all_resume_tech:
        scores['tech_match'] = (
            len(matched_tech) / len(all_resume_tech)
        ) * 100
    else:
        scores['tech_match'] = 0

    # --------------------------
    # Contextual Match
    # --------------------------
    scores['contextual_match'] = calculate_contextual_match(
        pdf_text,
        job_description
    )

    # --------------------------
    # Semantic Similarity
    # --------------------------
    semantic_sim = calculate_semantic_similarity(
        resume_doc,
        job_doc
    )

    if semantic_sim is not None:
        scores['semantic_match'] = semantic_sim
    else:
        scores['semantic_match'] = 0

    # --------------------------
    # Final Score
    # --------------------------
    final_score = (
        scores['lemma_match'] * 0.15 +
        scores['tech_match'] * 0.40 +
        scores['contextual_match'] * 0.20 +
        scores['semantic_match'] * 0.25
    )

    return min(final_score, 100), scores


def display_detailed_analysis(pdf_text, job_description, scores):
    st.markdown("### 📊 Score Breakdown")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Lemma Match", f"{scores['lemma_match']:.1f}%")

    with col2:
        st.metric("Tech Skills", f"{scores['tech_match']:.1f}%")

    with col3:
        st.metric("Contextual", f"{scores['contextual_match']:.1f}%")

    with col4:
        st.metric("Semantic", f"{scores['semantic_match']:.1f}%")

    st.markdown("### 🛠️ Technology Analysis")

    resume_tech = extract_technical_skills(pdf_text)
    job_tech = extract_technical_skills(job_description)

    all_resume_tech = set()
    all_job_tech = set()

    for category in resume_tech.values():
        all_resume_tech.update(category)

    for category in job_tech.values():
        all_job_tech.update(category)

    matched_tech = all_resume_tech.intersection(all_job_tech)
    missing_tech = all_job_tech - all_resume_tech

    if matched_tech:
        st.success(f"✅ Found: {', '.join(sorted(matched_tech))}")

    if missing_tech:
        st.warning(f"⚠️ Missing: {', '.join(sorted(missing_tech))}")

    if not all_job_tech:
        st.info("No specific technologies detected in job description")

# ==================== MAIN EXECUTION ====================

if analyze_resume and resume_file is not None and job_description.strip() != "":
    try:
        reader = PdfReader(resume_file)

        pdf_text = ""

        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                pdf_text += extracted

        if not pdf_text.strip():
            st.error(
                "Could not extract text from PDF. Please try another file."
            )

        else:
            final_score, scores = calculate_resume_score(
                pdf_text,
                job_description
            )

            st.markdown("---")

            if final_score >= 75:
                color = "green"
                emoji = "🎉"
                message = "Excellent Match!"

            elif final_score >= 50:
                color = "orange"
                emoji = "👍"
                message = "Good Match"

            else:
                color = "red"
                emoji = "📝"
                message = "Needs Improvement"

            st.markdown(
                f"""
                <h2 style='text-align: center; color: {color};'>
                {emoji} Your Resume Score: {final_score:.2f}%
                </h2>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                f"""
                <h4 style='text-align: center;'>
                {message}
                </h4>
                """,
                unsafe_allow_html=True
            )

            st.markdown("---")

            display_detailed_analysis(
                pdf_text,
                job_description,
                scores
            )

    except Exception as e:
        st.error(f"Error processing resume: {str(e)}")