import json
from collections import defaultdict

print("Loading data...")
with open("normalization_dict_v2.json", "r", encoding="utf-8") as f:
    norm_dict = json.load(f)

with open("urdu_vocab_v2.json", "r", encoding="utf-8") as f:
    urdu_vocab = json.load(f)

with open("cluster_info_v2.json", "r", encoding="utf-8") as f:
    cluster_info = json.load(f)

# Build reverse map: canonical -> [variants]
canonical_to_variants = defaultdict(list)
for variant, canonical in norm_dict.items():
    canonical_to_variants[canonical].append(variant)

# Words that are their own canonical (not mapped to anything)
all_canonicals = set(canonical_to_variants.keys()) | (
    set(urdu_vocab.keys()) - set(norm_dict.keys())
)

print(f"Current normalization rules: {len(norm_dict)}")
print(f"Words with no variants found: "
      f"{sum(1 for w in urdu_vocab if w not in norm_dict and not canonical_to_variants[w])}")

# ================================================================
# EDIT DISTANCE PASS
# For words not yet captured by clustering,
# use Levenshtein distance to find close matches
# among high-frequency canonical words
# ================================================================

def levenshtein(s1, s2):
    if abs(len(s1) - len(s2)) > 3:
        return 999
    m, n = len(s1), len(s2)
    dp = list(range(n + 1))
    for i in range(1, m + 1):
        prev = dp[0]
        dp[0] = i
        for j in range(1, n + 1):
            temp = dp[j]
            if s1[i-1] == s2[j-1]:
                dp[j] = prev
            else:
                dp[j] = 1 + min(prev, dp[j], dp[j-1])
            prev = temp
    return dp[n]

def shares_substring(w1, w2, min_len=3):
    if len(w1) < min_len or len(w2) < min_len:
        return True
    for i in range(len(w1) - min_len + 1):
        if w1[i:i+min_len] in w2:
            return True
    return False

# High-frequency canonicals are the target forms
# These are words frequent enough to be reliable canonical forms
HIGH_FREQ_THRESHOLD = 500
high_freq_canonicals = {
    w: c for w, c in urdu_vocab.items()
    if c >= HIGH_FREQ_THRESHOLD and w not in norm_dict
}
print(f"\nHigh-frequency canonical targets: {len(high_freq_canonicals)}")
print("Sample:", list(high_freq_canonicals.keys())[:20])

# Find unmapped words that are close to a high-freq canonical
new_rules = {}
unmapped = [w for w in urdu_vocab 
            if w not in norm_dict and w not in canonical_to_variants]

print(f"Unmapped words to check: {len(unmapped)}")
print("Running edit distance pass...")

for i, word in enumerate(unmapped):
    if i % 2000 == 0:
        print(f"  {i}/{len(unmapped)}...")
    
    best_canonical = None
    best_dist = 999
    word_len = len(word)
    
    for canonical, freq in high_freq_canonicals.items():
        if canonical == word:
            continue
        if abs(len(canonical) - word_len) > 3:
            continue
        if not shares_substring(word, canonical, 3):
            continue
        
        dist = levenshtein(word, canonical)
        
        # Stricter threshold for shorter words (avoid false merges)
        max_dist = 1 if word_len <= 4 else 2
        
        if dist <= max_dist and dist < best_dist:
            best_dist = dist
            best_canonical = canonical
    
    if best_canonical:
        new_rules[word] = best_canonical

print(f"New rules from edit distance: {len(new_rules)}")

# Show what was found
print("\nSample new rules (edit distance):")
sample = sorted(new_rules.items(), 
                key=lambda x: -urdu_vocab.get(x[0], 0))[:30]
for variant, canonical in sample:
    dist = levenshtein(variant, canonical)
    print(f"  {variant}({urdu_vocab.get(variant,0)}) "
          f"→ {canonical}({urdu_vocab.get(canonical,0)}) [dist={dist}]")

# Merge with existing rules
combined_dict = {**norm_dict, **new_rules}

# Verify key words now have variants
print("\n" + "="*50)
print("SPOT CHECKS AFTER HYBRID FIX")
print("="*50)
spot_checks = ["nhi", "nahi", "acha", "achha", "accha",
               "bhai", "bhe", "bohat", "boht", "bht",
               "bilkul", "blkl", "karna", "krna"]

for word in spot_checks:
    if word in combined_dict:
        print(f"  {word} → {combined_dict[word]}")
    elif word in urdu_vocab:
        # It's a canonical - show its variants
        variants = [v for v, c in combined_dict.items() if c == word]
        print(f"  {word} [CANONICAL] → variants: {variants[:8]}")
    else:
        print(f"  {word}: not in vocab")

# Save final combined normalization dictionary
with open("normalization_dict_final.json", "w", encoding="utf-8") as f:
    json.dump(combined_dict, f, ensure_ascii=False, indent=2)

print(f"\nFinal normalization rules: {len(combined_dict)}")
print("Saved normalization_dict_final.json")

# Quick stats
print(f"\nCoverage: {len(combined_dict)} of {len(urdu_vocab)} "
      f"vocab words have normalization rules "
      f"({100*len(combined_dict)/len(urdu_vocab):.1f}%)")