"""
Design tokens and global CSS.

Direction: a broadcast scoreboard at a night match. Deep navy surfaces,
trophy gold for what matters (the leader, primary actions), pitch green
only for "live", and a condensed face for scores and table figures.

Motion is deliberate and small: one staggered entrance per page, a live
pulse, the progress meter filling, and hover lifts that answer the pointer.
Everything is disabled under prefers-reduced-motion.
"""

import streamlit as st

# Python-side copies of the tokens, used by ui/charts.py.
TOKENS = {
    "bg": "#0b1626",
    "surface": "#13263a",
    "surface_2": "#1a3148",
    "line": "#243b55",
    "line_2": "#2f4a68",
    "ink": "#eef3f8",
    "ink_2": "#b7c4d4",
    "ink_3": "#8496ab",
    "gold": "#e9b949",
    "gold_2": "#f3cf6e",
    "good": "#0ca30c",
    "warn": "#fab219",
    "bad": "#d03b3b",
    "blue": "#3987e5",
    "font": "Barlow, 'Segoe UI', system-ui, sans-serif",
    "display": "'Barlow Condensed', Barlow, 'Segoe UI', system-ui, sans-serif",
}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600;700&family=Barlow+Condensed:wght@500;600;700&display=swap');

:root {
  --ea-bg: #0b1626; --ea-surface: #13263a; --ea-surface-2: #1a3148;
  --ea-line: #243b55; --ea-line-2: #2f4a68;
  --ea-ink: #eef3f8; --ea-ink-2: #b7c4d4; --ea-ink-3: #8496ab;
  --ea-gold: #e9b949; --ea-gold-2: #f3cf6e; --ea-on-gold: #1a1405;
  --ea-good: #0ca30c; --ea-warn: #fab219; --ea-bad: #d03b3b; --ea-blue: #3987e5;
  --ea-font: 'Barlow', 'Segoe UI', system-ui, sans-serif;
  --ea-display: 'Barlow Condensed', 'Barlow', 'Segoe UI', system-ui, sans-serif;
  --ea-radius: 14px; --ea-radius-sm: 10px;
  --ea-ease: cubic-bezier(.2, .7, .2, 1);
}

/* ---- Motion ---------------------------------------------------------- */
@keyframes ea-rise { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }
@keyframes ea-fill { from { width: 0; } }
@keyframes ea-pulse { 0%, 100% { box-shadow: 0 0 0 3px rgba(12,163,12,.25); } 50% { box-shadow: 0 0 0 7px rgba(12,163,12,.06); } }
@keyframes ea-pop { from { opacity: 0; transform: scale(.5); } to { opacity: 1; transform: none; } }
@keyframes ea-glow { 0%, 100% { box-shadow: inset 0 0 0 1px rgba(12,163,12,.25); } 50% { box-shadow: inset 0 0 0 1px rgba(12,163,12,.6), 0 0 18px rgba(12,163,12,.12); } }
.ea-hero, .ea-tile, .ea-score, .ea-table-wrap, .ea-res, .ea-empty, .ea-vs, .ea-player, .ea-club,
.ea-root .ea-club-hero, .ea-root .ea-tl li, .ea-root .ea-fx { animation: ea-rise .5s var(--ea-ease) both; animation-delay: calc(var(--i, 0) * 55ms); }
.ea-meter .fill { animation: ea-fill 1.1s var(--ea-ease) both; }
.ea-form span { animation: ea-pop .35s var(--ea-ease) both; animation-delay: calc(140ms + var(--i, 0) * 50ms); }
.ea-pill.live::before { animation: ea-pulse 1.6s ease-in-out infinite; }
.ea-root .ea-score.live, .ea-root .ea-fx .s.live { animation: ea-rise .5s var(--ea-ease) both, ea-glow 2.4s ease-in-out infinite; }
.ea-root .ea-score, .ea-root .ea-tile, .ea-root .ea-player, .ea-root .ea-club { transition: transform .18s var(--ea-ease), border-color .18s, box-shadow .18s; }
.ea-root .ea-score:hover, .ea-root .ea-tile:hover, .ea-root .ea-player:hover, .ea-root .ea-club:hover { transform: translateY(-2px); border-color: var(--ea-line-2); box-shadow: 0 10px 24px rgba(0,0,0,.25); }
.ea-root .ea-table tbody tr td { transition: background .15s; }
.ea-root .ea-table tbody tr:hover td { background: rgba(255,255,255,.035); }
[data-testid="stSidebar"] [role="radiogroup"] > label { transition: background .15s, border-color .15s; }
@media (prefers-reduced-motion: reduce) {
  .stApp *, .stApp *::before, .stApp *::after { animation: none !important; transition: none !important; }
}

/* ---- Base ---------------------------------------------------------- */
/* Text elements only: icon spans keep their own icon font. */
html, body, .stApp p, .stApp label, .stApp input, .stApp textarea, .stApp li,
.stApp [data-testid="stMarkdownContainer"], .stApp [data-testid="stWidgetLabel"] { font-family: var(--ea-font); }
.stApp { background: var(--ea-bg); color: var(--ea-ink); }
[data-testid="stHeader"] { background: transparent; }
.block-container { padding: 4rem 2.2rem 3.5rem; max-width: 1480px; }
.stApp h1, .stApp h2, .stApp h3 { font-family: var(--ea-display); letter-spacing: 0; }
.stApp a { color: var(--ea-gold-2); }
[data-testid="stCaptionContainer"], .stApp small { color: var(--ea-ink-3); }

/* ---- Component root (st.markdown wrapper) --------------------------- */
.ea-root p, .ea-root ul, .ea-root ol { margin: 0; }
.ea-root ol { padding-left: 1.2rem; }
.ea-root ul { padding: 0; }
.ea-root img { max-width: none; }

/* ---- Icons, crests, avatars ----------------------------------------- */
.ea-ico { width: 1em; height: 1em; vertical-align: -.15em; flex: none; }
.ea-head .t .ea-ico { width: 1.7rem; height: 1.7rem; margin-right: .55rem; color: var(--ea-gold); vertical-align: -.22rem; }
.ea-crest { display: inline-grid; place-items: center; border-radius: 8px; overflow: hidden; flex: none; vertical-align: middle; filter: drop-shadow(0 2px 4px rgba(0,0,0,.35)); }
.ea-crest img, .ea-crest svg { width: 100%; height: 100%; object-fit: contain; display: block; }
.ea-avatar { display: inline-grid; place-items: center; border-radius: 50%; overflow: hidden; color: #fff; font-family: var(--ea-display); font-weight: 700; flex: none; box-shadow: inset 0 0 0 2px rgba(255,255,255,.18); }
.ea-avatar img { width: 100%; height: 100%; object-fit: cover; display: block; }
.ea-team { display: inline-flex; align-items: center; gap: .5rem; min-width: 0; }
.ea-team > span:last-child { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.ea-team.rev { flex-direction: row-reverse; }

/* ---- Sidebar ------------------------------------------------------- */
[data-testid="stSidebar"] { background: #0d1b2d; border-right: 1px solid var(--ea-line); }
.ea-brand { font-family: var(--ea-display); font-size: 1.7rem; font-weight: 700; line-height: 1; color: var(--ea-ink); padding: .4rem 0 .9rem; display: flex; align-items: center; gap: .55rem; }
.ea-brand .ea-ico { width: 1.5rem; height: 1.5rem; color: var(--ea-gold); }
.ea-brand small { display: block; font-family: var(--ea-font); font-size: .78rem; font-weight: 500; color: var(--ea-ink-3); margin-top: .3rem; }
[data-testid="stSidebar"] [role="radiogroup"] { gap: .1rem; }
[data-testid="stSidebar"] [role="radiogroup"] > label { padding: .5rem .75rem; border-radius: 8px; border-left: 3px solid transparent; margin: 0; cursor: pointer; }
[data-testid="stSidebar"] [role="radiogroup"] > label:hover { background: rgba(255,255,255,.04); }
[data-testid="stSidebar"] [role="radiogroup"] > label:has(input:checked) { background: var(--ea-surface-2); border-left-color: var(--ea-gold); }
[data-testid="stSidebar"] [role="radiogroup"] > label > div:first-child { display: none; }
[data-testid="stSidebar"] [role="radiogroup"] > label p { font-weight: 600; font-size: .98rem; }
[data-testid="stSidebar"] [role="radiogroup"] > label:has(input:checked) [data-testid="stIconMaterial"] { color: var(--ea-gold); }
.ea-season { border-top: 1px solid var(--ea-line); margin-top: 1rem; padding-top: 1rem; display: grid; gap: .45rem; }
.ea-season .n { font-family: var(--ea-display); font-size: 1.25rem; font-weight: 600; line-height: 1.1; }
.ea-season .r { display: flex; justify-content: space-between; color: var(--ea-ink-2); font-size: .9rem; }
.ea-season .r b { color: var(--ea-ink); font-weight: 600; font-variant-numeric: tabular-nums; }

/* ---- Page header & sections --------------------------------------- */
.ea-head { display: flex; align-items: flex-end; justify-content: space-between; gap: 1rem; margin: 0 0 1.1rem; flex-wrap: wrap; }
.ea-head .t { font-family: var(--ea-display); font-size: 2.3rem; font-weight: 700; line-height: 1; margin: 0; color: var(--ea-ink); }
.ea-head p { margin: .35rem 0 0; color: var(--ea-ink-2); font-size: 1rem; max-width: 72ch; }
.ea-sec { display: flex; align-items: baseline; justify-content: space-between; gap: 1rem; margin: 1.2rem 0 .55rem; }
.ea-sec .h { font-family: var(--ea-display); font-size: 1.35rem; font-weight: 600; margin: 0; color: var(--ea-ink); }
.ea-sec span { color: var(--ea-ink-3); font-size: .86rem; }

/* ---- Pills ---------------------------------------------------------- */
.ea-pill { display: inline-flex; align-items: center; gap: .4rem; padding: .18rem .6rem; border-radius: 999px; font-size: .78rem; font-weight: 600; background: var(--ea-surface-2); color: var(--ea-ink-2); border: 1px solid var(--ea-line-2); white-space: nowrap; vertical-align: middle; }
.ea-pill.live { background: rgba(12,163,12,.16); color: #9bf09b; border-color: rgba(12,163,12,.55); }
.ea-pill.live::before { content: ''; width: 7px; height: 7px; border-radius: 50%; background: var(--ea-good); box-shadow: 0 0 0 3px rgba(12,163,12,.25); }
.ea-pill.gold { background: rgba(233,185,73,.14); color: var(--ea-gold-2); border-color: rgba(233,185,73,.5); }
.ea-pill.bad { background: rgba(208,59,59,.14); color: #f3a3a3; border-color: rgba(208,59,59,.5); }

/* ---- Hero ----------------------------------------------------------- */
.ea-hero { position: relative; overflow: hidden; background: var(--ea-surface) center / cover no-repeat; border: 1px solid var(--ea-line); border-radius: var(--ea-radius); padding: 1.4rem 1.6rem; display: grid; grid-template-columns: 1.5fr 1fr; gap: 1.5rem; margin-bottom: 1rem; }
.ea-hero > * { position: relative; }
.ea-hero .name { font-family: var(--ea-display); font-size: 2.6rem; font-weight: 700; line-height: 1; margin: 0 0 .55rem; display: flex; align-items: center; gap: .8rem; flex-wrap: wrap; text-shadow: 0 2px 12px rgba(0,0,0,.35); }
.ea-hero .meta { color: var(--ea-ink-2); display: flex; flex-wrap: wrap; gap: .4rem 1.3rem; font-size: .95rem; }
.ea-hero .meta span { display: inline-flex; align-items: center; gap: .35rem; }
.ea-hero .meta .ea-ico { color: var(--ea-ink-3); }
.ea-hero .meta b { color: var(--ea-ink); font-weight: 600; }
.ea-meter { margin-top: 1rem; }
.ea-meter .track { height: 8px; border-radius: 999px; background: rgba(255,255,255,.08); overflow: hidden; }
.ea-meter .fill { height: 100%; background: var(--ea-gold); border-radius: 999px; }
.ea-meter .cap { display: flex; justify-content: space-between; color: var(--ea-ink-3); font-size: .82rem; margin-top: .4rem; }
.ea-hero .leader { border-left: 1px solid rgba(255,255,255,.1); padding-left: 1.5rem; display: flex; flex-direction: column; justify-content: center; }
.ea-hero .leader .lbl { color: var(--ea-ink-3); font-size: .86rem; display: flex; align-items: center; gap: .35rem; }
.ea-hero .leader .lbl .ea-ico { color: var(--ea-gold); }
.ea-hero .leader .team { font-family: var(--ea-display); font-size: 2rem; font-weight: 600; line-height: 1.05; margin: .3rem 0 .45rem; color: var(--ea-gold-2); display: flex; align-items: center; gap: .7rem; }
.ea-hero .leader .team.muted { color: var(--ea-ink-3); }
.ea-hero .leader .pts { color: var(--ea-ink-2); display: flex; gap: 1rem; align-items: center; flex-wrap: wrap; }
.ea-hero .leader .pts b { font-family: var(--ea-display); font-size: 1.5rem; color: var(--ea-ink); font-weight: 700; }
@media (max-width: 900px) {
  .ea-hero { grid-template-columns: 1fr; }
  .ea-hero .leader { border-left: 0; padding-left: 0; border-top: 1px solid rgba(255,255,255,.1); padding-top: 1rem; }
}

/* ---- Scoreboards ---------------------------------------------------- */
.ea-root .ea-strip { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: .7rem; }
.ea-root .ea-score { background: var(--ea-surface); border: 1px solid var(--ea-line); border-radius: var(--ea-radius-sm); padding: .7rem .9rem; display: grid; grid-template-columns: 1fr auto; gap: .3rem .8rem; align-items: center; }
.ea-root .ea-score.live { border-color: rgba(12,163,12,.6); }
.ea-root .ea-score .t { font-weight: 600; color: var(--ea-ink); min-width: 0; }
.ea-root .ea-score .t.lost { color: var(--ea-ink-3); font-weight: 500; }
.ea-root .ea-score .g { font-family: var(--ea-display); font-size: 1.55rem; font-weight: 700; text-align: right; font-variant-numeric: tabular-nums; min-width: 1.4ch; line-height: 1.1; }
.ea-root .ea-score .g.lost { color: var(--ea-ink-3); }
.ea-root .ea-score .foot { grid-column: 1 / -1; display: flex; justify-content: space-between; align-items: center; color: var(--ea-ink-3); font-size: .78rem; margin-top: .35rem; }

/* Large fixture header (Fixtures page) */
.ea-root .ea-fx { display: grid; grid-template-columns: 1fr auto 1fr; gap: 1.2rem; align-items: center; padding: .2rem 0 .6rem; }
.ea-root .ea-fx .h, .ea-root .ea-fx .a { display: flex; align-items: center; gap: .9rem; }
.ea-root .ea-fx .h { justify-content: flex-end; text-align: right; }
.ea-root .ea-fx .t { font-family: var(--ea-display); font-size: 1.6rem; font-weight: 600; line-height: 1.1; }
.ea-root .ea-fx .t.lost { color: var(--ea-ink-3); }
.ea-root .ea-fx .sub { color: var(--ea-ink-3); font-size: .82rem; margin-top: .15rem; }
.ea-root .ea-fx .s { font-family: var(--ea-display); font-size: 2.2rem; font-weight: 700; background: var(--ea-surface-2); border-radius: 10px; padding: .1rem .9rem; font-variant-numeric: tabular-nums; min-width: 5.5rem; text-align: center; line-height: 1.3; }
.ea-root .ea-fx .meta { grid-column: 1 / -1; display: flex; gap: .6rem; align-items: center; justify-content: center; color: var(--ea-ink-3); font-size: .82rem; }

/* ---- Stat tiles ----------------------------------------------------- */
.ea-tile { position: relative; background: var(--ea-surface); border: 1px solid var(--ea-line); border-radius: var(--ea-radius-sm); padding: .85rem 1rem; min-height: 98px; }
.ea-tile .ic { position: absolute; top: .8rem; right: .9rem; color: var(--ea-ink-3); display: inline-grid; place-items: center; width: 32px; height: 32px; border-radius: 8px; background: rgba(255,255,255,.04); }
.ea-tile .ic .ea-ico { width: 18px; height: 18px; }
.ea-tile.gold .ic { color: var(--ea-gold); background: rgba(233,185,73,.1); }
.ea-tile .l { color: var(--ea-ink-3); font-size: .86rem; }
.ea-tile .v { font-family: var(--ea-display); font-size: 2.1rem; font-weight: 700; line-height: 1.05; margin: .2rem 0 .15rem; color: var(--ea-ink); }
.ea-tile .v small { font-size: 1.1rem; color: var(--ea-ink-2); font-weight: 600; margin-left: .25rem; }
.ea-tile .n { color: var(--ea-ink-2); font-size: .82rem; }
.ea-tile.gold .v { color: var(--ea-gold-2); }
.ea-tile.live .v { color: #9bf09b; }

/* ---- Standings table ------------------------------------------------ */
.ea-root .ea-table-wrap { background: var(--ea-surface); border: 1px solid var(--ea-line); border-radius: var(--ea-radius); padding: .3rem .6rem; overflow-x: auto; }
.ea-root .ea-table { width: 100%; border-collapse: separate; border-spacing: 0; font-size: .95rem; }
.ea-root .ea-table th { text-align: right; color: var(--ea-ink-3); font-weight: 600; font-size: .78rem; padding: .5rem .55rem; border-bottom: 1px solid var(--ea-line); white-space: nowrap; }
.ea-root .ea-table th.left { text-align: left; }
.ea-root .ea-table td { padding: .45rem .55rem; border-bottom: 1px solid var(--ea-line); vertical-align: middle; }
.ea-root .ea-table tr:last-child td { border-bottom: 0; }
.ea-root .ea-table .num { text-align: right; font-variant-numeric: tabular-nums; color: var(--ea-ink-2); }
.ea-root .ea-table .pts { font-family: var(--ea-display); font-size: 1.25rem; font-weight: 700; color: var(--ea-ink); text-align: right; font-variant-numeric: tabular-nums; }
.ea-root .ea-table .rank { width: 2.4rem; color: var(--ea-ink-3); font-variant-numeric: tabular-nums; text-align: center; }
.ea-root .ea-table tr.first .rank { color: var(--ea-gold-2); font-weight: 700; }
.ea-root .ea-table tr.first td:first-child { box-shadow: inset 3px 0 0 var(--ea-gold); }
.ea-root .ea-table .team { font-weight: 600; white-space: nowrap; text-align: left; }
.ea-root .ea-table .team .ea-team { max-width: 200px; }
.ea-root .ea-table .team small { color: var(--ea-ink-3); font-weight: 500; margin-left: .4rem; }
.ea-root .ea-table tr.inactive .team { color: var(--ea-ink-3); }
.ea-root .ea-table tr.hl td { background: rgba(57,135,229,.12); }

/* ---- Form pills ----------------------------------------------------- */
.ea-form { display: inline-flex; gap: 3px; vertical-align: middle; }
.ea-form span { width: 20px; height: 20px; border-radius: 5px; display: inline-grid; place-items: center; font-size: .7rem; font-weight: 700; color: #fff; }
.ea-form .W { background: var(--ea-good); }
.ea-form .D { background: #4e637a; }
.ea-form .L { background: var(--ea-bad); }
.ea-form .none { background: transparent; border: 1px dashed var(--ea-line-2); color: var(--ea-ink-3); }

/* ---- Players & clubs ------------------------------------------------ */
.ea-root .ea-players, .ea-root .ea-clubs { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: .7rem; }
.ea-root .ea-player, .ea-root .ea-club { display: flex; align-items: center; gap: .8rem; background: var(--ea-surface); border: 1px solid var(--ea-line); border-radius: var(--ea-radius-sm); padding: .7rem .85rem; min-width: 0; }
.ea-root .ea-player > div, .ea-root .ea-club > div { min-width: 0; flex: 1; }
.ea-root .ea-player .n, .ea-root .ea-club .n { font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.ea-root .ea-player .r, .ea-root .ea-club .r { color: var(--ea-ink-3); font-size: .82rem; }
.ea-root .ea-player .st { font-size: .72rem; font-weight: 600; color: #9bf09b; }
.ea-root .ea-player.banned { border-color: rgba(208,59,59,.45); }
.ea-root .ea-player.banned .n { color: var(--ea-ink-3); }
.ea-root .ea-player.banned .st { color: #f3a3a3; }
.ea-root .ea-club.inactive { opacity: .6; }
.ea-root .ea-club-hero { display: flex; align-items: center; gap: 1.2rem; background: var(--ea-surface); border: 1px solid var(--ea-line); border-radius: var(--ea-radius); padding: 1.1rem 1.4rem; margin-bottom: .9rem; }
.ea-root .ea-club-hero .n { font-family: var(--ea-display); font-size: 2.2rem; font-weight: 700; line-height: 1; }
.ea-root .ea-club-hero .r { color: var(--ea-ink-2); margin-top: .3rem; }
.ea-root .ea-club-hero .f { display: flex; align-items: center; gap: .6rem; margin-top: .6rem; color: var(--ea-ink-3); font-size: .86rem; }

/* ---- Timeline ------------------------------------------------------- */
.ea-root .ea-tl { list-style: none; margin: 0; padding: 0; position: relative; }
.ea-root .ea-tl::before { content: ''; position: absolute; left: 11px; top: 10px; bottom: 10px; width: 1px; background: var(--ea-line); }
.ea-root .ea-tl li { position: relative; padding: .35rem 0 .35rem 2.1rem; display: grid; grid-template-columns: 7.4rem 1fr; gap: .8rem; align-items: baseline; }
.ea-root .ea-tl .dot { position: absolute; left: 0; top: .45rem; width: 23px; height: 23px; border-radius: 50%; background: var(--ea-surface-2); color: var(--ea-ink-2); display: grid; place-items: center; box-shadow: 0 0 0 3px var(--ea-surface); }
.ea-root .ea-tl .dot .ea-ico { width: 12px; height: 12px; }
.ea-root .ea-tl li.match_finished .dot { background: rgba(57,135,229,.25); color: #9cc4f2; }
.ea-root .ea-tl li.match_started .dot { background: rgba(12,163,12,.22); color: #9bf09b; }
.ea-root .ea-tl li.card .dot { background: rgba(250,178,25,.22); color: #f7cf6e; }
.ea-root .ea-tl li.send_off .dot, .ea-root .ea-tl li.player_banned .dot, .ea-root .ea-tl li.team_deactivated .dot { background: rgba(208,59,59,.22); color: #f3a3a3; }
.ea-root .ea-tl li.schedule_generated .dot, .ea-root .ea-tl li.team_registered .dot { background: rgba(233,185,73,.2); color: var(--ea-gold-2); }
.ea-root .ea-tl .when { color: var(--ea-ink-3); font-size: .8rem; font-variant-numeric: tabular-nums; white-space: nowrap; }
.ea-root .ea-tl .what { color: var(--ea-ink); font-size: .95rem; }
.ea-root .ea-tl .what b { font-weight: 600; color: var(--ea-ink-2); margin-right: .45rem; }
@media (max-width: 700px) { .ea-tl li { grid-template-columns: 1fr; gap: .1rem; } }

/* ---- Result rows ---------------------------------------------------- */
.ea-root .ea-res { display: grid; grid-template-columns: 1fr auto 1fr; gap: .8rem; align-items: center; padding: .5rem 0; border-bottom: 1px solid var(--ea-line); }
.ea-root .ea-res:last-child { border-bottom: 0; }
.ea-root .ea-res .h { display: flex; justify-content: flex-end; font-weight: 600; min-width: 0; }
.ea-root .ea-res .a { display: flex; font-weight: 600; min-width: 0; }
.ea-root .ea-res .lost { color: var(--ea-ink-3); font-weight: 500; }
.ea-root .ea-res .s { font-family: var(--ea-display); font-size: 1.25rem; font-weight: 700; background: var(--ea-surface-2); border-radius: 6px; padding: .05rem .6rem; font-variant-numeric: tabular-nums; min-width: 4rem; text-align: center; }
.ea-root .ea-res .s.live { box-shadow: inset 0 0 0 1px rgba(12,163,12,.6); }
.ea-root .ea-res .sub { grid-column: 1 / -1; color: var(--ea-ink-3); font-size: .78rem; text-align: center; margin-top: -.25rem; }

/* ---- Head-to-head / compare ---------------------------------------- */
.ea-root .ea-vs { display: grid; grid-template-columns: 1fr auto 1fr; gap: 1rem; align-items: center; background: var(--ea-surface); border: 1px solid var(--ea-line); border-radius: var(--ea-radius); padding: 1.1rem 1.4rem; }
.ea-root .ea-vs .t { font-family: var(--ea-display); font-size: 1.9rem; font-weight: 600; line-height: 1.05; display: flex; align-items: center; gap: .8rem; }
.ea-root .ea-vs .t.r { justify-content: flex-end; text-align: right; }
.ea-root .ea-vs .rec { font-family: var(--ea-display); font-size: 2.4rem; font-weight: 700; font-variant-numeric: tabular-nums; color: var(--ea-ink); white-space: nowrap; }
.ea-root .ea-vs .rec small { font-size: 1rem; color: var(--ea-ink-3); font-family: var(--ea-font); font-weight: 500; display: block; text-align: center; }
.ea-root .ea-vs .sub { color: var(--ea-ink-2); font-size: .9rem; margin-top: .3rem; }
.ea-root .ea-vs .sub.r { text-align: right; }

/* ---- Empty state ---------------------------------------------------- */
.ea-root .ea-empty { display: flex; gap: 1rem; align-items: flex-start; border: 1px dashed var(--ea-line-2); border-radius: var(--ea-radius); padding: 1.4rem 1.6rem; margin: .4rem 0 .8rem; }
.ea-root .ea-empty .ic { color: var(--ea-gold); display: grid; place-items: center; width: 48px; height: 48px; border-radius: 12px; background: rgba(233,185,73,.1); flex: none; }
.ea-root .ea-empty .h { font-family: var(--ea-display); font-size: 1.5rem; font-weight: 600; margin: 0 0 .3rem; }
.ea-root .ea-empty p { color: var(--ea-ink-2); margin: 0; max-width: 64ch; }
.ea-root .ea-empty ol { color: var(--ea-ink-2); margin: .6rem 0 0; padding-left: 1.2rem; }

/* ---- Tab bar (horizontal radio, see components.tab_bar) ------------- */
[class*="st-key-tabs-"] [role="radiogroup"] { gap: 0; border-bottom: 1px solid var(--ea-line); margin-bottom: .9rem; flex-wrap: wrap; }
[class*="st-key-tabs-"] [role="radiogroup"] > label { padding: .5rem 1rem; margin: 0 0 -1px; border-bottom: 2px solid transparent; cursor: pointer; transition: border-color .15s, background .15s; }
[class*="st-key-tabs-"] [role="radiogroup"] > label:hover { background: rgba(255,255,255,.03); }
[class*="st-key-tabs-"] [role="radiogroup"] > label:has(input:checked) { border-bottom-color: var(--ea-gold); }
[class*="st-key-tabs-"] [role="radiogroup"] > label > div:first-child { display: none; }
[class*="st-key-tabs-"] [role="radiogroup"] > label p { font-weight: 600; color: var(--ea-ink-2); }
[class*="st-key-tabs-"] [role="radiogroup"] > label:has(input:checked) p { color: var(--ea-ink); }

/* ---- Streamlit chrome ---------------------------------------------- */
[class*="st-key-card-"] { background: var(--ea-surface); }
.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button { font-weight: 600; transition: transform .12s var(--ea-ease), background .15s, border-color .15s; }
.stButton > button:active, .stFormSubmitButton > button:active { transform: scale(.98); }
button:focus-visible, a:focus-visible, input:focus-visible { outline: 2px solid var(--ea-gold); outline-offset: 2px; }
[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }
[data-testid="stMetric"] { background: var(--ea-surface); border: 1px solid var(--ea-line); border-radius: 10px; padding: .8rem 1rem; }
[data-testid="stForm"] { border-color: var(--ea-line); background: var(--ea-surface); }
[data-testid="stFileUploaderDropzone"] { background: var(--ea-surface-2); border: 1px dashed var(--ea-line-2); border-radius: 10px; }
</style>
"""


def inject_styles():
    st.html(CSS)
