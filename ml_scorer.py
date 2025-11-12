from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
import numpy as np

# Load the Sentence-Transformer model globally to avoid reloading on every request
try:
    BERT_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    print(f"Error loading BERT model: {e}")
    BERT_MODEL = None


# --- A. TF-IDF Scoring ---
def calculate_tfidf_score(resume_text: str, jd_text: str) -> float:
    """Calculates Cosine Similarity using TF-IDF vectorization."""
    if not resume_text or not jd_text:
        return 0.0
        
    vectorizer = TfidfVectorizer(stop_words='english')
    vectors = vectorizer.fit_transform([resume_text, jd_text])
    
    tfidf_score = cosine_similarity(vectors[0], vectors[1])[0][0]
    return float(tfidf_score)


# --- B. BERT Scoring ---
def calculate_bert_score(resume_text: str, jd_text: str) -> float:
    """Calculates Semantic Cosine Similarity using BERT embeddings."""
    if BERT_MODEL is None or not resume_text or not jd_text:
        return 0.0
        
    embeddings = BERT_MODEL.encode([resume_text, jd_text], convert_to_tensor=True)
    
    bert_score = cos_sim(embeddings[0], embeddings[1]).item()
    return float(bert_score)


# --- C. Weighted Final Score (Placeholder for Skills/Experience logic) ---
def calculate_final_score(bert_score: float, tfidf_score: float, skill_match_percent: float = 0.8, experience_match_score: float = 1.0) -> float:
    """
    Calculates the final weighted score (0.0 to 1.0)
    """
    
    # Define weights (adjust these based on desired importance)
    W_BERT = 0.50
    W_TFIDF = 0.20
    W_SKILL = 0.20
    W_EXP = 0.10
    
    final_score = (W_BERT * bert_score) + \
                  (W_TFIDF * tfidf_score) + \
                  (W_SKILL * skill_match_percent) + \
                  (W_EXP * experience_match_score)
    
    return final_score