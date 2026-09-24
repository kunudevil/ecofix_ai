import streamlit as st
import sys
import os

# Ensure core modules can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.hardware_edu import load_hardware_knowledge, calculate_power_and_resistor

st.set_page_config(
    page_title="Hardware & Tools Guide - EcoFix AI",
    page_icon="🧰",
    layout="wide"
)

st.title("🧰 Hardware, Tools & Circuit Fundamentals")
st.caption("Master diagnostic tools, explore circuit components, and verify safe operating parameters before attempting repairs.")

# Load Knowledge Base Data
kb_data = load_hardware_knowledge()

# Navigation Tabs
tab1, tab2, tab3 = st.tabs([
    "🛠️ Multimeter & Tool Tutorials",
    "⚡ Component Encyclopedia",
    "📐 Circuit & Power Calculator"
])

# TAB 1: TOOL TUTORIALS
with tab1:
    st.header("How to Use Essential Diagnostic Tools")
    st.info("⚠️ **Fundamental Rule:** Always turn off power and disconnect batteries before performing continuity or resistance tests!")

    tools = kb_data.get("tools", [])
    if tools:
        for tool in tools:
            with st.expander(f"🔹 {tool.get('tool_name')} — {tool.get('mode')}"):
                st.markdown(f"**Purpose:** {tool.get('purpose')}")

                st.markdown("#### How to Measure:")
                for step in tool.get("how_to_use", []):
                    st.write(f"- {step}")

                if tool.get("safety_warning"):
                    st.warning(f"⚠️ **Safety Warning:** {tool.get('safety_warning')}")
    else:
        st.warning("No tool tutorials found. Please check `data/hardware_knowledge.json`.")

# TAB 2: COMPONENT ENCYCLOPEDIA
with tab2:
    st.header("Electronic Components & Circuit Impact")
    st.write("Understand what each component does, how it fails, and how to verify it.")

    components = kb_data.get("components", [])
    if components:
        cols = st.columns(2)
        for idx, comp in enumerate(components):
            with cols[idx % 2]:
                with st.container(border=True):
                    st.subheader(f"⚡ {comp.get('name')}")
                    st.markdown(f"**Function:** {comp.get('function')}")
                    st.markdown(f"**Failure Symptom:** {comp.get('circuit_impact')}")
                    st.markdown(f"**How to Test:** {comp.get('how_to_test')}")
                    st.info(f"📌 **Operating Parameters:** {comp.get('operating_parameters')}")
    else:
        st.warning("No component entries found. Please check `data/hardware_knowledge.json`.")

# TAB 3: CIRCUIT & POWER CALCULATOR
with tab3:
    st.header("📐 Circuit Parameters & Power Calculator")
    st.write("Calculate Power ($P = V \\times I$), Resistance ($R = V / I$), and determine required component wattage ratings.")

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Input Operating Conditions")
        v_input = st.number_input("Operating Voltage (Volts)", min_value=0.1, max_value=250.0, value=5.0, step=0.1)
        i_input = st.number_input("Operating Current (Amperes)", min_value=0.001, max_value=50.0, value=0.5, step=0.01)

        calc_trigger = st.button("Calculate Circuit Parameters", type="primary")

    with col_b:
        st.subheader("Calculated Output")
        if calc_trigger:
            res = calculate_power_and_resistor(v_input, i_input)
            if "error" in res:
                st.error(res["error"])
            else:
                m_col1, m_col2 = st.columns(2)
                m_col1.metric("Power Dissipation (P)", f"{res['power_watts']} W")
                m_col2.metric("Resistance (R)", f"{res['resistance_ohms']} \u03a9")

                st.success(f"💡 **Recommended Resistor Rating:** {res['recommended_wattage']}")
                st.caption(f"🔒 **Safety Margin:** {res['safety_note']}")
        else:
            st.info("Enter Voltage and Current values on the left and click **Calculate** to view parameters.")
