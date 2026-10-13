"""RECYCLE demo site on Streamlit Community Cloud: Overview, Launchpad, Create token.

Each page is a self-contained HTML file rendered full width. The pages link to each other through
Streamlit's URLs (/home, /launchpad, /create). Launches created and buys made in the demo live in
the visitor's browser (localStorage), shared by the three pages.

The mint rate shown on the pages comes from Papertrade's public summary, read server-side every
5 minutes. If Papertrade does not answer, the pages use the flat rate (100 PAPER per $1).
"""
import json
import time
from pathlib import Path

import requests
import streamlit as st

ROOT = Path(__file__).parent
RAW = 10 ** 18

st.set_page_config(page_title="RECYCLE Launchpad", page_icon="♻️", layout="wide")
st.markdown("<style>.block-container{padding:0!important;max-width:100%!important}"
            "header[data-testid='stHeader']{display:none}</style>", unsafe_allow_html=True)


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


def show(file: str, height: int):
    html = (ROOT / file).read_text(encoding="utf-8")
    live = live_mint()
    inject = f"<script>window.RECYCLE_HOST = 'streamlit'; window.RECYCLE_LIVE = {json.dumps(live)};</script>"
    # full documents get the script inside <head>, so the doctype stays first
    html = html.replace("<head>", "<head>" + inject, 1) if "<head>" in html else inject + html
    st.iframe(html, height=height)


def overview():
    show("index.html", 4300)


def launchpad():
    show("launchpad.html", 2200)


def create():
    show("create.html", 3000)


nav = st.navigation(
    [st.Page(overview, title="Overview", default=True),
     st.Page(launchpad, title="Launchpad", url_path="launchpad"),
     st.Page(create, title="Create token", url_path="create")],
    position="hidden")
nav.run()
