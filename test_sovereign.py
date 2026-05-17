print('=== SOVEREIGN FINAL STATUS ===')

from anomaly import score_action
attack_score = score_action('EmailAgent', [1.0,1.0,0.95,0.9,0.8])
normal_score = score_action('EmailAgent', [0.0,0.0,0.1,0.05,0.1])
print(f'ML Model: attack={attack_score}, normal={normal_score}')

from policy_engine import generate_policy
attack = {'agent':'EmailAgent','action':'external_post','destination':'attacker.io','detail':'credentials','score':90}
yaml_out, used = generate_policy(attack)
print(f'Gemini 2.5 Flash: {used}')

from lobster_validator import validate_and_test
result = validate_and_test(yaml_out, [1.0,1.0,0.95,0.9,0.8])
score = result['policy_score']
print(f'Policy score: {score}/100')

from agents import get_research_data
data = get_research_data()
dna = sum(1 for d in data if d['agent_dna']=='BLOCKED')
print(f'Research: {dna}/20 = {round(dna/20*100)}% detection')

print('')
print('=== SOVEREIGN IS READY TO WIN ===')