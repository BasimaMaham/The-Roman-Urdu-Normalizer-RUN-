import json
import re
from normalizer import normalize_text

with open("eval_data.json", "r", encoding="utf-8") as f:
    eval_data = json.load(f)

OK_IDS = {
    1,2,3,4,5,6,7,10,12,13,14,16,17,18,20,21,22,23,24,25,
    30,32,33,35,37,38,40,42,43,44,45,47,49,50,51,52,53,54,55,56,
    59,60,61,62,66,67,68,69,71,72,74,75,76,78,79,80,
    82,83,84,85,86,89,91,93,94,95,96,97,98,99,100,
    101,103,105,106,107,108,109,111,114,115,116,117,118,119,
    120,121,123,124,125,126,128,129,130,131,134,135,136,138,139,140,
    141,142,143,144,145,146,147,150,152,153,154,155,157,159,
    160,162,165,168,170,174,175,179,180,181,182,183,185,
    189,192,195,196,197,199,200,
    15,28,34,64,132,133,137,163,166,169,191,
}
SKIP_IDS = {57}

# Pre-compute RUN gold standard changes (for recall)
run_changes = {}
for item in eval_data:
    if item['id'] in SKIP_IDS: continue
    run_out = normalize_text(item['original'])
    if item['original'] != run_out and item['id'] in OK_IDS:
        pairs = [(o,n) for o,n in zip(item['original'].split(), run_out.split())
                 if o.lower() != n.lower()]
        run_changes[item['id']] = pairs
total_norm = sum(len(v) for v in run_changes.values())

def parse_outputs(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        raw = f.read()
    pattern = r'ID:\s*(\d+)\s*\nOUTPUT:\s*(.+?)(?=\nID:|\Z)'
    matches = re.findall(pattern, raw, re.DOTALL)
    return {int(sid): output.strip() for sid, output in matches}

def evaluate(name, outputs):
    total_changed = ok_changed = fix_changed = 0
    total_tokens = correct_tokens = 0

    for item in eval_data:
        if item['id'] in SKIP_IDS: continue
        if item['id'] not in outputs: continue
        original = item['original']
        out = outputs[item['id']]
        if original == out: continue
        total_changed += 1
        n = sum(1 for o,t in zip(original.split(), out.split())
                if o.lower() != t.lower())
        total_tokens += n
        if item['id'] in OK_IDS:
            ok_changed += 1
            correct_tokens += n
        else:
            fix_changed += 1

    # Recall
    caught = 0
    for item in eval_data:
        if item['id'] not in run_changes: continue
        if item['id'] not in outputs: continue
        sys_pairs = {o.lower(): t.lower() for o,t in
                    zip(item['original'].split(), outputs[item['id']].split())
                    if o.lower() != t.lower()}
        for o,n in run_changes[item['id']]:
            if sys_pairs.get(o.lower()) == n.lower():
                caught += 1

    sp = ok_changed/total_changed if total_changed else 0
    tp = correct_tokens/total_tokens if total_tokens else 0
    recall = 100*caught/total_norm if total_norm else 0

    def f1(p, r):
        if p+r == 0: return 0.0
        return 200*p*r/(100*(p+r))

    f1_val = f1(100*sp, recall)

    return {
        'name': name,
        'sentences_changed': total_changed,
        'ok_changed': ok_changed,
        'fix_changed': fix_changed,
        'sentence_precision': round(100*sp, 1),
        'token_changes': total_tokens,
        'correct_token_changes': correct_tokens,
        'token_precision': round(100*tp, 1),
        'recall': round(recall, 1),
        'f1': round(f1_val, 1),
    }

# Load all outputs
llm_files = {
    'Claude':   'claude_baseline_raw.txt',
    'Gemini':   'gemini_baseline_raw.txt',
    'DeepSeek': 'deepseek_baseline_raw.txt',
}

results = {}
for name, filepath in llm_files.items():
    try:
        outputs = parse_outputs(filepath)
        print(f"Loaded {len(outputs)} outputs from {filepath}")
        results[name] = evaluate(name, outputs)
    except FileNotFoundError:
        print(f"WARNING: {filepath} not found, skipping {name}")

# Also evaluate RUN
run_outputs = {item['id']: normalize_text(item['original']) for item in eval_data}
results['RUN'] = evaluate('RUN (our system)', run_outputs)

# Manual baselines (pre-computed)
manual_results = {
    'No normalization': {'sentence_precision': None, 'recall': None, 'f1': None,
                         'token_precision': None, 'sentences_changed': 0},
    'Baseline 1: Manual rules': {'sentence_precision': 75.1, 'recall': 81.1,
                                  'f1': 78.0, 'token_precision': 63.2,
                                  'sentences_changed': 177},
    'Baseline 2: Edit distance': {'sentence_precision': 72.5, 'recall': 0.0,
                                   'f1': 0.0, 'token_precision': 70.5,
                                   'sentences_changed': 91},
}

# Print detailed per-system stats
print(f"\n{'='*65}")
print(f"DETAILED RESULTS")
print(f"{'='*65}")
for name, r in results.items():
    print(f"\n{name}:")
    print(f"  Sentences changed:     {r['sentences_changed']}")
    print(f"  Correct (OK):          {r['ok_changed']}")
    print(f"  Sentence precision:    {r['sentence_precision']}%")
    print(f"  Token changes:         {r['token_changes']}")
    print(f"  Correct token changes: {r['correct_token_changes']}")
    print(f"  Token precision:       {r['token_precision']}%")
    print(f"  Recall:                {r['recall']}%")
    print(f"  F1:                    {r['f1']}%")

# Print comparison table
print(f"\n{'='*70}")
print(f"COMPLETE COMPARISON TABLE")
print(f"{'='*70}")
print(f"{'System':<30} {'Sent.Prec':>10} {'Tok.Prec':>10} {'Recall':>8} {'F1':>8}")
print(f"{'-'*70}")

# No normalization row
print(f"{'No normalization':<30} {'N/A':>10} {'N/A':>10} {'N/A':>8} {'N/A':>8}")

# Manual baselines
for name, r in manual_results.items():
    if name == 'No normalization': continue
    sp = f"{r['sentence_precision']}%" if r['sentence_precision'] else 'N/A'
    tp = f"{r['token_precision']}%" if r['token_precision'] else 'N/A'
    rc = f"{r['recall']}%" if r['recall'] is not None else 'N/A'
    f1 = f"{r['f1']}%" if r['f1'] is not None else 'N/A'
    print(f"{name:<30} {sp:>10} {tp:>10} {rc:>8} {f1:>8}")

# LLM baselines
llm_order = ['Claude', 'Gemini', 'DeepSeek']
for name in llm_order:
    if name not in results: continue
    r = results[name]
    label = f"Baseline 3: {name}"
    print(f"{label:<30} {r['sentence_precision']:>9.1f}% "
          f"{r['token_precision']:>9.1f}% "
          f"{r['recall']:>7.1f}% "
          f"{r['f1']:>7.1f}%")

# RUN
r = results['RUN']
print(f"{'RUN (our system)':<30} {r['sentence_precision']:>9.1f}% "
      f"{r['token_precision']:>9.1f}% "
      f"{r['recall']:>7.1f}% "
      f"{r['f1']:>7.1f}%")
print(f"{'='*70}")

# Save all results
all_results = {
    'manual_baselines': manual_results,
    'llm_baselines': {k: v for k,v in results.items() if k != 'RUN'},
    'run': results.get('RUN'),
}
with open("all_baseline_results.json","w") as f:
    json.dump(all_results, f, indent=2)
print("\nSaved all_baseline_results.json")