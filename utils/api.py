"""
utils/api.py  —  All API calls for MedMedia Analytics Hub
==========================================================
Free data sources (no credit card needed):
  - ClinicalTrials.gov v2  https://clinicaltrials.gov/api/v2/studies
  - PubMed E-utilities     https://eutils.ncbi.nlm.nih.gov/entrez/eutils/
  - Groq AI                https://console.groq.com          (free key)
  - Google Gemini          https://aistudio.google.com       (free key)
  - OpenRouter             https://openrouter.ai             (free key)
"""

import os
import time
import requests
import streamlit as st

# ── ClinicalTrials.gov ──────────────────────────────────────────────────────

CT_BASE = "https://clinicaltrials.gov/api/v2/studies"

DEMO_TRIALS = [
    {"title": "Pembrolizumab + Chemotherapy in Advanced NSCLC (KEYNOTE-789)", "status": "RECRUITING", "phase": "Phase 3", "sponsor": "Merck Sharp & Dohme", "conditions": ["Non-Small Cell Lung Cancer"], "nct_id": "NCT03989232", "start_date": "2019-06-01", "enrollment": 492},
    {"title": "Lecanemab Safety Extension in Early Alzheimer's Disease", "status": "ACTIVE_NOT_RECRUITING", "phase": "Phase 3", "sponsor": "Eisai Inc.", "conditions": ["Alzheimer Disease"], "nct_id": "NCT03887455", "start_date": "2019-03-01", "enrollment": 1795},
    {"title": "Semaglutide 2.4mg vs Placebo — Cardiovascular Outcomes (SELECT)", "status": "COMPLETED", "phase": "Phase 4", "sponsor": "Novo Nordisk A/S", "conditions": ["Obesity", "Cardiovascular Disease"], "nct_id": "NCT03574597", "start_date": "2018-10-01", "enrollment": 17604},
    {"title": "Axicabtagene Ciloleucel CAR-T in Relapsed/Refractory DLBCL", "status": "RECRUITING", "phase": "Phase 2", "sponsor": "Kite, a Gilead Company", "conditions": ["Diffuse Large B-Cell Lymphoma"], "nct_id": "NCT04531046", "start_date": "2020-10-01", "enrollment": 180},
    {"title": "Donanemab vs Placebo in Symptomatic Alzheimer's — TRAILBLAZER-ALZ 2", "status": "COMPLETED", "phase": "Phase 3", "sponsor": "Eli Lilly and Company", "conditions": ["Alzheimer Disease"], "nct_id": "NCT04437511", "start_date": "2020-06-01", "enrollment": 1736},
    {"title": "Trastuzumab Deruxtecan in HER2+ Breast Cancer — DESTINY-Breast06", "status": "RECRUITING", "phase": "Phase 3", "sponsor": "AstraZeneca", "conditions": ["Breast Cancer", "HER2-Positive"], "nct_id": "NCT04494425", "start_date": "2020-08-01", "enrollment": 866},
    {"title": "Nivolumab + Ipilimumab in Unresectable Hepatocellular Carcinoma", "status": "RECRUITING", "phase": "Phase 3", "sponsor": "Bristol-Myers Squibb", "conditions": ["Hepatocellular Carcinoma"], "nct_id": "NCT04039607", "start_date": "2019-09-01", "enrollment": 650},
    {"title": "Olaparib Maintenance in BRCA-Mutated Pancreatic Cancer", "status": "ACTIVE_NOT_RECRUITING", "phase": "Phase 3", "sponsor": "AstraZeneca", "conditions": ["Pancreatic Cancer", "BRCA Mutation"], "nct_id": "NCT02184195", "start_date": "2015-01-01", "enrollment": 154},
]

DEMO_SPONSORS = [
    {"name": "Pfizer",               "count": 847, "focus": "Oncology, Vaccines"},
    {"name": "Novartis",             "count": 734, "focus": "CAR-T, Cardiology"},
    {"name": "Roche / Genentech",    "count": 698, "focus": "Oncology, Neurology"},
    {"name": "Merck Sharp & Dohme",  "count": 612, "focus": "Immunotherapy, Oncology"},
    {"name": "AstraZeneca",          "count": 589, "focus": "Oncology, Respiratory"},
    {"name": "Bristol-Myers Squibb", "count": 543, "focus": "Immuno-oncology"},
    {"name": "Eli Lilly",            "count": 498, "focus": "Diabetes, Neurology"},
    {"name": "Novo Nordisk",         "count": 412, "focus": "GLP-1, Diabetes, Obesity"},
    {"name": "Johnson & Johnson",    "count": 387, "focus": "Oncology, Immunology"},
    {"name": "Sanofi",               "count": 356, "focus": "Rare Disease, Oncology"},
]


@st.cache_data(ttl=300, show_spinner=False)
def fetch_trials(query: str, status: str = "RECRUITING", count: int = 20) -> dict:
    params = {"query.cond": query, "pageSize": count, "sort": "LastUpdatePostDate:desc", "format": "json"}
    if status:
        params["filter.overallStatus"] = status
    try:
        r = requests.get(CT_BASE, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        studies = []
        for s in data.get("studies", []):
            p = s.get("protocolSection", {})
            studies.append({
                "title":      p.get("identificationModule", {}).get("briefTitle", "No title"),
                "nct_id":     p.get("identificationModule", {}).get("nctId", ""),
                "status":     p.get("statusModule", {}).get("overallStatus", "Unknown"),
                "phase":      ", ".join(p.get("designModule", {}).get("phases", [])) or "N/A",
                "sponsor":    p.get("sponsorCollaboratorsModule", {}).get("leadSponsor", {}).get("name", "Unknown"),
                "conditions": p.get("conditionsModule", {}).get("conditions", []),
                "enrollment": p.get("designModule", {}).get("enrollmentInfo", {}).get("count", 0),
                "start_date": p.get("statusModule", {}).get("startDateStruct", {}).get("date", "—"),
            })
        return {"studies": studies, "total": len(studies), "demo_mode": False}
    except Exception as e:
        return {"studies": DEMO_TRIALS, "total": 470_000, "demo_mode": True, "error": str(e)}


@st.cache_data(ttl=300, show_spinner=False)
def fetch_trial_count(query: str) -> int:
    try:
        r = requests.get(CT_BASE, params={"query.cond": query, "pageSize": 1, "format": "json"}, timeout=8)
        r.raise_for_status()
        return r.json().get("totalCount", 0)
    except Exception:
        return 0
    
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_total_registry_size() -> int:
    """Get total number of studies in ClinicalTrials.gov registry."""
    try:
        r = requests.get(CT_BASE, params={"pageSize": 1, "format": "json"}, timeout=8)
        r.raise_for_status()
        return r.json().get("totalCount", 0)
    except Exception:
        return 0    


@st.cache_data(ttl=600, show_spinner=False)
def fetch_specialty_trial_counts(specialties: list) -> dict:
    results = {}
    for spec in specialties:
        results[spec] = fetch_trial_count(spec)
        time.sleep(0.3)
    return results


@st.cache_data(ttl=300, show_spinner=False)
def fetch_sponsor_intel(query: str = "oncology cardiology", count: int = 50) -> list:
    try:
        r = requests.get(CT_BASE, params={"query.cond": query, "filter.overallStatus": "RECRUITING", "pageSize": count, "format": "json"}, timeout=10)
        r.raise_for_status()
        sponsor_map: dict = {}
        for s in r.json().get("studies", []):
            p    = s.get("protocolSection", {})
            name = p.get("sponsorCollaboratorsModule", {}).get("leadSponsor", {}).get("name", "")
            cond = ", ".join(p.get("conditionsModule", {}).get("conditions", [])[:2])
            if name:
                if name not in sponsor_map:
                    sponsor_map[name] = {"count": 0, "focus": cond}
                sponsor_map[name]["count"] += 1
        top = sorted(sponsor_map.items(), key=lambda x: x[1]["count"], reverse=True)[:10]
        return [{"name": n, "count": d["count"], "focus": d["focus"]} for n, d in top]
    except Exception:
        return DEMO_SPONSORS


# ── PubMed ──────────────────────────────────────────────────────────────────

PUBMED_SEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_SUMM   = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
EMAIL         = "portfolio_demo@example.com"

DEMO_ARTICLES = [
    {"pmid": "38234567", "title": "Checkpoint inhibitor combination therapy in advanced melanoma: a systematic review", "journal": "Journal of Clinical Oncology", "date": "2024", "authors": "Smith J, Johnson A, Williams B"},
    {"pmid": "38198765", "title": "Long-term outcomes of CAR-T cell therapy in relapsed/refractory B-cell lymphoma", "journal": "New England Journal of Medicine", "date": "2024", "authors": "Chen W, Patel R, Garcia M"},
    {"pmid": "38156432", "title": "Semaglutide in cardiovascular risk reduction: mechanisms and clinical evidence", "journal": "Lancet", "date": "2024", "authors": "Brown K, Davis S, Miller T"},
    {"pmid": "38112387", "title": "Tau biomarkers for early detection of Alzheimer's disease", "journal": "Nature Medicine", "date": "2024", "authors": "Wilson E, Anderson F, Thompson G"},
    {"pmid": "38089201", "title": "CRISPR-Cas9 base editing for treatment of genetic hematologic disorders", "journal": "Nature Biotechnology", "date": "2024", "authors": "Lee H, Martinez I, Robinson J"},
]


@st.cache_data(ttl=300, show_spinner=False)
def search_pubmed(query: str, count: int = 10) -> dict:
    try:
        sr = requests.get(PUBMED_SEARCH, params={"db": "pubmed", "term": query, "retmax": count, "retmode": "json", "email": EMAIL, "sort": "pub date"}, timeout=10)
        sr.raise_for_status()
        sd    = sr.json()
        ids   = sd["esearchresult"].get("idlist", [])
        total = int(sd["esearchresult"].get("count", 0))
        if not ids:
            return {"articles": [], "total": total, "demo_mode": False}
        smr = requests.get(PUBMED_SUMM, params={"db": "pubmed", "id": ",".join(ids), "retmode": "json", "email": EMAIL}, timeout=10)
        smr.raise_for_status()
        summ = smr.json().get("result", {})
        articles = [{"pmid": pid, "title": summ.get(pid, {}).get("title", "No title"), "journal": summ.get(pid, {}).get("source", "—"), "date": (summ.get(pid, {}).get("pubdate") or "—").split(" ")[0], "authors": ", ".join([x["name"] for x in summ.get(pid, {}).get("authors", [])[:3]])} for pid in ids]
        return {"articles": articles, "total": total, "demo_mode": False}
    except Exception as e:
        return {"articles": DEMO_ARTICLES[:count], "total": 0, "demo_mode": True, "error": str(e)}


@st.cache_data(ttl=600, show_spinner=False)
def pubmed_yearly_counts(query: str, years: list = None) -> dict:
    if years is None:
        years = list(range(2018, 2026))
    counts = []
    for yr in years:
        try:
            r = requests.get(PUBMED_SEARCH, params={"db": "pubmed", "term": query, "datetype": "pdat", "mindate": str(yr), "maxdate": str(yr), "retmax": 0, "retmode": "json", "email": EMAIL}, timeout=8)
            r.raise_for_status()
            counts.append(int(r.json()["esearchresult"].get("count", 0)))
            time.sleep(0.35)
        except Exception:
            counts.append(0)
    return {"years": years, "counts": counts}


@st.cache_data(ttl=600, show_spinner=False)
def pubmed_specialty_counts(specialties: list, days: int = 365) -> dict:
    results = {}
    for spec in specialties:
        try:
            r = requests.get(PUBMED_SEARCH, params={"db": "pubmed", "term": f"{spec}[MeSH Terms]", "datetype": "pdat", "reldate": str(days), "retmax": 0, "retmode": "json", "email": EMAIL}, timeout=8)
            r.raise_for_status()
            results[spec] = int(r.json()["esearchresult"].get("count", 0))
            time.sleep(0.35)
        except Exception:
            results[spec] = 0
    return results


@st.cache_data(ttl=600, show_spinner=False)
def pubmed_topic_counts(topics: list, days: int = 90) -> dict:
    results = {}
    for topic in topics:
        try:
            r = requests.get(PUBMED_SEARCH, params={"db": "pubmed", "term": topic, "datetype": "pdat", "reldate": str(days), "retmax": 0, "retmode": "json", "email": EMAIL}, timeout=8)
            r.raise_for_status()
            results[topic] = int(r.json()["esearchresult"].get("count", 0))
            time.sleep(0.35)
        except Exception:
            results[topic] = 0
    return results


# ── AI Layer — Groq → Gemini → OpenRouter (all free, no credit card) ────────

def call_ai(prompt: str, system: str = None) -> str:
    """
    Tries free AI providers in order: Groq → Gemini → OpenRouter.
    Set at least one key in your .env file. All are 100% free:
      GROQ_API_KEY       → https://console.groq.com        (Google/GitHub login)
      GEMINI_API_KEY     → https://aistudio.google.com     (Google login)
      OPENROUTER_API_KEY → https://openrouter.ai           (GitHub login)
    """

    # 1. Groq — fastest, Llama 3.3 70B, free
    groq_key = os.environ.get("GROQ_API_KEY")
    if groq_key:
        try:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
                json={"model": "llama-3.3-70b-versatile", "messages": messages, "max_tokens": 1024},
                timeout=30,
            )
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
        except Exception:
            pass

    # 2. Google Gemini — 1,500 req/day free
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key:
        try:
            full_prompt = f"{system}\n\n{prompt}" if system else prompt
            r = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_key}",
                headers={"Content-Type": "application/json"},
                json={"contents": [{"parts": [{"text": full_prompt}]}]},
                timeout=30,
            )
            r.raise_for_status()
            return r.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            pass

    # 3. OpenRouter — 11+ free models
    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    if openrouter_key:
        try:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            r = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {openrouter_key}", "Content-Type": "application/json"},
                json={"model": "deepseek/deepseek-r1:free", "messages": messages, "max_tokens": 1024},
                timeout=30,
            )
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
        except Exception:
            pass

    return (
        "⚠️ **No AI key found in your .env file.**\n\n"
        "Add one of these free keys (no credit card needed):\n\n"
        "- **GROQ_API_KEY** → [console.groq.com](https://console.groq.com) — Google login, instant\n"
        "- **GEMINI_API_KEY** → [aistudio.google.com](https://aistudio.google.com) — Google login, instant\n"
        "- **OPENROUTER_API_KEY** → [openrouter.ai](https://openrouter.ai) — GitHub login, instant\n\n"
        "Then restart the app with `streamlit run app.py`."
    )
