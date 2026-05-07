import json

# Results from manual annotation
OK_IDS = {1,2,3,4,5,6,12,13,17,18,20,  # 1-20
           21,23,30,32,35,37,           # 21-40
           43,44,45,49,51,52,54,59,     # 41-60
           61,71,72,74,75,76,78,80,     # 61-80
           84,85,86,89,91,94,95,96,98,100, # 81-100
           105,106,107,108,116,117,119,     # 101-120
           121,123,125,130,134,135,138,139,140, # 121-140
           141,142,143,144,146,150,154,155,157,159, # 141-160
           162,163,166,169,174,175,                 # 161-180
           183,185,189,191,192,197,200}     # 181-200

FIX_IDS = set(range(1,201)) - OK_IDS - {57}
SKIP_IDS = {57}

# Load eval data
with open("eval_data.json", "r", encoding="utf-8") as f:
    eval_data = json.load(f)

# Categorize sentences
changed = [item for item in eval_data if item['changed']]
unchanged = [item for item in eval_data if not item['changed']]

print(f"Total sentences: {len(eval_data)}")
print(f"Sentences where system made changes: {len(changed)}")
print(f"Sentences where system made no changes: {len(unchanged)}")
print(f"Skipped (too noisy): {len(SKIP_IDS)}")

# Among sentences where system made changes:
# OK = system was correct
# FIX = system made at least one error
ok_changed = [i for i in OK_IDS if eval_data[i-1]['changed']]
fix_changed = [i for i in FIX_IDS if eval_data[i-1]['changed']]

print(f"\nAmong {len(changed)} sentences where system made changes:")
print(f"  Fully correct (OK): {len(ok_changed)}")
print(f"  Had errors (FIX):   {len(fix_changed)}")

# Sentence-level precision
precision = len(ok_changed) / (len(ok_changed) + len(fix_changed))
print(f"\nSentence-level precision: {precision:.3f} ({100*precision:.1f}%)")
print(f"  = when system changed something, it was fully right {100*precision:.1f}% of the time")

# Now compute token-level WER/CER
# We need to compare system output to corrected output for FIX sentences
# For OK sentences: system output = correct
# For FIX sentences: we use the corrected versions from annotation

# Load corrected versions (we'll add them manually below)
# For now compute upper/lower bounds

total_changes = sum(
    len([1 for o,n in zip(item['original'].split(), 
                           item['system_output'].split()) 
         if o.lower() != n.lower()])
    for item in eval_data if item['changed']
)

ok_changes = sum(
    len([1 for o,n in zip(eval_data[i-1]['original'].split(),
                           eval_data[i-1]['system_output'].split())
         if o.lower() != n.lower()])
    for i in ok_changed
)

print(f"\nToken-level analysis:")
print(f"  Total token changes made: {total_changes}")
print(f"  Token changes in correct sentences: {ok_changes}")
print(f"  Estimated correct changes: {ok_changes}")
print(f"  Token-level precision (estimate): {ok_changes/total_changes:.3f} ({100*ok_changes/total_changes:.1f}%)")

# Error categories from annotation
print(f"\nError categories identified:")
print(f"  1. Proper noun mangling (pakistan→pakistanio, etc)")
print(f"  2. English context interference (to→toh in English sentences)")  
print(f"  3. Gender form confusion (masculine/feminine)")
print(f"  4. Number confusion (singular/plural)")
print(f"  5. Tense confusion (past/present/future)")
print(f"  6. Semantic collision (different words with similar spelling)")
print(f"\nThese categories will form Section 5 (Error Analysis) of your paper.")

# Code-switch accuracy
english_frozen_correctly = sum(
    1 for item in eval_data
    if item['id'] in OK_IDS
    and any(w in item['original'].lower().split() 
            for w in ['the','and','but','for','to','is','in','on','at',
                      'with','from','have','this','that','are','was'])
)
print(f"\nCode-switch protection working in {english_frozen_correctly} OK sentences")