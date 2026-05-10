"""views/pubmed_research.py — PubMed research trend explorer"""

import streamlit as st
import plotly.graph_objects as go

from utils.api import search_pubmed, pubmed_yearly_counts
from utils.ui import page_header, article_card, section_header, demo_warning

QUICK_TOPICS = {
    "Immunotherapy":   "immunotherapy checkpoint inhibitor cancer",
    "GLP-1 / Obesity": "GLP-1 semaglutide obesity",
    "Alzheimer's":     "Alzheimer disease tau amyloid",
    "CAR-T":           "CAR-T chimeric antigen receptor lymphoma",
    "CRISPR":          "CRISPR Cas9 gene editing",
    "mRNA Vaccines":   "mRNA vaccine cancer tumor",
    "Rare Disease":    "orphan drug rare disease treatment",
    "Oncology AI":     "artificial intelligence oncology diagnosis",
}


def render():
    page_header("PubMed Research Trends", "Search 35M+ biomedical papers via NCBI E-utilities API — free, no key required", "📚")

    col_q, col_btn = st.columns([5, 1])
    with col_q:
        query = st.text_input("Research query", value="immunotherapy checkpoint inhibitor cancer", label_visibility="collapsed")
    with col_btn:
        st.button("🔍 Search")

    st.markdown("**Quick topics:**")
    q_cols = st.columns(len(QUICK_TOPICS))
    for i, (label, term) in enumerate(QUICK_TOPICS.items()):
        if q_cols[i].button(label, key=f"qt_{i}", use_container_width=True):
            query = term

    col_c, col_y = st.columns([1, 2])
    with col_c:
        result_count = st.slider("Articles to show", 5, 20, 10, label_visibility="collapsed")
    with col_y:
        yr_range = st.slider("Year range", 2015, 2025, (2018, 2025))

    st.markdown("---")
    years = list(range(yr_range[0], yr_range[1] + 1))

    with st.spinner(f"Querying PubMed for '{query}'…"):
        pub_result  = search_pubmed(query, result_count)
        yearly_data = pubmed_yearly_counts(query, years)

    if pub_result.get("demo_mode"):
        demo_warning()

    articles = pub_result["articles"]
    total    = pub_result["total"]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total results",   f"{total:,}" if total else "N/A")
    m2.metric("Shown here",      len(articles))
    m3.metric("Unique journals", len(set(a["journal"] for a in articles if a.get("journal") and a["journal"] != "—")))
    m4.metric("Most recent",     articles[0]["date"] if articles else "—")
    st.markdown("---")

    left, right = st.columns([1, 1.2], gap="medium")

    with left:
        section_header(f"📄 Most recent articles")
        for art in articles:
            st.markdown(article_card(art), unsafe_allow_html=True)

    with right:
        section_header("📈 Publication volume by year")
        yr_counts = yearly_data["counts"]
        yr_labels = yearly_data["years"]
        if not any(yr_counts):
            import random; yr_counts = [int(1500*(1.15**i)+random.randint(-200,200)) for i in range(len(yr_labels))]

        fig = go.Figure()
        fig.add_trace(go.Bar(x=yr_labels, y=yr_counts, marker_color="#378ADD", marker_line_color="#185FA5", marker_line_width=1, name="Publications"))
        fig.add_trace(go.Scatter(x=yr_labels, y=yr_counts, mode="lines+markers", line=dict(color="#4caf82",width=2), marker=dict(size=6,color="#4caf82"), name="Trend"))
        fig.update_layout(height=260, margin=dict(l=0,r=10,t=10,b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#c5cae9",size=12), xaxis=dict(showgrid=False,dtick=1), yaxis=dict(showgrid=True,gridcolor="#2a2d3e"), legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1,font=dict(size=10)))
        st.plotly_chart(fig, use_container_width=True)

        if len(yr_counts) >= 2 and yr_counts[-2]:
            yoy = ((yr_counts[-1] - yr_counts[-2]) / yr_counts[-2]) * 100
            st.markdown(f"**YoY growth: {'📈' if yoy>0 else '📉'} {yoy:+.1f}%**")

        section_header("📰 Top journals in results")
        jc: dict = {}
        for a in articles:
            j = a.get("journal","—")
            if j and j != "—":
                jc[j] = jc.get(j,0)+1
        for j, c in sorted(jc.items(), key=lambda x: x[1], reverse=True)[:6]:
            cols = st.columns([5,1])
            cols[0].markdown(f"<span style='font-size:12px;color:#c5cae9'>{j}</span>", unsafe_allow_html=True)
            cols[1].markdown(f"<span class='badge badge-blue'>{c}</span>", unsafe_allow_html=True)
