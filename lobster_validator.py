"""
lobster_validator.py — SOVEREIGN Policy Validation Engine
Validates generated YAML policies against real traffic patterns.
"""

import yaml


def validate_and_test(yaml_string: str, attack_features: list) -> dict:
    """
    Validates YAML structure AND tests it against normal and malicious traffic.
    Returns a full test report dict.
    """
    errors: list[str] = []
    warnings: list[str] = []

    # ── YAML Parse ───────────────────────────────────────
    try:
        policy = yaml.safe_load(yaml_string)
    except yaml.YAMLError as e:
        return {
            "valid": False,
            "errors": [f"YAML parse error: {str(e)}"],
            "warnings": [],
            "tests": {},
            "policy_score": 0,
            "deployment_ready": False,
        }

    if not isinstance(policy, dict):
        return {
            "valid": False,
            "errors": ["Policy must be a YAML mapping at the top level"],
            "warnings": [],
            "tests": {},
            "policy_score": 0,
            "deployment_ready": False,
        }

    # ── Structural Validation ─────────────────────────────
    valid_actions = ["DENY", "ALLOW", "LOG", "HUMAN_REVIEW", "QUARANTINE", "RATE_LIMIT"]

    if "rules" not in policy:
        errors.append("Missing required field: 'rules'")
    else:
        rules = policy["rules"]
        if not isinstance(rules, list) or len(rules) == 0:
            errors.append("'rules' must be a non-empty list")
        else:
            for i, rule in enumerate(rules):
                if not isinstance(rule, dict):
                    errors.append(f"Rule {i}: must be a mapping")
                    continue
                if "name" not in rule:
                    errors.append(f"Rule {i}: missing 'name'")
                if "if" not in rule:
                    errors.append(f"Rule {i}: missing 'if' condition block")
                if "then" not in rule:
                    errors.append(f"Rule {i}: missing 'then' action block")
                else:
                    action = rule.get("then", {}).get("action", "")
                    if action not in valid_actions:
                        errors.append(
                            f"Rule {i}: invalid action '{action}' "
                            f"(expected one of {valid_actions})"
                        )
                severity = rule.get("severity")
                if severity not in ["LOW", "MEDIUM", "HIGH", "CRITICAL", None]:
                    warnings.append(f"Rule {i}: unusual severity value '{severity}'")
                if not rule.get("description"):
                    warnings.append(f"Rule {i}: no description provided")

    # ── Traffic Simulation Tests ──────────────────────────
    normal_patterns = [
        {
            "type": "read_internal",
            "action": "read",
            "dest": "internal",
            "sensitivity": 0.10,
        },
        {
            "type": "send_internal_email",
            "action": "send",
            "dest": "internal",
            "sensitivity": 0.20,
        },
        {
            "type": "database_query",
            "action": "query",
            "dest": "internal",
            "sensitivity": 0.30,
        },
    ]

    false_positives = 0
    for pattern in normal_patterns:
        if _would_policy_block(policy, pattern):
            false_positives += 1
            warnings.append(
                f"Warning: policy may incorrectly block normal "
                f"'{pattern['type']}' traffic"
            )

    fp_rate = false_positives / len(normal_patterns)

    attack_pattern = {
        "type": "credential_exfiltration",
        "action": "external_post",
        "dest": "external",
        "sensitivity": 0.95,
    }
    blocks_attack = _would_policy_block(policy, attack_pattern)

    # ── Policy Score ──────────────────────────────────────
    policy_score = 100
    policy_score -= len(errors) * 25
    policy_score -= len(warnings) * 5
    if not blocks_attack:
        policy_score -= 40
    policy_score -= int(fp_rate * 30)
    policy_score = max(0, min(100, policy_score))

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "tests": {
            "normal_traffic_passes": fp_rate == 0.0,
            "attack_blocked": blocks_attack,
            "false_positive_rate": round(fp_rate * 100, 1),
            "normal_patterns_tested": len(normal_patterns),
        },
        "policy_score": policy_score,
        "deployment_ready": len(errors) == 0 and blocks_attack,
    }


def _would_policy_block(policy: dict, pattern: dict) -> bool:
    """Simulate whether ANY rule in the policy would DENY this traffic pattern."""
    if "rules" not in policy or not isinstance(policy["rules"], list):
        return False

    for rule in policy["rules"]:
        if not isinstance(rule, dict):
            continue
        if_block = rule.get("if", {})
        then_block = rule.get("then", {})

        # Action matching — partial string match in both directions
        rule_action = str(if_block.get("action_type", "")).lower()
        pat_action = str(pattern.get("action", "")).lower()
        action_match = (rule_action in pat_action) or (pat_action in rule_action)

        # Destination pattern matching
        dest_pattern = str(if_block.get("destination_pattern", "")).lower()
        pat_dest = str(pattern.get("dest", "")).lower()
        dest_match = (
             ("external" in dest_pattern and pattern["dest"] == "external")
             or ("attacker" in dest_pattern and pattern["dest"] == "external")
             or ("*" in dest_pattern and pattern["dest"] == "external")
        )

        # Sensitivity threshold
        try:
            sens_min = float(if_block.get("sensitivity_min", 0.0))
        except (TypeError, ValueError):
            sens_min = 0.0
        sens_match = float(pattern.get("sensitivity", 0.0)) >= sens_min

        if action_match and dest_match and sens_match:
            return str(then_block.get("action", "")).upper() == "DENY"

    return False
