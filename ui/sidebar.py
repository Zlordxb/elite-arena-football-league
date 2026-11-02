"""Sidebar: branding, navigation and a short season summary."""

import streamlit as st


def render_sidebar(tournament, page_names):
    with st.sidebar:
        st.markdown(
            '<div class="ea-brand">ELITE <span>ARENA</span></div>',
            unsafe_allow_html=True,
        )
        st.caption("FOOTBALL LEAGUE MANAGEMENT")
        st.markdown("---")

        page = st.radio("NAVIGATION", page_names)

        st.markdown("---")
        st.markdown("**CURRENT SEASON**")
        st.markdown(f"🏆 {tournament.name}")
        st.markdown(f"👥 {len(tournament.teams)} teams")
        st.markdown(f"⚽ {len(tournament.matches)} fixtures")
        st.markdown("---")
        st.caption("ELITE ARENA • OOP EDITION")

    return page
