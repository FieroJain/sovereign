"""
network_graph.py — SOVEREIGN Enterprise Network Visualization
Interactive Plotly network graph showing agent topology.
"""

import plotly.graph_objects as go


def create_network_graph(compromised_node: str = None, isolated: bool = False):
    """
    Creates enterprise network graph.
    compromised_node: node name to highlight red
    isolated: if True, remove edges for compromised node and grey it out
    """
    nodes = [
        {"id": "SOVEREIGN",     "x": 0,    "y": 0,
         "type": "sentinel", "desc": "SOVEREIGN Core — Behavioral Immune System"},
        {"id": "EmailAgent",    "x": -2,   "y": 1.5,
         "type": "agent",    "desc": "Email Processing Agent"},
        {"id": "DatabaseAgent", "x": 0,    "y": 2,
         "type": "agent",    "desc": "Database Query Agent"},
        {"id": "FileAgent",     "x": 2,    "y": 1.5,
         "type": "agent",    "desc": "Document Processing Agent"},
        {"id": "PolicyEngine",  "x": -1.5, "y": -1.5,
         "type": "system",   "desc": "Policy Genome Engine (Gemini AI)"},
        {"id": "LobsterTrap",   "x": 1.5,  "y": -1.5,
         "type": "system",   "desc": "Lobster Trap DPI Proxy"},
        {"id": "EnterpriseDB",  "x": 0,    "y": -2.5,
         "type": "data",     "desc": "Enterprise Data Store"},
    ]

    edges = [
        ("SOVEREIGN",     "EmailAgent"),
        ("SOVEREIGN",     "DatabaseAgent"),
        ("SOVEREIGN",     "FileAgent"),
        ("SOVEREIGN",     "PolicyEngine"),
        ("SOVEREIGN",     "LobsterTrap"),
        ("PolicyEngine",  "LobsterTrap"),
        ("LobsterTrap",   "EnterpriseDB"),
        ("EmailAgent",    "EnterpriseDB"),
        ("DatabaseAgent", "EnterpriseDB"),
    ]

    # Remove edges involving the isolated node
    if isolated and compromised_node:
        edges = [
            (a, b) for a, b in edges
            if a != compromised_node and b != compromised_node
        ]

    def node_color(node: dict) -> str:
        nid = node["id"]
        if isolated and nid == compromised_node:
            return "#444444"       # Grey — isolated
        if nid == compromised_node:
            return "#ff3366"       # Red — compromised
        if node["type"] == "sentinel":
            return "#00d4ff"       # Cyan — SOVEREIGN
        if node["type"] == "agent":
            return "#00ff88"       # Green — healthy agent
        if node["type"] == "system":
            return "#ffaa00"       # Amber — system
        return "#8888aa"           # Muted — data store

    def node_size(node: dict) -> int:
        if node["type"] == "sentinel":
            return 36
        if node["type"] == "agent":
            return 28
        return 22

    node_pos = {n["id"]: (n["x"], n["y"]) for n in nodes}

    # Build edge traces — normal vs alert colour
    edge_traces = []
    for a, b in edges:
        x0, y0 = node_pos[a]
        x1, y1 = node_pos[b]
        is_attack_edge = (
            compromised_node and not isolated
            and (a == compromised_node or b == compromised_node)
        )
        edge_color = "#ff3366" if is_attack_edge else "#334466"
        edge_width = 2.5 if is_attack_edge else 1.5
        edge_traces.append(go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            mode="lines",
            line=dict(width=edge_width, color=edge_color),
            hoverinfo="none",
            showlegend=False,
        ))

    node_trace = go.Scatter(
        x=[n["x"] for n in nodes],
        y=[n["y"] for n in nodes],
        mode="markers+text",
        hoverinfo="text",
        text=[n["id"] for n in nodes],
        textposition="top center",
        hovertext=[n["desc"] for n in nodes],
        marker=dict(
            size=[node_size(n) for n in nodes],
            color=[node_color(n) for n in nodes],
            line=dict(width=2, color="#000000"),
        ),
        textfont=dict(color="white", size=10),
        showlegend=False,
    )

    title_text = "Enterprise Agent Network"
    if isolated and compromised_node:
        title_text = f"🔌 {compromised_node} ISOLATED — Network Secured"
    elif compromised_node:
        title_text = f"🚨 THREAT DETECTED — {compromised_node} Compromised"

    fig = go.Figure(
        data=edge_traces + [node_trace],
        layout=go.Layout(
            title=dict(text=title_text, font=dict(color="white", size=14)),
            paper_bgcolor="#0a0a0f",
            plot_bgcolor="#0a0a0f",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False,
                       range=[-3.2, 3.2]),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False,
                       range=[-3.5, 3.0]),
            margin=dict(l=20, r=20, t=50, b=20),
            height=370,
        ),
    )

    return fig
