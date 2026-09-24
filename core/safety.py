"""
core/safety.py
One-time-per-session Responsible AI safety disclaimer for the Diagnostic
Assistant page.

show_safety_disclaimer_if_needed() must be called at the top of any page
that involves electrical repair guidance. It reads and writes Streamlit
session state but contains no other page-level logic.
"""

import streamlit as st

# ---------------------------------------------------------------------------
# Disclaimer content
# ---------------------------------------------------------------------------

DISCLAIMER_TEXT = """
## ⚠️ Safety Disclaimer — Please Read Before Proceeding

EcoFix AI provides general educational repair guidance. **You are responsible for your own safety.**

Before attempting any electronic repair, acknowledge the following:

- 🔴 **Electric Shock Risk** — Mains-connected devices (chargers, laptops, appliances) can retain lethal voltages even when unplugged. Always discharge capacitors before touching internal components.
- 🔥 **Battery Fire / Thermal Runaway** — Lithium-ion batteries can catch fire if punctured, overcharged, or short-circuited. Never use metal tools near battery connectors. Dispose of swollen batteries at a certified e-waste facility.
- ⚡ **ESD Damage** — Electrostatic discharge can silently destroy microchips and sensors. Use an ESD wrist strap when handling PCBs and ICs.
- 🛑 **High Voltage DC Bus** — Inverter appliances (air conditioners, induction cooktops) maintain a 300V+ DC bus internally. Wait at least 10 minutes after unplugging and verify discharge with a multimeter before touching any components.
- 🔧 **Use the Right Tools** — Improvised tools (kitchen knives, random screwdrivers) cause damage and injury. Use insulated, properly sized tools.
- 📋 **Know Your Limits** — If a repair involves mains AC wiring or high-voltage components and you are not a qualified technician, take the device to a professional or to a certified e-waste recycling hub.

*EcoFix AI is not liable for any injury, damage, or data loss resulting from repair attempts.*
"""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def show_safety_disclaimer_if_needed() -> bool:
    """
    Check whether the user has acknowledged the safety disclaimer this session.

    - If not yet acknowledged: render the disclaimer and an acknowledgement
      button. Returns False (page should not proceed past this point).
    - If already acknowledged: returns True immediately (page proceeds normally).

    The flag is stored in st.session_state["safety_acknowledged"] and persists
    for the entire browser tab session — page reloads will not re-show it.
    """
    # Initialise flag if first visit
    st.session_state.setdefault("safety_acknowledged", False)

    if st.session_state["safety_acknowledged"]:
        return True

    # Show disclaimer and block further rendering
    st.markdown(DISCLAIMER_TEXT)
    st.divider()

    if st.button("✅ I understand — I will follow all safety precautions", type="primary"):
        st.session_state["safety_acknowledged"] = True
        st.rerun()

    return False
