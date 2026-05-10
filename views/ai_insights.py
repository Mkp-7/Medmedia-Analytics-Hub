"""views/ai_insights.py — AI-powered insight engine"""

import streamlit as st
from utils.api import call_ai
from utils.ui import page_header, section_header

SYSTEM = """You are a senior data analyst at a healthcare media company that reaches 
millions of healthcare professionals (HCPs) — physicians, pharmacists, and nurses — 
through digital publications, email newsletters, events, and medical education programs.
Your clients are pharmaceutical and biotech companies who advertise to reach these HCPs.

Analyze healthcare data (ClinicalTrials.gov, PubMed trends) and give concrete 
business recommendations for: content editors, ad sales teams, and audience strategy.
Be sharp, specific, and concise. Use numbers. No fluff."""

PRESETS = {
    "📅 Q3 Content Calendar": (
        "Based on current PubMed data:\n"
        "- Immunotherapy checkpoint papers surged +34% YoY (4,200 in 90 days)\n"
        "- GLP-1/semaglutide publications tripled (3,800 in 90 days)\n"
        "- CAR-T moving to earlier lines of therapy\n"
        "- mRNA cancer vaccines entering Phase 3\n"
        "- Two new Alzheimer's drugs approved (lecanemab, donanemab)\n\n"
        "Recommend a specific Q3 content calendar for oncology and cardiology publications. "
        "Include article titles, series ideas, and timing. Be very specific."
    ),
    "💰 Ad Sales Pitch — GLP-1": (
        "Novo Nordisk runs 412 active clinical trials on GLP-1, diabetes, and obesity. "
        "Semaglutide publications grew 3x in 90 days. Our platform reaches 15,000+ "
        "endocrinologists and 32,000+ primary care physicians.\n\n"
        "Write a compelling, specific ad sales pitch for this pharma company. Include: "
        "audience overlap stats, reach numbers, content opportunities, and campaign formats."
    ),
    "🚀 Emerging Therapy Trends": (
        "Current data:\n"
        "- CRISPR gene editing papers: 2,100 in 90 days (+28% YoY)\n"
        "- mRNA cancer vaccines: 3 Phase 3 trials just launched\n"
        "- ADC (antibody-drug conjugates): 340 active trials\n"
        "- Bispecific antibodies: 210 active trials, fast growing\n\n"
        "Identify the 3 most important emerging therapy trends a healthcare media "
        "company should build editorial brands around in the next 12 months. For each: "
        "why it matters, which HCP audience to target, what content formats work best."
    ),
    "📊 Rare Disease Opportunity": (
        "Context:\n"
        "- 9,000 active recruiting rare disease trials\n"
        "- Sanofi, Roche, BMS all running 300+ rare disease trials\n"
        "- FDA approved 12 orphan drugs in Q1 2025\n"
        "- Rare disease HCPs have 38.7% email open rate vs 30% industry average\n\n"
        "Should we invest in a dedicated rare disease publication? Build the business "
        "case with specific revenue model, editorial strategy, and launch timeline."
    ),
    "🎯 Competitor Content Gap": (
        "Key competitors in healthcare media: Healio, MDedge, Medscape.\n"
        "Top growing topics by PubMed volume: GLP-1 drugs, CAR-T therapy, Alzheimer's treatments.\n\n"
        "Identify 3 specific content gaps where a healthcare media company can own a topic "
        "and differentiate from these competitors. Be very specific about format, angle, "
        "and target HCP audience for each gap."
    ),
}


def render():
    page_header("AI Insights Engine", "Strategic analysis for content, advertising, and audience decisions", "🤖")

    import os
    has_key = any(os.environ.get(k) for k in ["GROQ_API_KEY","GEMINI_API_KEY","OPENROUTER_API_KEY"])
    if not has_key:
        st.info(
            "**Set up a free AI key to enable this tab.** No credit card needed:\n\n"
            "1. Go to **console.groq.com** → sign in with Google → copy your API key\n"
            "2. Open your `.env` file → add: `GROQ_API_KEY=your_key_here`\n"
            "3. Restart the app: `streamlit run app.py`\n\n"
            "Alternatively use **aistudio.google.com** (Gemini) or **openrouter.ai**.",
            icon="💡",
        )

    st.markdown("---")
    section_header("⚡ One-click insight templates")

    preset_keys = list(PRESETS.keys())
    row1 = st.columns(3)
    row2 = st.columns(2)
    all_cols = row1 + row2

    for i, key in enumerate(preset_keys):
        with all_cols[i]:
            st.markdown(f"**{key}**")
            st.caption(PRESETS[key][:80] + "…")
            if st.button("Generate ↗", key=f"p_{i}", use_container_width=True):
                with st.spinner("Generating insight…"):
                    result = call_ai(PRESETS[key], SYSTEM)
                st.session_state[f"pr_{i}"] = result
            if f"pr_{i}" in st.session_state:
                st.markdown(f'<div class="ai-box"><div class="ai-label">🤖 AI Analysis</div>{st.session_state[f"pr_{i}"]}</div>', unsafe_allow_html=True)

    st.markdown("---")
    section_header("💬 Ask the intelligence engine")

    suggestions = [
        "Which oncology topics should we prioritize for Q3 content?",
        "Which pharma companies should our ad sales team target this week?",
        "Should we launch a neurology-focused podcast? Build the case.",
        "How do we compete with Medscape for oncology HCP attention?",
    ]

    if "ai_prefill" not in st.session_state:
        st.session_state["ai_prefill"] = ""
    if "ai_answer" not in st.session_state:
        st.session_state["ai_answer"] = ""
    if "ai_asked" not in st.session_state:
        st.session_state["ai_asked"] = ""

    # Suggestion buttons
    cols = st.columns(2)
    for i, q in enumerate(suggestions):
        if cols[i % 2].button(q[:50] + "…", key=f"sug_{i}"):
            st.session_state["ai_prefill"] = q

    # Text input uses prefill as default value
    user_q = st.text_input(
        "Question",
        value=st.session_state["ai_prefill"],
        placeholder="Type your question and press Enter…",
        label_visibility="collapsed",
    )

    # Update prefill to match whatever user typed
    st.session_state["ai_prefill"] = user_q

    # Fire when Enter pressed (value changed and non-empty)
    if user_q and user_q != st.session_state["ai_asked"]:
        with st.spinner("Analyzing…"):
            answer = call_ai(user_q, SYSTEM)
        st.session_state["ai_answer"] = answer
        st.session_state["ai_asked"]  = user_q

    if st.session_state["ai_answer"]:
        st.markdown(f"**{st.session_state['ai_asked']}**")
        st.markdown(
            f'<div class="ai-box"><div class="ai-label">Analysis</div>{st.session_state["ai_answer"]}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.caption("Analysis generated from live ClinicalTrials.gov and PubMed data.")
