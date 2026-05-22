import json
import random
from normalizer import normalize_text

# Load all sentences
with open("cleaned_sentences.txt", "r", encoding="utf-8") as f:
    all_sentences = [l.strip() for l in f if l.strip()]

# Load normalization dict to find sentences with variants
with open("normalization_dict_final.json", "r", encoding="utf-8") as f:
    norm_dict = json.load(f)

# Load already-used sentence IDs from eval_data.json
with open("eval_data.json", "r", encoding="utf-8") as f:
    eval_data = json.load(f)

used_sentences = set(item['original'] for item in eval_data)

# Find fresh candidates — sentences with 2+ variants, not used before
fresh_candidates = []
for sent in all_sentences:
    if sent in used_sentences:
        continue
    tokens = sent.split()
    variants = [t for t in tokens if t in norm_dict and norm_dict[t] != t]
    if len(variants) >= 2:
        fresh_candidates.append((sent, variants))

print(f"Fresh candidate sentences: {len(fresh_candidates)}")

# Sample 200
random.seed(100)  # different seed from original (which used 42)
selected = random.sample(fresh_candidates, 200)

# Normalize all
print("Normalizing...")
round1_data = []
for i, (sent, variants) in enumerate(selected):
    normalized = normalize_text(sent)
    round1_data.append({
        "id": i + 1,
        "original": sent,
        "system_output": normalized,
        "changed": sent != normalized,
        "variants_detected": variants,
        "judgment": "",
        "corrected": ""
    })

# Save annotation sheet
with open("round1_eval_sheet.txt", "w", encoding="utf-8") as f:
    f.write("ROUND 1 DEVELOPMENT SET — Roman Urdu Normalizer\n")
    f.write("="*70 + "\n")
    f.write("INSTRUCTIONS:\n")
    f.write("  OK   = normalized output is correct\n")
    f.write("  FIX  = wrong, write correct version on CORRECTED line\n")
    f.write("  SKIP = sentence too noisy to judge\n")
    f.write("="*70 + "\n\n")

    changed_count = 0
    for item in round1_data:
        f.write(f"ID: {item['id']}\n")
        f.write(f"ORIGINAL:   {item['original']}\n")
        f.write(f"NORMALIZED: {item['system_output']}\n")
        if item['changed']:
            changed_count += 1
            orig_tokens = item['original'].split()
            norm_tokens = item['system_output'].split()
            changes = [f"{o}→{n}" for o, n in
                      zip(orig_tokens, norm_tokens)
                      if o.lower() != n.lower()]
            f.write(f"CHANGES:    {', '.join(changes)}\n")
        else:
            f.write(f"CHANGES:    (none)\n")
        f.write(f"JUDGMENT:   \n")
        f.write(f"CORRECTED:  \n\n")

print(f"Total sentences: {len(round1_data)}")
print(f"Sentences with changes: {changed_count}")
print(f"Saved round1_eval_sheet.txt")

with open("round1_eval_data.json", "w", encoding="utf-8") as f:
    json.dump(round1_data, f, ensure_ascii=False, indent=2)
print("Saved round1_eval_data.json")

# Preview first 5
print("\nPREVIEW (first 5):")
for item in round1_data[:5]:
    print(f"\nID {item['id']}:")
    print(f"  ORIG: {item['original']}")
    print(f"  NORM: {item['system_output']}")
    changes = [f"{o}→{n}" for o, n in
               zip(item['original'].split(), item['system_output'].split())
               if o.lower() != n.lower()]
    if changes:
        print(f"  DIFF: {', '.join(changes)}")