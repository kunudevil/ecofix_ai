"""
core/diagnostics.py
Hybrid repair-guide engine with Repairability Index and PROMPT 5-Stage workflow.

  1. If OPENAI_API_KEY is set → calls gpt-4o-mini for an AI-enhanced guide.
  2. On failure or missing key → keyword match against data/repair_guides.json.
  3. If no match → returns a not-found sentinel dict.

Every result dict is enriched with:
  - repairability_index  (French Repairability Index, 0–10 composite score)
  - safety_assessment    (hazard_level + mandatory_warnings)
  - prompt_workflow      (PROMPT 5-Stage Diagnostic Framework)
  - triage_recommendation

No Streamlit imports — unit-testable as plain Python.
"""

import json
import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_DATA_FILE = Path(__file__).parent.parent / "data" / "repair_guides.json"

# Module-level cache — loaded once per interpreter lifetime
_GUIDES_CACHE: list | None = None

# ---------------------------------------------------------------------------
# Sentinel returned when no guide is found
# ---------------------------------------------------------------------------
NOT_FOUND = {
    "title": "No repair guide found",
    "steps": [],
    "safety_warnings": [
        "If the device is beyond repair, please use the Recycling Locator "
        "to find a certified e-waste hub near you."
    ],
    "difficulty": "",
    "tools_needed": [],
    "repairability_index": None,
    "safety_assessment": {"hazard_level": "UNKNOWN", "mandatory_warnings": []},
    "prompt_workflow": None,
    "triage_recommendation": {
        "action": "SEEK_PROFESSIONAL_OR_RECYCLE",
        "alternative_redirect": "Use the Recycling Locator to find a certified e-waste hub.",
    },
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def load_guides() -> list:
    """Read and cache data/repair_guides.json."""
    global _GUIDES_CACHE
    if _GUIDES_CACHE is None:
        try:
            with open(_DATA_FILE, "r", encoding="utf-8") as f:
                _GUIDES_CACHE = json.load(f)
        except Exception:
            _GUIDES_CACHE = []
    return _GUIDES_CACHE


def keyword_match(user_input: str, guides: list) -> dict | None:
    """
    Lowercase the user input, then scan every guide entry for any matching
    keyword. Returns the first matched guide dict or None.
    """
    text = user_input.lower()
    for device_entry in guides:
        for guide in device_entry.get("guides", []):
            for keyword in guide.get("keywords", []):
                if keyword in text:
                    return guide
    return None


# ---------------------------------------------------------------------------
# Repairability Index (French Repairability Index formula)
# R = 0.25(Disassembly) + 0.15(Fasteners) + 0.15(Tools) +
#     0.15(Spare Parts) + 0.15(Software) + 0.15(Documentation)
# ---------------------------------------------------------------------------

_DIFFICULTY_REPAIRABILITY = {
    "easy":   {"disassembly": 9.0, "fasteners": 9.0, "tools": 9.0},
    "medium": {"disassembly": 5.0, "fasteners": 6.0, "tools": 6.0},
    "hard":   {"disassembly": 3.0, "fasteners": 4.0, "tools": 4.0},
    "":       {"disassembly": 5.0, "fasteners": 5.0, "tools": 5.0},
}

# Hazard keywords → hazard level
_HIGH_HAZARD_KEYWORDS = [
    "battery", "lithium", "inverter", "igbt", "capacitor", "300v",
    "high voltage", "mains", "soldering", "thermal runaway",
]
_MEDIUM_HAZARD_KEYWORDS = [
    "screen", "display", "charging port", "pcb", "motherboard",
]


def calculate_repairability_index(guide: dict) -> dict:
    """
    Compute a French Repairability Index composite score (0–10) from
    the guide's difficulty and tools_needed fields.
    """
    difficulty = guide.get("difficulty", "").lower()
    scores = _DIFFICULTY_REPAIRABILITY.get(difficulty, _DIFFICULTY_REPAIRABILITY[""])

    tools = guide.get("tools_needed", [])
    # Spare parts score: higher if replacement part is mentioned
    spare_parts = 8.0 if any(
        t for t in tools if any(k in t.lower() for k in ["replacement", "new", "battery", "screen"])
    ) else 6.0
    # Software reset score: higher for easier repairs
    software = 7.0 if difficulty == "easy" else (5.5 if difficulty == "medium" else 4.0)
    # Documentation: EcoFix guides are always bundled
    documentation = 8.0

    composite = round(
        0.25 * scores["disassembly"]
        + 0.15 * scores["fasteners"]
        + 0.15 * scores["tools"]
        + 0.15 * spare_parts
        + 0.15 * software
        + 0.15 * documentation,
        1,
    )

    return {
        "composite_score_out_of_10": composite,
        "scoring_formula_applied": (
            "R = 0.25(Disassembly) + 0.15(Fasteners) + 0.15(Tools) "
            "+ 0.15(Spare Parts) + 0.15(Software) + 0.15(Documentation)"
        ),
        "breakdown": {
            "criterion_1_documentation": f"{documentation}/10 (Bundled repair guide available)",
            "criterion_2_disassembly_and_tools": f"{scores['disassembly']}/10 (Difficulty: {difficulty or 'N/A'})",
            "criterion_3_spare_parts_availability": f"{spare_parts}/10",
            "criterion_4_spare_parts_price_ratio": "6.5/10 (Typical part cost < 20% of device MSRP)",
            "criterion_5_product_specific_reset": f"{software}/10",
        },
    }


def assess_safety(guide: dict) -> dict:
    """
    Derive hazard level and mandatory warnings from the guide's
    safety_warnings and tools_needed fields.
    """
    combined = " ".join(
        guide.get("safety_warnings", []) + guide.get("tools_needed", [])
    ).lower()

    if any(k in combined for k in _HIGH_HAZARD_KEYWORDS):
        hazard_level = "HIGH"
    elif any(k in combined for k in _MEDIUM_HAZARD_KEYWORDS):
        hazard_level = "MEDIUM"
    else:
        hazard_level = "LOW"

    return {
        "hazard_level": hazard_level,
        "mandatory_warnings": guide.get("safety_warnings", []),
    }


def build_prompt_workflow(guide: dict, user_input: str) -> dict:
    """
    Map the guide's steps onto the 5-stage PROMPT Diagnostic Framework:
      1. Fault Detection  2. Fault Location  3. Fault Isolation
      4. Repair Action    5. Functional Test
    Uses the guide steps; falls back to generic descriptions per stage.
    """
    steps = guide.get("steps", [])
    n = len(steps)

    def _stage(idx: int, default: str) -> str:
        return steps[idx] if idx < n else default

    return {
        "stage_1_fault_detection": _stage(
            0, f"Observational evidence from user report: '{user_input[:120]}'"
        ),
        "stage_2_fault_location": _stage(
            1, "Visual inspection and symptom localisation to affected subassembly."
        ),
        "stage_3_fault_isolation": _stage(
            2, "Continuity / resistance / voltage measurement to isolate failed component."
        ),
        "stage_4_repair_action": _stage(
            3, "Replace defective component per repair guide steps."
        ),
        "stage_5_functional_test": _stage(
            max(n - 1, 4),
            "Power on and verify normal operation; monitor for recurrence.",
        ),
    }


def _triage(guide: dict, hazard_level: str) -> dict:
    """Return a triage recommendation dict based on hazard level and difficulty."""
    if hazard_level == "HIGH" or guide.get("difficulty") == "hard":
        return {
            "action": "DIY_REPAIR_WITH_CAUTION",
            "alternative_redirect": (
                "If any battery swelling, burn marks, or high-voltage components are present, "
                "route immediately to a certified e-waste hub via the ♻️ Recycling Locator."
            ),
        }
    return {
        "action": "DIY_REPAIR_RECOMMENDED",
        "alternative_redirect": (
            "If repair is unsuccessful, use the ♻️ Recycling Locator to responsibly recycle the device."
        ),
    }


def _enrich(guide: dict, user_input: str) -> dict:
    """Add repairability_index, safety_assessment, prompt_workflow, triage to a guide dict."""
    repairability = calculate_repairability_index(guide)
    safety = assess_safety(guide)
    prompt = build_prompt_workflow(guide, user_input)
    triage = _triage(guide, safety["hazard_level"])
    return {
        **guide,
        "repairability_index": repairability,
        "safety_assessment": safety,
        "prompt_workflow": prompt,
        "triage_recommendation": triage,
    }


def _openai_guide(user_input: str) -> dict | None:
    """
    Call gpt-4o-mini with a safety-first repair system prompt.
    Returns a parsed guide dict on success, None on any failure.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        from openai import OpenAI  # lazy import — not required if key absent

        client = OpenAI(api_key=api_key)
        system_prompt = (
            "You are EcoFix AI, an expert electronics repair assistant aligned with "
            "UN SDG 12 (Responsible Consumption & Production). "
            "When a user describes a device problem, respond ONLY with a valid JSON object "
            "using this exact schema:\n"
            '{"title": "string", "steps": ["string"], "safety_warnings": ["string"], '
            '"difficulty": "easy|medium|hard", "tools_needed": ["string"]}\n'
            "Always include at least one safety warning covering electrical, battery, "
            "or ESD hazards as appropriate. "
            "Recommend professional repair if the repair is unsafe for a non-expert. "
            "Do not include any text outside the JSON object."
        )
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
            temperature=0.3,
            max_tokens=600,
        )
        raw = response.choices[0].message.content.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_repair_guide(user_input: str) -> dict:
    """
    Main entry point used by the Diagnostic Assistant page.

    Priority:
      1. OpenAI gpt-4o-mini (if OPENAI_API_KEY is set and call succeeds)
      2. Keyword match against repair_guides.json
      3. NOT_FOUND sentinel

    Every successful result is enriched with:
      - repairability_index  (French Repairability Index, 0–10)
      - safety_assessment    (hazard_level + mandatory_warnings)
      - prompt_workflow      (PROMPT 5-Stage Diagnostic Framework)
      - triage_recommendation
    """
    if not user_input or not user_input.strip():
        return NOT_FOUND

    # 1. Try OpenAI
    ai_result = _openai_guide(user_input)
    if ai_result and ai_result.get("title") and ai_result.get("steps"):
        return _enrich(ai_result, user_input)

    # 2. Keyword fallback
    guides = load_guides()
    matched = keyword_match(user_input, guides)
    if matched:
        return _enrich(matched, user_input)

    # 3. Not found
    return NOT_FOUND
