import streamlit as st
import pandas as pd
from resume_processor import process_resumes

# Page configuration
st.set_page_config(
    page_title="AI Resume Screener",
    page_icon="📄",
    layout="wide"
)

def main():
    # Header section
    st.title("AI Resume Screener")
    st.markdown("""
    This application helps you find the most relevant resumes for a job posting.
    Upload PDF resumes and enter a job description to get started.
    """)
    
    # Job Description Input
    st.header("Job Description")
    job_description = st.text_area(
        "Enter the job description here:",
        height=200,
        placeholder="Paste the job description here..."
    )
    
    # Resume Upload Section
    st.header("Upload Resumes")
    st.markdown("Upload multiple PDF resumes to analyze (max 10 files).")
    
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=["pdf"],
        accept_multiple_files=True
    )
    
    if st.button("Analyze Resumes"):
        if not job_description.strip():
            st.error("Please enter a job description.")
        elif not uploaded_files:
            st.error("Please upload at least one resume.")
        elif len(uploaded_files) > 10:
            st.error("Maximum 10 files can be processed at once.")
        else:
            with st.spinner("Processing resumes... This may take a moment."):
                try:
                    # Process the resumes and get ranked results
                    results = process_resumes(job_description, uploaded_files)
                    
                    if not results:
                        st.error("No valid text could be extracted from the uploaded resumes.")
                    else:
                        # Display results
                        st.success(f"Successfully analyzed {len(results)} resume(s)!")
                        
                        # Create a DataFrame for display
                        df = pd.DataFrame(results)
                        df.columns = ["Resume", "Similarity Score"]
                        df["Similarity Score"] = df["Similarity Score"].apply(lambda x: f"{x:.2%}")
                        
                        # Display results in a table
                        st.header("Resume Rankings")
                        st.markdown("Here are the resumes ranked by relevance to the job description:")
                        st.dataframe(
                            df,
                            use_container_width=True,
                            hide_index=True
                        )
                        
                        # Provide some interpretation
                        st.info("""
                        **How to interpret the results:**
                        - Higher percentage scores indicate better matches to the job description
                        - Scores above 70% typically indicate strong matches
                        - Consider reviewing all resumes with scores above 50%
                        """)
                except Exception as e:
                    st.error(f"An error occurred during processing: {str(e)}")

if __name__ == "__main__":
    main()
