import streamlit as st
import google.generativeai as genai
import json
from PIL import Image
import io
import os
from dotenv import load_dotenv

# Load environment variables for local development
load_dotenv()

# ─── Page Configuration ───
st.set_page_config(page_title="Fin-Shield AI", page_icon="🛡️", layout="wide")

# ─── Premium CSS Styling ───
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Global Overrides ── */
html, body, [data-testid="stAppViewContainer"], .stApp {
    font-family: 'Inter', sans-serif !important;
    background: #0a0e1a !important;
    color: #e2e8f0;
}
[data-testid="stHeader"] {
    background: transparent !important;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1225 0%, #111832 100%) !important;
    border-right: 1px solid rgba(99, 102, 241, 0.15) !important;
}

/* ── Hero Header ── */
.hero-container {
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(10, 14, 26, 0.98) 100%);
    border: 1px solid rgba(99, 102, 241, 0.2);
    border-radius: 20px;
    padding: 3rem 2rem 2.5rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    margin-bottom: 2rem;
}
.hero-container::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #6366f1, #06b6d4, #10b981, #6366f1);
    background-size: 300% 100%;
    animation: shimmer 4s ease-in-out infinite;
}
@keyframes shimmer {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}
.hero-icon {
    font-size: 3rem;
    margin-bottom: 0.75rem;
    display: inline-block;
    animation: float 3s ease-in-out infinite;
}
@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-8px); }
}
.hero-title {
    font-size: 2.6rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, #6366f1 0%, #06b6d4 40%, #10b981 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem;
    line-height: 1.2;
}
.hero-subtitle {
    color: #94a3b8;
    font-size: 1.05rem;
    font-weight: 400;
    max-width: 600px;
    margin: 0 auto;
    line-height: 1.6;
}
.hero-badge {
    display: inline-block;
    margin-top: 1.25rem;
    padding: 0.35rem 1rem;
    border-radius: 9999px;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    background: rgba(99, 102, 241, 0.12);
    color: #818cf8;
    border: 1px solid rgba(99, 102, 241, 0.25);
}

/* ── Status Pill ── */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 0.3rem 0.9rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-bottom: 1rem;
}
.status-online {
    background: rgba(16, 185, 129, 0.1);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.25);
}
.status-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #34d399;
    animation: pulse-dot 2s ease-in-out infinite;
}
@keyframes pulse-dot {
    0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.4); }
    50% { opacity: 0.7; box-shadow: 0 0 0 6px rgba(52, 211, 153, 0); }
}

/* ── Upload Zone ── */
.upload-zone {
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.6) 0%, rgba(30, 41, 59, 0.3) 100%);
    border: 2px dashed rgba(99, 102, 241, 0.25);
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    transition: all 0.3s ease;
    margin-bottom: 1.5rem;
}
.upload-zone:hover {
    border-color: rgba(99, 102, 241, 0.5);
    background: rgba(99, 102, 241, 0.04);
}
.upload-icon {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
}
.upload-text {
    color: #94a3b8;
    font-size: 0.9rem;
}

/* ── Glass Card ── */
.glass-card {
    background: rgba(15, 23, 42, 0.6);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(99, 102, 241, 0.12);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.glass-card:hover {
    border-color: rgba(99, 102, 241, 0.3);
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
}

/* ── Risk Badge ── */
.risk-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 0.45rem 1.2rem;
    border-radius: 10px;
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 1rem;
}
.risk-critical {
    background: rgba(239, 68, 68, 0.12);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.3);
}
.risk-moderate {
    background: rgba(245, 158, 11, 0.12);
    color: #fbbf24;
    border: 1px solid rgba(245, 158, 11, 0.3);
}
.risk-safe {
    background: rgba(16, 185, 129, 0.12);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.3);
}

/* ── Threat Alert Card ── */
.threat-card {
    border-radius: 16px;
    padding: 1.75rem;
    margin-bottom: 1.25rem;
    position: relative;
    overflow: hidden;
}
.threat-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 4px; height: 100%;
}
.threat-critical {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.08) 0%, rgba(185, 28, 28, 0.04) 100%);
    border: 1px solid rgba(239, 68, 68, 0.2);
}
.threat-critical::before { background: linear-gradient(180deg, #ef4444, #b91c1c); }

.threat-moderate {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.08) 0%, rgba(217, 119, 6, 0.04) 100%);
    border: 1px solid rgba(245, 158, 11, 0.2);
}
.threat-moderate::before { background: linear-gradient(180deg, #f59e0b, #d97706); }

.threat-safe {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(5, 150, 105, 0.04) 100%);
    border: 1px solid rgba(16, 185, 129, 0.2);
}
.threat-safe::before { background: linear-gradient(180deg, #10b981, #059669); }

.threat-label {
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.5rem;
}
.threat-value {
    font-size: 1.4rem;
    font-weight: 700;
    line-height: 1.3;
}

/* ── Progress Ring (Risk Meter) ── */
.risk-meter {
    display: flex;
    align-items: center;
    gap: 1.25rem;
    margin-bottom: 1rem;
}
.risk-score {
    font-size: 3rem;
    font-weight: 800;
    line-height: 1;
}
.risk-max {
    font-size: 1.2rem;
    font-weight: 400;
    color: #64748b;
}
.risk-bar-bg {
    flex: 1;
    height: 8px;
    background: rgba(148, 163, 184, 0.1);
    border-radius: 9999px;
    overflow: hidden;
}
.risk-bar-fill {
    height: 100%;
    border-radius: 9999px;
    transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ── Info Sections ── */
.info-section {
    background: rgba(15, 23, 42, 0.5);
    border: 1px solid rgba(148, 163, 184, 0.08);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 0.75rem;
}
.info-label {
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #64748b;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 6px;
}
.info-content {
    font-size: 0.95rem;
    color: #cbd5e1;
    line-height: 1.7;
}

/* ── Warning Banner ── */
.warning-banner {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.05) 100%);
    border-left: 4px solid;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-top: 0.75rem;
}
.warning-banner-critical { border-color: #ef4444; }
.warning-banner-moderate { border-color: #f59e0b; }
.warning-banner-safe { border-color: #10b981; }

.warning-title {
    font-weight: 700;
    font-size: 0.85rem;
    margin-bottom: 0.4rem;
    display: flex;
    align-items: center;
    gap: 6px;
}
.warning-text {
    font-size: 0.9rem;
    line-height: 1.65;
    color: #e2e8f0;
}

/* ── Placeholder Card ── */
.placeholder-card {
    background: rgba(15, 23, 42, 0.4);
    border: 1px dashed rgba(99, 102, 241, 0.2);
    border-radius: 16px;
    padding: 3rem 2rem;
    text-align: center;
}
.placeholder-icon {
    font-size: 3.5rem;
    margin-bottom: 1rem;
    opacity: 0.5;
}
.placeholder-text {
    color: #64748b;
    font-size: 0.95rem;
    line-height: 1.6;
}

/* ── Feature Pills ── */
.feature-row {
    display: flex;
    justify-content: center;
    gap: 0.75rem;
    flex-wrap: wrap;
    margin-top: 1.5rem;
}
.feature-pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 0.35rem 0.85rem;
    border-radius: 9999px;
    font-size: 0.72rem;
    font-weight: 500;
    background: rgba(99, 102, 241, 0.08);
    color: #a5b4fc;
    border: 1px solid rgba(99, 102, 241, 0.15);
}

/* ── Sidebar Tweaks ── */
[data-testid="stSidebar"] .stMarkdown p {
    color: #94a3b8;
    font-size: 0.85rem;
}

/* ── Streamlit Element Overrides ── */
.stFileUploader > div {
    border-radius: 12px !important;
}
.stSpinner > div > div {
    border-color: #6366f1 transparent transparent transparent !important;
}

/* ── Footer ── */
.footer {
    text-align: center;
    padding: 2rem 0 1rem;
    color: #475569;
    font-size: 0.75rem;
    border-top: 1px solid rgba(99, 102, 241, 0.08);
    margin-top: 2rem;
}
.footer a {
    color: #818cf8;
    text-decoration: none;
}
</style>
""", unsafe_allow_html=True)

# ─── Hero Header ───
st.markdown("""
<div class="hero-container">
    <div class="hero-icon">🛡️</div>
    <div class="hero-title">Fin-Shield AI</div>
    <div class="hero-subtitle">
        Cyber-Based Financial Inclusion Gateway for Everyday India — Protecting vulnerable citizens
        from hyper-localized financial scams using advanced AI forensics.
    </div>
    <div class="hero-badge">✦ Powered by Gemini AI</div>
</div>
""", unsafe_allow_html=True)

# ─── API Key Verification ───
if os.getenv("GEMINI_API_KEY"):
    api_key = os.getenv("GEMINI_API_KEY")
elif "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    st.error("⚠️ Configuration Error: GEMINI_API_KEY is missing. Add it to your .env file locally or Streamlit Cloud Secrets.")
    st.stop()

# ─── Initialize Gemini ───
genai.configure(api_key=api_key)

# Dynamically select the best available Flash model
model_name = "gemini-2.0-flash"
try:
    available_models = [m.name.split("/")[-1] for m in genai.list_models() if "generateContent" in m.supported_generation_methods]
    for preferred in ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-flash-latest"]:
        if preferred in available_models:
            model_name = preferred
            break
except Exception:
    pass

model = genai.GenerativeModel(model_name)

# ─── Sidebar ───
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0 0.5rem;">
        <div style="font-size: 1.6rem; font-weight: 700; background: linear-gradient(135deg, #6366f1, #06b6d4);
             -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.25rem;">
            Fin-Shield AI
        </div>
        <div style="font-size: 0.78rem; color: #64748b;">Threat Analysis Console</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Status indicator
    st.markdown(f"""
    <div class="status-pill status-online">
        <div class="status-dot"></div>
        Engine Online · {model_name}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")
    st.markdown("##### 📎 Upload Evidence")
    uploaded_file = st.file_uploader(
        "Upload screenshot of suspicious message",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed"
    )

    st.markdown("")
    st.markdown("##### 💬 Additional Context")
    user_description = st.text_area(
        "Describe the situation",
        placeholder="e.g., I received this SMS claiming my electricity will be cut off...",
        label_visibility="collapsed",
        height=100
    )

    st.markdown("---")

    # Feature highlights
    st.markdown("""
    <div style="font-size: 0.75rem; color: #64748b; line-height: 1.8;">
        <div style="margin-bottom: 0.4rem;">🔍 <b style="color: #94a3b8;">Threat Detection</b> — Phishing, KYC fraud, UPI scams</div>
        <div style="margin-bottom: 0.4rem;">🌐 <b style="color: #94a3b8;">Vernacular NLP</b> — Telugu, Hindi, slang extraction</div>
        <div style="margin-bottom: 0.4rem;">📊 <b style="color: #94a3b8;">Risk Scoring</b> — 5-point forensic threat index</div>
        <div>🛡️ <b style="color: #94a3b8;">Citizen Advisory</b> — Actionable prevention steps</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.caption("Built for Idea2Impact Hackathon")

# ─── Main Content Area ───
col_left, col_right = st.columns([1, 1.3], gap="large")

# ── Left Column: Image Preview ──
with col_left:
    st.markdown("#### 📸 Evidence Preview")

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)
        st.markdown(f"""
        <div class="info-section">
            <div class="info-label">📄 File Details</div>
            <div class="info-content" style="font-size: 0.82rem;">
                <b>{uploaded_file.name}</b> · {uploaded_file.size / 1024:.1f} KB · {image.size[0]}×{image.size[1]}px
            </div>
        </div>
        """, unsafe_allow_html=True)

        analyze_btn = st.button("🔍  Run Forensic Analysis", use_container_width=True, type="primary")
    else:
        st.markdown("""
        <div class="placeholder-card">
            <div class="placeholder-icon">📤</div>
            <div class="placeholder-text">
                Upload a screenshot of a suspicious<br>
                SMS, WhatsApp, UPI, or payment message<br>
                from the sidebar to begin analysis.
            </div>
            <div class="feature-row">
                <div class="feature-pill">📱 SMS</div>
                <div class="feature-pill">💬 WhatsApp</div>
                <div class="feature-pill">💳 UPI</div>
                <div class="feature-pill">📧 Email</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        analyze_btn = False

# ── Right Column: Analysis Dashboard ──
with col_right:
    st.markdown("#### 📊 Threat Intelligence Dashboard")

    if analyze_btn and uploaded_file is not None:
        with st.spinner("🔬 Analyzing threat vectors and local vernacular..."):
            try:
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

                prompt_parts = [system_prompt, image]
                if user_description:
                    prompt_parts.append(f"\nUser-provided context: {user_description}")

                response = model.generate_content(
                    prompt_parts,
                    generation_config={"response_mime_type": "application/json"}
                )

                result = json.loads(response.text.strip())

                risk = int(result.get("risk_index", 1))
                category = result.get("threat_category", "Unknown")
                translation = result.get("english_translation", "No text extracted.")
                warning = result.get("localized_warning", "")

                # Determine risk styling
                if risk >= 4:
                    risk_class = "critical"
                    risk_color = "#f87171"
                    risk_label = "CRITICAL"
                    risk_icon = "🚨"
                elif 2 <= risk <= 3:
                    risk_class = "moderate"
                    risk_color = "#fbbf24"
                    risk_label = "MODERATE"
                    risk_icon = "⚠️"
                else:
                    risk_class = "safe"
                    risk_color = "#34d399"
                    risk_label = "LOW / SAFE"
                    risk_icon = "✅"

                bar_width = risk * 20

                # ── Risk Meter ──
                st.markdown(f"""
                <div class="glass-card">
                    <div class="risk-badge risk-{risk_class}">{risk_icon} {risk_label}</div>
                    <div class="risk-meter">
                        <div>
                            <span class="risk-score" style="color: {risk_color};">{risk}</span>
                            <span class="risk-max">/5</span>
                        </div>
                        <div class="risk-bar-bg">
                            <div class="risk-bar-fill" style="width: {bar_width}%; background: linear-gradient(90deg, {risk_color}, {risk_color}88);"></div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # ── Threat Category Card ──
                st.markdown(f"""
                <div class="threat-card threat-{risk_class}">
                    <div class="threat-label" style="color: {risk_color};">Detected Threat Vector</div>
                    <div class="threat-value" style="color: {risk_color};">{category}</div>
                </div>
                """, unsafe_allow_html=True)

                # ── Translation Section ──
                st.markdown(f"""
                <div class="info-section">
                    <div class="info-label">🌐 Extracted Text & English Translation</div>
                    <div class="info-content" style="font-style: italic;">"{translation}"</div>
                </div>
                """, unsafe_allow_html=True)

                # ── Warning Advisory ──
                st.markdown(f"""
                <div class="warning-banner warning-banner-{risk_class}">
                    <div class="warning-title" style="color: {risk_color};">
                        🛡️ Citizen Advisory
                    </div>
                    <div class="warning-text">{warning}</div>
                </div>
                """, unsafe_allow_html=True)

            except json.JSONDecodeError:
                st.error("❌ The AI engine returned an unexpected format. Please try uploading the image again.")
            except Exception as e:
                st.error(f"❌ Analysis error: {str(e)}")
    else:
        st.markdown("""
        <div class="placeholder-card">
            <div class="placeholder-icon">🛡️</div>
            <div class="placeholder-text">
                Upload an image and click <b>Run Forensic Analysis</b><br>
                to generate a comprehensive threat intelligence report.
            </div>
        </div>
        """, unsafe_allow_html=True)

# ─── Footer ───
st.markdown("""
<div class="footer">
    Fin-Shield AI · Forensic Scam Analyzer · Built with Streamlit & Gemini AI<br>
    Idea2Impact Hackathon — Empowering Everyday India 🇮🇳
</div>
""", unsafe_allow_html=True)
