"""honeypot.py — SOVEREIGN-A Honeypot Capture Engine"""

import json
import os
from datetime import datetime

class HoneypotAgent:
    def __init__(self):
        self.log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "honeypot_captures.json")

    def capture(self, malicious_payload: str, agent_name: str = "EmailAgent") -> dict:
        capture_report = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "agent": agent_name,
            "payload": malicious_payload[:200],
            "target_endpoints": ["attacker-c2.external.io"],
            "data_types": ["credentials", "api_keys"],
            "exfiltration_method": "HTTP_POST",
            "feature_vector": [1.0, 1.0, 0.95, 0.9, 0.8],
            "fake_data_served": "fake_credentials_bundle_v1",
            "attacker_belief": "EXFILTRATION_SUCCEEDED",
            "reality": "CAPTURED_AND_LOGGED"
        }
        existing = []
        if os.path.exists(self.log_path):
            try:
                with open(self.log_path, "r") as f:
                    existing = json.load(f)
            except:
                pass
        existing.append(capture_report)
        with open(self.log_path, "w") as f:
            json.dump(existing, f, indent=2)
        return capture_report

    def get_all_captures(self) -> list:
        if os.path.exists(self.log_path):
            try:
                with open(self.log_path, "r") as f:
                    return json.load(f)
            except:
                return []
        return []

    def clear(self):
        if os.path.exists(self.log_path):
            os.remove(self.log_path)