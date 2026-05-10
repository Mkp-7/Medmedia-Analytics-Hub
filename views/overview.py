"""views/overview.py — Overview dashboard"""

import streamlit as st
import plotly.graph_objects as go

from utils.api import fetch_trials, pubmed_specialty_counts, pubmed_topic_counts
from utils.ui import page_header, trial_card, section_header, demo_warning

SPECIALTIES = ["Oncology", "Cardiology", "Neurology", "Immunology", "Rare Disease", "Endocrinology"]
TOPICS = ["immunotherapy checkpoint inhibitor", "GLP-1 semaglutide obesity", "CAR-T lymphoma", "Alzheimer tau amyloid", "CRISPR gene editing therapy", "mRNA cancer vaccine"]
COLORS = ["#378ADD", "#1D9E75", "#BA7517", "#D4537E", "#534AB7", "#639922"]
DEMO_SPEC  = {"Oncology": 42000, "Cardiology": 31000, "Neurology": 24000, "Immunology": 19000, "Rare Disease": 9000, "Endocrinology": 15000}
DEMO_TOPIC = {"immunotherapy checkpoint inhibitor": 4200, "GLP-1 semaglutide obesity": 3800, "CAR-T lymphoma": 2900, "Alzheimer tau amyloid": 2600, "CRISPR gene editing therapy": 2100, "mRNA cancer vaccine": 1800}


def render():
    page_header("Healthcare Intelligence Overview", "Live data from ClinicalTrials.gov & PubMed - cached per session", "📊")
    with st.spinner("Loading live data…"):
        trial_data    = fetch_trials("oncology", "RECRUITING", 50)
        spec_counts   = pubmed_specialty_counts(SPECIALTIES, days=365)
        topic_counts  = pubmed_topic_counts(TOPICS, days=90)

    if trial_data.get("demo_mode"):
        demo_warning()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Active Trial Registry", "470,000+", "studies on ClinicalTrials.gov")
    k2.metric("PubMed Articles (1yr)",  f"{sum(spec_counts.values()) or sum(DEMO_SPEC.values()):,}", "6 specialties tracked")
    k3.metric("Pharma Sponsors Active", len(set(t['sponsor'] for t in trial_data['studies'])), "unique sponsors in results")
    k4.metric("Trending Topics Tracked", len(TOPICS), "topics monitored")
    st.markdown("---")

    left, right = st.columns([1.4, 1], gap="medium")

    with left:
        section_header("📈 Research volume by specialty — PubMed (last 12 months)")
        counts = spec_counts if any(spec_counts.values()) else DEMO_SPEC
        fig = go.Figure(go.Bar(x=list(counts.values()), y=list(counts.keys()), orientation="h", marker=dict(color=COLORS[::-1]), text=[f"{v:,}" for v in counts.values()], textposition="outside"))
        fig.update_layout(height=280, margin=dict(l=0,r=50,t=10,b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#c5cae9", size=12), xaxis=dict(showgrid=False, showticklabels=False), yaxis=dict(showgrid=False))
        st.plotly_chart(fig, use_container_width=True)

        section_header("🔥 Trending topics — publication surge (90 days)")
        tc = topic_counts if any(topic_counts.values()) else DEMO_TOPIC
        sorted_t = sorted(tc.items(), key=lambda x: x[1], reverse=True)
        fig2 = go.Figure(go.Bar(x=[t[0].split()[0].capitalize() for t in sorted_t], y=[t[1] for t in sorted_t], marker=dict(color=[t[1] for t in sorted_t], colorscale=[[0,"#1a3a5c"],[1,"#378ADD"]]), text=[f"{t[1]:,}" for t in sorted_t], textposition="outside"))
        fig2.update_layout(height=240, margin=dict(l=0,r=10,t=10,b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#c5cae9",size=11), xaxis=dict(showgrid=False), yaxis=dict(showgrid=True,gridcolor="#2a2d3e",showticklabels=False))
        st.plotly_chart(fig2, use_container_width=True)

    with right:
        section_header("🧪 Latest clinical trials — live feed")
        for trial in trial_data["studies"][:6]:
            st.markdown(trial_card(trial), unsafe_allow_html=True)

    st.markdown("---")
    section_header("💡 Intelligence snapshot")
    b1, b2, b3 = st.columns(3)
    tc2 = topic_counts if any(topic_counts.values()) else DEMO_TOPIC
    sc2 = spec_counts  if any(spec_counts.values())  else DEMO_SPEC
    with b1:
        st.markdown("**🔥 Top content priorities**")
        for i, (t, c) in enumerate(sorted(tc2.items(), key=lambda x: x[1], reverse=True)[:3], 1):
            st.markdown(f"{i}. **{t.split()[0].capitalize()}** — {c:,} pubs/90d")
    with b2:
        st.markdown("**👥 Most-active HCP audiences**")
        for i, (s, c) in enumerate(sorted(sc2.items(), key=lambda x: x[1], reverse=True)[:3], 1):
            st.markdown(f"{i}. **{s}** — {c:,} articles/yr")
    with b3:
        st.markdown("**🏢 Key ad targets (active sponsors)**")
        for s in list(set(t["sponsor"] for t in trial_data["studies"]))[:5]:
            st.markdown(f"• {s[:30]}")
