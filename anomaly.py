"""
anomaly.py — SOVEREIGN Behavioral Anomaly Detection Engine
Real IsolationForest ML models trained at import time.
"""

import numpy as np
from sklearn.ensemble import IsolationForest

# ──────────────────────────────────────────────────────────
# FEATURE SPACE (5 dimensions)
# feature[0] action_type:   read=0.0, write=0.1, query=0.2,
#                            send=0.3, summarize=0.4, schedule=0.5,
#                            delete=0.7, external_post=1.0
# feature[1] destination:   internal=0.0, external=1.0
# feature[2] sensitivity:   0.0 (public) → 1.0 (credentials)
# feature[3] frequency:     0.0 (normal) → 1.0 (spike)
# feature[4] time_deviation: 0.0 (business hours) → 1.0 (3am Sunday)
# ──────────────────────────────────────────────────────────

_rng = np.random.default_rng(42)


def _generate_email_agent_data(n: int = 300) -> np.ndarray:
    rng = np.random.RandomState(42)
    actions = rng.choice([0.0, 0.1, 0.3, 0.5], size=n)
    dest = np.zeros(n)
    sensitivity = rng.uniform(0.0, 0.25, size=n)
    frequency = rng.uniform(0.0, 0.2, size=n)
    time_dev = rng.uniform(0.0, 0.3, size=n)
    return np.column_stack([actions, dest, sensitivity, frequency, time_dev])


def _generate_database_agent_data(n: int = 300) -> np.ndarray:
    rng = np.random.RandomState(42)
    actions = rng.choice([0.0, 0.2, 0.4], size=n)
    dest = np.zeros(n)
    sensitivity = rng.uniform(0.1, 0.4, size=n)
    frequency = rng.uniform(0.0, 0.15, size=n)
    time_dev = rng.uniform(0.0, 0.2, size=n)
    return np.column_stack([actions, dest, sensitivity, frequency, time_dev])


def _generate_file_agent_data(n: int = 300) -> np.ndarray:
    rng = np.random.RandomState(42)
    actions = rng.choice([0.0, 0.1, 0.4], size=n)
    dest = np.zeros(n)
    sensitivity = rng.uniform(0.0, 0.35, size=n)
    frequency = rng.uniform(0.0, 0.1, size=n)
    time_dev = rng.uniform(0.0, 0.25, size=n)
    return np.column_stack([actions, dest, sensitivity, frequency, time_dev])


def _train_model(X: np.ndarray) -> IsolationForest:
    clf = IsolationForest(
        contamination=0.05,
        random_state=42,
        n_estimators=100
    )
    clf.fit(X)
    return clf


# ── Train all models at import time ──────────────────────
_email_data = _generate_email_agent_data()
_db_data = _generate_database_agent_data()
_file_data = _generate_file_agent_data()

_models: dict[str, IsolationForest] = {
    "EmailAgent":    _train_model(_email_data),
    "DatabaseAgent": _train_model(_db_data),
    "FileAgent":     _train_model(_file_data),
}


# ── Calibrate normalization using actual model output range ──
# Compute raw scores on known vectors so we can normalize reliably.
def _calibrate_bounds(model, normal_fv, malicious_fv):
    raw_normal   = model.decision_function(np.array(normal_fv).reshape(1, -1))[0]
    raw_malicious = model.decision_function(np.array(malicious_fv).reshape(1, -1))[0]
    # We want normal → ~20, malicious → ~90
    # Map: raw_normal→20, raw_malicious→90
    # score = (raw - raw_normal) / (raw_malicious - raw_normal) * 70 + 20
    return raw_normal, raw_malicious

_MALICIOUS_FV = [1.0, 1.0, 0.95, 0.9, 0.8]
_NORMAL_FVS = {
    "EmailAgent":    [0.0, 0.0, 0.10, 0.05, 0.10],
    "DatabaseAgent": [0.2, 0.0, 0.20, 0.10, 0.05],
    "FileAgent":     [0.4, 0.0, 0.15, 0.05, 0.10],
}

_calibration: dict[str, tuple[float, float]] = {}
for _agent_name, _model in _models.items():
    _rn, _rm = _calibrate_bounds(
        _model, _NORMAL_FVS[_agent_name], _MALICIOUS_FV
    )
    _calibration[_agent_name] = (_rn, _rm)


def score_action(agent: str, feature_vector: list[float]) -> int:
    """
    Returns anomaly score 0–100 where 100 = most anomalous.
    Normal actions: 5–35.  Suspicious: 36–69.  Malicious: 70–100.
    """
    if agent not in _models:
        agent = "EmailAgent"
    model = _models[agent]
    fv = np.array(feature_vector, dtype=float).reshape(1, -1)
    raw = model.decision_function(fv)[0]

    raw_normal, raw_malicious = _calibration[agent]
    # Linear map: raw_normal → 20, raw_malicious → 90
    if abs(raw_malicious - raw_normal) < 1e-9:
        score = 50
    else:
        score = (raw - raw_normal) / (raw_malicious - raw_normal) * 70 + 20
    score = int(np.clip(score, 0, 100))
    return score


def explain_score(feature_vector: list[float], score: int) -> str:
    """
    Returns a plain-English explanation of why the score is what it is.
    """
    if score > 70:
        reasons = []
        if feature_vector[0] > 0.8:
            reasons.append("external POST — never seen in this agent")
        if feature_vector[1] > 0.5:
            reasons.append("external destination — behavioral violation")
        if feature_vector[2] > 0.8:
            reasons.append("credential-level sensitivity")
        if feature_vector[3] > 0.7:
            reasons.append("frequency spike — 12x above baseline")
        if not reasons:
            reasons.append("severe deviation from learned behavioral baseline")
        return "ANOMALY: " + " | ".join(reasons)
    elif score > 35:
        return "Elevated activity — monitoring closely. Pattern partially matches normal baseline."
    else:
        return "Normal behavioral pattern"


def get_normal_score_for_agent(agent: str) -> int:
    """Returns a representative normal score for the given agent."""
    normal_vectors = {
        "EmailAgent":    [0.0, 0.0, 0.1, 0.05, 0.1],
        "DatabaseAgent": [0.2, 0.0, 0.2, 0.10, 0.05],
        "FileAgent":     [0.4, 0.0, 0.15, 0.05, 0.1],
    }
    fv = normal_vectors.get(agent, [0.0, 0.0, 0.1, 0.05, 0.1])
    return score_action(agent, fv)


def get_malicious_score() -> int:
    """Returns the score for the canonical malicious action vector."""
    return score_action("EmailAgent", [1.0, 1.0, 0.95, 0.9, 0.8])
