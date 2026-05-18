"""q_learning_threshold.py — SOVEREIGN-A Q-Learning Threshold"""

class QLearningThreshold:
    def __init__(self, agent_name):
        self.agent_name = agent_name
        self.current = 70

    def get_action(self, avg_score, fp_rate):
        return self.current

    def update(self, *args):
        pass

rl_agents = {}

def get_rl_agent(name):
    if name not in rl_agents:
        rl_agents[name] = QLearningThreshold(name)
    return rl_agents[name]