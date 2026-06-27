import streamlit as st
from pypdf import PdfReader
import spacy
import re
import warnings

# Suppress spacy warnings
warnings.filterwarnings("ignore", message=".*The model you're using has no word vectors.*")
warnings.filterwarnings("ignore")

# Initialize session state
if 'nlp_model' not in st.session_state:
    try:
        st.session_state.nlp_model = spacy.load("en_core_web_md")
    except:
        try:
            st.session_state.nlp_model = spacy.load("en_core_web_sm")
        except:
            st.session_state.nlp_model = spacy.blank("en")

st.set_page_config(page_title="Resume Score Checker", page_icon="logo.png", layout=None, initial_sidebar_state=None, menu_items=None)

with st.container(horizontal=True):
    st.space("stretch")
    st.image("logo.png", width=100)
    st.space("stretch")

st.title("Technical Resume Score Checker", text_alignment="center")
st.text("Upload you resume and paste the JD of the job to analyze your resume against any job description and receive an intelligent ATS match score with actionable insights.", text_alignment="center")

resume_file = st.file_uploader("Upload your Resume:", type="pdf", accept_multiple_files=False)  
job_description = st.text_area("Paste the Job Description:", height=300)

with st.container(horizontal=True):
    st.space("stretch")
    analyze_resume = st.button("Calculate Resume Score",type="primary")
    st.space("stretch")

# ==================== ADVANCED NLP FUNCTIONS ====================

def extract_technical_skills(text):
    """Extract technical skills using keyword matching"""
    tech_keywords = {
        'languages': ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'go', 'rust', 'php', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'sql', 'html', 'css', 'perl', 'groovy', 'lua', 'dart', 'elixir', 'erlang', 'clojure', 'haskell', 'f#'],
        'frameworks': ['django', 'flask', 'fastapi', 'react', 'angular', 'vue', 'svelte', 'nextjs', 'nuxt', 'spring', 'spring boot', 'hibernate', 'nodejs', 'node.js', 'express', 'rails', 'laravel', 'symfony', 'asp.net', '.net core', 'asp.net core', 'gin', 'echo', 'fiber', 'actix'],
        'databases': ['mysql', 'postgresql', 'postgres', 'mongodb', 'oracle', 'sql server', 'cassandra', 'redis', 'elasticsearch', 'dynamodb', 'firestore', 'couchdb', 'neo4j', 'mariadb', 'sqlite'],
        'tools': ['git', 'docker', 'kubernetes', 'k8s', 'jenkins', 'gitlab', 'github', 'circleci', 'travis', 'aws', 'azure', 'gcp', 'google cloud', 'linux', 'bash', 'shell', 'jira', 'confluence', 'slack', 'terraform', 'ansible', 'prometheus', 'grafana'],
        'data': ['machine learning', 'deep learning', 'nlp', 'cv', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'spark', 'hadoop', 'kafka', 'airflow', 'dbt', 'tableau', 'power bi', 'data science']
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
    """Extract lemmatized tokens (root form of words)"""
    return set(
        token.lemma_.lower()
        for token in doc
        if not token.is_stop and not token.is_punct and len(token.text.strip()) > 2
    )

def calculate_tfidf_similarity(text1, text2):
    """Calculate similarity using TF-IDF inspired approach (fallback method)"""
    words1 = set(re.findall(r'\b\w+\b', text1.lower())) - {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did'}
    words2 = set(re.findall(r'\b\w+\b', text2.lower())) - {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did'}
    
    if not words2:
        return 0
    
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    if union == 0:
        return 0
    
    similarity = (intersection / union) * 100
    return similarity

def calculate_semantic_similarity(resume_doc, job_doc):
    """Calculate semantic similarity between resume and job description"""
    try:
        if hasattr(resume_doc, 'vector') and resume_doc.vector_norm > 0 and job_doc.vector_norm > 0:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                similarity = resume_doc.similarity(job_doc)
                return similarity * 100
    except:
        pass
    return None

def calculate_contextual_match(resume_text, job_text):
    """Calculate match based on noun chunks and phrases"""
    nlp = st.session_state.nlp_model
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        resume_doc = nlp(resume_text[:500000])
        job_doc = nlp(job_text)
    
    resume_chunks = set(chunk.text.lower() for chunk in resume_doc.noun_chunks)
    job_chunks = set(chunk.text.lower() for chunk in job_doc.noun_chunks)
    
    if job_chunks:
        matching_chunks = resume_chunks.intersection(job_chunks)
        return (len(matching_chunks) / len(job_chunks)) * 100
    return 0

def calculate_resume_score(pdf_text, job_description):
    """Main scoring function with multiple metrics"""
    nlp = st.session_state.nlp_model
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        resume_doc = nlp(pdf_text[:1000000])
        job_doc = nlp(job_description)
    
    scores = {}
    
    # 1. Lemmatized word matching (15%)
    resume_lemmas = lemmatize_tokens(resume_doc)
    job_lemmas = lemmatize_tokens(job_doc)
    if job_lemmas:
        lemma_match = len(resume_lemmas.intersection(job_lemmas)) / len(job_lemmas)
        scores['lemma_match'] = lemma_match * 100
    else:
        scores['lemma_match'] = 0
    
    # 2. Technical skills matching (40%)
    # BONUS SYSTEM - Only reward matched skills, don't penalize missing ones
    resume_tech = extract_technical_skills(pdf_text)
    job_tech = extract_technical_skills(job_description)
    
    all_job_tech = set()
    for category in job_tech.values():
        all_job_tech.update(category)
    
    all_resume_tech = set()
    for category in resume_tech.values():
        all_resume_tech.update(category)
    
    # Calculate match based on matched skills
    matched_tech_count = len(all_resume_tech.intersection(all_job_tech))
    
    if matched_tech_count > 0:
        # If resume has any matching skills, give credit (bonus system)
        # More matches = higher score, but no penalty for missing skills
        scores['tech_match'] = min(matched_tech_count * 20, 100)  # Each match = 20 points, max 100
    else:
        # No matching skills found, but don't heavily penalize
        scores['tech_match'] = 0
    
    # 3. Contextual phrase matching (20%)
    scores['contextual_match'] = calculate_contextual_match(pdf_text, job_description)
    
    # 4. Semantic similarity (25%)
    semantic_sim = calculate_semantic_similarity(resume_doc, job_doc)
    if semantic_sim is not None:
        scores['semantic_match'] = semantic_sim
    else:
        scores['semantic_match'] = calculate_tfidf_similarity(pdf_text, job_description)
    
    # Weighted scoring
    final_score = (
        scores['lemma_match'] * 0.15 +
        scores['tech_match'] * 0.40 +
        scores['contextual_match'] * 0.20 +
        scores['semantic_match'] * 0.25
    )
    
    return min(final_score, 100), scores, all_resume_tech, all_job_tech

def display_detailed_analysis(final_score, scores, all_resume_tech, all_job_tech):
    
    # Extract and display matched technologies
    st.markdown("### 🛠️ Matched Technologies")
    
    matched_tech = all_resume_tech.intersection(all_job_tech)
    missing_tech = all_job_tech - all_resume_tech
    
    if matched_tech:
        st.success(f"✅ Found: {', '.join(sorted(matched_tech))}")
    else:
        st.info("No matching technologies found")
    
    if missing_tech:
        st.warning(f"⚠️ Missing: {', '.join(sorted(missing_tech))}")

def generate_resume_suggestions(scores, all_resume_tech, all_job_tech, pdf_text):
    st.markdown("### 💡 Suggestions to Improve Your Resume")

    suggestions = []

    # Missing technical skills
    missing_tech = all_job_tech - all_resume_tech

    if missing_tech:
        suggestions.append(
            f"Consider adding experience or projects involving: "
            f"{', '.join(sorted(missing_tech))}."
        )

    # Weak technical match
    if scores['tech_match'] < 40:
        suggestions.append(
            "Include more technical skills relevant to the job description "
            "in your Skills section."
        )

    # Weak semantic match
    if scores['semantic_match'] < 50:
        suggestions.append(
            "Try aligning your resume wording with the terminology used in the job description."
        )

    # Weak contextual match
    if scores['contextual_match'] < 40:
        suggestions.append(
            "Add more project descriptions and work experience details that reflect the responsibilities in the job description."
        )

    # Weak keyword match
    if scores['lemma_match'] < 40:
        suggestions.append(
            "Use more keywords from the job description naturally throughout your resume."
        )

    # Check for projects section
    if "project" not in pdf_text.lower():
        suggestions.append(
            "Add a Projects section to demonstrate practical experience."
        )

    # Check for certifications
    if "certification" not in pdf_text.lower() and "certificate" not in pdf_text.lower():
        suggestions.append(
            "Adding relevant certifications can improve ATS visibility."
        )

    # Check for achievements
    achievement_words = [
        "improved", "increased", "reduced", "optimized",
        "developed", "implemented", "designed", "built"
    ]

    if not any(word in pdf_text.lower() for word in achievement_words):
        suggestions.append(
            "Use action verbs and measurable achievements such as "
            "'Improved API response time by 30%' or "
            "'Developed a scalable microservice architecture'."
        )

    # Positive feedback
    if not suggestions:
        st.success(
            "🎉 Your resume already aligns very well with this job description."
        )
    else:
        with st.container(border=True):
            for suggestion in suggestions:
                st.text(f"✨ {suggestion}")
            

def application_recommendation(final_score, all_resume_tech, all_job_tech):
    st.markdown("### 🎯 Application Recommendation")

    matched_skills = len(all_resume_tech.intersection(all_job_tech))
    total_jd_skills = len(all_job_tech)

    skill_coverage = (
        (matched_skills / total_jd_skills) * 100
        if total_jd_skills > 0 else 100
    )

    if final_score >= 80 and skill_coverage >= 60:
        st.info(
            "🚀 Strongly Recommended to Apply\n\n"
            "Your resume aligns very well with this job description."
        )

    elif final_score >= 65 and skill_coverage >= 40:
        st.info(
            "👍 Recommended to Apply\n\n"
            "You meet many of the requirements and have a competitive profile."
        )

    elif final_score >= 50:
        st.info(
            "⚠️ Apply if You Can Demonstrate Missing Skills\n\n"
            "You match some requirements, but your application would be stronger "
            "with additional experience or projects related to the missing skills."
        )

    else:
        st.error(
            "❌ Consider Upskilling Before Applying\n\n"
            "Your profile currently does not align closely with this role."
        )



# ==================== MAIN EXECUTION ====================

if analyze_resume and resume_file is not None and job_description.strip() != "":
    try:
        # Extract text from PDF
        reader = PdfReader(resume_file)
        pdf_text = ""
        for page in reader.pages:
            pdf_text += page.extract_text()
        
        if not pdf_text.strip():
            st.error("Could not extract text from PDF. Please try another file.")
        else:
            # Calculate score with warning suppression
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                final_score, scores, all_resume_tech, all_job_tech = calculate_resume_score(pdf_text, job_description)
            
            # Display main score with visual indicator
            st.markdown("---")
            
            # Color-coded score display
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
            
            st.markdown(f"<h2 style='text-align: center; color: {color};'>{emoji} Your Resume Score: {final_score:.2f}%</h2>", unsafe_allow_html=True)
            st.markdown(f"<h4 style='text-align: center;'>{message}</h4>", unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Display detailed analysis
            display_detailed_analysis(
                final_score,
                scores,
                all_resume_tech,
                all_job_tech
            )

            application_recommendation(
                final_score,
                all_resume_tech,
                all_job_tech
            )
            
            generate_resume_suggestions(
                scores,
                all_resume_tech,
                all_job_tech,
                pdf_text
            )
            
    except Exception as e:
        st.error(f"Error processing resume: {str(e)}")