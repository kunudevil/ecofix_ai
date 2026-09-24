"""
pages/1_Diagnostic_Assistant.py
EcoFix AI — Step 1: Diagnose your device.

Shows the one-time safety disclaimer (core/safety.py) before rendering
the chat interface. Calls core/diagnostics.get_repair_guide() and renders:
  - Repairability Index gauge (French Repairability Index, 0–10)
  - Hazard level badge (LOW / MEDIUM / HIGH)
  - Safety warnings
  - PROMPT 5-Stage Diagnostic Workflow
  - Triage recommendation
  - Step-by-step repair guide

Increments st.session_state["diagnosed_count"] on each successful lookup.
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from core.safety import show_safety_disclaimer_if_needed
from core.diagnostics import get_repair_guide

st.set_page_config(
    page_title="Diagnostic Assistant — EcoFix AI",
    page_icon="🔧",
    layout="wide",
)

# Initialise session counters
st.session_state.setdefault("diagnosed_count", 0)
st.session_state.setdefault("safety_acknowledged", False)

# ---------------------------------------------------------------------------
# Safety gate — blocks page until user acknowledges
# ---------------------------------------------------------------------------
st.title("🔧 Diagnostic Assistant")
st.caption(
    "Describe your device problem and receive a step-by-step repair guide, "
    "Repairability Index score, and PROMPT 5-Stage Diagnostic Workflow."
)

if not show_safety_disclaimer_if_needed():
    st.stop()

# ---------------------------------------------------------------------------
# AI mode indicator
# ---------------------------------------------------------------------------
openai_key_set = bool(os.getenv("OPENAI_API_KEY"))
if openai_key_set:
    st.success("🤖 AI Mode: OpenAI gpt-4o-mini enhanced guidance is active.")
else:
    st.info(
        "📖 Offline Mode: Using built-in keyword repair guide library. "
        "Add an OpenAI API key in `.env` to enable AI-enhanced responses."
    )

st.divider()

# ---------------------------------------------------------------------------
# Helper: render the full guide card outside the chat bubble
# (chat_message containers have limited nesting support for columns/expanders)
# ---------------------------------------------------------------------------

def _hazard_badge(level: str) -> str:
    return {
        "HIGH":    "🔴 HIGH HAZARD",
        "MEDIUM":  "🟡 MEDIUM HAZARD",
        "LOW":     "🟢 LOW HAZARD",
    }.get(level.upper(), "⚪ UNKNOWN")


def _score_bar(score: float) -> str:
    """Unicode progress bar 0–10."""
    filled = int(round(score))
    return "█" * filled + "░" * (10 - filled) + f"  {score}/10"


def render_guide_card(guide: dict) -> None:
    """Render the full diagnostic result card in the current Streamlit context."""

    # ── Title & metadata ────────────────────────────────────────────────────
    st.markdown(f"## 🔧 {guide['title']}")

    meta_c1, meta_c2 = st.columns(2)
    with meta_c1:
        difficulty = guide.get("difficulty", "").capitalize()
        d_icon = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}.get(difficulty, "⚪")
        st.markdown(f"**Difficulty:** {d_icon} {difficulty}")
    with meta_c2:
        tools = guide.get("tools_needed", [])
        if tools:
            st.markdown(f"**Tools needed:** {', '.join(tools)}")

    st.divider()

    # ── Repairability Index ──────────────────────────────────────────────────
    ri = guide.get("repairability_index")
    if ri:
        with st.expander("📊 **Repairability Index (French Repairability Index)**", expanded=True):
            score = ri.get("composite_score_out_of_10", 0)
            # Colour threshold
            if score >= 7:
                st.success(f"**Composite Score: {_score_bar(score)}**")
            elif score >= 4.5:
                st.warning(f"**Composite Score: {_score_bar(score)}**")
            else:
                st.error(f"**Composite Score: {_score_bar(score)}**")

            st.caption(f"Formula: {ri.get('scoring_formula_applied', '')}")

            breakdown = ri.get("breakdown", {})
            b_col1, b_col2 = st.columns(2)
            items = list(breakdown.items())
            for i, (key, val) in enumerate(items):
                label = key.replace("_", " ").replace("criterion ", "✔ ").title()
                (b_col1 if i % 2 == 0 else b_col2).markdown(f"**{label}:** {val}")

    # ── Safety Assessment ────────────────────────────────────────────────────
    safety = guide.get("safety_assessment", {})
    hazard_level = safety.get("hazard_level", "UNKNOWN")
    badge = _hazard_badge(hazard_level)

    if hazard_level == "HIGH":
        st.error(f"### ⚠️ Safety Assessment: {badge}")
    elif hazard_level == "MEDIUM":
        st.warning(f"### ⚠️ Safety Assessment: {badge}")
    else:
        st.success(f"### ✅ Safety Assessment: {badge}")

    for warning in safety.get("mandatory_warnings", []):
        st.warning(f"🚨 {warning}")

    st.divider()

    # ── PROMPT 5-Stage Diagnostic Workflow ──────────────────────────────────
    pw = guide.get("prompt_workflow")
    if pw:
        with st.expander("🔬 **PROMPT 5-Stage Diagnostic Workflow**", expanded=False):
            stages = [
                ("1️⃣ Fault Detection",  "stage_1_fault_detection"),
                ("2️⃣ Fault Location",   "stage_2_fault_location"),
                ("3️⃣ Fault Isolation",  "stage_3_fault_isolation"),
                ("4️⃣ Repair Action",    "stage_4_repair_action"),
                ("5️⃣ Functional Test",  "stage_5_functional_test"),
            ]
            for label, key in stages:
                st.markdown(f"**{label}**")
                st.markdown(f"> {pw.get(key, 'N/A')}")

    # ── Step-by-step repair guide ────────────────────────────────────────────
    st.markdown("### 🛠️ Repair Steps")
    for i, step in enumerate(guide.get("steps", []), 1):
        st.markdown(f"**{i}.** {step}")

    st.divider()

    # ── Triage recommendation ────────────────────────────────────────────────
    triage = guide.get("triage_recommendation", {})
    action = triage.get("action", "")
    if action == "DIY_REPAIR_RECOMMENDED":
        st.success(f"✅ **Triage:** {action.replace('_', ' ')}")
    elif action == "DIY_REPAIR_WITH_CAUTION":
        st.warning(f"⚠️ **Triage:** {action.replace('_', ' ')}")
    else:
        st.error(f"🔴 **Triage:** {action.replace('_', ' ')}")

    redirect = triage.get("alternative_redirect", "")
    if redirect:
        st.info(f"♻️ {redirect}")


# ---------------------------------------------------------------------------
# Chat history (persists within the session)
# ---------------------------------------------------------------------------
st.session_state.setdefault("chat_history", [])

# Display previous messages
for message in st.session_state["chat_history"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------------------------------------------------------------------
# User input
# ---------------------------------------------------------------------------
user_input = st.chat_input(
    "Describe your device problem (e.g. 'my smartphone battery drains too fast')…"
)

if user_input:
    # Echo user message
    st.session_state["chat_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Fetch repair guide
    with st.spinner("Analysing fault and computing Repairability Index…"):
        guide = get_repair_guide(user_input)

    # Render inside assistant chat bubble for summary line
    with st.chat_message("assistant"):
        if not guide.get("steps"):
            st.warning(
                "No specific repair guide found for your description. "
                "Try rephrasing (e.g. include the device type and symptom), "
                "or use the ♻️ Recycling Locator if the device is beyond repair."
            )
            reply_md = "⚠️ No repair guide found for that description."
        else:
            ri = guide.get("repairability_index") or {}
            score = ri.get("composite_score_out_of_10", "N/A")
            hazard = guide.get("safety_assessment", {}).get("hazard_level", "N/A")
            reply_md = (
                f"**{guide['title']}** — Repairability: **{score}/10** | "
                f"Hazard: **{_hazard_badge(hazard)}** | "
                f"Difficulty: {guide.get('difficulty', 'N/A').capitalize()}"
            )
            st.markdown(reply_md)

    st.session_state["chat_history"].append({"role": "assistant", "content": reply_md})

    # Render the full guide card outside the chat bubble (richer layout)
    if guide.get("steps"):
        st.markdown("---")
        render_guide_card(guide)
        st.session_state["diagnosed_count"] += 1

    # Show running counter
    count = st.session_state["diagnosed_count"]
    if count > 0:
        st.caption(f"🌱 Devices diagnosed this session: {count}")
