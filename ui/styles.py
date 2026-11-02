"""Global CSS for the Elite Arena theme."""

import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root { --ea-bg: #0b1220; --ea-card: #121d30; --ea-card2: #17243a;
        --ea-line: #26354b; --ea-green: #a3e635; --ea-text: #f3f6fb;
        --ea-muted: #9aa9bf; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: radial-gradient(ellipse at 15% 0%, #182943 0%, #0b1220 46%); color: var(--ea-text); }
.block-container { padding-top: 1.4rem; padding-bottom: 2.4rem; max-width: 1500px; }
[data-testid="stSidebar"] { background: #0d1727; border-right: 1px solid #223149; }
[data-testid="stSidebar"] * { color: #e9eef8; }
.ea-brand { font-size: 1.6rem; font-weight: 800; letter-spacing: .06em; color: #f7fafc; }
.ea-brand span { color: var(--ea-green); }
.ea-kicker { color: var(--ea-green); text-transform: uppercase; letter-spacing: .17em;
             font-size: .72rem; font-weight: 800; margin-bottom: .35rem; }
.ea-title { font-size: 2.2rem; font-weight: 800; letter-spacing: -.04em; margin: 0; color: #f7fafc; }
.ea-subtitle { color: var(--ea-muted); margin-top: .35rem; margin-bottom: 1.2rem; }
.ea-card { background: linear-gradient(145deg, rgba(23,36,58,.96), rgba(16,27,44,.96));
           border: 1px solid #2a3a51; border-radius: 18px; padding: 1.15rem 1.25rem; min-height: 120px; }
.ea-card-label { color: #a6b4c8; font-size: .78rem; font-weight: 600; letter-spacing: .06em; text-transform: uppercase; }
.ea-card-value { color: #f8fafc; font-size: 2rem; font-weight: 800; margin-top: .35rem; }
.ea-card-note { color: #a3e635; font-size: .78rem; margin-top: .25rem; }
.ea-section { font-size: 1.15rem; font-weight: 750; margin: .6rem 0 .8rem; color: #f5f7fb; }
.ea-panel { background: rgba(18,29,48,.78); border: 1px solid #26354b; border-radius: 16px; padding: 1rem 1.1rem; }
.ea-pill { display: inline-block; border-radius: 99px; padding: .22rem .62rem; font-size: .72rem; font-weight: 700;
           background: #243449; color: #dbe6f5; border: 1px solid #3a4c63; letter-spacing: .08em; }
.ea-pill-green { background: #263a19; border-color: #476a25; color: #c8f68a; }
.ea-pill-red { background: #3a1919; border-color: #6a2525; color: #f6a8a8; }
.ea-scoreline { text-align: center; font-size: 1.13rem; font-weight: 750; }
.ea-scoreline span { color: #a3e635; }
.ea-right-muted { text-align: right; color: #9aa9bf; }
div[data-testid="stMetric"] { background: #121d30; border: 1px solid #2a3a51; padding: 1rem; border-radius: 16px; }
div[data-testid="stMetricLabel"] { color: #a6b4c8; }
div[data-testid="stMetricValue"] { color: #f8fafc; }
.stButton > button { border-radius: 10px; border: 1px solid #3b4d65; font-weight: 700; }
.stButton > button[kind="primary"] { background: #a3e635; border-color: #a3e635; color: #17210b; }
.stButton > button[kind="primary"]:hover { background: #bef264; border-color: #bef264; color: #17210b; }
div[data-testid="stDataFrame"] { border: 1px solid #26354b; border-radius: 12px; overflow: hidden; }
hr { border-color: #26354b; }
.small-muted { color: #9aa9bf; font-size: .84rem; }
</style>
"""


def inject_styles():
    st.markdown(CSS, unsafe_allow_html=True)
