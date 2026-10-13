"""RECYCLE landing page (English) on Streamlit Community Cloud.

The mint rate on the page comes from Papertrade's public summary, read server-side every
5 minutes and passed to the page. If Papertrade does not answer, the page uses the flat
rate (100 PAPER per $1, valid while the tracked LP is under $2M).
"""
import json
import time
from pathlib import Path

import requests
import streamlit as st

st.set_page_config(page_title="RECYCLE Launchpad", page_icon="♻️", layout="wide")

RAW = 10 ** 18


@st.cache_data(ttl=300, show_spinner=False)
def live_mint() -> dict | None:
    """PAPER per $1 of loss basis: flat while trackedLp < cliff, then flat * (decay / (decay + tailProgress))^2."""
    try:
        r = requests.get("https://exchange.papertrade.xyz/query/protocol/summary", timeout=8,
                         headers={"User-Agent": "recycle-landing", "Accept": "application/json"})
        r.raise_for_status()
        p = r.json()["paper"]
        tracked, tail = int(p["trackedLp"]) / RAW, int(p["tailProgress"]) / RAW
        cliff, flat, decay = int(p["cliff"]) / RAW, int(p["rate"]) / RAW, int(p["decay"]) / RAW
        rate = flat if tracked < cliff else flat * (decay / (decay + tail)) ** 2
        if not 0 < rate <= flat:
            return None
        return {"rate": round(rate, 2), "trackedLp": tracked, "tailProgress": tail, "ts": int(time.time())}
    except Exception:  # noqa: BLE001
        return None


# Explainer page: the waitlist section is shown but stores nothing
# (submitting answers "Registration opens at public launch.").
st.markdown("<style>.block-container{padding:0!important;max-width:100%!important}"
            "header[data-testid='stHeader']{display:none}</style>", unsafe_allow_html=True)

live = live_mint()
inject = f"<script>window.RECYCLE_LIVE = {json.dumps(live)};</script>" if live else ""
html = (Path(__file__).parent / "index.html").read_text(encoding="utf-8")
st.iframe(inject + html, height=4300)
