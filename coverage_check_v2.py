from normalizer import normalize_text
import json

with open("eval_data.json", "r", encoding="utf-8") as f:
    eval_data = json.load(f)

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

# The key insight: compare each system's output against RUN's output
# If a system produces the SAME output as RUN on OK sentences = correct
# If it produces DIFFERENT output on OK sentences = wrong
# If it produces SAME output as RUN on FIX sentences = also wrong

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

print("Checking B1 output vs RUN output on OK sentences...")
print("="*70)
print("Sentences where B1 output DIFFERS from RUN output (both in OK_IDS):")
print("="*70)

differ_count = 0
b1_worse = 0
b1_better = 0

for item in eval_data:
    if item['id'] in SKIP_IDS: continue
    if item['id'] not in OK_IDS: continue

    original = item['original']
    run_out = normalize_text(original)
    b1_out = baseline1(original)

    if run_out == b1_out: continue

    differ_count += 1
    # Check if B1 made wrong changes (changed something RUN left alone correctly)
    run_changed_tokens = {i: (o,n) for i,(o,n) in
                         enumerate(zip(original.split(), run_out.split()))
                         if o.lower() != n.lower()}
    b1_changed_tokens = {i: (o,n) for i,(o,n) in
                        enumerate(zip(original.split(), b1_out.split()))
                        if o.lower() != n.lower()}

    b1_extra = set(b1_changed_tokens.keys()) - set(run_changed_tokens.keys())
    b1_missed = set(run_changed_tokens.keys()) - set(b1_changed_tokens.keys())

    print(f"\nID {item['id']}:")
    print(f"  ORIG: {original[:70]}")
    print(f"  RUN:  {run_out[:70]}")
    print(f"  B1:   {b1_out[:70]}")
    if b1_extra:
        extra_changes = [f"{original.split()[i]}→{b1_out.split()[i]}"
                        for i in b1_extra if i < len(original.split())]
        print(f"  B1 WRONG EXTRA changes: {extra_changes}")
        b1_worse += 1
    if b1_missed:
        missed_changes = [f"{original.split()[i]} not normalized"
                         for i in b1_missed if i < len(original.split())]
        print(f"  B1 MISSED correct changes: {missed_changes}")

print(f"\nSummary: {differ_count} OK sentences where B1 and RUN differ")
print(f"B1 made wrong extra changes: {b1_worse} sentences")