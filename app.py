# app.py (UPDATED)

import streamlit as st
import pandas as pd # Import pandas for the dataframe display
from pdf_parser import extract_text_from_pdf
from ml_scorer import calculate_tfidf_score, calculate_bert_score, calculate_final_score
from analysis_engine import compare_match_data # Make sure this import is present

# --- Function to apply custom CSS for aesthetics ---
def set_custom_css():
    st.markdown("""
        <style>
        /* General body styling */
        body {
            font-family: 'Segoe UI', sans-serif;
            color: #E0E0E0; /* Light gray text */
            background-color: #1a1a2e; /* Dark blue-purple background */
        }
        .stApp {
            background-color: #1a1a2e;
        }

        /* Title styling */
        h1 {
            color: #e94560; /* Vibrant red */
            text-align: center;
            font-size: 3.5em; /* Larger title */
            margin-bottom: 0.5em;
            text-shadow: 2px 2px 5px rgba(0,0,0,0.5); /* Subtle shadow */
        }
        h2 {
            color: #53BF9D; /* Greenish teal */
            font-size: 2em;
            margin-top: 1.5em;
            border-bottom: 2px solid #53BF9D;
            padding-bottom: 0.3em;
        }
        h3 {
            color: #f7b32b; /* Yellow/Orange */
            font-size: 1.5em;
            margin-top: 1em;
        }

        /* Text areas and file uploader */
        .stTextArea > label, .stFileUploader > label {
            color: #FFFFFF; /* White labels */
            font-size: 1.1em;
            font-weight: bold;
        }
        .stTextArea > div > div > textarea {
            background-color: #2e2e4a; /* Slightly lighter dark blue for input */
            color: #E0E0E0;
            border: 1px solid #53BF9D; /* Teal border */
            border-radius: 8px;
            padding: 10px;
        }
        .stFileUploader > div > div {
            background-color: #2e2e4a;
            border: 1px dashed #e94560; /* Dashed vibrant red border */
            border-radius: 8px;
            padding: 20px;
            color: #E0E0E0;
            text-align: center;
        }
        .stFileUploader > div > div > button {
            background-color: #e94560; /* Button matching title color */
            color: white;
            border-radius: 5px;
        }
        
        /* Buttons */
        .stButton > button {
            background-color: #e94560; /* Vibrant red button */
            color: white;
            font-weight: bold;
            padding: 0.75em 1.5em;
            border-radius: 10px;
            border: none;
            box-shadow: 3px 3px 5px rgba(0,0,0,0.3);
            transition: all 0.2s ease-in-out;
        }
        .stButton > button:hover {
            background-color: #FF6B81; /* Lighter red on hover */
            transform: translateY(-2px);
            box-shadow: 4px 4px 8px rgba(0,0,0,0.4);
        }

        /* Dataframe styling */
        .dataframe {
            background-color: #2e2e4a; /* Dark blue for table background */
            color: #E0E0E0;
            border-radius: 8px;
        }
        .dataframe th {
            background-color: #53BF9D; /* Teal headers */
            color: white;
            font-weight: bold;
            padding: 10px;
        }
        .dataframe td {
            padding: 10px;
        }
        .dataframe tr:nth-child(even) {
            background-color: #1f1f3a; /* Slightly different background for even rows */
        }
        
        /* Metric cards */
        [data-testid="stMetric"] {
            background-color: #2e2e4a; /* Dark background for metrics */
            border: 1px solid #f7b32b; /* Yellow border */
            border-radius: 10px;
            padding: 15px;
            box-shadow: 2px 2px 8px rgba(0,0,0,0.4);
        }
        [data-testid="stMetricLabel"] {
            color: #e94560; /* Vibrant red label */
            font-weight: bold;
        }
        [data-testid="stMetricValue"] {
            color: #53BF9D; /* Teal value */
            font-size: 2.5em;
        }

        /* Info box for report */
        .stAlert.info {
            background-color: #2e2e4a;
            color: #E0E0E0;
            border-left: 5px solid #f7b32b; /* Yellow left border */
            border-radius: 8px;
        }
        .stAlert p {
            color: #E0E0E0;
        }

        </style>
        """, unsafe_allow_html=True)


# --- Main Streamlit App ---
def main():
    st.set_page_config(page_title="AI Resume Screener", layout="wide")
    set_custom_css() # Apply custom CSS at the start

    st.title("AI Resume Screening System")

    # Initialize session state for storing results if not already present
    if 'ranked_results' not in st.session_state:
        st.session_state.ranked_results = []

    # --- INPUT SECTION ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("1. Job Description (JD)")
        job_description = st.text_area("Paste the Job Description Text", height=350)

    with col2:
        st.header("2. Resume Uploads")
        uploaded_files = st.file_uploader("Upload PDF Resumes", type="pdf", accept_multiple_files=True)
        
        # --- EXECUTION BUTTON ---
        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
        run_button = st.button("📈 Run Screening & Generate Report", use_container_width=True)

    # --- PROCESSING AND OUTPUT ---
    if run_button and job_description and uploaded_files:
        with st.spinner('Processing resumes and calculating scores...'):
            results = []
            
            for file in uploaded_files:
                # 1. Parse Resume Text
                resume_text = extract_text_from_pdf(file)
                
                # 2. Calculate ML Scores
                tfidf_score = calculate_tfidf_score(resume_text, job_description)
                bert_score = calculate_bert_score(resume_text, job_description)
                
                # 3. Calculate Weighted Final Score and get detailed report
                # compare_match_data now returns 3 values: skill_p, exp_s, report_data
                skill_p, exp_s, report_data = compare_match_data(resume_text, job_description)
                final_score = calculate_final_score(bert_score, tfidf_score, skill_p, exp_s)

                results.append({
                    "Candidate": file.name, 
                    "Final Score": final_score,
                    "BERT Score": bert_score, 
                    "TF-IDF Score": tfidf_score,
                    "Detailed Report": report_data
                })

            # Sort results by Final Score (Highest Match First)
            ranked_results = sorted(results, key=lambda x: x['Final Score'], reverse=True)
            
            # Store results in session state
            st.session_state.ranked_results = ranked_results
            st.session_state.candidate_names = [r['Candidate'] for r in ranked_results]
            
            st.success("Screening Complete!")

    # --- DISPLAY RESULTS (AFTER RUN BUTTON IS PRESSED) ---
    if st.session_state.ranked_results:
        ranked_results = st.session_state.ranked_results
        
        # --- RANKED LIST DISPLAY ---
        st.header("🏆 Ranked Candidate List")
        
        # Prepare data for a clean table
        display_data = []
        for i, r in enumerate(ranked_results):
            display_data.append({
                "Rank": i + 1,
                "Candidate": r['Candidate'], 
                "Final Match %": f"{r['Final Score'] * 100:.2f}%",
                "BERT (Semantic) Score": f"{r['BERT Score']:.4f}",
                "TF-IDF (Keyword) Score": f"{r['TF-IDF Score']:.4f}"
            })
        
        # Display the full ranked table
        st.dataframe(pd.DataFrame(display_data), use_container_width=True)

        # --- DETAILED REPORT SELECTION ---
        st.header("📝 AI Match Report (Detailed)")
        
        # Find the top candidate's name for the default selection
        default_candidate = ranked_results[0]['Candidate']
        
        # Dropdown to select the candidate for the detailed report
        selected_candidate_name = st.selectbox(
            "Select Candidate for Detailed Report:",
            options=st.session_state.candidate_names,
            index=st.session_state.candidate_names.index(default_candidate)
        )
        
        # Filter the results to get the selected candidate's data
        selected_candidate = next((r for r in ranked_results if r['Candidate'] == selected_candidate_name), None)
        
        if selected_candidate:
            # Display candidate info and metrics
            st.info(f"Report for: **{selected_candidate['Candidate']}**")
            
            col_d1, col_d2, col_d3 = st.columns(3)
            col_d1.metric("Final Match Score", f"{selected_candidate['Final Score'] * 100:.2f}%")
            col_d2.metric("BERT Score (Semantic)", f"{selected_candidate['BERT Score']:.4f}")
            col_d3.metric("TF-IDF Score (Keyword)", f"{selected_candidate['TF-IDF Score']:.4f}")
            
            # Display detailed skills and experience analysis from report_data
            st.subheader("Skills Breakdown")
            st.json(selected_candidate['Detailed Report']['Skills Analysis'])

            st.subheader("Experience Breakdown")
            st.json(selected_candidate['Detailed Report']['Experience Analysis'])
            
if __name__ == '__main__':
    main()