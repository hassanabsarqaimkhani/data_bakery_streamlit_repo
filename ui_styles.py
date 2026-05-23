from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st

from app_config import APP_NAME, HASSAN_AVATAR_PATH, HASSAN_PORTRAIT_PATH, POWERED_BY, STT_BANNER_PATH, TARGET_URL


def _b64(path: Path) -> str:
    if not path.exists():
        return ""
    mime = "image/jpeg" if path.suffix.lower() in {".jpg", ".jpeg"} else "image/png"
    data = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{mime};base64,{data}"


def inject_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');

        :root {
            --db-bg: #050508;
            --db-black: #050508;
            --db-ink: #0B0F19;
            --db-graphite: #111827;
            --db-panel: rgba(9, 12, 20, 0.90);
            --db-panel2: rgba(15, 23, 42, 0.76);
            --db-red: #E50914;
            --db-red2: #B00020;
            --db-cyan: #00E5FF;
            --db-lime: #B6FF00;
            --db-violet: #9B5CFF;
            --db-yellow: #FFE500;
            --db-white: #F8FAFC;
            --db-muted: #9CA3AF;
            --db-line: rgba(255,255,255,0.13);
        }

        html, body, [class*="css"] { font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif !important; }

        * { border-radius: 0 !important; }

        .stApp {
            background:
                linear-gradient(120deg, rgba(229,9,20,0.24), transparent 24%),
                radial-gradient(circle at 14% 16%, rgba(0,229,255,0.22), transparent 24%),
                radial-gradient(circle at 82% 8%, rgba(182,255,0,0.15), transparent 20%),
                radial-gradient(circle at 84% 82%, rgba(155,92,255,0.22), transparent 24%),
                linear-gradient(135deg, #030305 0%, #080A12 38%, #111827 100%);
            color: var(--db-white);
        }

        .stApp::before {
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            background-image:
                linear-gradient(rgba(255,255,255,0.035) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255,255,255,0.035) 1px, transparent 1px);
            background-size: 42px 42px;
            mask-image: linear-gradient(to bottom, rgba(0,0,0,0.75), transparent 78%);
            z-index: 0;
        }

        [data-testid="stAppViewContainer"] > .main { position: relative; z-index: 1; }
        [data-testid="stHeader"] { background: rgba(5, 5, 8, 0.0); }
        [data-testid="stToolbar"] { right: 1rem; }

        [data-testid="stSidebar"] {
            background:
                linear-gradient(180deg, rgba(176,0,32,0.30), rgba(5,5,8,0.96) 34%),
                linear-gradient(135deg, rgba(0,229,255,0.08), transparent 42%);
            border-right: 2px solid rgba(229,9,20,0.55);
            box-shadow: 12px 0 50px rgba(0,0,0,0.45);
        }
        [data-testid="stSidebar"] * { color: #F8FAFC; }

        h1, h2, h3 { letter-spacing: -0.04em; }
        h3 { color: #FFFFFF !important; font-weight: 900 !important; }
        p, label, span, div { font-feature-settings: 'cv02', 'cv03', 'cv04', 'cv11'; }

        .block-container { padding-top: 1.4rem !important; max-width: 1480px !important; }

        .db-shell-line {
            height: 3px;
            background: linear-gradient(90deg, var(--db-red), var(--db-cyan), var(--db-lime), var(--db-violet));
            margin: 0 0 18px 0;
            box-shadow: 0 0 28px rgba(0,229,255,0.35);
        }

        .db-hero {
            position: relative;
            overflow: hidden;
            border: 2px solid rgba(255,255,255,0.15);
            border-left: 8px solid var(--db-red);
            border-bottom: 4px solid var(--db-cyan);
            background:
                linear-gradient(122deg, rgba(5,5,8,0.97) 0%, rgba(12,17,30,0.92) 52%, rgba(80,0,14,0.74) 100%);
            box-shadow: 0 34px 90px rgba(0,0,0,0.45), inset 0 0 90px rgba(229,9,20,0.10);
            padding: 0;
            margin: 0 0 22px 0;
        }
        .db-hero::before {
            content: "";
            position: absolute;
            inset: 0;
            background:
                linear-gradient(90deg, transparent 0%, rgba(0,229,255,0.10) 48%, transparent 62%),
                repeating-linear-gradient(135deg, rgba(255,255,255,0.035) 0 1px, transparent 1px 14px);
            pointer-events: none;
        }
        .db-hero-grid {
            position: relative;
            display: grid;
            grid-template-columns: 1.3fr 0.55fr;
            min-height: 420px;
        }
        .db-hero-copy { padding: 42px 40px 38px 40px; }
        .db-superline {
            display: inline-block;
            color: #050508;
            background: linear-gradient(90deg, var(--db-lime), var(--db-cyan));
            font-weight: 950;
            font-size: 12px;
            letter-spacing: 0.22em;
            text-transform: uppercase;
            padding: 8px 12px;
            margin-bottom: 18px;
        }
        .db-title {
            font-size: clamp(44px, 6vw, 84px);
            line-height: 0.88;
            font-weight: 950;
            letter-spacing: -0.075em;
            color: #fff;
            max-width: 940px;
            text-transform: uppercase;
            margin: 0 0 18px 0;
        }
        .db-title .accent-red { color: var(--db-red); text-shadow: 0 0 24px rgba(229,9,20,0.38); }
        .db-title .accent-cyan { color: var(--db-cyan); text-shadow: 0 0 24px rgba(0,229,255,0.36); }
        .db-subtitle {
            font-size: 19px;
            line-height: 1.55;
            color: #D1D5DB;
            max-width: 970px;
            margin-bottom: 26px;
        }
        .db-hero-tags { display: flex; flex-wrap: wrap; gap: 10px; }
        .db-tag {
            border: 1px solid rgba(255,255,255,0.20);
            background: rgba(255,255,255,0.07);
            color: #FFFFFF;
            font-size: 12px;
            font-weight: 850;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            padding: 10px 12px;
        }
        .db-tag.hot { background: rgba(229,9,20,0.18); border-color: rgba(229,9,20,0.62); color: #FFCDD2; }
        .db-tag.cyan { background: rgba(0,229,255,0.12); border-color: rgba(0,229,255,0.50); color: #A5F3FC; }
        .db-tag.lime { background: rgba(182,255,0,0.12); border-color: rgba(182,255,0,0.48); color: #ECFCCB; }
        .db-hero-media {
            position: relative;
            border-left: 2px solid rgba(255,255,255,0.15);
            background: rgba(0,0,0,0.28);
            min-height: 420px;
        }
        .db-stt-banner {
            position: absolute;
            top: 22px;
            left: 18px;
            right: 18px;
            height: 92px;
            object-fit: cover;
            border: 2px solid rgba(229,9,20,0.75);
            filter: saturate(1.14) contrast(1.08);
            box-shadow: 0 18px 45px rgba(0,0,0,0.36);
        }
        .db-portrait {
            position: absolute;
            right: 50px;
            bottom: 105px;
            width: min(82%, 420px);
            height: 300px;
            object-fit: cover;
            object-position: top center;
            border-left: 3px solid var(--db-cyan);
            border-top: 3px solid var(--db-lime);
            filter: contrast(1.04) saturate(1.08);
        }
        .db-media-caption {
            position: absolute;
            left: 18px;
            bottom: 0;
            max-width: 190px;
            background: rgba(5,5,8,0.82);
            border: 1px solid rgba(255,255,255,0.18);
            border-left: 4px solid var(--db-red);
            padding: 14px;
            color: #E5E7EB;
            font-size: 12px;
            line-height: 1.35;
            font-weight: 700;
        }

        .db-stt-strip {
            display: grid;
            grid-template-columns: 150px 1fr auto;
            align-items: center;
            gap: 18px;
            border: 1px solid rgba(255,255,255,0.16);
            border-left: 6px solid var(--db-red);
            background: linear-gradient(90deg, rgba(229,9,20,0.22), rgba(0,229,255,0.10), rgba(182,255,0,0.06));
            padding: 14px 18px;
            margin: 0 0 20px 0;
        }
        .db-stt-strip img { width: 150px; height: 48px; object-fit: cover; border: 1px solid rgba(255,255,255,0.16); }
        .db-stt-strip-title { color: #FFFFFF; font-size: 18px; font-weight: 950; letter-spacing: -0.03em; }
        .db-stt-strip-sub { color: #CBD5E1; font-size: 13px; font-weight: 650; margin-top: 2px; }
        .db-stt-strip-badge { color: #050508; background: var(--db-lime); font-size: 12px; font-weight: 950; letter-spacing: 0.14em; text-transform: uppercase; padding: 9px 12px; }

        .db-kpi {
            position: relative;
            padding: 20px 18px;
            border: 1px solid rgba(255,255,255,0.16);
            border-top: 4px solid var(--db-red);
            background: rgba(5,8,16,0.78);
            box-shadow: 0 20px 60px rgba(0,0,0,0.26);
            min-height: 118px;
            overflow: hidden;
        }
        .db-kpi::after {
            content: "";
            position: absolute;
            right: -30px; top: -30px;
            width: 90px; height: 90px;
            background: radial-gradient(circle, rgba(0,229,255,0.24), transparent 60%);
        }
        .db-kpi-label { color: #9CA3AF; font-size: 12px; text-transform: uppercase; letter-spacing: 0.18em; font-weight: 850; }
        .db-kpi-value { color: #FFFFFF; font-size: 30px; font-weight: 950; margin-top: 8px; letter-spacing: -0.05em; }
        .db-kpi-note { color: #D1D5DB; font-size: 12px; margin-top: 8px; }

        .db-section-title {
            display: flex;
            align-items: center;
            gap: 12px;
            margin: 20px 0 8px 0;
        }
        .db-section-title .marker { width: 12px; height: 32px; background: linear-gradient(180deg, var(--db-red), var(--db-cyan)); display: inline-block; }
        .db-section-title .text { font-size: 28px; line-height: 1; font-weight: 950; letter-spacing: -0.055em; color: #FFFFFF; text-transform: uppercase; }
        .db-section-copy { color: #CBD5E1; font-size: 15px; line-height: 1.55; margin: 0 0 16px 0; }

        .db-sidebar-brand {
            border: 1px solid rgba(255,255,255,0.16);
            border-top: 4px solid var(--db-red);
            background: rgba(5,5,8,0.62);
            padding: 12px;
            margin-bottom: 14px;
        }
        .db-sidebar-logo { width: 100%; height: auto; display: block; border: 1px solid rgba(255,255,255,0.12); margin-bottom: 12px; }
        .db-sidebar-profile { display: grid; grid-template-columns: 58px 1fr; gap: 10px; align-items: center; }
        .db-sidebar-profile img { width: 58px; height: 58px; object-fit: cover; border: 2px solid var(--db-cyan); }
        .db-sidebar-name { font-size: 14px; font-weight: 950; letter-spacing: -0.02em; line-height: 1.1; }
        .db-sidebar-role { color: #D1D5DB; font-size: 11px; line-height: 1.25; margin-top: 4px; }

        .stButton > button, .stDownloadButton > button {
            border: 1px solid rgba(255,255,255,0.22) !important;
            border-left: 5px solid var(--db-red) !important;
            background: linear-gradient(90deg, #E50914, #8B00FF 52%, #00E5FF) !important;
            color: white !important;
            font-weight: 950 !important;
            letter-spacing: 0.02em !important;
            padding: 0.82rem 1.1rem !important;
            box-shadow: 0 14px 34px rgba(229,9,20,0.26), 0 0 30px rgba(0,229,255,0.12) !important;
            text-transform: uppercase !important;
        }
        .stButton > button:hover, .stDownloadButton > button:hover {
            border-left-color: var(--db-lime) !important;
            filter: brightness(1.08) saturate(1.16);
            transform: translateY(-1px);
        }

        div[data-testid="stExpander"] {
            border: 1px solid rgba(255,255,255,0.18) !important;
            border-left: 4px solid rgba(0,229,255,0.76) !important;
            background: rgba(8, 12, 20, 0.78) !important;
            box-shadow: 0 18px 45px rgba(0,0,0,0.20);
        }
        div[data-testid="stExpander"] summary { font-weight: 850 !important; color: #F8FAFC !important; }

        .stTabs [data-baseweb="tab-list"] { gap: 8px; border-bottom: 1px solid rgba(255,255,255,0.14); }
        .stTabs [data-baseweb="tab"] {
            background: rgba(5,5,8,0.70);
            border: 1px solid rgba(255,255,255,0.14);
            border-bottom: none;
            padding: 10px 18px;
            font-weight: 900;
            letter-spacing: 0.01em;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(90deg, rgba(229,9,20,0.28), rgba(0,229,255,0.12)) !important;
            border-top: 3px solid var(--db-lime) !important;
            color: #FFFFFF !important;
        }

        [data-testid="stNumberInput"] input,
        [data-testid="stTextInput"] input,
        [data-baseweb="select"] > div,
        textarea {
            background: rgba(5,8,16,0.84) !important;
            border: 1px solid rgba(255,255,255,0.18) !important;
            color: #FFFFFF !important;
        }
        [data-testid="stNumberInput"] input:focus,
        [data-testid="stTextInput"] input:focus,
        [data-baseweb="select"] > div:focus-within {
            border-color: var(--db-cyan) !important;
            box-shadow: 0 0 0 1px rgba(0,229,255,0.45) !important;
        }

        [data-testid="stDataFrame"] { border: 1px solid rgba(255,255,255,0.18) !important; }
        .stAlert { border-radius: 0 !important; border-left: 5px solid var(--db-yellow) !important; }
        [data-testid="stMetricValue"] { font-weight: 950 !important; }
        hr { border-color: rgba(255,255,255,0.12) !important; }

        @media (max-width: 920px) {
            .db-hero-grid { grid-template-columns: 1fr; }
            .db-hero-media { min-height: 360px; border-left: none; border-top: 2px solid rgba(255,255,255,0.15); }
            .db-stt-strip { grid-template-columns: 1fr; }
            .db-stt-strip img { width: 100%; height: auto; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def sidebar_brand():
    st.markdown(
        f"""
        <div class="db-sidebar-brand">
            <img class="db-sidebar-logo" src="{_b64(STT_BANNER_PATH)}" alt="STT Solutions" />
            <div class="db-sidebar-profile">
                <img src="{_b64(HASSAN_AVATAR_PATH)}" alt="Hassan Absar" />
                <div>
                    <div class="db-sidebar-name">Hassan Absar</div>
                    <div class="db-sidebar-role">AI & Data Learning Architect<br/>with STT Solutions</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def hero():
    st.markdown(
        f"""
        <div class="db-shell-line"></div>
        <div class="db-hero">
            <div class="db-hero-grid">
                <div class="db-hero-copy">
                    <div class="db-superline">STT Solutions Presents</div>
                    <div class="db-title"><span class="accent-cyan">Data</span> Bakery<br/><span class="accent-red">by Hassan Absar</span><br/><span class="accent-white"> STT SOLUTIONS</span></div>
                    <div class="db-subtitle">
                        An STT Solutions AI & Data learning product for baking realistic, intentionally dirty CSV datasets for Power BI. Configure the recipe, choose the learning objective, inject controlled data quality challenges, and download a professional CSV + PDF package.
                    </div>
                    <div class="db-hero-tags">
                        <span class="db-tag hot">{POWERED_BY}</span>
                        <span class="db-tag cyan">500K–550K Rows</span>
                        <span class="db-tag lime">5–25 Columns</span>
                        <span class="db-tag">CSV + PDF Only</span>
                    </div>
                </div>
                <div class="db-hero-media">
                    <img class="db-stt-banner" src="{_b64(STT_BANNER_PATH)}" alt="STT Solutions" />
                    <img class="db-portrait" src="{_b64(HASSAN_PORTRAIT_PATH)}" alt="Hassan Absar" />
                    <div class="db-media-caption">Built for STT Solutions learners. Designed by Hassan Absar for AI, Data Cleaning, and Power BI Learning Framework.</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def stt_strip():
    st.markdown(
        f"""
        <div class="db-stt-strip">
            <img src="{_b64(STT_BANNER_PATH)}" alt="STT Solutions" />
            <div>
                <div class="db-stt-strip-title">STT Solutions is the institutional engine behind Data Bakery.</div>
                <div class="db-stt-strip-sub">Every generated package carries the STT Solutions learning standard with Hassan Absar's dataset design system.</div>
            </div>
            <div class="db-stt-strip-badge">Powered Layer</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(title: str, copy: str = ""):
    st.markdown(
        f"""
        <div class="db-section-title"><span class="marker"></span><span class="text">{title}</span></div>
        {f'<div class="db-section-copy">{copy}</div>' if copy else ''}
        """,
        unsafe_allow_html=True,
    )


def kpi_cards():
    cols = st.columns(4)
    values = [
        ("Dataset Types", "32", "Full library from day one"),
        ("Recipe Size", "500K–550K", "Hosted Streamlit range"),
        ("Columns", "5–25", "Locked recipe limit"),
        ("Delivery", "ZIP", "CSV + PDF package"),
    ]
    for col, (label, value, note) in zip(cols, values):
        with col:
            st.markdown(
                f"<div class='db-kpi'><div class='db-kpi-label'>{label}</div><div class='db-kpi-value'>{value}</div><div class='db-kpi-note'>{note}</div></div>",
                unsafe_allow_html=True,
            )
