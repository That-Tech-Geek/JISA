import streamlit as st
import cohere
import pandas as pd
import json

# Initialize Cohere API
COHERE_API_KEY = "your_cohere_api_key"  # Replace with your API key
co = cohere.Client(COHERE_API_KEY)

st.title("AI-Powered Job Interview Form & Screening")

# Create tabs
tab1, tab2, tab3 = st.tabs(["Interview Form Generator", "Applicant Screening", "Applicant Tracking System (ATS)"])

with tab1:
    st.header("Generate Job Interview Form")
    job_description = st.text_area("Enter Job Description:")
    
    if st.button("Generate Interview Questions"):
        if job_description:
            response = co.generate(
                model='command',
                prompt=f"Create a structured job interview questionnaire for the following job description: {job_description}",
                max_tokens=500
            )
            questions = response.generations[0].text.strip()
            st.session_state['questions'] = questions
            st.success("Interview form generated successfully!")
            st.text_area("Generated Questions:", value=questions, height=300)
        else:
            st.error("Please enter a job description.")
    
    if 'questions' in st.session_state:
        st.download_button("Download Form", st.session_state['questions'], file_name="interview_form.txt")

with tab2:
    st.header("Applicant Screening")
    uploaded_file = st.file_uploader("Upload Applicant Responses (DOCX)", type=["docx"])
    job_description = st.text_area("Enter Job Description for Screening:")
    
    if uploaded_file is not None and job_description:
        df = pd.read_csv(uploaded_file, encoding="utf-8")
        st.write("Uploaded Data:", df.head())
        
        if st.button("Evaluate Applications"):
            evaluation_results = []
            for index, row in df.iterrows():
                answers = json.dumps(row.to_dict())
                response = co.generate(
                    model='command',
                    prompt=f"Evaluate this job application based on the following job description: {job_description} and the applicant's answers: {answers}. Provide a detailed hiring recommendation.",
                    max_tokens=300
                )
                evaluation = response.generations[0].text.strip()
                evaluation_results.append(evaluation)
            
            df["Evaluation"] = evaluation_results
            st.write("Evaluation Results:", df)
            st.download_button("Download Results", df.to_csv(index=False), file_name="evaluated_applicants.csv")

with tab3:
    st.header("Applicant Tracking System (ATS)")
    uploaded_resume = st.file_uploader("Upload Resumes (CSV)", type=["csv"])
    job_keywords = st.text_area("Enter Key Job Keywords (comma-separated):")
    
    if uploaded_resume is not None and job_keywords:
        try:
            df_resumes = pd.read_csv(uploaded_resume, encoding="utf-8")
            keywords = job_keywords.split(",")
            
            match_scores = []
            for index, row in df_resumes.iterrows():
                resume_text = json.dumps(row.to_dict())
                response = co.generate(
                    model='command',
                    prompt=f"Analyze the following resume: {resume_text}. Compare it against these job keywords: {keywords}. Provide a match percentage and a short summary of fit.",
                    max_tokens=300
                )
                match_score = response.generations[0].text.strip()
                match_scores.append(match_score)
            
            df_resumes["Match Score"] = match_scores
            st.write("ATS Results:", df_resumes)
            st.download_button("Download ATS Results", df_resumes.to_csv(index=False), file_name="ats_results.csv")
        except Exception as e:
            st.error(f"Error reading file: {e}")
