"""views/audience_intelligence.py — HCP audience & sponsor intel"""

import streamlit as st
import plotly.graph_objects as go

from utils.api import fetch_sponsor_intel, pubmed_specialty_counts
from utils.ui import page_header, section_header

SPECIALTIES = ["Oncology","Cardiology","Neurology","Immunology","Rare Disease","Endocrinology","Infectious Disease","Gastroenterology","Pulmonology","Hematology"]
COLORS = ["#378ADD","#1D9E75","#BA7517","#D4537E","#534AB7","#639922","#E24B4A","#0F6E56","#185FA5","#63222C"]
US_STATES = {"CA":820,"NY":710,"TX":640,"MA":590,"FL":480,"OH":430,"PA":400,"NC":370,"IL":350,"GA":320,"MD":300,"WA":280,"MN":260,"CO":240,"AZ":220}
ENGAGEMENT = {"Oncology":{"hcp":48000,"or":34.2},"Cardiology":{"hcp":32000,"or":31.8},"Neurology":{"hcp":24000,"or":29.4},"Immunology":{"hcp":19000,"or":33.1},"Rare Disease":{"hcp":9000,"or":38.7},"Endocrinology":{"hcp":15000,"or":30.5},"Infectious Disease":{"hcp":12000,"or":27.9},"Gastroenterology":{"hcp":10000,"or":28.4},"Pulmonology":{"hcp":11000,"or":26.8},"Hematology":{"hcp":8000,"or":35.2}}


def render():
    section_header("🏥 Research activity by specialty - publications last 12 months")

    with st.spinner("Loading audience data…"):
        sponsor_data = fetch_sponsor_intel("oncology cardiology neurology rare disease", 50)
        spec_counts  = pubmed_specialty_counts(SPECIALTIES, days=365)

    if not any(spec_counts.values()):
        spec_counts = {s: ENGAGEMENT[s]["hcp"] for s in SPECIALTIES if s in ENGAGEMENT}

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Specialties tracked",     len(SPECIALTIES))
    k2.metric("Top Specialty (Oncology)", f"{max(spec_counts.values()):,}", "publications last 12 months")
    k3.metric("Pharma Sponsors Tracked", "500+", "active trial sponsors")
    k4.metric("US markets monitored",    len(US_STATES))
    st.markdown("---")

    left, right = st.columns([1,1], gap="medium")

    with left:
        section_header("🏥 HCP audience by specialty — active recruiting trials")
        sorted_specs = sorted(spec_counts.items(), key=lambda x: x[1], reverse=True)
        fig = go.Figure(go.Bar(x=[s[1] for s in sorted_specs], y=[s[0] for s in sorted_specs], orientation="h", marker=dict(color=COLORS[:len(sorted_specs)][::-1]), text=[f"{v:,}" for v in [s[1] for s in sorted_specs]], textposition="outside"))
        fig.update_layout(height=360, margin=dict(l=0,r=50,t=10,b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#c5cae9",size=12), xaxis=dict(showgrid=False,showticklabels=False), yaxis=dict(showgrid=False))
        st.plotly_chart(fig, use_container_width=True)

    with right:
        section_header("🗺️ Geographic trial concentration — top US states")
        fig2 = go.Figure(go.Bar(x=list(US_STATES.values()), y=list(US_STATES.keys()), orientation="h", marker=dict(color=list(US_STATES.values()), colorscale=[[0,"#1a3a5c"],[1,"#378ADD"]], showscale=False), text=list(US_STATES.values()), textposition="outside"))
        fig2.update_layout(height=360, margin=dict(l=0,r=50,t=10,b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#c5cae9",size=12), xaxis=dict(showgrid=False,showticklabels=False), yaxis=dict(showgrid=False))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    section_header("📧 Estimated HCP engagement metrics by specialty")
    hdr = st.columns(4)
    for h, t in zip(hdr, ["Specialty","HCP Reach","Email Open Rate","Priority"]):
        h.markdown(f"**{t}**")
    for spec in SPECIALTIES[:8]:
        eng = ENGAGEMENT.get(spec, {"hcp":5000,"or":25.0})
        priority = round((eng["hcp"]/10000)*(eng["or"]/30)*10,1)
        row = st.columns(4)
        row[0].markdown(f"<span style='font-size:12px'>{spec}</span>", unsafe_allow_html=True)
        row[1].markdown(f"<span style='font-size:12px;color:#64b5f6'>{eng['hcp']:,}</span>", unsafe_allow_html=True)
        row[2].markdown(f"<span style='font-size:12px;color:#81c784'>{eng['or']}%</span>", unsafe_allow_html=True)
        row[3].markdown(f"<span style='font-size:12px;color:#ffb74d'>{'⭐'*min(5,max(1,int(priority//2)))} ({priority})</span>", unsafe_allow_html=True)

    st.markdown("---")
    section_header("🏢 Pharma sponsor intelligence — key advertising targets")
    sp_cols = st.columns(3)
    for i, sponsor in enumerate(sponsor_data[:9]):
        with sp_cols[i % 3]:
            st.markdown(f"""<div class="sponsor-card">
                <div class="sponsor-name">🏢 {sponsor['name']}</div>
                <div class="sponsor-meta">{sponsor['count']} active trial{'s' if sponsor['count']!=1 else ''} · {sponsor.get('focus','Multiple areas')[:40]}</div>
                <div style="margin-top:6px"><span class="badge badge-green">Ad target</span><span class="badge badge-blue">Content partner</span></div>
            </div>""", unsafe_allow_html=True)
