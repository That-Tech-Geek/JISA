import streamlit as st
import cohere
import pandas as pd
import json

# Initialize Cohere API
COHERE_API_KEY = st.secrets["API-TOKEN"]  # Replace with your API key
co = cohere.Client(COHERE_API_KEY)

st.title("AI-Powered Job Interview Form & Screening")

# Create tabs
tab1, tab2 = st.tabs(["Interview Form Generator", "Applicant Screening"])

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
    uploaded_file = st.file_uploader("Upload Applicant Responses (CSV)", type=["csv"])
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("Uploaded Data:", df.head())
        
        if st.button("Evaluate Applications"):
            evaluation_results = []
            for index, row in df.iterrows():
                answers = json.dumps(row.to_dict())
                response = co.generate(
                    model='command',
                    prompt=f"Evaluate this job application based on the following answers: {answers}",
                    max_tokens=300
                )
                evaluation = response.generations[0].text.strip()
                evaluation_results.append(evaluation)
            
            df["Evaluation"] = evaluation_results
            st.write("Evaluation Results:", df)
            st.download_button("Download Results", df.to_csv(index=False), file_name="evaluated_applicants.csv")
