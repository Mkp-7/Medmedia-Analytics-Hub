"""
utils/ui.py  —  Shared HTML components and helpers
"""

import streamlit as st

STATUS_BADGE = {
    "RECRUITING":              ("badge-green",  "🟢 Recruiting"),
    "ACTIVE_NOT_RECRUITING":   ("badge-blue",   "🔵 Active"),
    "COMPLETED":               ("badge-gray",   "⬜ Completed"),
    "TERMINATED":              ("badge-red",    "🔴 Terminated"),
    "SUSPENDED":               ("badge-amber",  "🟡 Suspended"),
    "NOT_YET_RECRUITING":      ("badge-amber",  "🟡 Not Yet"),
    "ENROLLING_BY_INVITATION": ("badge-purple", "🟣 By Invite"),
}

PHASE_BADGE = {
    "Phase 1":   "badge-gray",
    "Phase 2":   "badge-amber",
    "Phase 3":   "badge-blue",
    "Phase 4":   "badge-teal",
    "Phase 1/2": "badge-amber",
    "Phase 2/3": "badge-blue",
    "N/A":       "badge-gray",
}


def badge(text: str, cls: str = "badge-gray") -> str:
    return f'<span class="badge {cls}">{text}</span>'


def trial_card(trial: dict) -> str:
    status    = trial.get("status", "Unknown")
    bcls, blabel = STATUS_BADGE.get(status, ("badge-gray", status.replace("_", " ")))
    phase     = trial.get("phase", "N/A")
    pcls      = PHASE_BADGE.get(phase, "badge-gray")
    cond_str  = ", ".join(trial.get("conditions", [])[:2])
    sponsor   = (trial.get("sponsor") or "Unknown")[:35]
    title     = (trial.get("title") or "No title")
    if len(title) > 120:
        title = title[:120] + "…"
    nct    = trial.get("nct_id", "")
    enroll = trial.get("enrollment", 0)
    nct_link = f'<a href="https://clinicaltrials.gov/study/{nct}" target="_blank" style="color:#5c8fd6;font-size:10px;text-decoration:none;">{nct} ↗</a>' if nct else ""
    return f"""<div class="item-card">
        <div class="item-title">{title}</div>
        <div style="margin-top:6px">
            {badge(blabel, bcls)}
            {badge(phase, pcls)}
            {badge(f"🏢 {sponsor}", "badge-gray")}
            {badge(f"🧬 {cond_str}", "badge-teal") if cond_str else ""}
            {badge(f"👥 n={enroll:,}", "badge-purple") if enroll else ""}
        </div>
        <div style="margin-top:6px">{nct_link}</div>
    </div>"""


def article_card(article: dict) -> str:
    pmid    = article.get("pmid", "")
    title   = (article.get("title") or "No title")
    if len(title) > 130:
        title = title[:130] + "…"
    journal = article.get("journal", "—")
    date    = article.get("date", "—")
    authors = article.get("authors", "")
    link    = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "#"
    return f"""<div class="item-card">
        <div class="item-title">
            <a href="{link}" target="_blank" style="color:#64b5f6;text-decoration:none;">{title}</a>
        </div>
        <div style="margin-top:6px">
            {badge(journal, "badge-blue")}
            {badge(date, "badge-gray")}
            {badge(authors[:40] + ("…" if len(authors) > 40 else ""), "badge-teal") if authors else ""}
        </div>
    </div>"""


def section_header(text: str) -> None:
    st.markdown(f'<div class="section-header">{text}</div>', unsafe_allow_html=True)


def page_header(title: str, subtitle: str, icon: str = "📊") -> None:
    st.markdown(f"## {icon} {title}")
    st.caption(subtitle)
    st.markdown("---")


def demo_warning() -> None:
    st.warning("⚠️ **Demo mode** — live API unavailable. Showing cached sample data. Check your internet connection.", icon="⚠️")
