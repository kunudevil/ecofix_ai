# EcoFix AI 🌱
### E-Waste Repair & Circularity Assistant — SDG 12: Responsible Consumption & Production

---

## What is EcoFix AI?

EcoFix AI is an AI-powered Streamlit web application that helps users **repair electronics before discarding them**, find certified e-waste recycling hubs, and understand the environmental impact of responsible device management — all aligned with **UN SDG 12 (Responsible Consumption & Production)**.

---

## Features

| Page | Feature |
|---|---|
| 🔧 Diagnostic Assistant | Chatbot that diagnoses device symptoms and returns step-by-step DIY repair guides, a **French Repairability Index score (0–10)**, hazard level badge, **PROMPT 5-Stage Diagnostic Workflow**, and triage recommendation. Powered by keyword/rule matching with optional OpenAI `gpt-4o-mini` upgrade. |
| ♻️ Recycling Locator | Find certified local e-waste recycling hubs by device type and ZIP code. Uses bundled CSV data (no API key required) or live Earth911 API. |
| 📊 Impact Dashboard | Visualise your session's environmental impact: CO₂ saved, toxic waste diverted, landfill items avoided, and water conserved. |
| 🧰 Hardware & Tools Guide | Multimeter and soldering tutorials, component encyclopedia (consumer electronics + household appliances), and an Ohm's Law / Power calculator. |

---

## Quick Start (Local)

```bash
# 1. Clone the repository
git clone https://github.com/your-username/ecofix-ai.git
cd ecofix-ai/ecofix_ai

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Configure API keys
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY and/or EARTH911_API_KEY

# 5. Run the app
streamlit run app.py
```

The app opens at `http://localhost:8501`.

---

## Deploy to Streamlit Community Cloud (Free)

1. Push this repository to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in.
3. Click **New app** → select your repo → set **Main file path** to `ecofix_ai/app.py`.
4. Under **Advanced settings → Secrets**, add your API keys (optional):
   ```
   OPENAI_API_KEY = "sk-..."
   EARTH911_API_KEY = "..."
   ```
5. Click **Deploy**. Your app will be live at a public URL within minutes.

---

## Project Structure

```
ecofix_ai/
├── app.py                          # Home page & Streamlit entry point
├── pages/
│   ├── 1_Diagnostic_Assistant.py  # Repairability Index + PROMPT workflow + repair guide
│   ├── 2_Recycling_Locator.py     # Hub lookup (CSV primary + Earth911 optional)
│   ├── 3_Impact_Dashboard.py      # Environmental impact metrics
│   └── 4_Hardware_&_Tools_Guide.py # Tool tutorials + component encyclopedia + power calc
├── core/
│   ├── diagnostics.py             # Repair engine: keyword + OpenAI + RI + PROMPT
│   ├── safety.py                  # One-time session safety disclaimer
│   ├── recycling.py               # Hub lookup (CSV + Earth911 API)
│   ├── metrics.py                 # Environmental impact calculator
│   └── hardware_edu.py            # Hardware KB loader + power calculator
├── data/
│   ├── repair_guides.json         # Device symptom → repair guide knowledge base
│   ├── recycling_hubs.csv         # Static e-waste hub dataset (12 US hubs)
│   └── hardware_knowledge.json    # Tools & components encyclopedia (5 tools, 12 components)
├── .streamlit/config.toml         # SDG green theme & server config
├── .env.example                   # API key template
├── Procfile                       # Streamlit Community Cloud entry point
└── requirements.txt
```

---

## Design Thinking Documentation

### Stage 3 — Ideate: User Journey & Feature Architecture

The platform is organised around a 3-tier user journey:

**Tier 1 — Symptom Input & Safety Gate**
The user specifies a faulty device. Before diagnostic steps are displayed, a mandatory one-time session safety disclaimer covers high-voltage, thermal runaway, and ESD risks.

**Tier 2 — Interactive Triage & Hardware Guidance**
The diagnostic engine applies the **PROMPT 5-Stage Diagnostic Framework**:

```
Detection → Location → Isolation → Repair → Testing
```

If physical testing is required, the app loads the Hardware & Tools Guide with interactive multimeter tutorials and a power calculator (P = V × I).

**Tier 3 — Circularity & Impact Visualisation**
Devices beyond DIY repair are matched with certified local recycling hubs via ZIP code. The session feeds an environmental dashboard calculating CO₂ savings and avoided landfill mass.

```
             [ User Query / Symptom ]
                        │
                        ▼
          [ Session Safety Confirmation ]
                        │
         ┌──────────────┴──────────────┐
         ▼                             ▼
[ Diagnostic Assistant ]     [ Hardware & Tools Guide ]
  (Hybrid NLP + Rules)         (Multimeter & IC Tutorials)
         │                             │
         ├─────────────────────────────┘
         ▼
[ Triage Recommendation ]
      ┌──┴──┐
      ▼     ▼
  DIY    Unfixable
  Guide  /Hazardous
      │     │
      ▼     ▼
 [ Impact Dashboard ] ◄── [ Recycling Locator ]
```

---

### Stage 4 — Prototype: Modular Code Architecture

The prototype is a multi-page Streamlit application with a modular backend:

| File | Responsibility |
|---|---|
| `app.py` | Entry point, SDG 12 alignment, navigation |
| `pages/1_Diagnostic_Assistant.py` | Conversational interface, Repairability Index gauges, PROMPT workflow, repair guide rendering |
| `pages/2_Recycling_Locator.py` | ZIP + device-type filtering, hub cards |
| `pages/3_Impact_Dashboard.py` | Cumulative environmental savings metrics |
| `pages/4_Hardware_&_Tools_Guide.py` | Tool tutorials, appliance IC encyclopedia, Ohm's Law calculator |
| `core/diagnostics.py` | Hybrid engine: keyword rules → OpenAI gpt-4o-mini; computes Repairability Index + PROMPT workflow |
| `core/recycling.py` | CSV primary fallback; Earth911 API optional |
| `core/safety.py` | One-time session disclaimer gate |
| `core/metrics.py` | EPA-cited environmental impact coefficients |
| `core/hardware_edu.py` | KB loader; 2× safety-headroom power calculator |

**Data Schemas & Fallback Design:**
To guarantee 100% uptime during evaluation, the system uses bundled static files (`repair_guides.json`, `recycling_hubs.csv`, `hardware_knowledge.json`) as primary data sources. Live API integrations (OpenAI `gpt-4o-mini`, Earth911) activate dynamically when environment keys are detected and fall back silently on failure.

**Repairability Index Formula (French Repairability Index):**
```
R = 0.25(Disassembly Depth) + 0.15(Fasteners) + 0.15(Tools)
  + 0.15(Spare Parts) + 0.15(Software Reset) + 0.15(Documentation)
```
Scores are computed at runtime from each guide's `difficulty`, `tools_needed`, and `steps` fields. No manual pre-scoring required.

---

### Stage 5 — Test & Refine

**Testing Matrix:**

| Test Case | Scenario / Query | Expected Result | Status |
|---|---|---|---|
| Safety Enforcement | First-time access to Diagnostic Assistant | Session modal blocks repair guides until safety rules are acknowledged | ✅ PASS |
| Keyword Fallback | Query: "Laptop overheating" (Offline) | Matches `repair_guides.json`, returns fan cleaning + thermal paste guide | ✅ PASS |
| Repairability Index | Query: "Smartphone battery drains fast" | Computes composite score, renders 5-criterion breakdown | ✅ PASS |
| PROMPT Workflow | Any matched guide | 5-stage detection → test workflow rendered in collapsible expander | ✅ PASS |
| Recycling Filter | Search ZIP 10001 for "smartphone" | Filters CSV and returns certified hubs with addresses and phone numbers | ✅ PASS |
| Power Calculator | Input: 5.0V, 0.5A | Computes 2.5W / 10Ω, recommends 5W resistor (2× safety headroom) | ✅ PASS |
| Appliance IC Guide | Inspect Inverter AC Board entry | Displays IPM IC diode test procedure and 300V DC capacitor discharge warning | ✅ PASS |
| API-Key Absent | No `OPENAI_API_KEY` set | App falls back to keyword engine without error | ✅ PASS |

**Responsible AI & Refinement Actions:**
- **Safety First:** Colour-coded hazard banners (🔴 HIGH / 🟡 MEDIUM / 🟢 LOW) appear before physical disassembly steps.
- **Data Privacy:** No personal identifiers or serial numbers are stored in session state.
- **Fail-Safe Uptime:** Missing API keys trigger graceful silent fallback to local datasets — no uncaught exceptions.
- **2× Wattage Safety Margin:** Power calculator always recommends a resistor rated for double the calculated dissipation.

---

## SDG 12 Alignment

> *"Ensure sustainable consumption and production patterns."*

| Action | SDG 12 Target |
|---|---|
| Repairing a device instead of discarding it | 12.5 — Reduce waste generation |
| Sending to certified e-waste recycling | 12.4 — Responsible management of hazardous waste |
| Learning circuit diagnostics and repair | 12.8 — Education for sustainable development |

Per-device impact estimates (EPA / e-Stewards / iFixit):
- **~70 lbs CO₂** avoided per repaired device
- **~0.15 lbs toxic metals** diverted per recycled device  
- **~3,000 gallons manufacturing water** saved per repaired device

---

## API Keys (All Optional)

| Key | Purpose | Where to get |
|---|---|---|
| `OPENAI_API_KEY` | Enhanced AI repair guidance via `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com) |
| `EARTH911_API_KEY` | Live e-waste hub lookup | [earth911.com/recycling-api](https://earth911.com/recycling-api) |

The app runs fully without any API keys using its bundled knowledge base.

---

## License

MIT License — built for the 1M1B AI for Sustainability Capstone Programme.
