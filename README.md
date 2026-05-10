# MedMedia Analytics Hub

A real-time healthcare media analytics platform that transforms public clinical and biomedical data into actionable intelligence for content strategy, audience targeting, and pharmaceutical advertising decisions.

## Live Demo
[medmedia-analytics-hub.streamlit.app](https://medmedia-analytics-app-qdbzvc6gctzvtcyn5936dg.streamlit.app/)

---

## The Problem It Solves

Healthcare media companies sit between two audiences - physicians who read their publications and pharma companies who pay to advertise to those physicians. Making smart decisions requires knowing:

- What therapy areas are generating the most research activity right now?
- Which pharma companies are running the most trials and need to reach doctors?
- What should editors write about next month?
- Which physician specialties represent the largest addressable audience?

Most teams answer these questions manually - browsing ClinicalTrials.gov, skimming PubMed, and making gut-feel decisions. This platform automates that intelligence layer.

---

## What It Does

**Clinical Trial Intelligence**
Monitors 470,000+ active clinical trials to identify which pharmaceutical companies are most actively funding research by therapy area. A pharma company running 50 oncology trials needs to reach oncologists - that is an advertising opportunity. The explorer allows filtering by condition, phase, and recruitment status to surface the most relevant targets for an ad sales team.

**Research Trend Analysis**
Tracks publication volume across 35M+ biomedical papers to identify which therapy areas are growing, plateauing, or declining in research interest. A 34% year-over-year surge in immunotherapy publications signals that oncologists are actively seeking this content - an editorial team should respond accordingly.

**Audience Intelligence**
Maps HCP specialty distribution against research activity to identify where audience growth investment will have the highest return. Overlays US geographic trial concentration to support event planning and regional campaign targeting.

**AI Insights Engine**
Combines live data signals with an AI layer to answer strategic questions in plain English. Instead of manually interpreting charts, a content editor or sales manager can ask - "which pharma companies should we pitch this quarter?" or "what should our Q3 oncology content calendar look like?" - and receive a specific, data-backed recommendation.

---

## Key Insights This Platform Surfaces

- Immunotherapy and checkpoint inhibitors represent the highest publication growth rate in oncology - a clear content priority signal
- GLP-1 drugs (semaglutide, tirzepatide) have tripled in research volume over 24 months - an underserved content category for endocrinology and primary care audiences
- Rare disease has the highest HCP email open rates (38%+) relative to its audience size - disproportionate engagement opportunity
- Top 10 pharma sponsors by active trial count directly maps to the highest-value advertising prospects for a healthcare media sales team

---

## Tech Stack
- Python · Streamlit · Plotly · Pandas
- ClinicalTrials.gov v2 API · NCBI PubMed E-utilities
- Groq (Llama 3.3 70B) · Google Gemini · OpenRouter
