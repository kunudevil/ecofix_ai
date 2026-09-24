"""
app.py — EcoFix AI Home Page & Streamlit entry point.
"""

# Load .env file for local development (no-op on Streamlit Cloud where secrets are injected)
from dotenv import load_dotenv
load_dotenv()

import streamlit as st

st.set_page_config(
    page_title="EcoFix AI — E-Waste Repair & Circularity Assistant",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# SDG green branding
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Sidebar nav header */
    [data-testid="stSidebarNav"]::before {
        content: "🌱 EcoFix AI";
        display: block;
        font-size: 1.2rem;
        font-weight: 700;
        color: #2e7d32;
        padding: 1rem 1rem 0.5rem 1rem;
    }
    /* Hero banner */
    .hero-banner {
        background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 100%);
        border-left: 6px solid #2e7d32;
        border-radius: 8px;
        padding: 2rem 2.5rem;
        margin-bottom: 2rem;
    }
    .hero-banner h1 { color: #1b5e20; margin-bottom: 0.25rem; }
    .hero-banner p  { color: #33691e; font-size: 1.05rem; }
    /* Metric cards */
    .sdg-card {
        background: #f9fbe7;
        border: 1px solid #c5e1a5;
        border-radius: 8px;
        padding: 1.2rem 1.5rem;
        height: 100%;
    }
    .sdg-card h3 { color: #2e7d32; margin-bottom: 0.4rem; font-size: 1rem; }
    .sdg-card p  { color: #4e342e; font-size: 0.88rem; margin: 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Hero banner
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero-banner">
        <h1>🌱 EcoFix AI</h1>
        <p><strong>E-Waste Repair &amp; Circularity Assistant</strong> &nbsp;|&nbsp;
        SDG 12: Responsible Consumption &amp; Production</p>
        <p>Diagnose broken devices, find certified recycling hubs, track your environmental
        impact, and master the tools and components behind every repair.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# SDG 12 badge
# ---------------------------------------------------------------------------
col_badge, col_spacer = st.columns([1, 3])
with col_badge:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Sustainable_Development_Goal_12ResponsibleConsumption.svg/240px-Sustainable_Development_Goal_12ResponsibleConsumption.svg.png",
        width=160,
        caption="UN SDG 12 — Responsible Consumption & Production",
    )

st.divider()

# ---------------------------------------------------------------------------
# Feature cards
# ---------------------------------------------------------------------------
st.subheader("What would you like to do today?")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        """<div class="sdg-card">
        <h3>🔧 Diagnostic Assistant</h3>
        <p>Describe your device problem and get a step-by-step DIY repair guide
        with safety warnings. Powered by keyword matching or OpenAI gpt-4o-mini.</p>
        </div>""",
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        """<div class="sdg-card">
        <h3>♻️ Recycling Locator</h3>
        <p>Can't fix it? Find a certified local e-waste recycling hub that accepts
        your device type. Keeps toxic materials out of landfill.</p>
        </div>""",
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        """<div class="sdg-card">
        <h3>📊 Impact Dashboard</h3>
        <p>See the environmental impact your session has generated — CO₂ saved,
        toxic waste diverted, landfill items avoided, and water conserved.</p>
        </div>""",
        unsafe_allow_html=True,
    )

with c4:
    st.markdown(
        """<div class="sdg-card">
        <h3>🧰 Hardware & Tools Guide</h3>
        <p>Learn to use a multimeter, solder joints, test components, and calculate
        safe operating parameters for circuits before you pick up a tool.</p>
        </div>""",
        unsafe_allow_html=True,
    )

st.divider()

# ---------------------------------------------------------------------------
# SDG alignment callout
# ---------------------------------------------------------------------------
st.markdown(
    """
    ### 🌍 Our SDG 12 Mission
    Every repaired device keeps **~70 lbs of CO₂** and **~3,000 gallons of manufacturing
    water** out of the environment. Every device properly recycled diverts **~0.15 lbs
    of toxic heavy metals** from landfill.

    Use the sidebar to navigate between the four tools ↖
    """
)

# Initialise global session counters used by all pages
st.session_state.setdefault("diagnosed_count", 0)
st.session_state.setdefault("recycled_count", 0)
st.session_state.setdefault("safety_acknowledged", False)
