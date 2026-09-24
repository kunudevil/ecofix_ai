"""
core/hardware_edu.py
Hardware & Tools knowledge base loader and Ohm's Law / power calculator.

Functions
---------
load_hardware_knowledge(filepath)      — Load hardware_knowledge.json; safe fallback on error.
calculate_power_and_resistor(v, i)     — P = V*I, R = V/I, with 2x safety wattage tier.
"""

import json
import os
from pathlib import Path

# Resolve data file relative to THIS file so it works regardless of working directory
# (local dev, Streamlit Community Cloud, or any other runner)
_DEFAULT_KB_PATH = Path(__file__).parent.parent / "data" / "hardware_knowledge.json"


def load_hardware_knowledge(filepath=None):
    """
    Loads the hardware and tools knowledge base from a local JSON file.
    Defaults to data/hardware_knowledge.json next to the project root.
    Returns a fallback dictionary if the file is missing.
    """
    path = Path(filepath) if filepath else _DEFAULT_KB_PATH
    if not path.exists():
        return {
            "tools": [],
            "components": []
        }
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading hardware knowledge base: {e}")
        return {"tools": [], "components": []}


def calculate_power_and_resistor(voltage: float, current: float):
    """
    Calculates Power (P = V * I) and Resistance (R = V / I) using Ohm's Law.
    Recommends safe resistor wattage ratings with a 2x safety headroom factor.
    """
    if current <= 0 or voltage <= 0:
        return {"error": "Voltage and Current must both be greater than zero."}

    power = voltage * current
    resistance = voltage / current

    # Calculate recommended wattage with 2x safety margin
    safe_power = power * 2

    if safe_power <= 0.125:
        recommended_wattage = "0.125W (1/8 Watt - Small Signal)"
    elif safe_power <= 0.25:
        recommended_wattage = "0.25W (1/4 Watt - Standard Through-Hole)"
    elif safe_power <= 0.5:
        recommended_wattage = "0.5W (1/2 Watt)"
    elif safe_power <= 1.0:
        recommended_wattage = "1.0W (1 Watt Power Resistor)"
    elif safe_power <= 2.0:
        recommended_wattage = "2.0W (2 Watt Power Resistor)"
    else:
        recommended_wattage = f"{int(safe_power) + 1}W High-Power Wirewound Resistor"

    return {
        "voltage": voltage,
        "current": current,
        "power_watts": round(power, 3),
        "resistance_ohms": round(resistance, 2),
        "recommended_wattage": recommended_wattage,
        "safety_note": (
            "Always select a resistor rated for at least DOUBLE your calculated power "
            "to prevent thermal degradation and circuit fires!"
        ),
    }
