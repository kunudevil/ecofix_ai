"""
pages/3_Impact_Dashboard.py
EcoFix AI — Step 3: See your environmental impact.

Reads session counters (diagnosed_count, recycled_count) set by pages 1 and 2,
calls core/metrics.calculate_impact(), and renders four st.metric tiles plus
a bar chart of the four impact dimensions.
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
from core.metrics import calculate_impact

st.set_page_config(
    page_title="Impact Dashboard — EcoFix AI",
    page_icon="📊",
    layout="wide",
)

# Initialise counters in case user lands here first
st.session_state.setdefault("diagnosed_count", 0)
st.session_state.setdefault("recycled_count", 0)

st.title("📊 Environmental Impact Dashboard")
st.caption(
    "Track the positive environmental impact you've generated this session "
    "through device repair and responsible recycling."
)

st.divider()

# ---------------------------------------------------------------------------
# Read session counters & calculate impact
# ---------------------------------------------------------------------------
diagnosed = st.session_state["diagnosed_count"]
recycled = st.session_state["recycled_count"]
impact = calculate_impact(diagnosed, recycled)

# ---------------------------------------------------------------------------
# Session activity summary
# ---------------------------------------------------------------------------
st.subheader("🌿 This Session")

act_col1, act_col2 = st.columns(2)
with act_col1:
    st.metric(
        label="🔧 Repair Guides Retrieved",
        value=diagnosed,
        help="Number of devices diagnosed using the Diagnostic Assistant.",
    )
with act_col2:
    st.metric(
        label="♻️ Recycling Lookups",
        value=recycled,
        help="Number of recycling hub searches completed.",
    )

if diagnosed == 0 and recycled == 0:
    st.info(
        "No activity recorded yet. Use the **🔧 Diagnostic Assistant** or "
        "**♻️ Recycling Locator** and return here to see your impact."
    )

st.divider()

# ---------------------------------------------------------------------------
# Impact metrics
# ---------------------------------------------------------------------------
st.subheader("🌍 Estimated Environmental Impact")

m1, m2, m3, m4 = st.columns(4)

m1.metric(
    label="☁️ CO₂ Saved",
    value=f"{impact['co2_lbs_saved']:,.0f} lbs",
    help="Estimated CO₂ equivalent avoided by repairing devices instead of replacing them. (Source: EPA lifecycle analysis)",
)
m2.metric(
    label="☠️ Toxic Waste Diverted",
    value=f"{impact['toxic_waste_lbs_diverted']:.3f} lbs",
    help="Lead, mercury, and cadmium kept out of landfill through certified recycling. (Source: EPA e-waste fact sheet)",
)
m3.metric(
    label="🗑️ Landfill Items Avoided",
    value=f"{impact['landfill_items_avoided']}",
    help="Total devices kept out of the general waste stream.",
)
m4.metric(
    label="💧 Water Saved",
    value=f"{impact['water_gallons_saved']:,.0f} gal",
    help="Manufacturing water conserved by extending device lifespans. (Source: iFixit sustainability report)",
)

st.divider()

# ---------------------------------------------------------------------------
# Bar chart
# ---------------------------------------------------------------------------
st.subheader("📈 Impact Breakdown (Normalised View)")

if diagnosed > 0 or recycled > 0:
    chart_data = pd.DataFrame(
        {
            "Metric": [
                "CO₂ Saved (lbs)",
                "Toxic Waste Diverted (lbs × 100)",
                "Landfill Items Avoided",
                "Water Saved (gal ÷ 1000)",
            ],
            "Value": [
                impact["co2_lbs_saved"],
                impact["toxic_waste_lbs_diverted"] * 100,   # scale up for visibility
                float(impact["landfill_items_avoided"]),
                impact["water_gallons_saved"] / 1000,        # scale down for visibility
            ],
        }
    ).set_index("Metric")

    st.bar_chart(chart_data, height=320)
    st.caption(
        "Note: CO₂ and water values are scaled for visual comparison. "
        "Coefficients are per-device averages based on EPA and iFixit sustainability data."
    )
else:
    st.info("Complete at least one repair diagnosis or recycling lookup to see the chart.")

st.divider()

# ---------------------------------------------------------------------------
# SDG context footer
# ---------------------------------------------------------------------------
st.markdown(
    """
    ### 🌱 Why This Matters — SDG 12
    | Action | SDG 12 Target |
    |---|---|
    | Repairing a device instead of discarding it | 12.5 — Substantially reduce waste generation |
    | Sending to certified e-waste recycling | 12.4 — Responsible management of hazardous waste |
    | Learning to repair electronics | 12.8 — Education for sustainable development |

    *Coefficient sources: [US EPA Electronics Recycling](https://www.epa.gov/recycle/electronics-donation-and-recycling) · [e-Stewards](https://e-stewards.org) · [iFixit Right to Repair](https://www.ifixit.com/)*
    """
)
