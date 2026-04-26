import streamlit as st
from PyPDF2 import PdfReader
import spacy
from spacy.matcher import PhraseMatcher

st.set_page_config(page_title="Resume Score Checker", page_icon="logo.png", layout=None, initial_sidebar_state=None, menu_items=None)


with st.container(horizontal=True):
    st.space("stretch")
    st.image("logo.png", width=100)
    st.space("stretch")

st.title("Resume Score Checker",text_alignment="center")
st.text("Upload you resume and paste the JD of the job and see how your resume matches with the job you are applying for by checking your ATS score")

resume_file = st.file_uploader("Upload your Resume:", type="pdf", accept_multiple_files=False)  

job_description = st.text_area("Paste the Job Description:",height=300)

with st.container(horizontal=True):
    st.space("stretch")
    analyze_resume=st.button("Calculate Resume Score")
    st.space("stretch")


if analyze_resume and resume_file is not None and job_description.strip() != "":
    reader = PdfReader(resume_file)

    pdf_text = ""
    for page in reader.pages:
        pdf_text += page.extract_text()

    # pdf_container=st.container(height=500)
    # pdf_container.write(pdf_text)


    try:
        nlp = spacy.load("en_core_web_sm")
    except:
        nlp = spacy.blank("en")

    # Process text
    resume_doc = nlp(pdf_text)
    job_desc_doc = nlp(job_description)

    # Remove stopwords + punctuation
    resume_words = set(
        token.text.lower()
        for token in resume_doc
        if not token.is_stop and not token.is_punct
    )

    job_words = set(
        token.text.lower()
        for token in job_desc_doc
        if not token.is_stop and not token.is_punct
    )

    # Calculate match
    matched_words = resume_words.intersection(job_words)

    score = (len(matched_words) / len(job_words)) * 100 if job_words else 0

    print(len(matched_words))
    print(len(job_words))

    st.write(f"Your Resume Score: {score:.2f}%")

