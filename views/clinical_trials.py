"""views/clinical_trials.py — Clinical trial explorer"""

import streamlit as st
import pandas as pd
import plotly.express as px

from utils.api import fetch_trials
from utils.ui import page_header, trial_card, section_header, demo_warning

STATUS_OPTIONS = {"Recruiting": "RECRUITING", "Active (not recruiting)": "ACTIVE_NOT_RECRUITING", "Completed": "COMPLETED", "All statuses": ""}
PHASE_OPTIONS  = ["All", "Phase 1", "Phase 2", "Phase 3", "Phase 4", "Phase 1/2", "Phase 2/3"]
QUICK_TERMS    = ["Oncology", "Cardiology", "Alzheimer's", "Diabetes", "Immunotherapy", "Rare Disease", "GLP-1", "CAR-T", "CRISPR", "Multiple Sclerosis"]


def render():
    page_header("Clinical Trial Intelligence Explorer", "Search and filter 470,000+ active clinical trials by condition, phase, and sponsor", "🧪")

    col_q, col_s, col_p = st.columns([2.5, 1.2, 1.2])
    with col_q:
        query = st.text_input("Search", value="oncology", label_visibility="collapsed", placeholder="Search condition, drug, or keyword…")
    with col_s:
        status = STATUS_OPTIONS[st.selectbox("Status", list(STATUS_OPTIONS.keys()),index=3, label_visibility="collapsed")]
    with col_p:
        phase_filter = st.selectbox("Phase", PHASE_OPTIONS, label_visibility="collapsed")

    st.markdown("**Quick search:**")
    tag_cols = st.columns(len(QUICK_TERMS))
    for i, term in enumerate(QUICK_TERMS):
        if tag_cols[i].button(term, key=f"tag_{i}", use_container_width=True):
            query = term

    count = st.slider("Results to fetch", 5, 50, 20, 5, label_visibility="collapsed")
    st.markdown("---")

    with st.spinner(f"Querying ClinicalTrials.gov for '{query}'…"):
        result = fetch_trials(query, status, count)

    if result.get("demo_mode"):
        demo_warning()

    studies = result["studies"]
    if phase_filter != "All":
        studies = [s for s in studies if phase_filter in s.get("phase", "")]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total matching",   f"{result['total']:,}")
    m2.metric("Shown here",       len(studies))
    m3.metric("Unique sponsors",  len(set(s["sponsor"] for s in studies)))
    m4.metric("Recruiting now",   sum(1 for s in studies if s.get("status") == "RECRUITING"))
    st.markdown("---")

    left, right = st.columns([1.6, 1], gap="medium")

    with left:
        section_header(f"📋 Results for: '{query}'")
        for trial in studies:
            st.markdown(trial_card(trial), unsafe_allow_html=True)
        if studies:
            df = pd.DataFrame(studies)
            df["conditions"] = df["conditions"].apply(lambda x: ", ".join(x) if isinstance(x, list) else str(x))
            st.download_button("⬇️ Download CSV", df.to_csv(index=False), f"trials_{query.replace(' ','_')}.csv", "text/csv")

    with right:
        if studies:
            section_header("📊 Status breakdown")
            sc: dict = {}
            for s in studies:
                k = s.get("status","Unknown").replace("_"," ").title()
                sc[k] = sc.get(k,0)+1
            fig = px.pie(values=list(sc.values()), names=list(sc.keys()), hole=0.55, color_discrete_sequence=["#378ADD","#1D9E75","#888780","#BA7517","#D4537E"])
            fig.update_layout(height=220, margin=dict(l=0,r=0,t=10,b=10), paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#c5cae9",size=11))
            fig.update_traces(textinfo="percent+label", textfont_size=10)
            st.plotly_chart(fig, use_container_width=True)

            section_header("🔬 Phase breakdown")
            pc: dict = {}
            for s in studies:
                pc[s.get("phase","N/A")] = pc.get(s.get("phase","N/A"),0)+1
            fig2 = px.bar(x=list(pc.keys()), y=list(pc.values()), color=list(pc.keys()), color_discrete_sequence=["#888780","#BA7517","#378ADD","#1D9E75","#D4537E","#534AB7"])
            fig2.update_layout(height=180, margin=dict(l=0,r=0,t=10,b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False, font=dict(color="#c5cae9",size=11), xaxis=dict(showgrid=False), yaxis=dict(showgrid=True,gridcolor="#2a2d3e"))
            st.plotly_chart(fig2, use_container_width=True)

            section_header("🏢 Top sponsors")
            sp: dict = {}
            for s in studies:
                n = (s.get("sponsor") or "Unknown")[:30]
                sp[n] = sp.get(n,0)+1
            for n, c in sorted(sp.items(), key=lambda x: x[1], reverse=True)[:8]:
                cols = st.columns([4,1])
                cols[0].markdown(f"<span style='font-size:12px'>{n}</span>", unsafe_allow_html=True)
                cols[1].markdown(f"<span class='badge badge-blue'>{c}</span>", unsafe_allow_html=True)
