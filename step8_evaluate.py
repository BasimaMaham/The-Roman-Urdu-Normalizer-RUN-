from normalizer import normalize_text
import json

with open("eval_data.json", "r", encoding="utf-8") as f:
    eval_data = json.load(f)

# Original OK IDs from human annotation
OK_IDS_ORIGINAL = {1,2,3,4,5,6,12,13,17,18,20,
                   21,23,30,32,35,37,38,
                   43,44,45,49,51,52,54,59,
                   61,71,72,74,75,76,78,80,
                   84,85,86,89,91,94,95,96,98,99,100,
                   105,106,108,116,117,119,
                   121,123,125,130,134,135,138,139,140,
                   141,142,143,144,146,150,154,155,157,159,
                   162,174,175,
                   183,185,189,192,197,200}

SKIP_IDS = {57}

# Sentences that improved from our fixes — manually verified
# Fix 1 (proper nouns) + Fix 2 (English context): IDs that went FIX→OK
FIX1_FIX2_NEWLY_OK = {42, 47, 67, 83, 124, 168, 173, 181, 182}

# Fix 1 removals that were already OK or neutral
FIX1_STILL_OK = {50, 56, 79, 114, 178, 199}

# Fix 3 (morphological): IDs that went FIX→OK — verified manually above
FIX3_NEWLY_OK = {145, 147, 195}

# Add to OK_IDS_FINAL in step8_evaluate.py
FIX4_NEWLY_OK = {7, 14, 38, 40, 60, 66, 68, 82, 99, 101, 103,
                 107, 111, 126, 128, 129, 131, 152, 153, 165, 170, 179}

# Combined final OK set
OK_IDS_FINAL = (OK_IDS_ORIGINAL | 
                FIX1_FIX2_NEWLY_OK | 
                FIX1_STILL_OK | 
                FIX3_NEWLY_OK |
                FIX4_NEWLY_OK)

# Re-normalize all sentences with current pipeline
print("Re-normalizing all 200 sentences with current pipeline...")
for item in eval_data:
    item['output_final'] = normalize_text(item['original'])
    item['changed_final'] = item['original'] != item['output_final']

# Compute metrics
evaluable = [item for item in eval_data if item['id'] not in SKIP_IDS]
changed = [item for item in evaluable if item['changed_final']]

ok_changed = [item for item in changed if item['id'] in OK_IDS_FINAL]
fix_changed = [item for item in changed if item['id'] not in OK_IDS_FINAL]

total_token_changes = 0
correct_token_changes = 0

for item in changed:
    orig_tokens = item['original'].split()
    out_tokens = item['output_final'].split()
    n = sum(1 for o, n in zip(orig_tokens, out_tokens) if o.lower() != n.lower())
    total_token_changes += n
    if item['id'] in OK_IDS_FINAL:
        correct_token_changes += n

sentence_precision = len(ok_changed) / len(changed) if changed else 0
token_precision = correct_token_changes / total_token_changes if total_token_changes else 0

print(f"\n{'='*55}")
print(f"FINAL EVALUATION RESULTS")
print(f"{'='*55}")
print(f"{'Metric':<38} {'V1':>7} {'Final':>7}")
print(f"{'-'*55}")
print(f"{'Sentences evaluated':<38} {'199':>7} {'199':>7}")
print(f"{'Sentences system changed':<38} {200:>7} {len(changed):>7}")
print(f"{'Fully correct (OK)':<38} {'82':>7} {len(ok_changed):>7}")
print(f"{'Had errors (FIX)':<38} {'117':>7} {len(fix_changed):>7}")
print(f"{'Sentence-level precision':<38} {'41.2%':>7} {100*sentence_precision:.1f}%")
print(f"{'Total token changes':<38} {'850':>7} {total_token_changes:>7}")
print(f"{'Correct token changes':<38} {'262':>7} {correct_token_changes:>7}")
print(f"{'Token-level precision':<38} {'30.8%':>7} {100*token_precision:.1f}%")
print(f"{'='*55}")

print(f"\nTotal improvement:")
print(f"  Sentence precision: 41.2% → {100*sentence_precision:.1f}% "
      f"(+{100*sentence_precision-41.2:.1f} pts)")
print(f"  Token precision:    30.8% → {100*token_precision:.1f}% "
      f"(+{100*token_precision-30.8:.1f} pts)")
print(f"\nNew correct sentences breakdown:")
print(f"  Originally correct:              {len(OK_IDS_ORIGINAL - SKIP_IDS)}")
print(f"  Fix 1+2 (proper noun + English): +{len(FIX1_FIX2_NEWLY_OK)}")
print(f"  Fix 1 neutral (removal only):    +{len(FIX1_STILL_OK)}")
print(f"  Fix 3 (morphological):           +{len(FIX3_NEWLY_OK)}")
print(f"  Fix 4 (bad mapping removal):     +{len(FIX4_NEWLY_OK)}")
print(f"  Total OK:                         {len(ok_changed)}")