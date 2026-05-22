from normalizer import normalize_text
import json
import time

with open("eval_data.json", "r", encoding="utf-8") as f:
    eval_data = json.load(f)

with open("urdu_vocab_v2.json", "r", encoding="utf-8") as f:
    urdu_vocab = json.load(f)

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

def evaluate(name, normalize_fn):
    total_changed = ok_changed = fix_changed = 0
    total_tokens = correct_tokens = 0
    for item in eval_data:
        if item['id'] in SKIP_IDS:
            continue
        original = item['original']
        output = normalize_fn(original)
        if original == output:
            continue
        total_changed += 1
        n = sum(1 for o,t in zip(original.split(), output.split())
                if o.lower() != t.lower())
        total_tokens += n
        if item['id'] in OK_IDS:
            ok_changed += 1
            correct_tokens += n
        else:
            fix_changed += 1
    sp = ok_changed/total_changed if total_changed else 0
    tp = correct_tokens/total_tokens if total_tokens else 0
    print(f"\n{name}")
    print(f"  Sentences changed:     {total_changed}")
    print(f"  Correct (OK):          {ok_changed}")
    print(f"  Sentence precision:    {100*sp:.1f}%")
    print(f"  Token changes:         {total_tokens}")
    print(f"  Correct token changes: {correct_tokens}")
    print(f"  Token precision:       {100*tp:.1f}%")
    return round(100*sp,1), round(100*tp,1)

# ================================================================
# BASELINE 1 — Manual rules only
# ================================================================
MANUAL_RULES = {
    'nhi':'nahi','ni':'nahi','nhe':'nahi','nhy':'nahi','nahin':'nahi','nai':'nahi',
    'ha':'hai','hy':'hai','hae':'hai',
    'me':'mein','mn':'mein',
    'mai':'main',
    'kia':'kya',
    'ye':'yeh','yh':'yeh',
    'wo':'woh','voh':'woh','vo':'woh',
    'ap':'aap',
    'hm':'hum',
    'or':'aur',
    'to':'toh',
    'say':'se','sey':'se',
    'bi':'bhi',
    'sub':'sab','sb':'sab',
    'aj':'aaj',
    'kl':'kal',
    'phr':'phir','fer':'phir','fir':'phir',
    'boht':'bohat','bht':'bohat','bhot':'bohat','buhat':'bohat',
    'achha':'acha','accha':'acha',
    'thek':'theek','thk':'theek',
    'kr':'kar','kro':'karo','krna':'karna',
    'rha':'raha','rhi':'rahi','rhe':'rahe',
    'pta':'pata',
    'bat':'baat','bt':'baat',
    'blkl':'bilkul',
    'bkwas':'bakwas',
    'yar':'yaar',
    'hmry':'hamaray','hmra':'hamara',
    'mtlb':'matlab',
    'smjh':'samajh',
    'wrna':'warna',
    'ghr':'ghar',
    'srf':'sirf',
    'lkn':'lekin',
    'ziyada':'zyada','ziada':'zyada',
    'sath':'saath',
    'abi':'abhi',
    'ana':'aana',
}

def baseline1(text):
    if not text or not text.strip():
        return text
    tokens = text.split()
    out = []
    for token in tokens:
        pre, suf, core = '', '', token
        while core and not core[0].isalpha():
            pre += core[0]; core = core[1:]
        while core and not core[-1].isalpha():
            suf = core[-1] + suf; core = core[:-1]
        if not core:
            out.append(token); continue
        norm = MANUAL_RULES.get(core.lower(), core)
        out.append(pre + norm + suf)
    return ' '.join(out)

# ================================================================
# BASELINE 2 — Edit distance only (Levenshtein)
# ================================================================
def levenshtein(s1, s2):
    if abs(len(s1)-len(s2)) > 2: return 999
    m, n = len(s1), len(s2)
    dp = list(range(n+1))
    for i in range(1, m+1):
        prev, dp[0] = dp[0], i
        for j in range(1, n+1):
            temp = dp[j]
            dp[j] = prev if s1[i-1]==s2[j-1] else 1+min(prev,dp[j],dp[j-1])
            prev = temp
    return dp[n]

vocab_by_freq = sorted(urdu_vocab.items(), key=lambda x: -x[1])
top_vocab = [w for w,f in vocab_by_freq[:5000]]

def baseline2(text):
    if not text or not text.strip():
        return text
    tokens = text.split()
    out = []
    for token in tokens:
        core = token.lower().strip('.,!?;:\'"')
        if len(core) < 3 or core in urdu_vocab:
            out.append(token); continue
        best, best_d = core, 2
        for candidate in top_vocab:
            if abs(len(candidate)-len(core)) > 2: continue
            d = levenshtein(core, candidate)
            if d < best_d:
                best_d = d; best = candidate
        out.append(best)
    return ' '.join(out)

# ================================================================
# RUN
# ================================================================
print("="*60)
print("BASELINES EVALUATION")
print("="*60)

b1_s, b1_t = evaluate("Baseline 1 — Manual rules only", baseline1)

print("\nRunning Baseline 2 (slow, ~2 min)...")
start = time.time()
b2_s, b2_t = evaluate("Baseline 2 — Edit distance only", baseline2)
print(f"  Finished in {time.time()-start:.0f}s")

run_s, run_t = evaluate("RUN — Our system", normalize_text)

print(f"\n{'='*60}")
print(f"SUMMARY TABLE")
print(f"{'='*60}")
print(f"{'System':<32} {'Sent. Prec.':>12} {'Token Prec.':>12}")
print(f"{'-'*60}")
print(f"{'No normalization':<32} {'N/A':>12} {'N/A':>12}")
print(f"{'Baseline 1: Manual rules':<32} {b1_s:>11.1f}% {b1_t:>11.1f}%")
print(f"{'Baseline 2: Edit distance':<32} {b2_s:>11.1f}% {b2_t:>11.1f}%")
print(f"{'RUN (our system)':<32} {run_s:>11.1f}% {run_t:>11.1f}%")
print(f"{'='*60}")

# Add to baseline_b1_b2.py after the summary table

print(f"\n{'='*60}")
print(f"COVERAGE AND F1 ANALYSIS")
print(f"{'='*60}")

# Count total normalizable tokens in the dataset
# (tokens that the gold standard says should be normalized)
# We approximate this as: tokens changed by RUN in OK sentences
# (since RUN + human annotation defines what's normalizable)

def count_coverage(normalize_fn, eval_data, ok_ids, skip_ids):
    tokens_changed = 0
    tokens_correct = 0
    tokens_missed = 0

    # For each OK sentence, compare what system changed vs what RUN changed
    run_changes = {}
    for item in eval_data:
        if item['id'] in skip_ids: continue
        original = item['original']
        run_out = normalize_text(original)
        if original != run_out and item['id'] in ok_ids:
            pairs = [(o,n) for o,n in zip(original.split(), run_out.split())
                     if o.lower() != n.lower()]
            run_changes[item['id']] = pairs

    # Total normalizable token changes (defined by RUN on OK sentences)
    total_normalizable = sum(len(v) for v in run_changes.values())

    # What this system catches
    caught = 0
    for item in eval_data:
        if item['id'] not in run_changes: continue
        original = item['original']
        sys_out = normalize_fn(original)
        sys_pairs = {o.lower(): n.lower() for o,n in
                     zip(original.split(), sys_out.split())
                     if o.lower() != n.lower()}
        for o, n in run_changes[item['id']]:
            if sys_pairs.get(o.lower()) == n.lower():
                caught += 1

    recall = caught / total_normalizable if total_normalizable else 0
    return total_normalizable, caught, round(100*recall, 1)

total_norm, b1_caught, b1_recall = count_coverage(baseline1, eval_data, OK_IDS, SKIP_IDS)
_, b2_caught, b2_recall = count_coverage(baseline2, eval_data, OK_IDS, SKIP_IDS)
_, run_caught, run_recall = count_coverage(normalize_text, eval_data, OK_IDS, SKIP_IDS)

print(f"Total normalizable token changes: {total_norm}")
print(f"\n{'System':<32} {'Recall':>8}")
print(f"{'-'*42}")
print(f"{'Baseline 1: Manual rules':<32} {b1_recall:>7.1f}%")
print(f"{'Baseline 2: Edit distance':<32} {b2_recall:>7.1f}%")
print(f"{'RUN (our system)':<32} {run_recall:>7.1f}%")

# F1 scores
def f1(precision, recall):
    p, r = precision/100, recall/100
    if p+r == 0: return 0
    return round(200*p*r/(p+r), 1)

print(f"\n{'System':<32} {'Prec.':>8} {'Recall':>8} {'F1':>8}")
print(f"{'-'*58}")
print(f"{'Baseline 1: Manual rules':<32} {b1_s:>7.1f}% {b1_recall:>7.1f}% {f1(b1_s,b1_recall):>7.1f}%")
print(f"{'Baseline 2: Edit distance':<32} {b2_s:>7.1f}% {b2_recall:>7.1f}% {f1(b2_s,b2_recall):>7.1f}%")
print(f"{'RUN (our system)':<32} {run_s:>7.1f}% {run_recall:>7.1f}% {f1(run_s,run_recall):>7.1f}%")
print(f"{'='*58}")

with open("baseline_b1_b2_results.json","w") as f:
    json.dump({
        'baseline1':{'sentence_precision':b1_s,'token_precision':b1_t},
        'baseline2':{'sentence_precision':b2_s,'token_precision':b2_t},
        'run':{'sentence_precision':run_s,'token_precision':run_t},
    }, f, indent=2)
print("\nSaved baseline_b1_b2_results.json")