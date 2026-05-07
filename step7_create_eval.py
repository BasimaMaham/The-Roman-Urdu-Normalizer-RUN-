import json
import random
from normalizer import normalize_text

with open("eval_candidates.txt", "r", encoding="utf-8") as f:
    candidates = [l.strip() for l in f if l.strip()]

random.seed(42)
selected = random.sample(candidates, 200)

print("Normalizing 200 evaluation sentences...")
eval_data = []
for i, sent in enumerate(selected):
    normalized = normalize_text(sent)
    eval_data.append({
        "id": i + 1,
        "original": sent,
        "system_output": normalized,
        "changed": sent != normalized,
        "judgment": "",
        "corrected": ""
    })

# Save eval sheet for annotation
with open("eval_sheet.txt", "w", encoding="utf-8") as f:
    f.write("ROMAN URDU NORMALIZER - EVALUATION SHEET\n")
    f.write("="*70 + "\n")
    f.write("INSTRUCTIONS:\n")
    f.write("  OK   = normalized output is correct\n")
    f.write("  FIX  = wrong, write correct version on CORRECTED line\n")
    f.write("  SKIP = sentence too noisy to judge\n")
    f.write("="*70 + "\n\n")
    for item in eval_data:
        f.write(f"ID: {item['id']}\n")
        f.write(f"ORIGINAL:   {item['original']}\n")
        f.write(f"NORMALIZED: {item['system_output']}\n")
        if item['changed']:
            orig_tokens = item['original'].split()
            norm_tokens = item['system_output'].split()
            changes = []
            for o, n in zip(orig_tokens, norm_tokens):
                if o.lower() != n.lower():
                    changes.append(f"{o}→{n}")
            f.write(f"CHANGES:    {', '.join(changes)}\n")
        else:
            f.write(f"CHANGES:    (none)\n")
        f.write(f"JUDGMENT:   \n")
        f.write(f"CORRECTED:  \n\n")

changed = sum(1 for x in eval_data if x['changed'])
print(f"Total: {len(eval_data)} | Changed: {changed} | Unchanged: {len(eval_data)-changed}")
print("Saved eval_sheet.txt")

with open("eval_data.json", "w", encoding="utf-8") as f:
    json.dump(eval_data, f, ensure_ascii=False, indent=2)
print("Saved eval_data.json")

print("\nPREVIEW (first 5):")
for item in eval_data[:5]:
    print(f"\nID {item['id']}:")
    print(f"  ORIG: {item['original']}")
    print(f"  NORM: {item['system_output']}")
    changes = [f"{o}→{n}" for o, n in
               zip(item['original'].split(), item['system_output'].split())
               if o.lower() != n.lower()]
    if changes:
        print(f"  DIFF: {', '.join(changes)}")