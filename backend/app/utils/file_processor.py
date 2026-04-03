import os
from PyPDF2 import PdfReader
from docx import Document
import logging

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    try:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        return ""

def extract_text_from_docx(file_path):
    """Extract text from DOCX file"""
    try:
        text = ""
        doc = Document(file_path)
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {e}")
        return ""

def extract_text_from_txt(file_path):
    """Extract text from TXT file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read().strip()
        except Exception as e:
            logger.error(f"Error extracting text from TXT: {e}")
            return ""

def extract_text_from_file(file_path, file_type):
    """Extract text from file based on type"""
    file_type = file_type.lower()
    
    if file_type in ['pdf']:
        return extract_text_from_pdf(file_path)
    elif file_type in ['docx', 'doc']:
        return extract_text_from_docx(file_path)
    elif file_type in ['txt', 'text']:
        return extract_text_from_txt(file_path)
    else:
        logger.warning(f"Unsupported file type: {file_type}")
        return ""

def clean_text(text):
    """Clean and preprocess text"""
    import re
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?;:\'-]', '', text)
    
    # Remove excessive punctuation
    text = re.sub(r'([.!?,;:])\1+', r'\1', text)
    
    return text.strip()

def chunk_text(text, chunk_size=500, overlap=50):
    """Split text into chunks for vectorization"""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    
    return chunks

def extract_key_concepts(text, num_concepts=10):
    """Extract key concepts from text using simple TF-IDF"""
    from sklearn.feature_extraction.text import TfidfVectorizer
    
    sentences = text.split('.')
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) < 2:
        return []
    
    try:
        vectorizer = TfidfVectorizer(max_features=num_concepts, stop_words='english')
        vectorizer.fit(sentences)
        concepts = vectorizer.get_feature_names_out()
        return list(concepts)
    except Exception as e:
        logger.error(f"Error extracting concepts: {e}")
        return []

def summarize_text(text, max_sentences=3):
    """Simple text summarization"""
    sentences = text.split('.')
    sentences = [s.strip() + '.' for s in sentences if s.strip()]
    
    if len(sentences) <= max_sentences:
        return ' '.join(sentences)
    
    # Score sentences by word frequency
    words = text.split()
    word_freq = {}
    for word in words:
        word_freq[word.lower()] = word_freq.get(word.lower(), 0) + 1
    
    sentence_scores = {}
    for i, sentence in enumerate(sentences):
        for word in sentence.split():
            if word.lower() in word_freq:
                sentence_scores[i] = sentence_scores.get(i, 0) + word_freq[word.lower()]
    
    top_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:max_sentences]
    top_sentences = sorted(top_sentences)
    
    summary = ' '.join([sentences[i] for i in top_sentences])
    return summary
