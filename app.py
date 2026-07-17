import streamlit as st
import google.generativeai as genai
import json
from PIL import Image
import io
import os
from dotenv import load_dotenv

# Load environment variables for local development
load_dotenv()

# 1. Page Configuration & Styling
st.set_page_config(page_title="Fin-Shield AI", page_icon="🛡️", layout="centered")

st.markdown("""
    <style>
    .main-title { font-size: 2.5rem; font-weight: bold; color: #00FFCC; text-align: center; margin-bottom: 0.5rem; }
    .sub-title { font-size: 1.1rem; text-align: center; color: #888888; margin-bottom: 2rem; }
    .critical-box { background-color: #FF4B4B; color: white; padding: 1.5rem; border-radius: 10px; margin-top: 1rem; }
    .warning-box { background-color: #FFA500; color: white; padding: 1.5rem; border-radius: 10px; margin-top: 1rem; }
    .safe-box { background-color: #28A745; color: white; padding: 1.5rem; border-radius: 10px; margin-top: 1rem; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🛡️ Fin-Shield AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">🌱 Cyber-Based Financial Inclusion Gateway for Everyday India</div>', unsafe_allow_html=True)

# 2. Strict API Key Verification
if os.getenv("GEMINI_API_KEY"):
    api_key = os.getenv("GEMINI_API_KEY")
elif "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    st.error("⚠️ Configuration Error: GEMINI_API_KEY is missing. Add it to your .env file locally or Streamlit Cloud Secrets.")
    st.stop()

# Initialize Gemini
genai.configure(api_key=api_key)

# Dynamically select the best available Flash model
model_name = "gemini-2.0-flash"  # Default fallback
try:
    available_models = [m.name.split("/")[-1] for m in genai.list_models() if "generateContent" in m.supported_generation_methods]
    for preferred in ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-flash-latest"]:
        if preferred in available_models:
            model_name = preferred
            break
except Exception:
    pass

model = genai.GenerativeModel(model_name)

# 3. File Upload UI
uploaded_file = st.file_uploader("Upload a screenshot of a suspicious message, WhatsApp forward, or payment receipt", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display the uploaded image cleanly
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Screenshot for Analysis", use_column_width=True)
    
    # Add a processing spinner
    with st.spinner("Analyzing threat vectors and local vernacular dialects..."):
        try:
            # System Prompt forced inside the backend logic
            system_prompt = (
                "You are an elite financial forensic AI operating for a digital literacy platform. "
                "Your objective is to protect vulnerable citizens from hyper-localized financial scams. "
                "Analyze the provided image and the user's optional text description. "
                "Perform these tasks strictly: "
                "1. Threat Detection: Identify the primary threat vector (e.g., Phishing URL, Fake KYC Request, Electricity Scam). If safe, output Safe. "
                "2. Risk Assessment: Assign a risk_index from 1 to 5, where 5 is the highest risk. "
                "3. Translation and Extraction: Extract any vernacular text (Telugu, Hindi, slang) from the image and translate it to formal English. "
                "4. Localized Warning: Draft a short 2-sentence warning explaining the scam and immediate preventative action. "
                "Output ONLY a valid JSON object with the exact keys: threat_category, risk_index, english_translation, and localized_warning. "
                "Do not include markdown formatting or json code blocks in the output. Return raw JSON."
            )
            
            # Fire the prompt and image payload to Gemini
            # We specify response_mime_type to ensure raw JSON output
            response = model.generate_content(
                [system_prompt, image],
                generation_config={"response_mime_type": "application/json"}
            )
            
            # Parse the clean JSON response
            result = json.loads(response.text.strip())
            
            # 4. Display the Analysis Results Dashboard
            st.write("---")
            st.subheader("📊 Threat Intelligence Report")
            
            risk = int(result.get("risk_index", 1))
            category = result.get("threat_category", "Unknown")
            translation = result.get("english_translation", "No text extracted.")
            warning = result.get("localized_warning", "")
            
            # Dynamic styling based on Risk Index
            if risk >= 4:
                st.markdown(f'<div class="critical-box">🚨 CRITICAL RISK (Level {risk}/5)<br><br><b>Threat Category:</b> {category}</div>', unsafe_allow_html=True)
            elif 2 <= risk <= 3:
                st.markdown(f'<div class="warning-box">⚠️ MODERATE RISK (Level {risk}/5)<br><br><b>Threat Category:</b> {category}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="safe-box">✅ LOW RISK / SAFE (Level {risk}/5)<br><br><b>Threat Category:</b> {category}</div>', unsafe_allow_html=True)
                
            # Content breakdown sections
            with st.expander("🔍 Extracted Text & Localized Translation"):
                st.write(translation)
                
            with st.expander("🛡️ Actionable Citizen Advisory Warning"):
                st.info(warning)
                
        except json.JSONDecodeError:
            st.error("❌ The AI engine encountered an unexpected formatting issue. Please try uploading the image again.")
        except Exception as e:
            st.error(f"❌ Connection error: {str(e)}")
