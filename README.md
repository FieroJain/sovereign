# 🛡️ SOVEREIGN — Enterprise AI Immune System

> *Predict. Detect. Neutralize. Automatically.*

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.35-red.svg)](https://streamlit.io/)
[![Gemini AI](https://img.shields.io/badge/gemini-2.0--flash-green.svg)](https://aistudio.google.com/)

## What It Does

SOVEREIGN is a behavioral security platform for enterprise AI agents. It:

1. **Learns** each agent's normal behavior (300 logged actions → IsolationForest model)
2. **Detects** anomalies in real time using behavioral DNA, not keyword matching
3. **Generates** security policies autonomously using Gemini 2.0 Flash
4. **Validates** policies against real traffic before deployment
5. **Isolates** compromised nodes at hardware level — no human required

## Quick Start (3 commands)

```bash
git clone https://github.com/YOUR_USERNAME/sovereign
cd sovereign
cp .env.example .env        # Add your Gemini API key
pip install -r requirements.txt
streamlit run app.py
```

## Get Gemini API Key (Free, 2 minutes)

Visit: https://aistudio.google.com/app/apikey

Paste it into your `.env` file:
```
GEMINI_API_KEY=AIza...your_key_here
```

> **Works without a key too.** Fallback mode uses a pre-built valid policy.

## Architecture

```
Enterprise AI Agents (EmailAgent, DatabaseAgent, FileAgent)
         │
         ▼
  SOVEREIGN Core ──────────────────────────────────────────┐
  (Behavioral Monitor)                                     │
         │                                                 │
         ├──► Anomaly Detector (IsolationForest)           │
         │    • 5-dimensional behavioral feature space     │
         │    • 300 normal actions per agent baseline      │
         │    • Real-time scoring 0–100                    │
         │                                                 │
         ├──► Policy Genome Engine (Gemini 2.0 Flash)      │
         │    • Autonomous YAML policy generation          │
         │    • Falls back gracefully if offline           │
         │                                                 │
         ├──► Lobster Trap Validator                       │
         │    • YAML structure validation                  │
         │    • Normal traffic simulation (no false pos.)  │
         │    • Attack traffic simulation (must block)     │
         │                                                 │
         └──► Physical Isolation (Veea Edge API)           │
              • Hardware-level network disconnection       │
              • Requires human auth to reconnect           │
```

## The Research Finding

| Detection Method | Attacks Caught | Rate |
|---|---|---|
| Rule-based (keyword) | 8/20 | **40%** |
| Agent DNA (SOVEREIGN) | 19/20 | **95%** |

**2.35× better detection.** Subtle behavioral attacks with no alarm keywords are invisible to rules-based systems. They're not invisible to SOVEREIGN.

## Demo Flow (3 minutes)

1. **Tab 1 — Live Monitor**: Watch 3 agents running normally → Click **INJECT ATTACK** → EmailAgent anomaly score spikes to 94
2. **Tab 2 — Threat Response**: Click **Generate Policy** (Gemini AI writes YAML) → **Validate** → **Deploy** → **Isolate Node**
3. **Tab 3 — Research**: Empirical proof that Agent DNA beats rule-based security 2.35×

## Track Alignment

| Track | How SOVEREIGN addresses it |
|---|---|
| **Track 1: Agent Security & AI Governance** | Core purpose — behavioral monitoring, guardrails, audit trails |
| **Track 2: AI Agents with Google AI Studio** | Policy Genome Engine powered by Gemini 2.0 Flash |
| **Track 4: Data & Intelligence** | Behavioral analytics, real ML, empirical research |

## File Structure

```
sovereign/
├── app.py               # Streamlit dashboard (3 tabs)
├── agents.py            # Agent simulation engine + research data
├── anomaly.py           # IsolationForest ML engine
├── policy_engine.py     # Gemini policy generation
├── lobster_validator.py # YAML policy validation
├── network_graph.py     # Plotly network topology graph
├── requirements.txt     # Pinned dependencies
├── Dockerfile           # Container deployment
└── .env.example         # API key template
```

## License

MIT — built for the lablab.ai "Transforming Enterprise Through AI" Hackathon 2026.
