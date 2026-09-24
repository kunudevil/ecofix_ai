"""
pages/2_Recycling_Locator.py
EcoFix AI — Step 2: Find a certified e-waste recycling hub.

Presents a device type dropdown and optional ZIP code input.
Calls core/recycling.find_hubs() and renders results as expander cards.
Increments st.session_state["recycled_count"] on each successful lookup.
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from core.recycling import find_hubs

st.set_page_config(
    page_title="Recycling Locator — EcoFix AI",
    page_icon="♻️",
    layout="wide",
)

# Initialise session counters
st.session_state.setdefault("recycled_count", 0)

st.title("♻️ E-Waste Recycling Locator")
st.caption(
    "Find a certified local recycling hub that accepts your device. "
    "Proper recycling keeps toxic materials — lead, mercury, cadmium — out of landfill."
)

# ---------------------------------------------------------------------------
# API mode indicator
# ---------------------------------------------------------------------------
earth911_key_set = bool(os.getenv("EARTH911_API_KEY"))
if earth911_key_set:
    st.success("🌐 Live Mode: Earth911 API hub lookup is active.")
else:
    st.info("📂 Offline Mode: Using bundled hub database. Add an EARTH911_API_KEY to enable live lookup.")

st.divider()

# ---------------------------------------------------------------------------
# Search form
# ---------------------------------------------------------------------------
DEVICE_TYPES = ["smartphone", "laptop", "tablet", "headphones", "earbuds", "smartwatch"]

with st.form("recycling_search"):
    col_a, col_b = st.columns([2, 1])
    with col_a:
        device_type = st.selectbox(
            "Device type",
            options=DEVICE_TYPES,
            index=0,
            help="Select the type of device you want to recycle.",
        )
    with col_b:
        zip_code = st.text_input(
            "ZIP code (optional)",
            placeholder="e.g. 90210",
            help="Used for live API distance filtering. Not required for offline mode.",
        )
    submitted = st.form_submit_button("🔍 Find Recycling Hubs", type="primary")

# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------
if submitted:
    with st.spinner(f"Searching for {device_type} recycling hubs…"):
        hubs = find_hubs(device_type, zip_code)

    if not hubs:
        st.warning(
            f"No recycling hubs found for **{device_type}**. "
            "Try a different device type or visit [Earth911.com](https://earth911.com) directly."
        )
    else:
        st.success(f"Found **{len(hubs)}** hub(s) accepting **{device_type}** devices.")
        st.markdown("---")

        for hub in hubs:
            certified_badge = "✅ Certified" if str(hub.get("certified", "")).lower() in ("true", "1", "yes") else "⬜ Uncertified"
            label = f"🏭 **{hub.get('name', 'Unknown Hub')}** — {hub.get('city', '')}, {hub.get('state', '')}  {certified_badge}"

            with st.expander(label, expanded=False):
                info_cols = st.columns(2)
                with info_cols[0]:
                    st.markdown(f"📍 **Location:** {hub.get('city', '')}, {hub.get('state', '')} {hub.get('zip', '')}")
                    st.markdown(f"📱 **Phone:** {hub.get('phone', 'N/A')}")
                with info_cols[1]:
                    st.markdown(f"♻️ **Accepts:** {hub.get('accepts', 'N/A')}")
                    url = hub.get("url", "")
                    if url and url.startswith("http"):
                        st.markdown(f"🔗 [Visit Website]({url})")

        # Increment session counter (count unique searches, not total hubs)
        st.session_state["recycled_count"] += 1

        count = st.session_state["recycled_count"]
        st.caption(f"🌱 Recycling lookups this session: {count}")

st.divider()
st.markdown(
    "💡 **Tip:** Can't find a hub near you? Visit "
    "[Call2Recycle](https://www.call2recycle.org) or "
    "[Earth911](https://earth911.com) for the most up-to-date national directory."
)
