"""RECYCLE landing page (English) on Streamlit Community Cloud."""
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="RECYCLE Launchpad", page_icon="♻️", layout="wide")

# The waitlist form needs claude.ai's database, which does not exist here: hide it.
# The page then shows "The waitlist opens at public launch."
HIDE = "<style>#wl,#wl-count-box{display:none!important}</style>"
# Full-width page, no Streamlit padding
st.markdown("<style>.block-container{padding:0!important;max-width:100%!important}"
            "header[data-testid='stHeader']{display:none}</style>", unsafe_allow_html=True)

html = (Path(__file__).parent / "index.html").read_text(encoding="utf-8")
st.iframe(HIDE + html, height=4300)
