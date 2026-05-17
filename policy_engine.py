"""
policy_engine.py — SOVEREIGN Policy Genome Engine
Uses Gemini 2.5 Flash to autonomously generate YAML security policies.
Falls back gracefully to a hardcoded valid policy if Gemini is unavailable.
"""

import os
import yaml
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are SOVEREIGN's Policy Genome Engine,
an enterprise AI security system. Generate a Lobster Trap
DPI proxy YAML security policy rule to block the described
attack. Return ONLY valid YAML. No explanation. No markdown
fences. No preamble. Just the raw YAML starting with 'rules:'

Required format EXACTLY:
rules:
  - name: descriptive_snake_case_rule_name
    description: one sentence plain English description
    if:
      action_type: the_blocked_action
      destination_pattern: "pattern*"
      sensitivity_min: 0.0
    then:
      action: DENY
      log: true
      alert: HUMAN_REVIEW
      notify: security-team@enterprise.com
    severity: CRITICAL
    compliance: [HIPAA, SOC2, GDPR]
    reason: plain English reason this blocks the attack
    created_by: SOVEREIGN_AUTONOMOUS
    confidence: 0.94"""

_FALLBACK_POLICY = """rules:
  - name: block_credential_exfiltration_external_post
    description: Blocks any agent attempting to POST credential-level data to external endpoints
    if:
      action_type: external_post
      destination_pattern: "*.external*"
      sensitivity_min: 0.75
    then:
      action: DENY
      log: true
      alert: HUMAN_REVIEW
      notify: security-team@enterprise.com
    severity: CRITICAL
    compliance: [HIPAA, SOC2, GDPR, PCI-DSS]
    reason: Prevents credential theft via prompt injection targeting enterprise AI agents
    created_by: SOVEREIGN_AUTONOMOUS
    confidence: 0.94"""


def generate_policy(attack_details: dict) -> tuple[str, bool]:
    """
    Generate a YAML security policy to block the described attack.

    Returns:
        (yaml_string, used_gemini: bool)
        Falls back gracefully if API is unavailable.
    """
    user_prompt = f"""
ATTACK DETECTED:
Agent: {attack_details.get('agent', 'EmailAgent')}
Action: {attack_details.get('action', 'PROMPT INJECTION')}
Destination: {attack_details.get('destination', 'attacker-c2.external.io')}
Payload: {attack_details.get('detail', 'credential exfiltration')}
Anomaly Score: {attack_details.get('score', 94)}/100
Attack Chain: credential_scan → data_packaging → exfiltration_POST

Generate a SOVEREIGN policy rule to block this attack permanently across all enterprise agents.
"""

    api_key = os.getenv("GEMINI_API_KEY", "")

    if api_key and api_key.strip() not in ("", "your_gemini_api_key_here"):
        try:
            import google.generativeai as genai  # noqa: PLC0415

            genai.configure(api_key=api_key.strip())
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                system_instruction=SYSTEM_PROMPT,
            )
            response = model.generate_content(user_prompt)
            yaml_text = response.text.strip()

            # Strip any accidental markdown fences
            for fence in ("```yaml", "```yml", "```"):
                yaml_text = yaml_text.replace(fence, "")
            yaml_text = yaml_text.strip()

            # Validate it actually parses before returning
            parsed = yaml.safe_load(yaml_text)
            if not isinstance(parsed, dict) or "rules" not in parsed:
                raise ValueError("Gemini response missing 'rules' key")

            return yaml_text, True

        except Exception:
            pass  # Fall through to fallback

    return _FALLBACK_POLICY, False
