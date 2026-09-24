"""
core/metrics.py
Environmental impact calculator.

Coefficients are evidence-based estimates derived from:
  - US EPA "Electronics Donation and Recycling" fact sheet
  - e-Stewards e-waste impact studies
  - iFixit Right to Repair environmental impact reports

calculate_impact() is pure Python — no Streamlit imports — and is
unit-testable in isolation.
"""

# ---------------------------------------------------------------------------
# Per-device impact coefficients
# ---------------------------------------------------------------------------

# CO₂ equivalent saved by repairing vs. manufacturing a new device (lbs)
# Source: EPA lifecycle analysis — avg. consumer electronics device ≈ 70 lbs CO₂e
CO2_LBS_PER_REPAIRED_DEVICE = 70.0

# Toxic heavy metals diverted from landfill per device sent to certified recycling (lbs)
# Source: EPA — avg. e-waste device contains ~0.15 lbs of lead, mercury, cadmium
TOXIC_WASTE_LBS_PER_RECYCLED_DEVICE = 0.15

# Water consumed during electronics manufacturing per device (gallons)
# Source: iFixit — avg. smartphone manufacturing uses ~13,000 gallons of water;
#         using a conservative cross-device average of 3,000 gallons
WATER_GALLONS_PER_REPAIRED_DEVICE = 3_000.0

# Each device kept out of landfill = 1 item avoided
LANDFILL_ITEMS_PER_DEVICE = 1


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def calculate_impact(devices_diagnosed: int, devices_recycled: int) -> dict:
    """
    Calculate aggregate environmental impact for a session.

    Parameters
    ----------
    devices_diagnosed : int
        Number of devices for which a repair guide was retrieved (repairs attempted).
    devices_recycled : int
        Number of devices for which a recycling hub was found (sent to proper recycling).

    Returns
    -------
    dict with keys:
        co2_lbs_saved          — CO₂ equivalent avoided by repair
        toxic_waste_lbs_diverted — Toxic material kept out of landfill via recycling
        landfill_items_avoided — Total devices kept from general waste stream
        water_gallons_saved    — Manufacturing water avoided through repair
    """
    diagnosed = max(0, int(devices_diagnosed))
    recycled = max(0, int(devices_recycled))

    return {
        "co2_lbs_saved": round(diagnosed * CO2_LBS_PER_REPAIRED_DEVICE, 1),
        "toxic_waste_lbs_diverted": round(recycled * TOXIC_WASTE_LBS_PER_RECYCLED_DEVICE, 3),
        "landfill_items_avoided": diagnosed + recycled,
        "water_gallons_saved": round(diagnosed * WATER_GALLONS_PER_REPAIRED_DEVICE, 0),
    }
