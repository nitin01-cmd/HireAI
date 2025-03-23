import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download necessary NLTK resources
def download_nltk_resources():
    """Download required NLTK resources if not already present."""
    try:
        # Download essential resources directly, without checking first
        nltk.download('stopwords', quiet=True)
        nltk.download('wordnet', quiet=True)
        print("Successfully downloaded NLTK resources")
    except Exception as e:
        print(f"Error downloading NLTK resources: {str(e)}")

# Call this function to ensure resources are downloaded
download_nltk_resources()

def preprocess_text(text):
    """
    Preprocess text by converting to lowercase, removing special characters,
    removing stopwords, and lemmatizing.
    
    Args:
        text (str): Raw text to be preprocessed
        
    Returns:
        str: Preprocessed text
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters and numbers
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    # Simple tokenization by splitting on whitespace
    tokens = text.split()
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words]
    
    # Lemmatize
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(word) for word in filtered_tokens]
    
    # Join tokens back into text
    processed_text = ' '.join(lemmatized_tokens)
    
    return processed_text
