"""causal_inference.py — SOVEREIGN-A Causal Inference Engine"""

class CausalInference:
    def __init__(self):
        pass

    def infer_root_cause(self, feature_vector, action_desc, score):
        if "external" in action_desc.lower() and "credential" in action_desc.lower():
            return "prompt_injection", 0.92
        return "unknown", 0.5

    def explain_cause(self, cause, confidence):
        return f"Root cause: {cause.replace('_',' ').title()} (confidence {confidence:.0%})"