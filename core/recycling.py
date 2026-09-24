"""
core/recycling.py
E-waste hub lookup.

Primary path  : CSV (data/recycling_hubs.csv) — always available, no API key needed.
Optional path : Earth911 live API — used first if EARTH911_API_KEY is set; falls
                back to CSV on any failure.

No Streamlit imports — unit-testable as plain Python.
"""

import os
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_CSV_FILE = Path(__file__).parent.parent / "data" / "recycling_hubs.csv"

# Module-level cache
_HUBS_CACHE: list[dict] | None = None


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def load_hubs_csv() -> list[dict]:
    """Read and cache data/recycling_hubs.csv as a list of dicts."""
    global _HUBS_CACHE
    if _HUBS_CACHE is None:
        try:
            df = pd.read_csv(_CSV_FILE, dtype=str)
            _HUBS_CACHE = df.fillna("").to_dict(orient="records")
        except Exception:
            _HUBS_CACHE = []
    return _HUBS_CACHE


def csv_lookup(device_type: str) -> list[dict]:
    """
    Filter hubs from the CSV whose 'accepts' column contains device_type
    (case-insensitive substring match).
    """
    device_lower = device_type.lower().strip()
    return [
        hub for hub in load_hubs_csv()
        if device_lower in hub.get("accepts", "").lower()
    ]


def _api_lookup(device_type: str, zip_code: str) -> list[dict] | None:
    """
    Query the Earth911 API: materials.search → locations.search.
    Returns a list of hub dicts on success, None on any failure.
    """
    api_key = os.getenv("EARTH911_API_KEY")
    if not api_key:
        return None

    try:
        import requests  # lazy import

        base = "http://api.earth911.com"

        # Step 1: find material ID for the device type
        mat_resp = requests.get(
            f"{base}/earth911.materials.search",
            params={"api_key": api_key, "query": device_type},
            timeout=8,
        )
        mat_resp.raise_for_status()
        materials = mat_resp.json().get("result", [])
        if not materials:
            return None
        material_id = materials[0].get("material_id")

        # Step 2: find locations near the ZIP code
        loc_resp = requests.get(
            f"{base}/earth911.locations.search",
            params={
                "api_key": api_key,
                "material_id": material_id,
                "postal_code": zip_code,
                "max_distance": 25,
                "max_results": 10,
            },
            timeout=8,
        )
        loc_resp.raise_for_status()
        locations = loc_resp.json().get("result", [])

        # Normalise to our standard hub dict shape
        return [
            {
                "name": loc.get("description", "Unknown"),
                "city": loc.get("city", ""),
                "state": loc.get("province", ""),
                "zip": loc.get("postal_code", ""),
                "accepts": device_type,
                "certified": str(loc.get("verified", False)),
                "phone": loc.get("phone", ""),
                "url": loc.get("url", ""),
            }
            for loc in locations
        ]
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def find_hubs(device_type: str, zip_code: str = "") -> list[dict]:
    """
    Return a list of recycling hub dicts for the given device type.

    Priority:
      1. Earth911 live API (if EARTH911_API_KEY set and call succeeds)
      2. CSV static fallback (always works)
    """
    # 1. Try live API
    api_results = _api_lookup(device_type, zip_code)
    if api_results is not None:
        return api_results

    # 2. CSV fallback
    return csv_lookup(device_type)
