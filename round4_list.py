import json
import random
from normalizer import normalize_text

with open("cleaned_sentences.txt", "r", encoding="utf-8") as f:
    all_sentences = [l.strip() for l in f if l.strip()]

with open("normalization_dict_final.json", "r", encoding="utf-8") as f:
    norm_dict = json.load(f)

used_files = [
    "eval_data.json",
    "round1_eval_data.json",
    "round2_eval_data.json",
    "round3_eval_data.json",
]
used = set()
for fname in used_files:
    try:
        with open(fname, "r", encoding="utf-8") as f:
            used.update(item['original'] for item in json.load(f))
    except FileNotFoundError:
        print(f"Warning: {fname} not found, skipping")

fresh = []
for sent in all_sentences:
    if sent in used:
        continue
    tokens = sent.split()
    variants = [t for t in tokens if t in norm_dict and norm_dict[t] != t]
    if len(variants) >= 2:
        fresh.append((sent, variants))

print(f"Fresh candidates: {len(fresh)}")
random.seed(400)
selected = random.sample(fresh, 200)

print("Normalizing...")
data = []
for i, (sent, variants) in enumerate(selected):
    normalized = normalize_text(sent)
    data.append({
        "id": i+1, "original": sent,
        "system_output": normalized,
        "changed": sent != normalized,
        "variants_detected": variants,
        "judgment": "", "corrected": ""
    })

with open("round4_eval_sheet.txt", "w", encoding="utf-8") as f:
    f.write("ROUND 4 DEVELOPMENT SET — Roman Urdu Normalizer\n")
    f.write("="*70 + "\n")
    f.write("  OK=correct  FIX=wrong  SKIP=too noisy\n")
    f.write("="*70 + "\n\n")
    for item in data:
        f.write(f"ID: {item['id']}\n")
        f.write(f"ORIGINAL:   {item['original']}\n")
        f.write(f"NORMALIZED: {item['system_output']}\n")
        if item['changed']:
            changes = [f"{o}→{n}" for o,n in
                zip(item['original'].split(), item['system_output'].split())
                if o.lower() != n.lower()]
            f.write(f"CHANGES:    {', '.join(changes)}\n")
        else:
            f.write(f"CHANGES:    (none)\n")
        f.write(f"JUDGMENT:   \n")
        f.write(f"CORRECTED:  \n\n")

with open("round4_eval_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

changed = sum(1 for item in data if item['changed'])
print(f"Total: {len(data)} | Changed: {changed}")
print("Saved round4_eval_sheet.txt and round4_eval_data.json")