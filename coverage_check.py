from normalizer import normalize_text
import json

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

MANUAL_RULES = {
    'nhi':'nahi','ni':'nahi','nhe':'nahi','nhy':'nahi','nahin':'nahi','nai':'nahi',
    'ha':'hai','hy':'hai','hae':'hai',
    'me':'mein','mn':'mein','mai':'main',
    'kia':'kya','ye':'yeh','yh':'yeh',
    'wo':'woh','voh':'woh','vo':'woh',
    'ap':'aap','hm':'hum','or':'aur','to':'toh',
    'say':'se','sey':'se','bi':'bhi',
    'sub':'sab','sb':'sab','aj':'aaj','kl':'kal',
    'phr':'phir','fer':'phir','fir':'phir',
    'boht':'bohat','bht':'bohat','bhot':'bohat','buhat':'bohat',
    'achha':'acha','accha':'acha','thek':'theek','thk':'theek',
    'kr':'kar','kro':'karo','krna':'karna',
    'rha':'raha','rhi':'rahi','rhe':'rahe',
    'pta':'pata','bat':'baat','bt':'baat',
    'blkl':'bilkul','bkwas':'bakwas','yar':'yaar',
    'hmry':'hamaray','hmra':'hamara','mtlb':'matlab',
    'smjh':'samajh','wrna':'warna','ghr':'ghar',
    'srf':'sirf','lkn':'lekin',
    'ziyada':'zyada','ziada':'zyada',
    'sath':'saath','abi':'abhi','ana':'aana',
}

def baseline1(text):
    if not text or not text.strip(): return text
    tokens = text.split()
    out = []
    for token in tokens:
        pre, suf, core = '', '', token
        while core and not core[0].isalpha():
            pre += core[0]; core = core[1:]
        while core and not core[-1].isalpha():
            suf = core[-1] + suf; core = core[:-1]
        if not core: out.append(token); continue
        norm = MANUAL_RULES.get(core.lower(), core)
        out.append(pre + norm + suf)
    return ' '.join(out)

# Compare which sentences each system gets right
run_ok = set()
b1_ok = set()
run_only = []   # RUN correct, B1 wrong
b1_only = []    # B1 correct, RUN wrong
both_ok = []    # both correct
both_fix = []   # both wrong

for item in eval_data:
    if item['id'] in SKIP_IDS: continue
    original = item['original']
    run_out = normalize_text(original)
    b1_out = baseline1(original)

    run_changed = original != run_out
    b1_changed = original != b1_out

    if item['id'] in OK_IDS:
        if run_changed: run_ok.add(item['id'])
        if b1_changed: b1_ok.add(item['id'])

# Now find the differences
for item in eval_data:
    if item['id'] in SKIP_IDS: continue
    original = item['original']
    run_out = normalize_text(original)
    b1_out = baseline1(original)
    run_correct = (item['id'] in OK_IDS) and (original != run_out)
    b1_correct = (item['id'] in OK_IDS) and (original != b1_out)

    if run_correct and not b1_correct:
        run_only.append(item['id'])
    elif b1_correct and not run_correct:
        b1_only.append(item['id'])
    elif run_correct and b1_correct:
        both_ok.append(item['id'])
    else:
        both_fix.append(item['id'])

print("="*60)
print("DIAGNOSTIC: RUN vs Baseline 1")
print("="*60)
print(f"Both correct (OK):           {len(both_ok)}")
print(f"RUN correct, B1 wrong:       {len(run_only)}")
print(f"B1 correct, RUN wrong:       {len(b1_only)}")
print(f"Both wrong (FIX):            {len(both_fix)}")

print(f"\nSentences RUN gets right that B1 misses ({len(run_only)}):")
for sid in run_only[:10]:
    item = next(x for x in eval_data if x['id']==sid)
    run_out = normalize_text(item['original'])
    b1_out = baseline1(item['original'])
    print(f"\n  ID {sid}:")
    print(f"  ORIG: {item['original'][:65]}")
    print(f"  RUN:  {run_out[:65]}")
    print(f"  B1:   {b1_out[:65]}")

print(f"\nSentences B1 gets right that RUN misses ({len(b1_only)}):")
for sid in b1_only[:10]:
    item = next(x for x in eval_data if x['id']==sid)
    run_out = normalize_text(item['original'])
    b1_out = baseline1(item['original'])
    print(f"\n  ID {sid}:")
    print(f"  ORIG: {item['original'][:65]}")
    print(f"  RUN:  {run_out[:65]}")
    print(f"  B1:   {b1_out[:65]}")

# Coverage analysis
print(f"\n{'='*60}")
print(f"COVERAGE ANALYSIS")
print(f"{'='*60}")

total_variants = 0
run_fixed = 0
b1_fixed = 0

for item in eval_data:
    if item['id'] in SKIP_IDS: continue
    original = item['original']
    run_out = normalize_text(original)
    b1_out = baseline1(original)

    orig_tokens = original.split()
    run_tokens = run_out.split()
    b1_tokens = b1_out.split()

    for o, r, b in zip(orig_tokens, run_tokens, b1_tokens):
        if o.lower() != r.lower() or o.lower() != b.lower():
            total_variants += 1
            if o.lower() != r.lower(): run_fixed += 1
            if o.lower() != b.lower(): b1_fixed += 1

print(f"Total tokens normalized by either system: {total_variants}")
print(f"RUN normalized: {run_fixed} tokens")
print(f"B1 normalized:  {b1_fixed} tokens")
print(f"RUN coverage:   {100*run_fixed/total_variants:.1f}%")
print(f"B1 coverage:    {100*b1_fixed/total_variants:.1f}%")