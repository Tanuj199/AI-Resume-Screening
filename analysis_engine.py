# analysis_engine.py (COMPLETE UPDATED CODE)

import re
from typing import List, Tuple, Dict, Any

# Define a normalization map for common technical abbreviations
SKILL_NORMALIZATION_MAP = {
    "ML": "Machine Learning",
    "NLP": "Natural Language Processing",
    "DL": "Deep Learning",
    "CV": "Computer Vision",
    "DSA": "Data Structures and Algorithms",
    # Add other common pairs as needed
}

# --- 1. Dynamic Skill Extraction Logic ---

def extract_candidate_skills_from_jd(jd_text: str) -> List[str]:
    """
    Dynamically extracts potential technical skills and keywords from the Job Description.
    """
    
    candidate_skills = set()
    
    # Target specific sections/phrasing common in tech JDs (e.g., lists, framework names)
    keywords_of_interest = re.findall(r'[A-Z]{2,}[a-z]+|[A-Z]{2,}(?:\/[A-Z]{2,})?|'
                                     r'(?:Python|PyTorch|TensorFlow|AWS|Azure|GCP|Docker|Kubernetes|Git|SQL)\b', 
                                     jd_text)
    
    # Add common technology abbreviations explicitly
    common_tech_terms = [
        "Python", "TensorFlow", "PyTorch", "scikit-learn", "Pandas", "NumPy",
        "BERT", "TF-IDF", "NLP", "Machine Learning", "Deep Learning", 
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Git", "SQL",
        "Flask", "FastAPI", "SageMaker", "MLOps", "RoBERTa", "Keras", "Java", "C++"
    ]
    
    for term in common_tech_terms:
        if re.search(r'\b' + re.escape(term) + r'\b', jd_text, re.IGNORECASE):
            candidate_skills.add(term)

    # Filter and clean capitalized findings
    for keyword in keywords_of_interest:
        # Ignore very short common words like 'To', 'A', 'In', or common titles
        if len(keyword) > 2 and keyword.lower() not in ['model', 'deep', 'data', 'software', 'engineer', 'developer', 'systems', 'design', 'testing']:
            candidate_skills.add(keyword)
            
    # Remove obvious duplicates based on case (e.g., Python vs PYTHON)
    unique_skills = set()
    lower_skills = set()
    for skill in candidate_skills:
        if skill.lower() not in lower_skills:
            unique_skills.add(skill)
            lower_skills.add(skill.lower())
            
    return sorted(list(unique_skills))


# --- 2. Skill Extraction and Comparison Logic ---

def extract_and_match_skills(resume_text: str, jd_text: str) -> Tuple[Dict[str, List[str]], float]:
    """
    Dynamically extracts required skills from JD and compares them to the resume,
    incorporating normalization to handle abbreviations vs. full names.
    """
    
    # Step 1: Dynamically determine the required skills from the JD
    jd_required_skills = extract_candidate_skills_from_jd(jd_text)
    
    # Step 2: Helper function to find skills in a given text
    def get_found_skills(text, required_skills):
        found_skills = set()
        
        for skill in required_skills:
            # 1. Check for the skill exactly
            if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
                found_skills.add(skill)
                continue
            
            # 2. Check for the normalized/alternate form (e.g., 'ML' for 'Machine Learning')
            # Look up in the map (Abbreviation -> Full Form)
            full_form = SKILL_NORMALIZATION_MAP.get(skill.upper())
            if full_form and re.search(r'\b' + re.escape(full_form) + r'\b', text, re.IGNORECASE):
                found_skills.add(skill)
                continue

            # 3. Reverse check: If the skill is a long name, check for its common abbreviation
            reverse_abbr = next((abbr for abbr, full in SKILL_NORMALIZATION_MAP.items() if full.upper() == skill.upper()), None)
            if reverse_abbr and re.search(r'\b' + re.escape(reverse_abbr) + r'\b', text, re.IGNORECASE):
                found_skills.add(skill)
                continue
        
        return found_skills

    # 3. Identify target skills present in the resume
    resume_found_skills = get_found_skills(resume_text, jd_required_skills)
    
    # 4. Comparison
    # Normalize skills to avoid double counting in the final report list (e.g., "ML" vs "Machine Learning")
    
    # Create a map for normalization based on the JD required skills
    normalized_jd_map = {}
    for skill in jd_required_skills:
        # Check for full form's abbreviation
        key = next((abbr.upper() for abbr, full in SKILL_NORMALIZATION_MAP.items() if full.upper() == skill.upper()), skill.upper())
        # If it's an abbreviation itself
        if skill.upper() in SKILL_NORMALIZATION_MAP:
             key = skill.upper()
        
        normalized_jd_map[key] = skill # Store the original JD casing
        
    # Create a normalized set of found skills keys
    normalized_found_keys = set()
    for skill in resume_found_skills:
        key = next((abbr.upper() for abbr, full in SKILL_NORMALIZATION_MAP.items() if full.upper() == skill.upper()), skill.upper())
        if skill.upper() in SKILL_NORMALIZATION_MAP:
             key = skill.upper()
        normalized_found_keys.add(key)


    # The final matched and missing skills lists contain the original JD casing
    matched_skills = []
    missing_skills = []

    for key, original_skill in normalized_jd_map.items():
        if key in normalized_found_keys:
            matched_skills.append(original_skill)
        else:
            missing_skills.append(original_skill)
    
    # Ensure lists are unique, though the set logic should largely prevent this
    matched_skills = sorted(list(set(matched_skills)))
    missing_skills = sorted(list(set(missing_skills)))

    # 5. Calculate Match Percentage
    total_jd_skills = len(jd_required_skills)
    if total_jd_skills == 0:
        match_percentage = 0.0
    else:
        # Use the length of the matched skills list
        match_percentage = len(matched_skills) / total_jd_skills

    analysis_report = {
        "Keywords Matched": matched_skills,
        "Missing Skills": missing_skills,
        "JD Requirements Found": len(matched_skills),
        "Total JD Requirements": total_jd_skills
    }

    return analysis_report, match_percentage

# --- 3. Final Combined Analysis Function ---

# FIX: Updated return type hint and added placeholder for experience score to match app.py
def compare_match_data(resume_text: str, jd_text: str) -> Tuple[float, float, Dict[str, Any]]:
    """
    Runs skill analysis and compiles the final report data.

    Returns:
        skill_match_percent: float (0.0-1.0)
        experience_score: float (0.0-1.0) - Placeholder
        report_data: Dictionary containing detailed analysis for display.
    """
    # Run Skill Analysis
    skills_report, skill_match_percent = extract_and_match_skills(resume_text, jd_text)
    
    # FIX: Placeholder for non-implemented Experience Score
    experience_score = 1.0 
    
    # Compile the final report structure
    report_data = {
        "Skills Analysis": skills_report,
        # FIX: Added the missing "Experience Analysis" key
        "Experience Analysis": {"Note": "Experience analysis feature is under development. Placeholder score of 1.0 used."}
    }
    
    # FIX: Return all three expected values
    return skill_match_percent, experience_score, report_data