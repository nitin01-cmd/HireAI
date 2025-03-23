import pdfplumber
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from text_utils import preprocess_text

def extract_text_from_pdf(pdf_file):
    """
    Extract text from a PDF file using pdfplumber.
    
    Args:
        pdf_file: Uploaded PDF file object
        
    Returns:
        str: Extracted text from the PDF
    """
    try:
        text = ""
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    except Exception as e:
        print(f"Error extracting text from {pdf_file.name}: {str(e)}")
        return ""

def calculate_similarity(job_description, resume_text):
    """
    Calculate cosine similarity between job description and resume text.
    
    Args:
        job_description (str): Preprocessed job description
        resume_text (str): Preprocessed resume text
        
    Returns:
        float: Similarity score between 0 and 1
    """
    # Create a TF-IDF vectorizer
    vectorizer = TfidfVectorizer()
    
    # Fit and transform the texts
    try:
        tfidf_matrix = vectorizer.fit_transform([job_description, resume_text])
        
        # Calculate cosine similarity
        cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return cosine_sim
    except Exception as e:
        print(f"Error calculating similarity: {str(e)}")
        return 0.0
    
def process_resumes(job_description, uploaded_files):
    """
    Process multiple resumes and rank them by similarity to job description.
    
    Args:
        job_description (str): Job description text
        uploaded_files (list): List of uploaded PDF files
        
    Returns:
        list: List of tuples containing (filename, similarity_score)
    """
    # Preprocess job description
    processed_job_desc = preprocess_text(job_description)
    
    # Process each resume
    results = []
    
    for pdf_file in uploaded_files:
        try:
            # Extract text from PDF
            resume_text = extract_text_from_pdf(pdf_file)
            
            if not resume_text.strip():
                print(f"Warning: No text extracted from {pdf_file.name}")
                continue
                
            # Preprocess resume text
            processed_resume = preprocess_text(resume_text)
            
            # Calculate similarity
            similarity = calculate_similarity(processed_job_desc, processed_resume)
            
            # Add to results
            results.append((pdf_file.name, similarity))
            
        except Exception as e:
            print(f"Error processing {pdf_file.name}: {str(e)}")
            
    # Sort by similarity score (descending)
    results.sort(key=lambda x: x[1], reverse=True)
    
    return results
