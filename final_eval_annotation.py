from normalizer import normalize_text
import json

with open("eval_data.json", "r", encoding="utf-8") as f:
    eval_data = json.load(f)

# Final OK/FIX/SKIP sets from complete human annotation
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

with open("final_annotation_sheet.txt", "w", encoding="utf-8") as f:
    f.write("FINAL EVALUATION ANNOTATION — RUN (Roman Urdu Normalizer)\n")
    f.write("="*70 + "\n")
    f.write("200 held-out test sentences. Annotated through iterative error analysis.\n")
    f.write("OK = system output fully correct\n")
    f.write("FIX = system output has errors\n")
    f.write("SKIP = sentence too noisy to judge (ID 57 only)\n")
    f.write("="*70 + "\n\n")

    for item in eval_data:
        sid = item['id']
        original = item['original']
        output = normalize_text(original)

        if sid in SKIP_IDS:
            judgment = "SKIP"
        elif sid in OK_IDS:
            judgment = "OK"
        else:
            judgment = "FIX"

        changes = []
        if original != output:
            orig_tokens = original.split()
            out_tokens = output.split()
            changes = [f"{o}→{n}" for o, n in
                      zip(orig_tokens, out_tokens)
                      if o.lower() != n.lower()]

        f.write(f"ID: {sid}\n")
        f.write(f"ORIGINAL:   {original}\n")
        f.write(f"NORMALIZED: {output}\n")
        f.write(f"CHANGES:    {', '.join(changes) if changes else '(none)'}\n")
        f.write(f"JUDGMENT:   {judgment}\n\n")

# Also save as JSON for easy loading
annotation_data = []
for item in eval_data:
    sid = item['id']
    output = normalize_text(item['original'])
    if sid in SKIP_IDS:
        judgment = "SKIP"
    elif sid in OK_IDS:
        judgment = "OK"
    else:
        judgment = "FIX"
    annotation_data.append({
        'id': sid,
        'original': item['original'],
        'system_output': output,
        'judgment': judgment,
        'changed': item['original'] != output
    })

with open("final_annotation_data.json", "w", encoding="utf-8") as f:
    json.dump(annotation_data, f, ensure_ascii=False, indent=2)

ok_count = len([x for x in annotation_data if x['judgment'] == 'OK' and x['changed']])
fix_count = len([x for x in annotation_data if x['judgment'] == 'FIX'])
print(f"Saved final_annotation_sheet.txt and final_annotation_data.json")
print(f"OK (changed): {ok_count} | FIX: {fix_count} | SKIP: {len(SKIP_IDS)}")