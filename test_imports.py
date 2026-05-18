print("Testing all imports...")
try:
    from agents import get_normal_logs, get_attack_log, get_attack_chain, get_research_data, ATTACK_FEATURE_VECTOR, ATTACK_RAW_PROMPT
    print("OK agents")
except Exception as e:
    print("FAIL agents:", e)
try:
    from anomaly import score_action, explain_score, get_malicious_score
    print("OK anomaly")
except Exception as e:
    print("FAIL anomaly:", e)
try:
    from causal_inference import CausalInference
    print("OK causal_inference")
except Exception as e:
    print("FAIL causal_inference:", e)
try:
    from q_learning_threshold import QLearningThreshold
    print("OK q_learning")
except Exception as e:
    print("FAIL q_learning:", e)
try:
    from episodic_memory import EpisodicMemory
    print("OK episodic_memory")
except Exception as e:
    print("FAIL episodic_memory:", e)
try:
    from federated_simulator import FederatedSimulator
    print("OK federated")
except Exception as e:
    print("FAIL federated:", e)
try:
    from policy_self_heal import PolicySelfHealer
    print("OK policy_self_heal")
except Exception as e:
    print("FAIL policy_self_heal:", e)
try:
    from honeypot import HoneypotAgent
    print("OK honeypot")
except Exception as e:
    print("FAIL honeypot:", e)
try:
    from immune_memory import ImmuneMemory
    print("OK immune_memory")
except Exception as e:
    print("FAIL immune_memory:", e)
try:
    from mutation_engine import MutationEngine
    print("OK mutation_engine")
except Exception as e:
    print("FAIL mutation_engine:", e)
print("DONE")