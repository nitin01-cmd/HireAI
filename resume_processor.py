import pdfplumber
import pandas as pd
import re
from collections import Counter
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

def extract_key_skills(text):
    """
    Extract potential skills from text (words that might represent technical skills).
    
    Args:
        text (str): Text to extract skills from
        
    Returns:
        list: List of potential skill keywords
    """
    # Simple regex pattern to identify potential skill keywords
    # Looks for capitalized words, acronyms, and technical terms
    skill_pattern = r'\b([A-Z][a-z]+|[A-Z]{2,}|[a-z]+\+\+|[a-z]+#|[a-z]+\.js)\b'
    skills = re.findall(skill_pattern, text)
    
    # Add common lowercase technical skills
    common_skills = [
        'python', 'java', 'javascript', 'html', 'css', 'sql', 'nosql', 
        'react', 'angular', 'vue', 'node', 'express', 'django', 'flask',
        'tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit', 'aws', 'azure',
        'gcp', 'devops', 'agile', 'scrum', 'kanban', 'git', 'docker', 'kubernetes'
    ]
    
    # Check for common skills in lowercase text
    text_lower = text.lower()
    for skill in common_skills:
        if f' {skill} ' in f' {text_lower} ':
            skills.append(skill)
    
    return list(set(skills))

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

def identify_matching_skills(job_skills, resume_skills):
    """
    Identify skills from the resume that match the job requirements.
    
    Args:
        job_skills (list): List of skills extracted from job description
        resume_skills (list): List of skills extracted from resume
        
    Returns:
        tuple: (matching_skills, missing_skills)
    """
    # Convert to lowercase for case-insensitive matching
    job_skills_lower = [s.lower() for s in job_skills]
    resume_skills_lower = [s.lower() for s in resume_skills]
    
    # Find matching skills
    matching_skills = [s for s in resume_skills if s.lower() in job_skills_lower]
    
    # Find missing important skills
    missing_skills = [s for s in job_skills if s.lower() not in resume_skills_lower]
    
    return matching_skills, missing_skills
    
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
    
    # Extract potential skills from job description
    job_skills = extract_key_skills(job_description)
    
    # Process each resume
    results = []
    
    for pdf_file in uploaded_files:
        try:
            # Extract text from PDF
            resume_text = extract_text_from_pdf(pdf_file)
            
            if not resume_text.strip():
                print(f"Warning: No text extracted from {pdf_file.name}")
                continue
            
            # Extract skills from resume
            resume_skills = extract_key_skills(resume_text)
            
            # Identify matching and missing skills
            matching_skills, missing_skills = identify_matching_skills(job_skills, resume_skills)
                
            # Preprocess resume text
            processed_resume = preprocess_text(resume_text)
            
            # Calculate similarity
            similarity = calculate_similarity(processed_job_desc, processed_resume)
            
            # Add to results - just keep original format for backward compatibility
            results.append((pdf_file.name, similarity))
            
        except Exception as e:
            print(f"Error processing {pdf_file.name}: {str(e)}")
            
    # Sort by similarity score (descending)
    results.sort(key=lambda x: x[1], reverse=True)
    
    return results

def get_detailed_analysis(job_description, resume_text):
    """
    Get detailed analysis of a resume against a job description.
    This is a placeholder for future enhancement.
    
    Args:
        job_description (str): Job description text
        resume_text (str): Resume text
        
    Returns:
        dict: Analysis details
    """
    # Extract skills
    job_skills = extract_key_skills(job_description)
    resume_skills = extract_key_skills(resume_text)
    
    # Identify matching and missing skills
    matching_skills, missing_skills = identify_matching_skills(job_skills, resume_skills)
    
    # Calculate skill match percentage
    skill_match_pct = len(matching_skills) / len(job_skills) if job_skills else 0
    
    # Preprocess for similarity
    processed_job = preprocess_text(job_description)
    processed_resume = preprocess_text(resume_text)
    
    # Calculate similarity
    similarity = calculate_similarity(processed_job, processed_resume)
    
    # Return detailed analysis
    return {
        "similarity_score": similarity,
        "skill_match_percentage": skill_match_pct,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "resume_skills": resume_skills,
        "job_skills": job_skills
    }
