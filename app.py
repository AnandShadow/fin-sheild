import os
import io
import json
import requests
import streamlit as st
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv

# Set Streamlit page config
st.set_page_config(
    page_title="Forensic Scam Analyzer",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Dark UI
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

/* Global Font & Background overrides */
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Outfit', sans-serif;
    background-color: #0b0f19;
    color: #e2e8f0;
}

/* Custom Header styling */
.header-container {
    background: linear-gradient(135deg, #111827 0%, #0b0f19 100%);
    padding: 2.5rem;
    border-radius: 16px;
    border: 1px solid #1f2937;
    margin-bottom: 2.5rem;
    text-align: center;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
}

.header-title {
    background: linear-gradient(90deg, #38bdf8 0%, #6366f1 50%, #ec4899 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.8rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    letter-spacing: -0.025em;
}

.header-subtitle {
    color: #94a3b8;
    font-size: 1.15rem;
    font-weight: 400;
}

/* Card components */
.result-card {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.25rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.result-card:hover {
    transform: translateY(-2px);
    border-color: #374151;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
}

/* Badge styling */
.badge {
    display: inline-block;
    padding: 0.3rem 0.8rem;
    border-radius: 9999px;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 1rem;
}

.badge-low {
    background-color: rgba(16, 185, 129, 0.15);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.3);
}
.badge-medium {
    background-color: rgba(245, 158, 11, 0.15);
    color: #fbbf24;
    border: 1px solid rgba(245, 158, 11, 0.3);
}
.badge-high {
    background-color: rgba(239, 68, 68, 0.15);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.3);
}

.card-title {
    font-size: 0.9rem;
    color: #64748b;
    text-transform: uppercase;
    font-weight: 600;
    letter-spacing: 0.05em;
    margin-bottom: 0.5rem;
}

.card-value {
    font-size: 1.25rem;
    color: #f1f5f9;
    line-height: 1.5;
}

/* Custom Warning Box */
.warning-box {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.05) 100%);
    border-left: 5px solid #ef4444;
    border-radius: 8px;
    padding: 1.25rem;
    margin-top: 1rem;
}

.warning-title {
    color: #f87171;
    font-weight: 600;
    font-size: 1rem;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Sidebar Customizations */
[data-testid="stSidebar"] {
    background-color: #0f172a;
    border-right: 1px solid #1f2937;
}
</style>
""", unsafe_allow_html=True)

# ----------------- App Header -----------------
st.markdown("""
<div class="header-container">
    <div class="header-title">🛡️ Forensic Scam Analyzer</div>
    <div class="header-subtitle">Empowering vulnerable citizens by detecting and translating hyper-localized financial threats using Gemini AI</div>
</div>
""", unsafe_allow_html=True)

# ----------------- Config & Constants -----------------
TEST_SCAMS_DIR = "test_scams"

# Load environment variables from .env if present (for local development)
load_dotenv()

# Retrieve the API Key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        api_key = None

# Configure Gemini SDK
if api_key:
    genai.configure(api_key=api_key)

SYSTEM_PROMPT = r"""You are an elite financial forensic AI operating for a digital literacy platform. Your objective is to protect vulnerable citizens from hyper-localized financial scams.
Analyze the provided image and the user's optional text description.
Perform these tasks strictly:

Threat Detection: Identify the primary threat vector (e.g., Phishing URL, Fake KYC Request, Electricity Scam). If safe, output Safe.

Risk Assessment: Assign a risk_index from 1 to 5, where 5 is the highest risk.

Translation and Extraction: Extract any vernacular text (Telugu, Hindi, slang) from the image and translate it to formal English.

Localized Warning: Draft a short 2-sentence warning explaining the scam and immediate preventative action.
Output ONLY a valid JSON object with the exact keys: threat_category, risk_index, english_translation, and localized_warning. Do not include markdown formatting or json code blocks in the output. Return raw JSON."""

def analyze_image(image_bytes: bytes, description: str = None) -> dict:
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured. Please add it to your .env file or Streamlit secrets.")
        
    try:
        image = Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        raise ValueError(f"Invalid image file: {str(e)}")
    
    # Build contents for generation
    prompt_contents = [image, SYSTEM_PROMPT]
    if description:
        prompt_contents.append(f"\nUser-provided context/description: {description}")
    
    # Try gemini-1.5-flash as default, then fallback
    model_name = "gemini-1.5-flash"
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(
            prompt_contents,
            generation_config={"response_mime_type": "application/json"}
        )
    except Exception as e:
        if "not found" in str(e).lower() or "404" in str(e) or "not supported" in str(e).lower():
            fallback_models = ["gemini-2.0-flash", "gemini-2.5-flash", "gemini-flash-latest"]
            success = False
            last_err = e
            for fb_model in fallback_models:
                try:
                    model = genai.GenerativeModel(fb_model)
                    response = model.generate_content(
                        prompt_contents,
                        generation_config={"response_mime_type": "application/json"}
                    )
                    success = True
                    break
                except Exception as fb_err:
                    last_err = fb_err
                    continue
            if not success:
                raise last_err
        else:
            raise e

    response_text = response.text.strip()
    data = json.loads(response_text)
    
    # Validate keys
    required_keys = ["threat_category", "risk_index", "english_translation", "localized_warning"]
    for key in required_keys:
        if key not in data:
            data[key] = "Not analyzed" if key != "risk_index" else 1
            
    return data

# ----------------- Sidebar Controls -----------------
st.sidebar.title("Configuration")

# Connection Status Indicator
if api_key:
    st.sidebar.success("🟢 Gemini API Configured")
else:
    st.sidebar.error("🔴 Gemini API Key Missing")
    st.sidebar.info("""
    **To configure Gemini API:**
    - **Locally:** Add `GEMINI_API_KEY=your_key_here` to your `.env` file in the project folder.
    - **In Production:** Add `GEMINI_API_KEY` to the **App Secrets** in the Streamlit Cloud dashboard.
    """)

st.sidebar.markdown("---")
st.sidebar.subheader("Select Scam Source")
source_option = st.sidebar.radio(
    "Choose Input Method",
    options=["Upload screenshot", "Demo test scams directory"]
)

selected_file_path = None
uploaded_file = None

if source_option == "Upload screenshot":
    uploaded_file = st.sidebar.file_uploader(
        "Upload an image (PNG, JPG, JPEG)",
        type=["png", "jpg", "jpeg"]
    )
else:
    # Read files in test_scams directory
    if os.path.exists(TEST_SCAMS_DIR):
        scam_files = [f for f in os.listdir(TEST_SCAMS_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if scam_files:
            selected_file = st.sidebar.selectbox("Choose a demo image:", scam_files)
            selected_file_path = os.path.join(TEST_SCAMS_DIR, selected_file)
            st.sidebar.success(f"Selected: {selected_file}")
        else:
            st.sidebar.warning(f"No image files found in '{TEST_SCAMS_DIR}' directory.")
    else:
        st.sidebar.error(f"'{TEST_SCAMS_DIR}' directory not found in workspace.")

user_description = st.sidebar.text_area(
    "Optional Description / Text",
    placeholder="e.g., I received this SMS today claiming my electricity will be cut off."
)

st.sidebar.markdown("---")
st.sidebar.caption("Hackathon Project - Advanced Forensic Scam Shield")

# ----------------- Main UI Layout -----------------
col1, col2 = st.columns([1, 1.2])

image_to_analyze = None
image_bytes = None

# Load image based on selection
if source_option == "Upload screenshot" and uploaded_file is not None:
    image_bytes = uploaded_file.getvalue()
    image_to_analyze = Image.open(io.BytesIO(image_bytes))
elif source_option == "Demo test scams directory" and selected_file_path is not None:
    try:
        with open(selected_file_path, "rb") as f:
            image_bytes = f.read()
        image_to_analyze = Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        st.error(f"Error loading demo file: {e}")

# Left Column: Image Preview & Analysis trigger
with col1:
    st.subheader("📸 Screenshot Preview")
    if image_to_analyze is not None:
        st.image(image_to_analyze, width='stretch')
        
        # Analyze button
        analyze_button = st.button("🔍 Run Forensic Analysis", width='stretch', type="primary")
    else:
        st.info("Please upload a screenshot or select a demo file from the sidebar to begin.")
        analyze_button = False

# Right Column: Dashboard Results
with col2:
    st.subheader("📊 Forensic Analysis Dashboard")
    
    if analyze_button and image_bytes is not None:
        if not api_key:
            st.error("Cannot analyze. GEMINI_API_KEY is not configured. Please add it to your .env file or Streamlit secrets.")
        else:
            with st.spinner("Analyzing threat with Gemini AI..."):
                try:
                    analysis = analyze_image(image_bytes, user_description)
                    
                    if analysis:
                        # Extract data from backend JSON response
                        threat_category = analysis.get("threat_category", "Unknown")
                        risk_index = analysis.get("risk_index", 1)
                        english_translation = analysis.get("english_translation", "No vernacular text detected.")
                        localized_warning = analysis.get("localized_warning", "No warning generated.")
                        
                        # Determine styling classes based on Risk Index
                        if risk_index >= 4:
                            risk_class = "badge-high"
                            risk_text = "HIGH / CRITICAL"
                            border_color = "#ef4444"
                        elif risk_index == 3:
                            risk_class = "badge-medium"
                            risk_text = "MODERATE"
                            border_color = "#f59e0b"
                        else:
                            risk_class = "badge-low"
                            risk_text = "LOW / SAFE"
                            border_color = "#10b981"
                        
                        # 1. Threat Category & Risk Badge
                        st.markdown(f"""
                        <div class="result-card" style="border-left: 6px solid {border_color};">
                            <span class="badge {risk_class}">{risk_text} (RISK {risk_index}/5)</span>
                            <div class="card-title">Detected Threat Vector</div>
                            <div class="card-value" style="font-size: 1.6rem; font-weight: 700; color: {border_color};">
                                {threat_category}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # 2. Translation & Extraction
                        st.markdown(f"""
                        <div class="result-card">
                            <div class="card-title">English Translation & Vernacular Extraction</div>
                            <div class="card-value" style="font-style: italic; color: #cbd5e1;">
                                "{english_translation}"
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # 3. Localized Warning Box
                        st.markdown(f"""
                        <div class="warning-box" style="border-left-color: {border_color};">
                            <div class="warning-title" style="color: {border_color};">
                                ⚠️ PREVENTION ALERT
                            </div>
                            <div style="font-size: 1.05rem; color: #f1f5f9; line-height: 1.6;">
                                {localized_warning}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        pass
                    else:
                        st.error("Analysis failed to generate results.")
                except Exception as e:
                    st.error(f"Analysis failed: {str(e)}")
    else:
        st.markdown("""
        <div style="background-color: #111827; border: 1px dashed #374151; border-radius: 12px; padding: 3rem; text-align: center; color: #64748b;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🛡️</div>
            <div>Select an image and click <b>Run Forensic Analysis</b> to display the threat index and translations.</div>
        </div>
        """, unsafe_allow_html=True)
