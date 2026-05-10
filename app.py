"""
MedMedia Analytics Hub
=======================
Real-time healthcare media analytics using free public APIs:
ClinicalTrials.gov, PubMed/NCBI, and free AI (Groq/Gemini/OpenRouter).
"""

# Load .env FIRST — before any other imports
import os
from dotenv import load_dotenv
load_dotenv()

import streamlit as st

st.set_page_config(
    page_title="MedMedia Analytics Hub",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    [data-testid="stSidebar"] { background: #0f1117; border-right: 1px solid #1e2130; }
    [data-testid="stSidebar"] * { color: #e0e0e0 !important; }

    .item-card { background: #1a1d2e; border: 1px solid #2a2d3e; border-radius: 8px; padding: 14px 16px; margin-bottom: 10px; }
    .item-title { font-size: 13px; font-weight: 600; color: #c5cae9; margin-bottom: 6px; line-height: 1.4; }
    .badge { display: inline-block; padding: 2px 9px; border-radius: 20px; font-size: 10px; font-weight: 600; margin-right: 4px; margin-bottom: 2px; }
    .badge-blue   { background: #1a3a5c; color: #64b5f6; }
    .badge-green  { background: #1a3a2e; color: #81c784; }
    .badge-amber  { background: #3a2e1a; color: #ffb74d; }
    .badge-gray   { background: #2a2d3e; color: #9e9e9e; }
    .badge-teal   { background: #1a3a38; color: #4db6ac; }
    .badge-purple { background: #2e1a3a; color: #ba68c8; }
    .badge-red    { background: #3a1a1a; color: #ef9a9a; }

    .ai-box { background: #1a1d2e; border: 1px solid #3a3d6e; border-radius: 10px; padding: 16px; font-size: 13px; line-height: 1.7; color: #c5cae9; margin-top: 8px; }
    .ai-label { font-size: 10px; font-weight: 700; letter-spacing: 0.1em; color: #5c6bc0; text-transform: uppercase; margin-bottom: 8px; }
    .section-header { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: #5c6bc0; border-bottom: 1px solid #2a2d3e; padding-bottom: 6px; margin-bottom: 12px; }
    .sponsor-card { background: #1a1d2e; border: 1px solid #2a2d3e; border-radius: 8px; padding: 12px 14px; margin-bottom: 8px; }
    .sponsor-name { font-size: 13px; font-weight: 600; color: #c5cae9; }
    .sponsor-meta { font-size: 11px; color: #8892a4; margin-top: 3px; }
    hr.thin { border: none; border-top: 1px solid #2a2d3e; margin: 10px 0; }

    [data-testid="metric-container"] { background: #1a1d2e; border: 1px solid #2a2d3e; border-radius: 10px; padding: 12px 16px; }
    [data-testid="metric-container"] label { color: #8892a4 !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: 0.06em; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] { color: #e8eaf6 !important; font-size: 26px !important; }
    [data-testid="metric-container"] [data-testid="stMetricDelta"] { font-size: 12px !important; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 MedMedia Analytics")
    st.markdown("---")

    page = st.radio(
        "Navigate",
        [
            "📊 Overview",
            "🧪 Clinical Trials",
            "📚 PubMed Research",
            "👥 Audience Intelligence",
            "🤖 AI Insights",
        ],
        label_visibility="collapsed",
    )


# ── Import views and render the selected page ──────────────────────────────
# NOTE: views/ is a plain Python package — NOT Streamlit's reserved 'pages/' folder.
# This means Streamlit will NOT auto-generate any navigation from it.

import sys
sys.path.insert(0, os.path.dirname(__file__))

if page == "📊 Overview":
    from views import overview
    overview.render()

elif page == "🧪 Clinical Trials":
    from views import clinical_trials
    clinical_trials.render()

elif page == "📚 PubMed Research":
    from views import pubmed_research
    pubmed_research.render()

elif page == "👥 Audience Intelligence":
    from views import audience_intelligence
    audience_intelligence.render()

elif page == "🤖 AI Insights":
    from views import ai_insights
    ai_insights.render()