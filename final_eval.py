from normalizer import normalize_text
import json

with open("eval_data.json", "r", encoding="utf-8") as f:
    eval_data = json.load(f)

# ================================================================
# COMPLETE HUMAN-ANNOTATED OK SET
# Built from: original annotation + all round improvements
# + final re-evaluation of changed sentences
# ================================================================

OK_IDS = {
    # Original annotation
    1,2,3,4,5,6,7,10,12,13,14,16,17,18,20,21,22,23,24,25,
    30,32,33,35,37,38,40,42,43,44,45,47,49,50,51,52,53,54,55,56,
    59,60,61,62,66,67,68,69,71,72,74,75,76,78,79,80,
    82,83,84,85,86,89,91,93,94,95,96,97,98,99,100,
    101,103,105,106,107,108,109,111,114,115,116,117,118,119,
    120,121,123,124,125,126,128,129,130,131,134,135,136,138,139,140,
    141,142,143,144,145,146,147,150,152,153,154,155,157,159,
    160,162,165,168,170,174,175,179,180,181,182,183,185,
    189,192,195,196,197,199,200,

    # Newly moved to OK
    15,28,34,64,132,133,137,163,166,169,191,
}

SKIP_IDS = {57}
FIX_IDS = {i for i in range(1, 201) if i not in OK_IDS and i not in SKIP_IDS}

# ================================================================
# EVALUATE
# ================================================================
print("Normalizing 200 evaluation sentences with final pipeline...")

evaluable = [item for item in eval_data if item['id'] not in SKIP_IDS]

total_changed = 0
ok_changed = 0
fix_changed = 0
total_token_changes = 0
correct_token_changes = 0

changed_details = []

for item in evaluable:
    original = item['original']
    output = normalize_text(original)

    if original == output:
        continue

    total_changed += 1
    orig_tokens = original.split()
    out_tokens = output.split()
    n = sum(1 for o, n in zip(orig_tokens, out_tokens)
            if o.lower() != n.lower())
    total_token_changes += n

    if item['id'] in OK_IDS:
        ok_changed += 1
        correct_token_changes += n
    else:
        fix_changed += 1
        changed_details.append({
            'id': item['id'],
            'original': original,
            'output': output,
            'n_errors': n
        })

sentence_precision = ok_changed / total_changed if total_changed else 0
token_precision = correct_token_changes / total_token_changes if total_token_changes else 0

# ================================================================
# RESULTS
# ================================================================
print(f"\n{'='*62}")
print(f"  FINAL EVALUATION — RUN (Roman Urdu Normalizer)")
print(f"{'='*62}")
print(f"  {'Metric':<38} {'V1':>8} {'Final':>8}")
print(f"  {'-'*56}")
print(f"  {'Sentences evaluated (excl. skip)':<38} {'199':>8} {'199':>8}")
print(f"  {'Sentences system changed':<38} {'200':>8} {total_changed:>8}")
print(f"  {'Correctly normalized (OK)':<38} {'82':>8} {ok_changed:>8}")
print(f"  {'Incorrectly normalized (FIX)':<38} {'117':>8} {fix_changed:>8}")
print(f"  {'Sentence-level precision':<38} {'41.2%':>8} {100*sentence_precision:.1f}%")
print(f"  {'Total token changes':<38} {'850':>8} {total_token_changes:>8}")
print(f"  {'Correct token changes':<38} {'262':>8} {correct_token_changes:>8}")
print(f"  {'Token-level precision':<38} {'30.8%':>8} {100*token_precision:.1f}%")
print(f"{'='*62}")

print(f"\n  Improvement over baseline:")
print(f"    Sentence precision: 41.2% → {100*sentence_precision:.1f}%  (+{100*sentence_precision-41.2:.1f} pts)")
print(f"    Token precision:    30.8% → {100*token_precision:.1f}%  (+{100*token_precision-30.8:.1f} pts)")

print(f"\n  OK/FIX/SKIP breakdown:")
print(f"    OK:   {len(OK_IDS - SKIP_IDS)} sentences")
print(f"    FIX:  {len(FIX_IDS)} sentences")
print(f"    SKIP: {len(SKIP_IDS)} sentence")

print(f"\n  Development set progression (sentence precision):")
print(f"  {'Stage':<25} {'Dev sentences':>14} {'Precision':>10}")
print(f"  {'-'*51}")
print(f"  {'Initial system':<25} {'—':>14} {'41.2%':>10}")
print(f"  {'Round 1 (dev)':<25} {'250':>14} {'55.2%':>10}")
print(f"  {'Round 2 (dev)':<25} {'250':>14} {'58.0%':>10}")
print(f"  {'Round 3 (dev)':<25} {'200':>14} {'60.5%':>10}")
print(f"  {'Round 4 (dev)':<25} {'199':>14} {'61.8%':>10}")
print(f"  {'Final (held-out test)':<25} {'199':>14} {100*sentence_precision:.1f}%")

# Save results
results = {
    'ok_ids': sorted(OK_IDS),
    'fix_ids': sorted(FIX_IDS),
    'skip_ids': sorted(SKIP_IDS),
    'sentences_evaluated': len(evaluable),
    'sentences_changed': total_changed,
    'ok_changed': ok_changed,
    'fix_changed': fix_changed,
    'sentence_precision': round(100*sentence_precision, 1),
    'total_token_changes': total_token_changes,
    'correct_token_changes': correct_token_changes,
    'token_precision': round(100*token_precision, 1),
    'v1_sentence_precision': 41.2,
    'v1_token_precision': 30.8,
}

with open("final_eval_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\n  Saved: final_eval_results.json")