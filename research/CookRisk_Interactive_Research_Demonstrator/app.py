from __future__ import annotations

import base64
import html
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

# Initialize Plotly's array libraries before its validators run on the first Streamlit render.
import numpy
import pandas
import plotly.graph_objects as go
import streamlit as st

from research_data import (
    BATCH021_CURRENT_SHA256,
    BATCH021_HISTORICAL_AUDIT_SHA256,
    DATASET_FAMILIES,
    LIVE_EXPLORATION_DATASET_ID,
    PROTOTYPE,
    RECONSTRUCTION_SHA256,
    SCIENTIFIC_LIMITATIONS,
    annotate_saved_metric_provenance,
    load_consolidated_fold_evidence,
    load_consolidated_model_evidence,
    load_historical_metric_conflicts,
    load_provenance_gap_register,
    load_batch021_evaluation_provenance,
    load_acr_dataset,
    load_dataset_registry,
    load_dataset_catalog,
    load_selected_metrics,
    load_validation_folds,
    numeric,
)

TITLE = "CookRisk: A Computational Investigation of Cooking-Associated Changes in Bioactive Compound Concentrations Using Machine Learning"

ASSET_DIR = Path(__file__).parent / "assets" / "scientific_visual_identity"
IMAGE_ASSETS = {
    "hero": "cookrisk_food_science_hero.webp",
    "cooking": "cooking_methods_triptych.webp",
    "nutrients": "nutrient_molecules_botanical.webp",
    "raw_cooked": "raw_cooked_concept.webp",
    "laboratory": "laboratory_research.webp",
    "analysis": "data_analysis_process.webp",
}

ICON_PATHS = {
    "book": "<path d='M4 5.5A2.5 2.5 0 0 1 6.5 3H20v16H6.5A2.5 2.5 0 0 0 4 21z'/><path d='M4 5.5v13A2.5 2.5 0 0 1 6.5 16H20M8 7h8M8 10h7'/>",
    "evidence": "<path d='M6 3.5h8l4 4V13M14 3.5v4h4M6 3.5v17h6'/><circle cx='16.5' cy='17' r='3.5'/><path d='m19 19.5 2 2M9 8h2M9 11h2'/>",
    "chart": "<path d='M4 20V4M4 20h17'/><path d='M8 16v-4M12 16V8M16 16v-6M20 16V5'/>",
    "cooking": "<path d='M4 10h16l-1.3 10H5.3zM3 10h18M7 7c-1-1.2 1-1.8 0-3M12 7c-1-1.2 1-1.8 0-3M17 7c-1-1.2 1-1.8 0-3'/><path d='M7 21h10'/>",
    "network": "<circle cx='12' cy='5' r='2.2'/><circle cx='5' cy='18' r='2.2'/><circle cx='19' cy='18' r='2.2'/><path d='m10.9 7-4.8 9M13.1 7l4.8 9M7.3 18h9.4'/>",
    "shield": "<path d='M12 3 19 6v5.5c0 4.3-2.8 7.7-7 9.5-4.2-1.8-7-5.2-7-9.5V6z'/><path d='m8.5 12 2.3 2.3 4.8-5'/>",
    "info": "<circle cx='12' cy='12' r='9'/><path d='M12 11v5M12 8h.01'/>",
    "provenance": "<path d='M5 3.5h10l4 4V20H5zM15 3.5v4h4M8 11h8M8 14h5'/><circle cx='16.5' cy='17' r='2.5'/><path d='m18.3 18.8 1.8 1.8'/>",
    "leaf": "<path d='M20 4C11 4 5 7.5 5 14c0 3.5 2.5 6 5.5 6C17 20 20 12 20 4z'/><path d='M4 21c3-5 7-8 12-11M8 15l-1-4M12 12l4 1'/>",
    "microscope": "<path d='m9 4 4 4-2 2-4-4zM13 8l2-2 3 3-2 2M10 10l5 5M7 21h12M8 18h9'/><path d='M6 18a7 7 0 0 1 12-5M16 13l2-2'/>",
    "steam": "<path d='M5 15h14l-1.4 5H6.4zM4 15h16'/><path d='M8 12c-1.5-1.8 1.5-2.5 0-4M12 12c-1.5-1.8 1.5-2.5 0-4M16 12c-1.5-1.8 1.5-2.5 0-4'/>",
    "boil": "<path d='M6 9h12l-1.2 11H7.2zM4 11H2M22 11h-2M6 8h12'/><circle cx='9' cy='14' r='1'/><circle cx='14' cy='16' r='1'/><path d='M9 6c-1-1.2 1-1.8 0-3M15 6c-1-1.2 1-1.8 0-3'/>",
    "stir": "<path d='M4 14h14l-1.3 6H6zM18 15l4-5M8 12c1-3 6-4 8-1'/><path d='M7 22h10'/>",
    "database": "<ellipse cx='12' cy='5' rx='8' ry='3'/><path d='M4 5v6c0 1.7 3.6 3 8 3s8-1.3 8-3V5M4 11v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6'/><path d='M4 11c0 1.7 3.6 3 8 3s8-1.3 8-3'/>",
    "search": "<circle cx='10.5' cy='10.5' r='6.5'/><path d='m15.5 15.5 5 5M8 10.5h5M10.5 8v5'/>",
}
NAV_ICON_KEYS = ("book", "evidence", "chart", "cooking", "network", "shield", "info", "provenance")
PAGE_ICON_KEYS = dict(zip((
    "Research Overview", "Evidence Explorer", "ACR Distributions", "Cooking & Compound Patterns",
    "Existing ML Results", "Validation & Generalization", "Scientific Limitations", "Reproducibility & Evidence",
), NAV_ICON_KEYS))


def icon_svg(name: str, size: int = 20) -> str:
    return (
        f"<svg viewBox='0 0 24 24' width='{size}' height='{size}' fill='none' stroke='currentColor' "
        f"stroke-width='1.65' stroke-linecap='round' stroke-linejoin='round' aria-hidden='true'>"
        f"{ICON_PATHS[name]}</svg>"
    )


def icon_mask(name: str) -> str:
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='#000' "
        "stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'>"
        f"{ICON_PATHS[name]}</svg>"
    )
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"url('data:image/svg+xml;base64,{encoded}')"


NAV_ICON_CSS = "\n".join(
    f'[data-testid="stRadioOption"]:has(input[value="{index - 1}"]) {{ --nav-icon:{icon_mask(name)}; }}'
    for index, name in enumerate(NAV_ICON_KEYS, start=1)
)
FILTER_ICON_CSS = f"[data-testid=\"stMultiSelect\"] [data-testid=\"stWidgetLabel\"] p {{ --filter-icon:{icon_mask('search')}; }}"
BUTTON_ICON_CSS = "\n".join(
    f"div[class*='st-key-{key}'] button::before {{ --button-icon:{icon_mask(icon)}; }}"
    for key, icon in (("home_explore", "search"), ("home_methodology", "microscope"))
)


def asset_path(asset_key: str) -> Path:
    return ASSET_DIR / IMAGE_ASSETS[asset_key]


def evidence_badge(status: str) -> str:
    normalized = status.upper()
    if "VERIFIED" in normalized:
        style, icon = "verified", "shield"
    elif "CONFLICT" in normalized:
        style, icon = "conflict", "info"
    elif "REPORTED" in normalized:
        style, icon = "reported", "info"
    else:
        style, icon = "unknown", "info"
    return (
        f"<span class='evidence-badge evidence-{style}'>"
        f"{icon_svg(icon, 14)}<span>Evidence: {html.escape(status)}</span></span>"
    )

st.set_page_config(page_title="CookRisk Research Demonstrator", page_icon=":material/science:", layout="wide")
st.markdown(
    """
    <style>
    :root {
        --paper: #FAF8F5;
        --cream: #F3EFE8;
        --sage: #2D5A27;
        --sage-soft: #E7EEE3;
        --terra: #C85A32;
        --terra-ink: #A34325;
        --terra-button: #B34B28;
        --terra-soft: #F8EAE4;
        --ink: #302B27;
        --muted: #77716A;
        --line: #E5DED4;
        --white: #FFFEFC;
        --gold: #B39A68;
    }
    html, body, [data-testid="stAppViewContainer"] {background:var(--paper); color:var(--ink);}
    body, p, label, input, textarea, button, [data-testid="stMarkdownContainer"] {font-family:Inter, "Aptos", "Segoe UI", sans-serif; color:var(--ink);}
    .block-container {max-width:1320px; padding-top:2.2rem; padding-bottom:2.5rem;}
    [data-testid="stHeader"] {background:rgba(250,248,245,.94);}
    [data-testid="stToolbar"] {right:1rem;}
    h1, h2, h3, h4, [data-testid="stHeading"] h1, [data-testid="stHeading"] h2, [data-testid="stHeading"] h3 {
        font-family:Georgia, "Palatino Linotype", "Book Antiqua", serif !important;
        color:var(--ink); letter-spacing:-.025em;
    }
    h1 {font-size:clamp(2rem, 4vw, 3rem); line-height:1.08;}
    h2 {font-size:clamp(1.55rem, 2.4vw, 2.1rem); line-height:1.18;}
    h3 {font-size:1.35rem; line-height:1.25;}
    p, li {line-height:1.65;}
    [data-testid="stSidebar"] {background:var(--cream); border-right:1px solid var(--line);}
    [data-testid="stSidebar"] > div:first-child {padding-top:1.35rem;}
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {color:var(--muted); font-size:.9rem;}
    .brand-lockup {padding:.25rem .2rem 1.1rem; border-bottom:1px solid var(--line); margin-bottom:1rem;}
    .brand-lockup .brand-top {font:600 .77rem/1.25 Georgia,serif; letter-spacing:.13em; color:var(--sage);}
    .brand-lockup .brand-bottom {font:600 .72rem/1.5 Inter,"Aptos","Segoe UI",sans-serif; letter-spacing:.12em; color:var(--sage);}
    .brand-lockup .brand-app {margin-top:.7rem; color:var(--muted); font:600 .68rem/1.4 Inter,"Aptos","Segoe UI",sans-serif; letter-spacing:.1em; text-transform:uppercase;}
    [data-testid="stRadio"] > label {font-size:.72rem; font-weight:700; letter-spacing:.1em; text-transform:uppercase; color:var(--muted);}
    [data-testid="stRadio"] div[role="radiogroup"] {gap:.28rem;}
    [data-testid="stRadio"] div[role="radiogroup"] label {padding:.56rem .7rem; border-left:3px solid transparent; border-radius:0 9px 9px 0; transition:background .15s ease;}
    [data-testid="stRadio"] div[role="radiogroup"] label:hover {background:rgba(255,254,252,.72);}
    [data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {background:var(--white); border-left-color:var(--terra); color:var(--sage); font-weight:700;}
    .module-intro {padding:0 0 1.35rem; margin:0 0 1.65rem; border-bottom:1px solid var(--line);}
    .module-intro .eyebrow, .eyebrow {font:700 .7rem/1.4 Inter,"Aptos","Segoe UI",sans-serif; letter-spacing:.14em; color:var(--terra-ink); text-transform:uppercase; margin:0 0 .45rem;}
    .module-intro h1 {margin:.1rem 0 .55rem; color:var(--sage);}
    .module-intro p {max-width:850px; margin:0; color:var(--muted); font-size:1.02rem;}
    [data-testid="stVerticalBlockBorderWrapper"]:has(.home-hero-copy) {padding:clamp(1.35rem,4vw,3.15rem);background:var(--white);border:1px solid var(--line)!important;border-radius:22px;box-shadow:0 12px 34px rgba(48,43,39,.045);margin:.8rem 0 2.1rem;}
    .home-hero-copy h1 {max-width:720px;margin:.45rem 0 1rem;color:var(--sage);font-size:clamp(2.2rem,3.7vw,3.45rem);line-height:1.04;}
    .home-hero-copy .hero-copy {max-width:670px;color:var(--muted);font-size:1.08rem;line-height:1.7;margin:0 0 1.25rem;}
    .hero-note {display:inline-flex; gap:.5rem; align-items:center; color:var(--muted); font-size:.78rem; letter-spacing:.035em;}
    .hero-note:before {content:""; width:.48rem; height:.48rem; background:var(--terra); border-radius:50%;}
    .research-visual {min-height:350px; position:relative; overflow:hidden; display:grid; place-items:center; border-radius:18px; background:radial-gradient(circle at 60% 35%, #fffdf8 0 16%, transparent 16.5%), linear-gradient(145deg,#E7EEE3,#F4EDE1 70%,#F8EAE4); border:1px solid #DCE4D6;}
    .visual-orbit {position:absolute; width:min(72%,300px); aspect-ratio:1; border:1px solid rgba(45,90,39,.22); border-radius:50%; transform:rotate(-18deg);}
    .visual-orbit:before,.visual-orbit:after {content:"";position:absolute;border:1px solid rgba(200,90,50,.27);border-radius:50%;inset:12%;transform:rotate(42deg);}
    .visual-orbit:after {inset:25%;border-color:rgba(45,90,39,.2);transform:rotate(-32deg);}
    .visual-core {position:relative;z-index:1;width:42%;aspect-ratio:1;border-radius:50%;display:grid;place-items:center;background:var(--white);border:1px solid rgba(179,154,104,.65);box-shadow:0 8px 24px rgba(48,43,39,.08);color:var(--sage);font:600 1rem/1.3 Georgia,serif;text-align:center;}
    .visual-core span {display:block;font:700 .57rem/1.4 Inter,"Aptos","Segoe UI",sans-serif;letter-spacing:.12em;color:var(--terra);text-transform:uppercase;}
    .visual-tag {position:absolute;z-index:2;padding:.55rem .72rem;border:1px solid rgba(229,222,212,.95);border-radius:9px;background:rgba(255,254,252,.92);color:var(--sage);font:700 .61rem/1.35 Inter,"Aptos","Segoe UI",sans-serif;letter-spacing:.1em;box-shadow:0 4px 12px rgba(48,43,39,.04);}
    .visual-tag.tag-a {top:18%;left:8%;}.visual-tag.tag-b {right:7%;top:38%;}.visual-tag.tag-c {left:18%;bottom:15%;}
    .visual-sprig {position:absolute;top:14%;right:19%;width:42px;height:66px;border-left:1px solid rgba(45,90,39,.5);transform:rotate(34deg);}
    .visual-sprig:before,.visual-sprig:after {content:"";position:absolute;width:20px;height:11px;border:1px solid rgba(45,90,39,.58);border-radius:100% 0 100% 0;}
    .visual-sprig:before {left:-18px;top:20px;transform:rotate(-27deg);}.visual-sprig:after {left:0;top:37px;transform:rotate(22deg);}
    .topic-heading {margin:2.2rem 0 .9rem;}
    .topic-card {height:100%;min-height:145px;padding:1.1rem 1.15rem;background:var(--white);border:1px solid var(--line);border-radius:14px;}
    .topic-card .topic-icon {width:38px;height:38px;display:grid;place-items:center;border-radius:50%;background:var(--sage-soft);color:var(--sage);margin-bottom:.8rem;}
    .topic-card .topic-name {font:600 1.12rem/1.25 Georgia,serif;color:var(--ink);}
    .topic-card .topic-label {margin-top:.25rem;color:var(--muted);font-size:.83rem;}
    .topic-card .topic-kind {margin-top:.75rem;color:var(--terra-ink);font:700 .61rem/1.35 Inter,"Aptos","Segoe UI",sans-serif;letter-spacing:.11em;text-transform:uppercase;}
    .home-info-card {height:100%;padding:1.2rem 1.3rem;background:var(--white);border:1px solid var(--line);border-radius:14px;}
    .home-info-card h3 {margin:.1rem 0 .7rem;color:var(--sage);}
    [data-testid="stVerticalBlockBorderWrapper"] {background:var(--white);border-color:var(--line)!important;border-radius:13px;box-shadow:0 5px 18px rgba(48,43,39,.035);}
    [data-testid="stMetric"] {padding:.7rem .8rem;background:var(--white);border:1px solid var(--line);border-radius:11px;}
    [data-testid="stMetricLabel"] p {color:var(--muted);font-size:.75rem;font-weight:650;}
    [data-testid="stMetricValue"] {color:var(--sage);font-family:Georgia,"Palatino Linotype",serif;font-size:1.45rem;}
    [data-testid="stAlert"] {border-radius:11px;}
    [data-testid="stAlert"] [class*="stAlertContainer"] {background:var(--cream)!important;color:var(--ink)!important;border:1px solid var(--line);border-left:4px solid var(--sage);border-radius:11px;}
    [data-testid="stAlert"] p {line-height:1.55;color:var(--ink)!important;}
    [data-testid="stExpander"] {background:var(--white);border:1px solid var(--line);border-radius:11px;margin:.42rem 0;}
    [data-testid="stExpander"] summary {color:var(--sage);font-weight:650;}
    [data-testid="stDataFrame"] {border:1px solid var(--line);border-radius:10px;overflow:hidden;background:var(--white);}
    [data-testid="stDataFrame"] canvas {font-family:Inter,"Aptos","Segoe UI",sans-serif;}
    [data-testid="stTextInput"] input,[data-testid="stNumberInput"] input,[data-testid="stSelectbox"] [role="combobox"],[data-testid="stMultiSelect"] [role="combobox"] {border-color:var(--line);border-radius:9px;background:var(--white);}
    [data-testid="stSlider"] [role="slider"] {background:var(--sage);}
    div.stButton > button {border-radius:9px;border:1px solid var(--line);background:var(--white);color:var(--sage);font-weight:700;letter-spacing:.035em;min-height:2.7rem;transition:transform .15s ease,box-shadow .15s ease;}
    div.stButton > button:hover {border-color:var(--sage);color:var(--sage);box-shadow:0 4px 12px rgba(45,90,39,.1);transform:translateY(-1px);}
    div.stButton > button[kind="primary"] {background:var(--sage);color:#fff;border-color:var(--sage);}
    div.stButton > button[kind="primary"]:hover {background:#244B20;color:#fff;border-color:#244B20;}
    div[class*="st-key-home_methodology"] button {background:var(--terra-button);color:#fff;border-color:var(--terra-button);}
    div[class*="st-key-home_methodology"] button:hover {background:#923B21;color:#fff;border-color:#923B21;}
    hr {border-color:var(--line);}
    .site-footer {display:flex;justify-content:space-between;gap:1rem;align-items:center;border-top:1px solid var(--line);margin-top:3.2rem;padding:1.1rem .1rem .3rem;color:var(--muted);font-size:.75rem;}
    .site-footer strong {font:600 .9rem Georgia,serif;color:var(--sage);}
    @media (max-width: 900px) {
        .block-container {padding-top:1.5rem;padding-left:1.35rem;padding-right:1.35rem;}
        [data-testid="stVerticalBlockBorderWrapper"]:has(.home-hero-copy) {padding:1.5rem;}
        .research-visual {min-height:300px;}
        [data-testid="stHorizontalBlock"] {flex-wrap:wrap;gap:.85rem;}
        [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {flex:1 1 calc(50% - .85rem)!important;min-width:0!important;width:calc(50% - .85rem)!important;}
        [data-testid="stHorizontalBlock"]:has(.home-hero-copy) > [data-testid="stColumn"] {flex:1 1 100%!important;min-width:0!important;width:100%!important;}
    }
    @media (max-width: 640px) {
        .block-container {padding-top:1rem;padding-left:1rem;padding-right:1rem;padding-bottom:1.5rem;}
        [data-testid="stVerticalBlockBorderWrapper"]:has(.home-hero-copy) {padding:1.2rem;border-radius:15px;}
        .home-hero-copy h1 {font-size:2.25rem;}
        .research-visual {min-height:260px;}
        .site-footer {align-items:flex-start;flex-direction:column;}
        [data-testid="stHorizontalBlock"] {flex-wrap:wrap;gap:.65rem;}
        [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {flex:1 1 100%!important;min-width:0!important;width:100%!important;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    "<style>\n"
    + NAV_ICON_CSS
    + BUTTON_ICON_CSS
    + FILTER_ICON_CSS
    + """
    [data-testid="stRadioOption"] [data-testid="stMarkdownContainer"] p::before {
        content:"";width:19px;height:19px;flex:0 0 19px;background:currentColor;
        mask:var(--nav-icon) center/contain no-repeat;-webkit-mask:var(--nav-icon) center/contain no-repeat;
    }
    [data-testid="stRadioOption"] [data-testid="stMarkdownContainer"] p {display:flex;align-items:center;gap:.58rem;margin:0;}
    .module-intro .eyebrow {display:flex;align-items:center;gap:.55rem;}
    .module-badge {width:26px;height:26px;display:inline-grid;place-items:center;color:var(--sage);background:var(--sage-soft);border:1px solid #D9E3D4;border-radius:8px;flex:0 0 auto;}
    .model-identity {display:flex;align-items:center;gap:.5rem;color:var(--sage);font-size:1rem;}
    .model-identity svg {flex:0 0 auto;}
    .dataset-family-label {display:inline-flex;align-items:center;gap:.38rem;padding:.22rem .48rem;border-radius:999px;background:var(--sage-soft);color:var(--sage);font-size:.7rem;font-weight:700;}
    .evidence-badge {display:inline-flex;align-items:center;gap:.34rem;padding:.28rem .5rem;border:1px solid transparent;border-radius:999px;font-size:.66rem;font-weight:700;line-height:1.4;}
    .evidence-verified {background:#E7EEE3;color:#2D5A27;border-color:#D1DDCB;}
    .evidence-reported {background:#F7F0DE;color:#745B1F;border-color:#E7D9B5;}
    .evidence-conflict {background:#F8EAE4;color:#923B21;border-color:#EACFC3;}
    .evidence-unknown {background:#F3EFE8;color:#625C55;border-color:#E5DED4;}
    .topic-card {min-height:210px;padding:1.2rem 1.25rem;transition:transform .18s ease,box-shadow .18s ease,border-color .18s ease;}
    .topic-card:hover {transform:translateY(-2px);box-shadow:0 12px 24px rgba(48,43,39,.075);border-color:#CDD9C8;}
    .topic-card .topic-icon {width:42px;height:42px;border-radius:12px;margin-bottom:.85rem;transition:transform .18s ease;}
    .topic-card:hover .topic-icon {transform:scale(1.045);}
    .topic-card .topic-description {margin-top:.7rem;color:var(--muted);font-size:.88rem;line-height:1.55;}
    .method-icon-row {display:flex;align-items:center;gap:.75rem;flex-wrap:wrap;margin-top:.62rem;color:var(--sage);font-size:.72rem;font-weight:650;}
    .method-icon-row span {display:inline-flex;align-items:center;gap:.28rem;}
    [data-testid="stImage"] {overflow:hidden;border-radius:15px;}
    [data-testid="stImage"] img {max-width:100%;height:auto;object-fit:contain;border-radius:15px;}
    div.stButton > button {display:inline-flex;align-items:center;justify-content:center;gap:.58rem;}
    div.stButton > button::before {content:"";display:inline-block;width:18px;height:18px;flex:0 0 18px;background:currentColor;mask:var(--button-icon) center/contain no-repeat;-webkit-mask:var(--button-icon) center/contain no-repeat;}
    [data-testid="stMultiSelect"] [data-testid="stWidgetLabel"] p::before {content:"";display:inline-block;width:15px;height:15px;flex:0 0 15px;background:currentColor;mask:var(--filter-icon) center/contain no-repeat;-webkit-mask:var(--filter-icon) center/contain no-repeat;margin-right:.35rem;}
    div.stButton > button:focus-visible,[data-testid="stRadioOption"]:focus-visible,[data-testid="stExpander"] summary:focus-visible {outline:3px solid var(--gold)!important;outline-offset:2px!important;}
    [data-testid="stExpander"] {transition:box-shadow .16s ease,border-color .16s ease;}
    [data-testid="stExpander"]:hover {border-color:#D7CDC0!important;box-shadow:0 6px 18px rgba(48,43,39,.05);}
    [data-testid="stImage"] + div {color:var(--muted);}
    @media (prefers-reduced-motion: reduce) {
        *,*::before,*::after {scroll-behavior:auto!important;transition-duration:.01ms!important;animation-duration:.01ms!important;animation-iteration-count:1!important;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)

PAGES = [
    "Research Overview",
    "Evidence Explorer",
    "ACR Distributions",
    "Cooking & Compound Patterns",
    "Existing ML Results",
    "Validation & Generalization",
    "Scientific Limitations",
    "Reproducibility & Evidence",
]

with st.sidebar:
    st.markdown(
        '<div class="brand-lockup"><div class="brand-top">NUTRITION RETENTION</div>'
        '<div class="brand-bottom">RESEARCH INITIATIVE</div>'
        '<div class="brand-app">CookRisk · research demonstrator</div></div>',
        unsafe_allow_html=True,
    )
    page = st.radio("Research modules", PAGES, label_visibility="visible", key="page_navigation")
    st.divider()
    st.warning("Research demonstrator only. No predictions, risk scores, or cooking advice.")
    st.caption("Source data are read-only. Saved metrics are displayed, not recalculated.")


def header(title: str, subtitle: str) -> None:
    badge = icon_svg(PAGE_ICON_KEYS[title], 17)
    st.markdown(
        f'<section class="module-intro"><p class="eyebrow"><span class="module-badge">{badge}</span>CookRisk · Research demonstrator</p>'
        f'<h1>{title}</h1><p>{subtitle}</p></section>',
        unsafe_allow_html=True,
    )


def navigate_to(page_name: str) -> None:
    st.session_state["page_navigation"] = page_name


def acr_rows() -> tuple[list[dict[str, str]] | None, str | None, dict | None]:
    try:
        rows, digest, entry = load_acr_dataset(LIVE_EXPLORATION_DATASET_ID)
        return rows, digest, entry
    except (OSError, ValueError, KeyError) as exc:
        st.error(f"Record-level ACR exploration is unavailable: {exc}")
        return None, None, None


def number_values(rows: list[dict[str, str]], field: str) -> list[float]:
    return [value for row in rows if (value := numeric(row, field)) is not None and math.isfinite(value)]


def filtered_acr_controls(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    st.caption("Filters use the selected file's existing values only. Blank source fields remain visible when no filter is selected.")
    columns = st.columns(4)
    filters = [
        ("Food matrix", "food_matrix"),
        ("Compound", "compound"),
        ("Cooking method", "cooking_method"),
        ("DOI / source", "doi"),
    ]
    selected: dict[str, list[str]] = {}
    for col, (label, field) in zip(columns, filters):
        values = sorted({r.get(field, "").strip() for r in rows if r.get(field, "").strip()})
        if any(not r.get(field, "").strip() for r in rows):
            values.append("(blank / not recorded)")
        selected[field] = col.multiselect(label, values, key=f"filter_{field}")
    result = rows
    for field, choices in selected.items():
        if not choices:
            continue
        keep = set(choices)
        result = [
            r for r in result
            if (r.get(field, "").strip() in keep)
            or (not r.get(field, "").strip() and "(blank / not recorded)" in keep)
        ]
    return result


def source_provenance_card(digest: str, rows_count: int, entry: dict) -> None:
    target = entry["target_definition"]
    cols = st.columns(4)
    cols[0].metric("Rows × columns", f"{rows_count:,} × {entry['column_count']:,}")
    cols[1].metric("File identity", "SHA-256 verified")
    cols[2].metric("Target", "ACR (%)")
    cols[3].metric("Approved use", "Live exploration only")
    st.code(
        f"Dataset ID: {entry['dataset_id']}\n"
        f"{entry['repository_relative_path']}\n"
        f"Dimensions: {rows_count:,} rows × {entry['column_count']:,} columns\n"
        f"SHA-256  {digest}",
        language="text",
    )
    st.caption(
        f"Owner-approved for this demonstrator only. Target field `{target['field']}`: "
        f"{target['name']} = "
        f"{target['equation']}. This is an apparent concentration ratio, not total-mass "
        "retention. Approval does not make Reconstruction canonical or independently validated."
    )


def show_rows(rows: list[dict[str, str]], max_height: int = 540) -> None:
    st.dataframe(rows, height=max_height, hide_index=True, width="stretch")


def go_plot(fig: go.Figure, height: int = 430) -> None:
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=24, r=24, t=54, b=26),
        font=dict(family='Inter, "Aptos", "Segoe UI", sans-serif', color="#302B27", size=12),
        colorway=["#2D5A27", "#C85A32", "#B39A68", "#71816B", "#997462"],
        paper_bgcolor="#FFFEFC",
        plot_bgcolor="#FFFEFC",
        xaxis=dict(showgrid=False, linecolor="#E5DED4", ticks="outside", tickcolor="#E5DED4"),
        yaxis=dict(showgrid=True, gridcolor="#EEE9E1", zerolinecolor="#CFC6BA", linecolor="#E5DED4"),
        title_font=dict(family='Georgia, "Palatino Linotype", serif', size=17, color="#302B27"),
        legend=dict(bgcolor="rgba(255,254,252,.8)", borderwidth=0),
    )
    st.plotly_chart(fig, width="stretch", config={"displaylogo": False})


def consolidated_metric_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Build a display-only table while keeping pooled and fold means distinct."""
    display = []
    for row in rows:
        display.append({
            "Result record": row["result_id"],
            "Pooled OOF R²": row["pooled_oof_r2"] or "NOT ASSESSABLE",
            "Pooled R² evidence": row["pooled_metric_status"],
            "Mean-fold R²": row["mean_fold_r2"] or "NOT ASSESSABLE",
            "Mean-fold evidence": row["mean_fold_metric_status"],
        })
    return display


def consolidated_identity_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [{
        "Result record": row["result_id"],
        "Dataset family": row["dataset_family"],
        "Target": row["target"],
        "Model": row["model"],
        "Evaluation / split": row["evaluation_protocol"],
    } for row in rows]


def consolidated_context_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [{
            "Result record": row["result_id"],
            "Row count": row["row_count"],
            "Grouping unit": row["grouping_unit"],
            "Fold count": row["fold_count"],
            "Configuration": row["configuration"],
            "Configuration status": row["configuration_status"],
            "Output integrity": row["checksum_status"],
            "Input provenance": row["input_provenance_status"],
            "Saved evidence": row["supporting_evidence"],
        } for row in rows]


def render_saved_result_family(
    title: str,
    rows: list[dict[str, str]],
    *,
    conflict_warning: bool = False,
    show_details: bool = True,
) -> None:
    if not rows:
        return
    st.subheader(title)
    if conflict_warning:
        st.warning(
            "Conflicting saved evidence is shown as separate records. No version is selected, "
            "merged, or treated as a corrected result."
        )
    for row in rows:
        with st.container(border=True):
            st.markdown(
                f"<div class='model-identity'>{icon_svg('network', 17)}<strong>{html.escape(row['model'])}</strong></div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span class='dataset-family-label'>{icon_svg('database', 14)}{html.escape(row['dataset_family'])}</span>",
                unsafe_allow_html=True,
            )
            st.caption(
                f"Target: {row['target']} · Evaluation: {row['evaluation_protocol']} · Grouping: {row['grouping_unit']} · "
                f"Saved folds: {row['fold_count']}"
            )
            st.caption(f"Configuration: {row['configuration']} · {row['configuration_status']}")
            pooled_col, mean_col = st.columns(2)
            pooled_col.metric("Pooled OOF R²", row["pooled_oof_r2"] or "NOT ASSESSABLE")
            pooled_col.markdown(evidence_badge(row["pooled_metric_status"]), unsafe_allow_html=True)
            mean_col.metric("Mean-fold R²", row["mean_fold_r2"] or "NOT ASSESSABLE")
            mean_col.markdown(evidence_badge(row["mean_fold_metric_status"]), unsafe_allow_html=True)
            if show_details:
                with st.expander(f"Configuration and provenance — {row['result_id']}"):
                    st.markdown(f"**Configuration:** {row['configuration']}")
                    st.markdown(f"**Configuration status:** {row['configuration_status']}")
                    st.markdown(f"**Output integrity:** {row['checksum_status']}")
                    st.markdown(f"**Input provenance:** {row['input_provenance_status']}")
                    st.markdown(f"**Saved evidence:** `{row['supporting_evidence']}`")
                    st.markdown(f"**Interpretation:** {row['interpretation']}")


if page == "Research Overview":
    with st.container(border=True):
        hero_left, hero_right = st.columns([1.15, .85], gap="large", vertical_alignment="center")
        with hero_left:
            st.markdown(
                "<div class='home-hero-copy'><p class='eyebrow'>Research Overview · Nutrition Retention Research Initiative</p>"
                "<h1>Cooking, bioactive compounds &amp; apparent concentration change</h1>"
                "<p class='hero-copy'>Exploring reported cooking-associated changes in bioactive compound concentrations across foods and preparation methods.</p>"
                "<span class='hero-note'>An evidence-led computational research demonstrator</span></div>",
                unsafe_allow_html=True,
            )
            action_left, action_right = st.columns(2, gap="small")
            action_left.button(
                "EXPLORE OUR FINDINGS",
                type="primary",
                use_container_width=True,
                on_click=navigate_to,
                args=("Evidence Explorer",),
                key="home_explore",
            )
            action_right.button(
                "METHODOLOGY OVERVIEW",
                use_container_width=True,
                on_click=navigate_to,
                args=("Validation & Generalization",),
                key="home_methodology",
            )
        with hero_right:
            st.image(
                str(asset_path("hero")),
                width="stretch",
                alt="Botanical food-science illustration with broccoli, carrots, tomatoes, laboratory glassware, cooking vessel, and abstract nutrient nodes.",
            )
    st.info("This is an academic research demonstrator, not a validated predictor, deployed model, food-safety tool, or cooking-advice system.")

    st.markdown("<div class='topic-heading'><p class='eyebrow'>Exploratory themes</p><h2>Three research themes</h2></div>", unsafe_allow_html=True)
    st.caption("These themes describe the demonstrator's scope; they are not verified findings, rankings, or method recommendations.")
    topic_cols = st.columns(3, gap="medium")
    topics = [
        ("Cooking Methods", "Steaming · boiling · stir-frying", "Methods represented in the records are compared descriptively.", "cooking"),
        ("Nutrient Retention", "Reported concentration measures", "Stored ACR values describe concentration ratios, not total-mass retention.", "leaf"),
        ("Scientific Evidence", "Records · metrics · validation", "Evidence is shown with dataset identity and provenance limitations.", "evidence"),
    ]
    for col, (topic, label, description, icon) in zip(topic_cols, topics):
        with col:
            method_icons = (
                "<div class='method-icon-row'>"
                f"<span>{icon_svg('steam', 15)}Steam</span>"
                f"<span>{icon_svg('boil', 15)}Boil</span>"
                f"<span>{icon_svg('stir', 15)}Stir-fry</span></div>"
                if topic == "Cooking Methods" else ""
            )
            st.markdown(
                f"<div class='topic-card'><div class='topic-icon'>{icon_svg(icon, 22)}</div>"
                f"<div class='topic-name'>{topic}</div><div class='topic-label'>{label}</div>"
                f"<div class='topic-description'>{description}</div>{method_icons}</div>",
                unsafe_allow_html=True,
            )

    st.markdown("<div class='topic-heading'><p class='eyebrow'>Study frame</p><h2>How to read this research</h2></div>", unsafe_allow_html=True)
    left, right = st.columns([1.15, .85], gap="large")
    with left:
        with st.container(border=True):
            st.subheader("Research question")
            st.write("Can molecular, food-matrix, and cooking-process features characterize reported cooking-associated concentration changes, and do observed patterns transfer to held-out compounds and research sources?")
            st.subheader("Research workflow")
            st.markdown("1. Curate source-linked raw/cooked concentration evidence.\n2. Preserve compound, matrix, method, basis, and source identity.\n3. Compare exploratory ML evaluations under different validation designs.\n4. Examine source transfer, uncertainty, and evidence gaps.")
    with right:
        with st.container(border=True):
            st.subheader("Target definition")
            st.latex(r"\mathrm{ACR}(\%) = 100 \times \frac{C_{cooked}}{C_{raw}}")
            st.write("ACR is an apparent concentration ratio. It is not total-mass retention. ACR above 100% does not establish increased total analyte mass.")
    st.subheader("Research boundaries")
    cols = st.columns(3)
    cols[0].warning("No causal cooking-method claims")
    cols[1].warning("No bioavailability, exposure, or clinical-risk claims")
    cols[2].warning("No validated model or new-record prediction")
    st.caption("Saved results use the evidence labels VERIFIED FROM SAVED RECORDS, REPORTED — PROVENANCE INCOMPLETE, CONFLICTING SAVED EVIDENCE, UNVERIFIED, or NOT ASSESSABLE. These labels describe the saved evidence; they do not imply a fresh model run.")

elif page == "Evidence Explorer":
    header("Evidence Explorer", "Browse the owner-approved Reconstruction evidence snapshot; Batch021 remains a separate historical reference.")
    art_col, note_col = st.columns([.2, .8], vertical_alignment="center")
    with art_col:
        st.image(str(asset_path("analysis")), width=175, alt="Conceptual illustration of organized research records and analysis workflow; no values or results are shown.")
    with note_col:
        st.markdown("### Records with source context")
        st.caption("Illustrative research workflow only. The dataset identity, integrity checks, and record table below are the factual content.")
    st.subheader("Available research families")
    for item in DATASET_FAMILIES:
        with st.expander(f"{item['family']} — {item['status']}", expanded=item["family"] == "Verified concentration-ratio reconstruction"):
            st.write(f"**Snapshot:** {item['snapshot']}")
            st.write(f"**Target:** {item['target']}")
            st.write(f"**Hash / integrity:** {item['hash']}")
            st.write(f"**Source:** `{item['source']}`")
            st.write(item["interactive"])
    st.divider()
    st.subheader("Live record-level exploration: Reconstruction")
    st.info("Owner-approved for live exploration in this demonstrator only. This approval does not designate a canonical scientific dataset or establish independent validation. Batch021 records are not a fallback.")
    rows, digest, entry = acr_rows()
    if rows is not None and digest is not None and entry is not None:
        source_provenance_card(digest, len(rows), entry)
        subset = filtered_acr_controls(rows)
        st.write(f"Showing **{len(subset):,}** of **{len(rows):,}** source records. No observations are removed from the source file; filters only change this view.")
        if subset:
            show_rows(subset)
        else:
            st.info("No source records match the selected filters. Clear or broaden one or more filters; the source dataset is unchanged.")
        st.caption("Source locators, raw/cooked concentration strings, units, basis, evidence status, and target values are shown as stored. No unit conversion, imputation, or source-value edit is applied.")

elif page == "ACR Distributions":
    header("ACR Distributions", "Descriptive distributions of the Reconstruction's stored target values.")
    target_col, molecule_col = st.columns([.8, .2], vertical_alignment="center")
    with target_col:
        st.markdown("**ACR (%) = 100 × cooked concentration / raw concentration.** The analysis below reads the stored target column; it does not derive or convert concentration values.")
    with molecule_col:
        st.image(str(asset_path("nutrients")), width=170, alt="Abstract botanical nutrient illustration with citrus, tomato, leaves, and non-specific molecule nodes; no molecular structure is depicted.")
        st.caption("Conceptual; no specific structures shown.")
    rows, digest, entry = acr_rows()
    if rows is not None and entry is not None:
        source_provenance_card(digest or "", len(rows), entry)
        subset = filtered_acr_controls(rows)
        vals = number_values(subset, "target_value_percent")
        if not vals:
            st.warning("No numeric ACR values are available under the current filters.")
        else:
            mean = statistics.fmean(vals)
            median = statistics.median(vals)
            cols = st.columns(6)
            cols[0].metric("Rows in filtered view", f"{len(subset):,}")
            cols[1].metric("Rows with numeric target", f"{len(vals):,}")
            cols[2].metric("Mean ACR", f"{mean:,.2f}%")
            cols[3].metric("Median ACR", f"{median:,.2f}%")
            cols[4].metric("Minimum / maximum", f"{min(vals):,.2f}% / {max(vals):,.2f}%")
            cols[5].metric("Above 100%", f"{sum(v > 100 for v in vals):,}")
            st.caption(f"Rows with blank or nonnumeric stored target, excluded from numeric plots only: {len(subset) - len(vals)}. They remain present in the evidence table.")
            st.caption("These are interactive descriptive summaries of the filtered stored target values, not a recalculation of historical model metrics. The full reconstruction report's saved summaries remain separately cited in the documentation.")
            hist = go.Figure(go.Histogram(x=vals, nbinsx=40, marker_color="#2D5A27"))
            hist.update_layout(title="Stored ACR values (all observations retained)", xaxis_title="ACR (%)", yaxis_title="Observation count")
            go_plot(hist)
            dist = go.Figure()
            for label, mask, color in [
                ("Below 100%", [v for v in vals if v < 100], "#2D5A27"),
                ("Equal to 100%", [v for v in vals if v == 100], "#B39A68"),
                ("Above 100%", [v for v in vals if v > 100], "#C85A32"),
            ]:
                dist.add_trace(go.Bar(name=label, x=[label], y=[len(mask)], marker_color=color))
            dist.update_layout(title="Counts relative to 100%", xaxis_title="Stored ACR category", yaxis_title="Observation count", showlegend=False)
            go_plot(dist, 320)
            box = go.Figure(go.Box(y=vals, name="All filtered observations", boxpoints="outliers", marker_color="#2D5A27"))
            box.update_layout(title="Distribution and high-value observations (none removed)", yaxis_title="ACR (%)")
            go_plot(box, 380)
            st.info("ACR above 100% can reflect concentration/basis or analytical context; it does not establish an increase in total analyte mass. Outlying values are retained in every view.")

elif page == "Cooking & Compound Patterns":
    header("Cooking & Compound Patterns", "Descriptive group comparisons; these are not causal effects.")
    st.warning("Observed patterns can reflect source, analytical method, food matrix, preparation, units, moisture basis, or missing protocol metadata. No causal cooking-method claim is supported.")
    st.image(
        str(asset_path("cooking")),
        width="stretch",
        alt="Three botanical editorial vignettes showing vegetables steaming, boiling, and being stir-fried; no comparative outcome is implied.",
        caption="Illustrations of preparation methods only; no nutrient outcome is implied.",
    )
    rows, digest, entry = acr_rows()
    if rows is not None and entry is not None:
        source_provenance_card(digest or "", len(rows), entry)
        subset = filtered_acr_controls(rows)
        group_field = st.selectbox("Group stored ACR values by", ["cooking_method", "compound", "food_matrix", "doi"], format_func=lambda x: {"cooking_method":"Cooking method", "compound":"Compound", "food_matrix":"Food matrix", "doi":"DOI / source"}[x])
        min_n = st.slider("Minimum observations for a plotted group", 2, 30, 8)
        grouped: dict[str, list[float]] = defaultdict(list)
        for row in subset:
            key = row.get(group_field, "").strip()
            val = numeric(row, "target_value_percent")
            if key and val is not None and math.isfinite(val):
                grouped[key].append(val)
        eligible = [(key, vals) for key, vals in grouped.items() if len(vals) >= min_n]
        eligible.sort(key=lambda item: (-len(item[1]), item[0]))
        plotted_groups = eligible[:20]
        numeric_group_rows = sum(len(v) for v in grouped.values())
        plotted_rows = sum(len(v) for _, v in plotted_groups)
        st.caption(f"Filtered rows: {len(subset)}; rows with numeric target and recorded group: {numeric_group_rows}; rows represented in the chart's eligible top 20 groups: {plotted_rows}. The remaining rows are unplotted because of missing fields, the minimum-support threshold, or the top-20 display cap; source records remain unchanged.")
        if len(eligible) < 2:
            st.info(f"Fewer than two groups meet the minimum support of {min_n} observations. Lower the support threshold or broaden filters; no comparison is fabricated.")
        else:
            fig = go.Figure()
            for key, vals in plotted_groups:
                fig.add_trace(go.Box(y=vals, name=f"{key} (n={len(vals)})", boxpoints=False))
            fig.update_layout(title=f"Stored ACR distribution by {group_field.replace('_', ' ')} (groups with n ≥ {min_n})", yaxis_title="ACR (%)", xaxis_title="Documented group")
            go_plot(fig, max(430, 30 * min(len(plotted_groups), 18)))
            table = [{"group": key, "n": len(v), "median_acr_percent": statistics.median(v), "mean_acr_percent": statistics.fmean(v)} for key, v in plotted_groups]
            st.caption("Group summaries are calculated descriptively from stored ACR target values. They are not adjusted for source or protocol and must not be interpreted causally.")
            st.dataframe(table, hide_index=True, width="stretch")

elif page == "Existing ML Results":
    header("Existing ML Results", "Saved historical evidence shown separately for each dataset family and target.")
    st.info("These are historical saved results, not current predictions or a common leaderboard. No model is trained, no prediction is generated, and no historical metric is recalculated here.")
    st.caption("Pooled OOF R² summarizes concatenated out-of-fold predictions. Mean-fold R² is the arithmetic mean of fold R² values. They are distinct summaries and appear in separate columns.")
    try:
        evidence_rows = load_consolidated_model_evidence()
        stagea = [
            r for r in evidence_rows
            if r["result_id"].startswith("STAGEA-")
            and r["result_id"] != "STAGEA-XGBOOST-TUNED-REPLAY"
        ]
        render_saved_result_family("Historical Stage A benchmark — Retention_Final", stagea)
        st.warning("Retention_Final semantics, units, and scale remain unresolved. The displayed metrics are saved historical research evidence, not ACR, live inference, or deployment performance. Four initial model configurations are incompletely recorded.")

        batch_rows = [r for r in evidence_rows if r["dataset_family"] == "Batch021 ACR fixed audit"]
        render_saved_result_family("Batch021 ACR — fixed historical audit", batch_rows)
        st.caption("Batch021 identity, target, model, and evaluation provenance are retained with these records. DOI/source-held-out is a source-family proxy and does not establish independent-laboratory validation.")

        reconstruction_rows = [r for r in evidence_rows if r["dataset_family"] == "Verified Reconstruction ACR"]
        render_saved_result_family("Reconstruction ACR — separate historical model evidence", reconstruction_rows)
        st.warning("Reconstruction is approved for live record-level demonstrator exploration only. It is not designated canonical or independently scientifically validated. Pooled values have incomplete output provenance; mean-fold values are supported by saved fold records.")

        strict_rows = [r for r in evidence_rows if r["dataset_family"] == "338-row strict verified subset"]
        render_saved_result_family("338-row strict verified subset — separate evaluation record", strict_rows)
        st.caption("The saved mean-fold value is displayed with its fold evidence. A pooled OOF artifact/value was not located and remains NOT ASSESSABLE.")

        tuned = [r for r in evidence_rows if r["result_id"] in {"STAGEA-XGBoost_tuned", "STAGEA-XGBOOST-TUNED-REPLAY"}]
        if tuned:
            render_saved_result_family("Tuned XGBoost: conflicting saved evidence", tuned, conflict_warning=True)
            st.caption("The initial benchmark and separate replay disagree. Both are preserved; no winner or corrected value is selected.")
            st.caption("Initial benchmark: pooled / mean-fold 0.283246831302 / 0.400375824217. Separate checksummed replay: 0.275796345509 / 0.394286907872; its input SHA-256 is absent. The ambiguous QA JSON value 0.380461 matches Extra Trees mean-fold R² and is not another pooled result.")
    except (OSError, KeyError, ValueError) as exc:
        st.error(f"Consolidated saved model evidence is unavailable or malformed: {exc}")

    try:
        batch_provenance = load_batch021_evaluation_provenance()
        batch_entry = batch_provenance["entry"]
        st.subheader("Batch021 dataset identity and additional saved metrics")
        st.code(
            f"Dataset ID: {batch_entry['dataset_id']}\n"
            f"Path: {batch_entry['repository_relative_path']}\n"
            f"Dimensions: {batch_entry['row_count']:,} rows × {batch_entry['column_count']:,} columns\n"
            f"Current SHA-256: {batch_provenance['actual_sha256'] or 'unavailable'}\n"
            f"Saved evaluation input SHA-256: {batch_provenance['saved_input_sha256'] or 'unavailable'}\n"
            f"Target: {batch_entry['target_definition']['field']} — "
            f"{batch_entry['target_definition']['name']} = {batch_entry['target_definition']['equation']}",
            language="text",
        )
        if batch_provenance["identity_matches"]:
            st.success("Saved Batch021 audit input and current Batch021 file hashes match. This supports input-byte attribution; historical metrics have not been freshly reproduced.")
        else:
            st.warning("Batch021 current-snapshot attribution is not established. Historical metrics remain separate; no alternate dataset is substituted.")
        with st.expander("Additional curated Batch021 MAE/RMSE details and filters"):
            saved_batch021_metrics = [
                row for row in load_selected_metrics()
                if row.get("result_family") == "Batch021 fixed audit"
            ]
            metrics = annotate_saved_metric_provenance(saved_batch021_metrics, batch_provenance)
            family_options = sorted({r["result_family"] for r in metrics})
            default_families = ["Batch021 fixed audit"] if "Batch021 fixed audit" in family_options else []
            families = st.multiselect("Result family", family_options, default=default_families)
            target_options = sorted({r["target"] for r in metrics if r["result_family"] in families})
            targets = st.multiselect("Target", target_options, default=target_options)
            designs = sorted({r["validation"] for r in metrics if r["result_family"] in families and r["target"] in targets})
            selected_designs = st.multiselect("Evaluation design", designs, default=designs)
            filtered = [r for r in metrics if r["result_family"] in families and r["target"] in targets and r["validation"] in selected_designs]
            st.dataframe(filtered, hide_index=True, width="stretch")
            numeric_rows = [r for r in filtered if numeric(r, "r2") is not None]
            if numeric_rows and len(families) == 1 and len(targets) == 1:
                metric_choice = st.selectbox("Plot saved metric", ["r2", "mae", "rmse"], format_func=lambda x: {"r2":"Pooled R² (dimensionless)", "mae":"MAE (recorded target scale)", "rmse":"RMSE (recorded target scale)"}[x])
                fig = go.Figure(go.Bar(x=[f"{r['model']} · {r['validation']}" for r in numeric_rows], y=[numeric(r, metric_choice) for r in numeric_rows], marker_color=["#C85A32" if (metric_choice == "r2" and (numeric(r, metric_choice) or 0) < 0) else "#2D5A27" for r in numeric_rows]))
                y_label = "Pooled OOF R² (dimensionless)" if metric_choice == "r2" else "ACR percentage points"
                fig.update_layout(title=f"Saved {metric_choice.upper()} · {families[0]} · {targets[0]}", xaxis_title="Model and evaluation design", yaxis_title=y_label)
                go_plot(fig, max(450, len(numeric_rows) * 22))
            st.caption("These additional curated rows retain their recorded dataset snapshot, target, split, source file, and limitations. MAE/RMSE are ACR percentage points; no mean-fold value is inferred from this table.")
    except (OSError, KeyError, ValueError) as exc:
        st.error(f"Batch021 saved metric detail is unavailable or malformed: {exc}")

elif page == "Validation & Generalization":
    header("Validation & Generalization", "Inspect saved evaluation evidence, split designs, and provenance limits by dataset family.")
    art_col, note_col = st.columns([.18, .82], vertical_alignment="center")
    with art_col:
        st.image(str(asset_path("laboratory")), width=170, alt="Editorial food-science laboratory illustration with sample vials, glassware, produce, and a balance.")
    with note_col:
        st.caption("Illustrative research setting. Validation figures and tables below come from saved evidence records.")
    st.markdown("**Random split** can place related rows or sources on both sides. **Molecular-grouped** evaluation holds molecular identities out but can retain DOI overlap. **DOI/source-held-out** evaluation holds DOI groups out; DOI is only a proxy for independent research sources and does not guarantee laboratory independence.")
    st.info("Pooled OOF R² and mean-fold R² are different summaries. Dataset families and target definitions are kept separate; tables below are evidence registers, not a cross-dataset leaderboard.")
    try:
        validation_evidence = load_consolidated_model_evidence()
        validation_families = [
            ("Historical Stage A benchmark — Retention_Final", lambda r: r["result_id"].startswith("STAGEA-") and r["result_id"] != "STAGEA-XGBOOST-TUNED-REPLAY"),
            ("Historical Stage A tuned-XGBoost replay", lambda r: r["result_id"] == "STAGEA-XGBOOST-TUNED-REPLAY"),
            ("Batch021 ACR fixed audit", lambda r: r["dataset_family"] == "Batch021 ACR fixed audit"),
            ("Reconstruction ACR saved evaluation", lambda r: r["dataset_family"] == "Verified Reconstruction ACR"),
            ("338-row strict verified subset", lambda r: r["dataset_family"] == "338-row strict verified subset"),
        ]
        st.subheader("Saved evaluation evidence by dataset family")
        for title, predicate in validation_families:
            selected = [r for r in validation_evidence if predicate(r)]
            if selected:
                with st.expander(title):
                    render_saved_result_family(title, selected, show_details=False)
        st.caption("Configuration, grouping unit, fold count, pooled/mean-fold evidence status, output checksum status, and input provenance are taken from the final Phase 4 consolidation register.")
    except (OSError, KeyError, ValueError) as exc:
        st.error(f"Consolidated validation evidence is unavailable or malformed: {exc}")

    try:
        fold_rows = load_consolidated_fold_evidence()
        fold_families = [
            "Historical Stage A benchmark",
            "Historical Stage A replay",
            "Batch021 ACR fixed audit",
            "Verified Reconstruction ACR",
            "338-row strict verified subset",
        ]
        st.subheader("Saved fold records")
        for family_name in fold_families:
            family_folds = [r for r in fold_rows if r["dataset_family"] == family_name]
            if family_folds:
                with st.expander(f"{family_name} — {len(family_folds)} saved fold records"):
                    st.dataframe(family_folds, hide_index=True, width="stretch")
        st.caption("Fold R² values are read from saved records. No fold values are re-derived for display. Post1000 mean-fold R² is not assessable in the saved evidence.")
    except (OSError, KeyError, ValueError) as exc:
        st.error(f"Saved fold evidence is unavailable or malformed: {exc}")

    st.subheader("Post1000 historical checksum and metric conflicts")
    try:
        conflict_rows = load_historical_metric_conflicts()
        post1000_conflicts = [r for r in conflict_rows if r["conflict_id"].startswith("P21-")]
        hash_conflicts = [r for r in post1000_conflicts if "-HASH-" in r["conflict_id"]]
        row_conflicts = [r for r in post1000_conflicts if "-ROW-" in r["conflict_id"]]
        cols = st.columns(3)
        cols[0].metric("Aggregate checksum mismatches", len(hash_conflicts))
        cols[1].metric("Comparison rows that differ", len(row_conflicts))
        cols[2].metric("Other comparison rows agreeing", "9 of 21")
        st.warning("All three combined comparison/fold/OOF files fail their recorded hashes. Twelve of 21 comparison rows differ across views; nine agree numerically, but the aggregate remains checksum-invalid. The alternate-runner explanation is possible, not proven.")
        st.dataframe(post1000_conflicts, hide_index=True, width="stretch")
        st.caption("This conflict register preserves the component and combined values without selecting a winner, ranking models, changing outputs, or claiming that a checksum mismatch proves overwrite.")
    except (OSError, KeyError, ValueError) as exc:
        st.error(f"Historical conflict register is unavailable or malformed: {exc}")

    try:
        batch_provenance = load_batch021_evaluation_provenance()
        batch_entry = batch_provenance["entry"]
        if batch_provenance["identity_matches"]:
            st.success(
                f"Saved Batch021 audit input and current Batch021 file have matching SHA-256 "
                f"`{batch_provenance['actual_sha256']}`. This supports input-byte attribution only; "
                "the historical evaluation has not been freshly reproduced."
            )
        else:
            st.warning(
                "Saved Batch021 evaluation remains historical evidence, but its input-byte "
                "identity does not match the current file. Attribution is blocked; no alternate "
                "dataset is substituted."
            )
        st.markdown(
            f"**Historical dataset:** `{batch_entry['repository_relative_path']}`  \n"
            f"**Dataset ID:** `{batch_entry['dataset_id']}`  \n"
            f"**Target:** `{batch_entry['target_definition']['field']}` — "
            f"{batch_entry['target_definition']['name']} = "
            f"`{batch_entry['target_definition']['equation']}`  \n"
            f"**Model:** {batch_entry['saved_evaluation_provenance']['model']}  \n"
            f"**Splitter:** {batch_entry['saved_evaluation_provenance']['splitter']}"
        )
        summary = batch_provenance.get("summary")
        if summary and isinstance(summary.get("results"), list):
            summary_rows = []
            for result in summary["results"]:
                summary_rows.append({
                    "validation_strategy": result.get("validation_strategy"),
                    "observations": result.get("n_observations"),
                    "molecular_groups": result.get("n_molecular_groups"),
                    "source_groups": result.get("n_source_groups"),
                    "pooled_oof_r2": result.get("r2"),
                    "mean_fold_r2": result.get("mean_fold_r2"),
                    "mean_fold_mae": result.get("mean_fold_mae"),
                    "mean_fold_rmse": result.get("mean_fold_rmse"),
                })
            st.dataframe(summary_rows, hide_index=True, width="stretch")
            st.caption("These are values read from the saved validation summary. Pooled out-of-fold R² and mean fold R² are distinct summaries; neither is recalculated here.")
    except (OSError, KeyError, ValueError) as exc:
        st.warning(f"Batch021 validation provenance unavailable: {exc}")
    st.subheader("Pooled versus fold-wise R²")
    st.caption("The following plot reads saved fold-wise values. Fold metrics are shown separately from pooled out-of-fold results; no scores are recalculated.")
    try:
        folds = load_validation_folds()
        fig = go.Figure()
        colors = {"molecular_grouped":"#2D5A27", "source_held_out":"#C85A32"}
        labels = {"molecular_grouped":"Molecular-grouped (fold-wise)", "source_held_out":"DOI/source-held-out (fold-wise)"}
        for strategy in ("molecular_grouped", "source_held_out"):
            group = [r for r in folds if r.get("validation_strategy") == strategy]
            points = [(int(r["fold"]), numeric(r, "r2")) for r in group if numeric(r, "r2") is not None]
            if points:
                fig.add_trace(go.Scatter(x=[x for x, _ in points], y=[y for _, y in points], mode="lines+markers", name=labels[strategy], line=dict(color=colors[strategy], width=3), marker=dict(size=9)))
        fig.add_hline(y=0, line_dash="dash", line_color="#77716A")
        fig.update_layout(title="Saved Batch021 fold-wise R² — historical evaluation", xaxis_title="Fold", yaxis_title="Fold R²")
        if fig.data:
            go_plot(fig)
        else:
            st.info("No finite saved fold R² values are available for this chart.")
    except (OSError, KeyError, ValueError) as exc:
        st.error(f"Saved fold metrics unavailable or malformed: {exc}")
    st.caption("Local sources: `stageA/molecular_vs_source_validation_audit/fold_metrics.csv` and `validation_summary.json`. The saved summary records the Batch021 input SHA-256. DOI-held-out remains a source-family proxy, not proof of laboratory independence.")

elif page == "Scientific Limitations":
    header("Scientific Limitations", "Limitations are part of the evidence, not hidden behind a general disclaimer.")
    art_col, note_col = st.columns([.34, .66], vertical_alignment="center")
    with art_col:
        st.image(str(asset_path("raw_cooked")), width=300, alt="Conceptual, balanced illustration of raw and cooked vegetables with a neutral two-way arrow; it shows no direction of change.")
    with note_col:
        st.caption("Conceptual comparison only. It does not imply that cooking consistently increases or decreases concentration or total-mass retention.")
    st.caption("Each item records the evidence basis, its interpretive effect, its current status, and the handling used in this prototype.")
    for limitation in SCIENTIFIC_LIMITATIONS:
        with st.expander(f"{limitation['issue']} — {limitation['status']}"):
            st.markdown(f"**Evidence:** {limitation['evidence']}")
            st.markdown(f"**Effect on interpretation:** {limitation['effect_on_interpretation']}")
            st.markdown(f"**Handling:** {limitation['handling']}")
    st.info("No causal cooking effect, clinical or patient-specific risk, bioavailability, nutrition/exposure, consumer-ready prediction, or deployment claim is supported.")

elif page == "Reproducibility & Evidence":
    header("Reproducibility & Evidence", "Inspect snapshot identity, result status, and the limits of the available provenance.")
    st.subheader("Evidence status definitions")
    st.markdown(
        "- **VERIFIED FROM SAVED RECORDS:** the stated value is traceable to saved records such as fold results; this does not mean the model was freshly rerun.\n"
        "- **REPORTED — PROVENANCE INCOMPLETE:** a saved metric exists, but the run/input identity or other provenance is incomplete.\n"
        "- **CONFLICTING SAVED EVIDENCE:** multiple preserved records disagree; no version is selected.\n"
        "- **UNVERIFIED:** supporting records or essential identity details were not found.\n"
        "- **NOT ASSESSABLE:** the requested value cannot be established from the available saved evidence."
    )
    st.caption("Pooled OOF R² and arithmetic mean-fold R² are different summaries. Values are never compared across unrelated target or dataset families as one leaderboard.")
    st.subheader("Dataset family register")
    st.dataframe(DATASET_FAMILIES, hide_index=True, width="stretch")
    st.subheader("Approved dataset registry")
    try:
        registry = load_dataset_registry()
        st.info(registry["owner_decision"]["scope"])
        registry_rows = []
        for item in registry["datasets"].values():
            target = item.get("target_definition", {})
            registry_rows.append({
                "dataset_id": item.get("dataset_id"),
                "path": item.get("repository_relative_path"),
                "SHA-256": item.get("expected_sha256", item.get("current_file_sha256", "not recorded")),
                "rows × columns": f"{item.get('row_count')} × {item.get('column_count')}",
                "target": target.get("field"),
                "equation / meaning": target.get("equation") or target.get("scientific_meaning"),
                "designation": item.get("designation_status"),
                "canonical": item.get("canonical_scientific_dataset", False),
                "allowed uses": ", ".join(item.get("allowed_application_uses", [])),
            })
        st.dataframe(registry_rows, hide_index=True, width="stretch")
    except (OSError, KeyError, ValueError) as exc:
        st.error(f"Dataset registry unavailable or malformed: {exc}")
    st.subheader("Documented dataset snapshots")
    try:
        st.dataframe(load_dataset_catalog(), hide_index=True, width="stretch")
    except (OSError, KeyError) as exc:
        st.warning(f"Snapshot catalog unavailable: {exc}")
    st.subheader("Final Phase 4 model/R² evidence register")
    try:
        result_rows = load_consolidated_model_evidence()
        st.caption("All model evidence is keyed by dataset family, target, model, evaluation protocol, evidence status, checksum status, and input provenance. The register is read-only.")
        st.dataframe(consolidated_identity_rows(result_rows), hide_index=True, width="stretch")
        st.dataframe(consolidated_metric_rows(result_rows), hide_index=True, width="stretch")
        with st.expander("All configuration and provenance details"):
            st.dataframe(consolidated_context_rows(result_rows), hide_index=True, width="stretch")
    except (OSError, KeyError, ValueError) as exc:
        st.error(f"Consolidated model evidence is unavailable or malformed: {exc}")
    st.subheader("Unverified and provenance gaps")
    try:
        st.dataframe(load_provenance_gap_register(), hide_index=True, width="stretch")
    except (OSError, KeyError, ValueError) as exc:
        st.warning(f"Provenance-gap register is unavailable or malformed: {exc}")
    st.subheader("Key provenance limitation")
    st.code(
        f"Batch021 saved audit input: {BATCH021_HISTORICAL_AUDIT_SHA256}\n"
        f"Batch021 current CSV:        {BATCH021_CURRENT_SHA256}\n"
        f"Live Reconstruction:         {RECONSTRUCTION_SHA256}",
        language="text",
    )
    st.info("Reconstruction is approved for this demonstrator's live exploration only. Its 1,016 rows do not make it identical to Batch021; the approval does not designate it canonical or independently validate it. Batch021 remains a separate historical reference for saved results and metadata.")
    st.caption("The historical Stage A benchmark, Batch021 ACR, Reconstruction ACR, strict subset, and Batch021 post1000 evidence remain separate datasets/evaluation records. The demonstrator does not load the historical Retention_Final source CSV.")
    st.subheader("Local source references")
    for path in [
        "research/CookRisk_Computational_Research_Prototype/01_RESEARCH_OVERVIEW.md",
        "research/CookRisk_Computational_Research_Prototype/06_VALIDATION_AND_GENERALIZATION.md",
        "research/CookRisk_Computational_Research_Prototype/UPDATED_RESEARCH_READINESS_ASSESSMENT.md",
        "stageA/verified_concentration_ratio_reconstruction/final_dataset_eda_report.md",
        "stageA/molecular_vs_source_validation_audit/validation_summary.json",
        "stageA/final_prototype_2026_11_10/manifest.json",
    ]:
        st.code(path, language="text")
    st.caption("Open these paths in the local repository to inspect the underlying records. No Stage B or restricted Stage C/D content is read by this demonstrator.")

st.markdown(
    "<footer class='site-footer'><strong>Nutrition Retention Research Initiative</strong>"
    "<span>CookRisk · Computational research demonstrator · Historical evidence is not cooking advice</span></footer>",
    unsafe_allow_html=True,
)
