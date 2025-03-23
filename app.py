import streamlit as st
import pandas as pd
from resume_processor import process_resumes
import base64

# Page configuration
st.set_page_config(
    page_title="AI Resume Screener",
    page_icon="📄",
    layout="wide"
)

# Custom CSS styles
def local_css():
    st.markdown("""
    <style>
        /* Main container styling */
        .main {
            padding: 1rem 2rem;
            background-color: #f8f9fa;
        }
        
        /* Header styling */
        .big-title {
            font-size: 3rem !important;
            font-weight: bold !important;
            color: #4CAF50 !important;
            margin-bottom: 1.5rem !important;
            text-align: center;
        }
        
        /* Card styling */
        .card {
            border-radius: 10px;
            padding: 2rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            background-color: white;
        }
        
        /* Section headers */
        .section-header {
            color: #1E88E5;
            font-weight: 600;
            margin-bottom: 1rem;
            padding-left: 0.5rem;
            border-left: 4px solid #1E88E5;
        }
        
        /* Button styling */
        .stButton>button {
            width: 100%;
            background-color: #4CAF50;
            color: white;
            border-radius: 5px;
            padding: 0.5rem 1rem;
            font-weight: bold;
            border: none;
            transition: all 0.3s;
        }
        
        .stButton>button:hover {
            background-color: #388E3C;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        
        /* Results Table styling */
        .dataframe-container {
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        
        /* Score coloring */
        .high-score {
            color: #4CAF50;
            font-weight: bold;
        }
        
        .medium-score {
            color: #FB8C00;
            font-weight: bold;
        }
        
        .low-score {
            color: #E53935;
            font-weight: bold;
        }
        
        /* Footer styling */
        .footer {
            text-align: center;
            margin-top: 2rem;
            padding: 1rem;
            font-size: 0.8rem;
            color: #757575;
        }
        
        /* Divider line */
        .divider {
            height: 3px;
            background-color: #f0f0f0;
            margin: 1.5rem 0;
            border-radius: 2px;
        }
    </style>
    """, unsafe_allow_html=True)

# Apply custom CSS
local_css()

# Function to create a download link for the results
def get_table_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="resume_rankings.csv" class="download-link">Download CSV Results</a>'
    return href

def main():
    # Header section with logo and title
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        st.markdown('<h1 class="big-title">📄 AI Resume Screener</h1>', unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
            Find the best candidates by analyzing resumes against job descriptions using AI
        </div>
        """, unsafe_allow_html=True)
    
    # Main content
    col1, col2 = st.columns([1, 1], gap="large")
    
    # Job Description Input
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-header">Job Description</h2>', unsafe_allow_html=True)
        st.markdown("Enter the job requirements and qualifications below:")
        job_description = st.text_area(
            "",
            height=250,
            placeholder="Paste the complete job description here...",
            help="Include key skills, qualifications, and responsibilities for best results"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Resume Upload Section
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-header">Upload Resumes</h2>', unsafe_allow_html=True)
        st.markdown("Upload up to 10 PDF resumes to analyze:")
        uploaded_files = st.file_uploader(
            "",
            type=["pdf"],
            accept_multiple_files=True,
            help="Only PDF files are supported"
        )
        
        # Display number of uploaded files
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} resume(s) uploaded and ready for analysis")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Analysis button
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_button = st.button("🔍 Analyze Resumes")
    
    # Process resumes
    if analyze_button:
        if not job_description.strip():
            st.error("⚠️ Please enter a job description.")
        elif not uploaded_files:
            st.error("⚠️ Please upload at least one resume.")
        elif len(uploaded_files) > 10:
            st.error("⚠️ Maximum 10 files can be processed at once.")
        else:
            with st.spinner("🔄 Processing resumes... This may take a moment."):
                try:
                    # Process the resumes and get ranked results
                    results = process_resumes(job_description, uploaded_files)
                    
                    if not results:
                        st.error("⚠️ No valid text could be extracted from the uploaded resumes.")
                    else:
                        # Create a DataFrame for display
                        df_raw = pd.DataFrame(results)
                        df_raw.columns = ["Resume", "Similarity Score"]
                        
                        # Store raw scores
                        df_download = df_raw.copy()
                        df_download["Similarity Score"] = df_download["Similarity Score"].apply(lambda x: f"{x:.2%}")
                        
                        # Success message
                        st.success(f"✅ Successfully analyzed {len(results)} resume(s)!")
                        
                        # Results section
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.markdown('<h2 class="section-header">Resume Rankings</h2>', unsafe_allow_html=True)
                        
                        # Display table with scored results
                        st.markdown("Here are the resumes ranked by relevance to the job description:")
                        
                        # Define a function to color code the scores
                        def color_score(score_text):
                            score = float(score_text.strip('%')) / 100
                            if score >= 0.7:
                                return f'<span class="high-score">{score_text}</span>'
                            elif score >= 0.5:
                                return f'<span class="medium-score">{score_text}</span>'
                            else:
                                return f'<span class="low-score">{score_text}</span>'
                        
                        # Format the dataframe
                        df = df_raw.copy()
                        df["Similarity Score"] = df["Similarity Score"].apply(lambda x: f"{x:.2%}")
                        
                        # Display the table
                        st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
                        st.dataframe(
                            df,
                            column_config={
                                "Resume": "Resume Filename",
                                "Similarity Score": st.column_config.Column(
                                    "Match Score",
                                    help="Higher scores indicate better matches",
                                )
                            },
                            use_container_width=True,
                            hide_index=True
                        )
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Download link
                        st.markdown(get_table_download_link(df_download), unsafe_allow_html=True)
                        
                        # Interpretation guide
                        st.markdown('<div style="margin-top: 1.5rem;">', unsafe_allow_html=True)
                        st.markdown("### How to Interpret Results")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown("""
                            <div style="padding: 1rem; border-radius: 5px; background-color: #E8F5E9; margin-bottom: 0.5rem;">
                                <span style="color: #4CAF50; font-weight: bold;">70% - 100%</span>
                            </div>
                            <p style="font-size: 0.9rem;">Strong matches — these candidates closely match the job requirements</p>
                            """, unsafe_allow_html=True)
                            
                        with col2:
                            st.markdown("""
                            <div style="padding: 1rem; border-radius: 5px; background-color: #FFF3E0; margin-bottom: 0.5rem;">
                                <span style="color: #FB8C00; font-weight: bold;">50% - 69%</span>
                            </div>
                            <p style="font-size: 0.9rem;">Moderate matches — consider these candidates, may need additional screening</p>
                            """, unsafe_allow_html=True)
                            
                        with col3:
                            st.markdown("""
                            <div style="padding: 1rem; border-radius: 5px; background-color: #FFEBEE; margin-bottom: 0.5rem;">
                                <span style="color: #E53935; font-weight: bold;">0% - 49%</span>
                            </div>
                            <p style="font-size: 0.9rem;">Low matches — these candidates may not meet core requirements</p>
                            """, unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                except Exception as e:
                    st.error(f"⚠️ An error occurred during processing: {str(e)}")
    
    # Footer
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('''
    <div class="footer">
        <p>AI Resume Screener | NLP-powered resume matching tool</p>
        <p>Upload your resumes in PDF format for best results</p>
    </div>
    ''', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
