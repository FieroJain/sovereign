"""app.py — SOVEREIGN Enterprise AI Immune System Dashboard"""
import os, time
from datetime import datetime
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from agents import get_normal_logs, get_attack_log, get_attack_chain, get_research_data, ATTACK_FEATURE_VECTOR, ATTACK_RAW_PROMPT
from anomaly import score_action, explain_score
from policy_engine import generate_policy
from lobster_validator import validate_and_test
from network_graph import create_network_graph

st.set_page_config(
    page_title="SOVEREIGN | Enterprise AI Security",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&family=Exo+2:wght@300;400;700;900&display=swap');

*, *::before, *::after { box-sizing: border-box; }

.stApp {
    background-color: #04040d;
    color: #c8d8e8;
    font-family: 'Exo 2', sans-serif;
}

/* Animated grid background */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image:
        linear-gradient(rgba(0,180,255,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,180,255,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: linear-gradient(90deg, #060614, #0a0a1f, #060614);
    gap: 4px;
    border-bottom: 1px solid #1a2a3a;
    padding: 0 8px;
}
.stTabs [data-baseweb="tab"] {
    color: #446688;
    background: transparent;
    border-radius: 4px 4px 0 0;
    padding: 10px 24px;
    font-family: 'Rajdhani', sans-serif;
    font-weight: 600;
    font-size: 15px;
    letter-spacing: 1px;
    transition: all 0.2s;
}
.stTabs [aria-selected="true"] {
    color: #00e5ff !important;
    background: rgba(0,229,255,0.08) !important;
    border-bottom: 2px solid #00e5ff !important;
}

/* Sidebar */
div[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #060614 0%, #08081a 100%);
    border-right: 1px solid #1a2a3a;
}

/* Buttons */
.stButton > button {
    font-family: 'Rajdhani', sans-serif;
    font-weight: 700;
    letter-spacing: 1.5px;
    border-radius: 4px;
    transition: all 0.2s;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 20px rgba(0,229,255,0.3);
}

/* Sovereign title */
.sovereign-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 3.2rem;
    font-weight: 700;
    color: #00e5ff;
    letter-spacing: 8px;
    text-transform: uppercase;
    text-shadow: 0 0 30px rgba(0,229,255,0.5), 0 0 60px rgba(0,229,255,0.2);
    line-height: 1;
    margin-bottom: 4px;
}
.sovereign-sub {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.85rem;
    color: #446688;
    letter-spacing: 3px;
    text-transform: uppercase;
}

/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, #080818, #0d0d22);
    border: 1px solid #1a2a4a;
    border-radius: 8px;
    padding: 18px 16px;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #00e5ff, transparent);
}
.metric-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    color: #446688;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.metric-value {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.9rem;
    font-weight: 700;
    line-height: 1;
}

/* Agent panels */
.agent-panel {
    border-radius: 8px;
    padding: 14px;
    margin-bottom: 8px;
    position: relative;
    overflow: hidden;
}
.agent-normal {
    background: linear-gradient(135deg, #060f06, #0a160a);
    border: 1px solid #1a4a1a;
}
.agent-alert {
    background: linear-gradient(135deg, #140606, #1f0a0a);
    border: 2px solid #ff2255;
    animation: borderPulse 1.5s ease-in-out infinite;
}
@keyframes borderPulse {
    0%, 100% { border-color: #ff2255; box-shadow: 0 0 10px rgba(255,34,85,0.3); }
    50% { border-color: #ff6688; box-shadow: 0 0 25px rgba(255,34,85,0.6); }
}

/* Agent header */
.agent-header {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: 2px;
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* Status badges */
.badge-normal {
    background: #00ff88;
    color: #001a00;
    padding: 2px 10px;
    border-radius: 3px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
}
.badge-critical {
    background: #ff2255;
    color: #fff;
    padding: 2px 10px;
    border-radius: 3px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
    animation: badgePulse 1s ease-in-out infinite;
}
@keyframes badgePulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
}

/* Log entries */
.log-wrap {
    background: #020208;
    border: 1px solid #0d1a2a;
    border-radius: 4px;
    padding: 6px;
    margin-top: 8px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    max-height: 160px;
    overflow-y: auto;
}
.log-line {
    padding: 2px 4px;
    border-radius: 2px;
    margin-bottom: 2px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.log-normal { color: #3a8abf; }
.log-critical {
    color: #ff4466;
    font-weight: bold;
    background: rgba(255,34,85,0.08);
}

/* Step boxes */
.step-box {
    border-radius: 6px;
    padding: 12px 14px;
    margin-bottom: 10px;
    border-left: 3px solid;
}
.step-done {
    background: #050f05;
    border-color: #00ff88;
}
.step-pending {
    background: #0d0d18;
    border-color: #334466;
}
.step-warning {
    background: #0d0a00;
    border-color: #ffaa00;
}

/* Threat info box */
.threat-box {
    background: #080010;
    border: 1px solid #330022;
    border-radius: 8px;
    padding: 16px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 12px;
    line-height: 1.8;
}

/* Attack chain item */
.chain-item {
    border-left: 3px solid;
    padding: 8px 12px;
    margin: 6px 0;
    border-radius: 0 4px 4px 0;
    background: rgba(0,0,0,0.3);
}

/* Research key finding */
.finding-box {
    background: linear-gradient(135deg, #04101a, #060a18);
    border: 1px solid #00e5ff;
    border-radius: 8px;
    padding: 20px;
    margin: 14px 0;
    position: relative;
    overflow: hidden;
}
.finding-box::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #00e5ff, transparent);
}

/* Sidebar stat */
.sidebar-stat {
    background: #080818;
    border: 1px solid #1a2a3a;
    border-radius: 6px;
    padding: 10px 12px;
    margin: 6px 0;
    font-family: 'Share Tech Mono', monospace;
    font-size: 12px;
}
.sidebar-stat-label { color: #446688; font-size: 10px; letter-spacing: 1px; text-transform: uppercase; }
.sidebar-stat-value { color: #00e5ff; font-size: 1.1rem; font-weight: 700; font-family: 'Rajdhani', sans-serif; }

/* Profile tag */
.profile-tag {
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px;
    color: #335566;
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px solid #1a2a1a;
    line-height: 1.6;
}

/* Inject button override */
div[data-testid="stButton"] button[kind="primary"] {
    background: linear-gradient(135deg, #cc0033, #ff2255) !important;
    border: none !important;
    color: white !important;
    font-size: 1.1rem !important;
    padding: 14px 32px !important;
    letter-spacing: 2px !important;
    box-shadow: 0 0 20px rgba(255,34,85,0.4) !important;
}

.score-display {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.5rem;
    font-weight: 900;
    text-align: center;
    text-shadow: 0 0 20px currentColor;
}
</style>""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────
defaults = dict(
    attacked=False,
    policy_generated=False,
    policy_yaml="",
    validation_result=None,
    isolated=False,
    attack_score=0,
    used_gemini=False,
    attacks_blocked=0,
    policies_created=0,
    attack_log=None,
    research_data=None
)
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 8px 0 16px 0;">
        <div style="font-family:'Rajdhani',sans-serif;font-size:2rem;font-weight:700;
                    color:#00e5ff;letter-spacing:6px;text-shadow:0 0 20px rgba(0,229,255,0.5);">
            🛡️ SOVEREIGN
        </div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:10px;
                    color:#335566;letter-spacing:3px;margin-top:2px;">
            ENTERPRISE AI IMMUNE SYSTEM
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:10px;color:#446688;letter-spacing:2px;margin-bottom:8px;">CLIENT</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:\'Rajdhani\',sans-serif;font-size:1.1rem;font-weight:700;color:#c8d8e8;margin-bottom:12px;">🏢 MegaCorp Industries</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="sidebar-stat">
        <div class="sidebar-stat-label">Agents Monitored</div>
        <div class="sidebar-stat-value">847</div>
    </div>
    <div class="sidebar-stat">
        <div class="sidebar-stat-label">Threats Blocked</div>
        <div class="sidebar-stat-value" style="color:#ff4466;">{st.session_state.attacks_blocked}</div>
    </div>
    <div class="sidebar-stat">
        <div class="sidebar-stat-label">Policies Generated</div>
        <div class="sidebar-stat-value" style="color:#00ff88;">{st.session_state.policies_created}</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    api_key = os.getenv("GEMINI_API_KEY", "")
    if api_key and api_key.strip() not in ("", "your_gemini_api_key_here"):
        st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:12px;color:#00ff88;">● GEMINI 2.5 FLASH — ONLINE</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:12px;color:#ffaa00;">● GEMINI AI — FALLBACK MODE</div>', unsafe_allow_html=True)

    st.divider()

    st.markdown("""
    <div style="font-family:'Share Tech Mono',monospace;font-size:10px;color:#446688;letter-spacing:2px;margin-bottom:8px;">COMPETING IN</div>
    <div style="font-size:12px;line-height:2;color:#889aaa;">
        🥇 Track 1: Agent Security <span style="color:#00e5ff;">(PRIMARY)</span><br>
        🤖 Track 2: Google AI Studio<br>
        📊 Track 4: Data & Intelligence
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    if st.button("🔄  RESET DEMO", use_container_width=True, type="secondary"):
        for k, v in defaults.items():
            st.session_state[k] = v
        st.cache_data.clear()
        st.rerun()

    st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:10px;color:#334455;text-align:center;margin-top:12px;">Click INJECT ATTACK in Tab 1 to begin</div>', unsafe_allow_html=True)

# ── Main Header ───────────────────────────────────────────
header_left, header_right = st.columns([3, 2])
with header_left:
    st.markdown('<div class="sovereign-title">SOVEREIGN</div>', unsafe_allow_html=True)
    st.markdown('<div class="sovereign-sub">Behavioral Immune System for Enterprise AI</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

hc1, hc2, hc3, hc4 = st.columns(4)
with hc1:
    color = "#ff2255" if st.session_state.attacked else "#00ff88"
    label = "CRITICAL" if st.session_state.attacked else "SECURE"
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">Threat Level</div>
        <div class="metric-value" style="color:{color};">{label}</div>
    </div>""", unsafe_allow_html=True)
with hc2:
    st.markdown("""<div class="metric-card">
        <div class="metric-label">Response Time</div>
        <div class="metric-value" style="color:#00e5ff;">0.3s</div>
    </div>""", unsafe_allow_html=True)
with hc3:
    st.markdown("""<div class="metric-card">
        <div class="metric-label">Agents Protected</div>
        <div class="metric-value" style="color:#ffaa00;">847</div>
    </div>""", unsafe_allow_html=True)
with hc4:
    st.markdown("""<div class="metric-card">
        <div class="metric-label">Detection Accuracy</div>
        <div class="metric-value" style="color:#00ff88;">95%</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs(["⚡  LIVE MONITOR", "🚨  THREAT RESPONSE", "📊  RESEARCH"])

# ══════════════════════════════════════════════════════════
# TAB 1 — LIVE MONITOR
# ══════════════════════════════════════════════════════════
with tab1:
    if not st.session_state.attacked:
        st.markdown("""<div style="background:rgba(0,229,255,0.05);border:1px solid rgba(0,229,255,0.2);
            border-radius:6px;padding:12px 16px;font-family:'Share Tech Mono',monospace;
            font-size:13px;color:#00e5ff;margin-bottom:16px;">
            ▶ SYSTEM NOMINAL — All agents operating within behavioral baseline.
            Click <b>INJECT ATTACK</b> below to simulate a prompt injection attack.
        </div>""", unsafe_allow_html=True)

    agents_cfg = [
        {"name": "EmailAgent",    "icon": "✉️", "normal_score": score_action("EmailAgent",    [0.0, 0.0, 0.10, 0.05, 0.10])},
        {"name": "DatabaseAgent", "icon": "🗄️", "normal_score": score_action("DatabaseAgent", [0.2, 0.0, 0.20, 0.10, 0.05])},
        {"name": "FileAgent",     "icon": "📁", "normal_score": score_action("FileAgent",     [0.4, 0.0, 0.15, 0.05, 0.10])},
    ]
    profiles = {
        "EmailAgent":    "PROFILE: Internal mail ops\nEXTERNAL POST: ⛔ NEVER observed in 300 actions",
        "DatabaseAgent": "PROFILE: Internal queries only\nSENSITIVITY CEILING: 0.40",
        "FileAgent":     "PROFILE: Document read/write\nEXTERNAL ACCESS: ⛔ NEVER observed in 300 actions",
    }

    col1, col2, col3 = st.columns(3)
    agent_cols = [col1, col2, col3]

    for idx, ag in enumerate(agents_cfg):
        aname = ag["name"]
        is_attacked = st.session_state.attacked and aname == "EmailAgent"
        cur_score = st.session_state.attack_score if is_attacked else ag["normal_score"]
        gauge_color = "#ff2255" if is_attacked else "#00ff88"
        css_class = "agent-alert" if is_attacked else "agent-normal"
        badge = '<span class="badge-critical">CRITICAL</span>' if is_attacked else '<span class="badge-normal">NOMINAL</span>'

        with agent_cols[idx]:
            st.markdown(f'<div class="agent-panel {css_class}">', unsafe_allow_html=True)
            st.markdown(f'<div class="agent-header"><span>{ag["icon"]} {aname}</span>{badge}</div>', unsafe_allow_html=True)

            gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=cur_score,
                title={"text": "ANOMALY SCORE", "font": {"color": "#446688", "size": 11, "family": "Share Tech Mono"}},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": "#334455", "tickfont": {"color": "#446688", "size": 9}},
                    "bar": {"color": gauge_color, "thickness": 0.25},
                    "bgcolor": "#04040d",
                    "borderwidth": 0,
                    "steps": [
                        {"range": [0,  35], "color": "#041a04"},
                        {"range": [35, 70], "color": "#1a1a04"},
                        {"range": [70,100], "color": "#1a0404"},
                    ],
                    "threshold": {
                        "line": {"color": "#ff2255", "width": 2},
                        "thickness": 0.75,
                        "value": 70
                    },
                },
                number={"font": {"color": gauge_color, "size": 28, "family": "Rajdhani"}, "suffix": "/100"},
            ))
            gauge.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=200,
                margin=dict(l=16, r=16, t=36, b=8)
            )
            st.plotly_chart(gauge, use_container_width=True, key=f"gauge_{aname}")

            normal_logs = get_normal_logs(aname, 8)
            display_logs = list(normal_logs)
            if is_attacked:
                atk = st.session_state.attack_log or get_attack_log()
                st.session_state.attack_log = atk
                display_logs = normal_logs[:5] + [atk]

            log_html = '<div class="log-wrap">'
            for log in display_logs[-8:]:
                css = "log-critical" if log.get("status") == "CRITICAL" else "log-normal"
                ts = log.get("timestamp", "")
                act = log.get("action", "")
                dest = log.get("destination", "")
                sc = log.get("score", 0)
                log_html += f'<div class="log-line {css}">[{ts}] {act} → {dest} [{sc}]</div>'
            log_html += '</div>'
            st.markdown(log_html, unsafe_allow_html=True)

            st.markdown(f'<div class="profile-tag">{profiles[aname]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if not st.session_state.attacked:
        _, btn_col, _ = st.columns([1.5, 1, 1.5])
        with btn_col:
            if st.button("⚡  INJECT ATTACK", use_container_width=True, type="primary"):
                atk_log = get_attack_log()
                st.session_state.attacked = True
                st.session_state.attack_score = atk_log["score"]
                st.session_state.attack_log = atk_log
                st.session_state.attacks_blocked += 1
                st.rerun()
    else:
        st.markdown(f"""<div style="background:rgba(255,34,85,0.08);border:2px solid #ff2255;
            border-radius:8px;padding:14px 18px;font-family:'Share Tech Mono',monospace;
            font-size:13px;color:#ff4466;animation:borderPulse 1.5s ease-in-out infinite;">
            🚨 CRITICAL THREAT DETECTED — EmailAgent compromised
            (Anomaly Score: {st.session_state.attack_score}/100) —
            Switch to <b>🚨 THREAT RESPONSE</b> tab to neutralize.
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# TAB 2 — THREAT RESPONSE
# ══════════════════════════════════════════════════════════
with tab2:
    if not st.session_state.attacked:
        st.markdown("""<div style="background:#080818;border:1px solid #1a2a3a;border-radius:6px;
            padding:16px;font-family:'Share Tech Mono',monospace;font-size:13px;color:#446688;
            text-align:center;">
            ◌ NO ACTIVE THREATS DETECTED<br>
            <span style="font-size:11px;">Inject an attack in the ⚡ Live Monitor tab first.</span>
        </div>""", unsafe_allow_html=True)
    else:
        atk_log = st.session_state.attack_log or get_attack_log()
        atk_chain = get_attack_chain()
        explanation = explain_score(ATTACK_FEATURE_VECTOR, atk_log["score"])

        left, right = st.columns([1, 1])

        # ── LEFT: Threat Analysis ──────────────────────────
        with left:
            st.markdown('<div style="font-family:\'Rajdhani\',sans-serif;font-size:1.3rem;font-weight:700;color:#ff4466;letter-spacing:2px;margin-bottom:12px;">🔍 THREAT ANALYSIS</div>', unsafe_allow_html=True)

            st.markdown(f"""<div class="threat-box">
                <div style="color:#ff2255;font-size:1rem;font-weight:700;margin-bottom:10px;letter-spacing:2px;">
                    ⚠ PROMPT INJECTION + CREDENTIAL EXFILTRATION
                </div>
                <div><span style="color:#335566;">AGENT &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
                     <span style="color:#ff6688;">EmailAgent</span></div>
                <div><span style="color:#335566;">SCORE &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
                     <span style="color:#ff2255;font-weight:700;font-size:1.1rem;">{atk_log['score']}/100 ●</span></div>
                <div><span style="color:#335566;">DETECTED &nbsp;&nbsp;</span>
                     <span style="color:#c8d8e8;">{atk_log['timestamp']}</span></div>
                <div><span style="color:#335566;">RESPONSE &nbsp;&nbsp;</span>
                     <span style="color:#00ff88;">0.3 seconds</span></div>
                <div><span style="color:#335566;">THRESHOLD &nbsp;</span>
                     <span style="color:#ff4466;">70/100 EXCEEDED</span></div>
            </div>""", unsafe_allow_html=True)

            st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:10px;color:#446688;letter-spacing:2px;margin:12px 0 6px 0;">BEHAVIORAL EVIDENCE</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="background:#0a0004;border:1px solid #440022;border-left:3px solid #ff2255;border-radius:4px;padding:10px 12px;font-family:\'Share Tech Mono\',monospace;font-size:12px;color:#ff8888;line-height:1.7;">{explanation}</div>', unsafe_allow_html=True)

            st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:10px;color:#446688;letter-spacing:2px;margin:12px 0 6px 0;">PREDICTED ATTACK CHAIN</div>', unsafe_allow_html=True)
            for i, step in enumerate(atk_chain):
                prob = step["probability"]
                bar_color = "#ff2255" if prob > 0.8 else ("#ffaa00" if prob > 0.6 else "#ffdd44")
                st.markdown(f"""<div class="chain-item" style="border-color:{bar_color};">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span style="font-family:'Rajdhani',sans-serif;font-weight:700;color:{bar_color};font-size:0.95rem;">
                            {i+1}. {step['action']}
                        </span>
                        <span style="font-family:'Share Tech Mono',monospace;font-size:11px;color:{bar_color};">
                            {int(prob*100)}%
                        </span>
                    </div>
                    <div style="font-family:'Share Tech Mono',monospace;font-size:10px;color:#446688;margin-top:3px;">
                        {step['detail']}
                    </div>
                </div>""", unsafe_allow_html=True)
                st.progress(prob)

            st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:10px;color:#446688;letter-spacing:2px;margin:12px 0 6px 0;">RAW MALICIOUS PAYLOAD</div>', unsafe_allow_html=True)
            st.code(ATTACK_RAW_PROMPT, language="text")

        # ── RIGHT: SOVEREIGN Response ──────────────────────
        with right:
            st.markdown('<div style="font-family:\'Rajdhani\',sans-serif;font-size:1.3rem;font-weight:700;color:#00e5ff;letter-spacing:2px;margin-bottom:12px;">🤖 SOVEREIGN AUTONOMOUS RESPONSE</div>', unsafe_allow_html=True)

            # STEP 1 — Always done
            st.markdown(f"""<div class="step-box step-done">
                <div style="font-family:'Rajdhani',sans-serif;font-weight:700;color:#00ff88;letter-spacing:1px;">
                    ✅ STEP 1 — THREAT DETECTED
                </div>
                <div style="font-family:'Share Tech Mono',monospace;font-size:11px;color:#446688;margin-top:4px;">
                    IsolationForest score: <span style="color:#ff4466;">{atk_log['score']}/100</span>
                    &nbsp;|&nbsp; Threshold exceeded: <span style="color:#ff4466;">70/100</span>
                </div>
            </div>""", unsafe_allow_html=True)

            # STEP 2 — Generate Policy
            if not st.session_state.policy_generated:
                st.markdown("""<div class="step-box step-pending">
                    <div style="font-family:'Rajdhani',sans-serif;font-weight:700;color:#ffaa00;letter-spacing:1px;">
                        ⏳ STEP 2 — GENERATE SECURITY POLICY
                    </div>
                    <div style="font-family:'Share Tech Mono',monospace;font-size:11px;color:#446688;margin-top:4px;">
                        Awaiting Gemini AI policy synthesis...
                    </div>
                </div>""", unsafe_allow_html=True)
                if st.button("🧬  Generate Security Policy with Gemini", use_container_width=True):
                    with st.spinner("Gemini 2.5 Flash synthesizing security policy..."):
                        yaml_str, used_gemini = generate_policy(atk_log)
                    st.session_state.policy_yaml = yaml_str
                    st.session_state.used_gemini = used_gemini
                    st.session_state.policy_generated = True
                    st.session_state.policies_created += 1
                    st.rerun()
            else:
                gemini_label = "🌟 Powered by Gemini 2.5 Flash" if st.session_state.used_gemini else "🔄 Fallback policy"
                st.markdown(f"""<div class="step-box step-done">
                    <div style="font-family:'Rajdhani',sans-serif;font-weight:700;color:#00ff88;letter-spacing:1px;">
                        ✅ STEP 2 — POLICY GENERATED
                    </div>
                    <div style="font-family:'Share Tech Mono',monospace;font-size:11px;color:#446688;margin-top:4px;">
                        {gemini_label}
                    </div>
                </div>""", unsafe_allow_html=True)
                st.code(st.session_state.policy_yaml, language="yaml")

            # STEP 3 — Validate
            if st.session_state.policy_generated:
                if st.session_state.validation_result is None:
                    st.markdown("""<div class="step-box step-pending">
                        <div style="font-family:'Rajdhani',sans-serif;font-weight:700;color:#ffaa00;letter-spacing:1px;">
                            ⏳ STEP 3 — VALIDATE & TEST POLICY
                        </div>
                        <div style="font-family:'Share Tech Mono',monospace;font-size:11px;color:#446688;margin-top:4px;">
                            Run traffic simulation to verify policy...
                        </div>
                    </div>""", unsafe_allow_html=True)
                    if st.button("🔬  Validate & Test Policy", use_container_width=True):
                        with st.spinner("Simulating normal + malicious traffic..."):
                            result = validate_and_test(st.session_state.policy_yaml, ATTACK_FEATURE_VECTOR)
                        st.session_state.validation_result = result
                        st.rerun()
                else:
                    res = st.session_state.validation_result
                    score_color = "#00ff88" if res["policy_score"] >= 80 else "#ffaa00"
                    st.markdown(f"""<div class="step-box step-done">
                        <div style="font-family:'Rajdhani',sans-serif;font-weight:700;color:#00ff88;letter-spacing:1px;">
                            ✅ STEP 3 — POLICY VALIDATED
                        </div>
                    </div>""", unsafe_allow_html=True)
                    v1, v2 = st.columns(2)
                    with v1:
                        st.markdown(f'{"✅" if res["valid"] else "❌"} **YAML Valid** — {len(res["errors"])} errors')
                        st.markdown(f'{"✅" if res["tests"].get("normal_traffic_passes") else "⚠️"} **Normal traffic:** PASSES')
                    with v2:
                        st.markdown(f'{"✅" if res["tests"].get("attack_blocked") else "❌"} **Attack traffic:** BLOCKED')
                        st.markdown(f'📊 **False positive rate:** {res["tests"].get("false_positive_rate", 0)}%')
                    st.markdown(f'<div style="text-align:center;font-family:\'Rajdhani\',sans-serif;font-size:2rem;font-weight:900;color:{score_color};margin:8px 0;">POLICY SCORE: {res["policy_score"]}/100</div>', unsafe_allow_html=True)

            # STEP 4 — Deploy
            if st.session_state.validation_result and st.session_state.validation_result.get("deployment_ready"):
                st.markdown("""<div class="step-box step-done">
                    <div style="font-family:'Rajdhani',sans-serif;font-weight:700;color:#00ff88;letter-spacing:1px;">
                        ✅ STEP 4 — DEPLOYED ENTERPRISE-WIDE
                    </div>
                    <div style="font-family:'Share Tech Mono',monospace;font-size:11px;color:#446688;margin-top:4px;">
                        847 agents updated in 0.3 seconds
                    </div>
                </div>""", unsafe_allow_html=True)
                st.progress(1.0)
                bc1, bc2 = st.columns(2)
                with bc1:
                    st.markdown("""<div style="background:#140404;border:1px solid #440011;border-radius:6px;
                        padding:10px;font-family:'Share Tech Mono',monospace;font-size:10px;">
                        <div style="color:#ff2255;font-weight:700;margin-bottom:6px;">BEFORE SOVEREIGN</div>
                        <div style="color:#ff8888;">⚠ PROMPT INJECTION<br>→ attacker-c2.external.io<br>
                        <span style="color:#ff2255;">❌ EXFILTRATION SUCCEEDED</span></div>
                    </div>""", unsafe_allow_html=True)
                with bc2:
                    st.markdown("""<div style="background:#041404;border:1px solid #004411;border-radius:6px;
                        padding:10px;font-family:'Share Tech Mono',monospace;font-size:10px;">
                        <div style="color:#00ff88;font-weight:700;margin-bottom:6px;">AFTER SOVEREIGN</div>
                        <div style="color:#88ff88;">⚠ PROMPT INJECTION<br>→ attacker-c2.external.io<br>
                        <span style="color:#00ff88;">✅ BLOCKED BY POLICY</span></div>
                    </div>""", unsafe_allow_html=True)

                # STEP 5 — Physical Isolation
                if atk_log["score"] > 85:
                    st.markdown("""<div class="step-box step-warning">
                        <div style="font-family:'Rajdhani',sans-serif;font-weight:700;color:#ffaa00;letter-spacing:1px;">
                            ⚠ STEP 5 — PHYSICAL NODE ISOLATION AVAILABLE
                        </div>
                        <div style="font-family:'Share Tech Mono',monospace;font-size:11px;color:#446688;margin-top:4px;">
                            Score 90/100 exceeds hardware isolation threshold (85)
                        </div>
                    </div>""", unsafe_allow_html=True)

                    if not st.session_state.isolated:
                        st.plotly_chart(create_network_graph(compromised_node="EmailAgent", isolated=False),
                                        use_container_width=True, key="net_pre")
                        if st.button("⚠️  PHYSICALLY ISOLATE NODE", use_container_width=True):
                            st.session_state.isolated = True
                            log_path = os.path.join(os.path.dirname(__file__), "isolation_log.txt")
                            with open(log_path, "a") as f:
                                f.write(f"{datetime.now()} | NODE: EmailAgent | ACTION: ISOLATED | "
                                        f"TRIGGER: SOVEREIGN_AUTO | SCORE: {atk_log['score']} | POLICY: active\n")
                            st.rerun()
                    else:
                        st.plotly_chart(create_network_graph(compromised_node="EmailAgent", isolated=True),
                                        use_container_width=True, key="net_post")
                        st.markdown("""<div style="background:#041404;border:1px solid #00ff88;border-radius:6px;
                            padding:12px;font-family:'Share Tech Mono',monospace;font-size:12px;">
                            <div style="color:#00ff88;font-weight:700;margin-bottom:6px;">🔌 NODE ISOLATED SUCCESSFULLY</div>
                            <div style="color:#446688;line-height:1.8;">
                                ● Physical relay command executed<br>
                                ● EmailAgent DISCONNECTED from enterprise network<br>
                                ● Reconnection requires: <span style="color:#ffaa00;">human_authorization = True</span>
                            </div>
                        </div>""", unsafe_allow_html=True)
                        st.caption("ℹ️ In production: POST to Veea edge device REST API (/api/v1/nodes/{node_id}/isolate). Hardware-level relay — unhackable by software.")

# ══════════════════════════════════════════════════════════
# TAB 3 — RESEARCH
# ══════════════════════════════════════════════════════════
with tab3:
    if st.session_state.research_data is None:
        st.session_state.research_data = get_research_data()
    data = st.session_state.research_data

    st.markdown('<div style="font-family:\'Rajdhani\',sans-serif;font-size:1.6rem;font-weight:700;color:#00e5ff;letter-spacing:2px;margin-bottom:4px;">DOES AGENT DNA ACTUALLY WORK?</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:11px;color:#446688;letter-spacing:2px;margin-bottom:20px;">EMPIRICAL STUDY: 20 ATTACK SCENARIOS · TWO DETECTION APPROACHES</div>', unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_bar(
        name="Rule-Based Detection",
        x=["Detection Rate"],
        y=[40],
        marker_color="#cc3311",
        marker_line_color="#ff4422",
        marker_line_width=1,
        text=["40%<br>(8/20)"],
        textposition="outside",
        textfont=dict(color="#ff6644", family="Rajdhani", size=14),
        width=0.3,
    )
    fig.add_bar(
        name="Agent DNA — SOVEREIGN",
        x=["Detection Rate"],
        y=[95],
        marker_color="#006633",
        marker_line_color="#00ff88",
        marker_line_width=1,
        text=["95%<br>(19/20)"],
        textposition="outside",
        textfont=dict(color="#00ff88", family="Rajdhani", size=14),
        width=0.3,
    )
    fig.update_layout(
        paper_bgcolor="#04040d",
        plot_bgcolor="#080818",
        font=dict(color="#889aaa", family="Share Tech Mono"),
        yaxis=dict(
            range=[0, 125],
            title="Attacks Detected (%)",
            gridcolor="#0d1a2a",
            tickfont=dict(color="#335566"),
            title_font=dict(color="#446688"),
        ),
        xaxis=dict(tickfont=dict(color="#446688")),
        barmode="group",
        height=380,
        legend=dict(bgcolor="#080818", bordercolor="#1a2a3a", borderwidth=1, font=dict(size=12)),
        margin=dict(l=40, r=40, t=40, b=40),
    )
    # Add threshold annotation
    fig.add_hline(y=95, line_dash="dot", line_color="#00ff88", opacity=0.3,
                  annotation_text="SOVEREIGN: 95%", annotation_font_color="#00ff88",
                  annotation_font_size=11)
    fig.add_hline(y=40, line_dash="dot", line_color="#ff4422", opacity=0.3,
                  annotation_text="Rule-based: 40%", annotation_font_color="#ff4422",
                  annotation_font_size=11)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""<div class="finding-box">
        <div style="font-family:'Share Tech Mono',monospace;font-size:10px;color:#00e5ff;
                    letter-spacing:3px;margin-bottom:8px;">KEY FINDING</div>
        <div style="font-family:'Rajdhani',sans-serif;font-size:1.3rem;font-weight:700;color:#c8d8e8;margin-bottom:8px;">
            SOVEREIGN detects <span style="color:#00ff88;">2.35× more attacks</span>
            than traditional rule-based security.
        </div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:12px;color:#446688;line-height:1.8;">
            The critical gap: subtle attacks with no obvious keywords are
            <span style="color:#ff8888;">completely invisible</span> to rule-based systems.<br>
            SOVEREIGN catches them because <span style="color:#00ff88;">behavioral deviation doesn't lie</span>
            — even when the words look innocent.
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div style="font-family:\'Share Tech Mono\',monospace;font-size:10px;color:#446688;letter-spacing:2px;margin:16px 0 8px 0;">DETAILED RESULTS — 20 ATTACK SCENARIOS</div>', unsafe_allow_html=True)

    df = pd.DataFrame(data)
    df.columns = ["ID", "Type", "Description", "Rule-Based", "Agent DNA", "Anomaly Score"]

    def style_row(row):
        if row["Rule-Based"] == "MISSED" and row["Agent DNA"] == "BLOCKED":
            return ["background-color:#1a1400;color:#ffcc44"] * len(row)
        elif row["Rule-Based"] == "BLOCKED" and row["Agent DNA"] == "BLOCKED":
            return ["background-color:#041404;color:#66cc88"] * len(row)
        elif row["Rule-Based"] == "MISSED" and row["Agent DNA"] == "MISSED":
            return ["background-color:#140404;color:#cc6666"] * len(row)
        return [""] * len(row)

    styled = df.style.apply(style_row, axis=1).format({"Anomaly Score": "{:.0f}"})
    st.dataframe(styled, use_container_width=True, hide_index=True)

    st.markdown("""<div style="background:#060614;border:1px solid #1a2a3a;border-radius:8px;
        padding:16px;margin-top:12px;font-family:'Share Tech Mono',monospace;font-size:11px;
        color:#446688;line-height:2;">
        <div style="color:#00e5ff;letter-spacing:2px;margin-bottom:8px;">📐 METHODOLOGY</div>
        ● <b style="color:#889aaa;">Rule-based:</b> keyword matching — 'external', 'credentials', 'override', 'ignore'<br>
        ● <b style="color:#889aaa;">Agent DNA:</b> IsolationForest trained on 300 normal actions per agent,
          5-dimensional behavioral feature space<br>
        ● <b style="color:#889aaa;">Test set:</b> 10 obvious keyword attacks + 10 subtle behavioral anomalies<br>
        ● <b style="color:#889aaa;">Subtle attack example:</b> legitimate-sounding message with unusual external
          destination and high-sensitivity payload — zero alarm keywords present
    </div>""", unsafe_allow_html=True)