import json
from collections import defaultdict

print("Loading data...")
with open("normalization_dict_v2.json", "r", encoding="utf-8") as f:
    norm_dict = json.load(f)
with open("urdu_vocab_v2.json", "r", encoding="utf-8") as f:
    urdu_vocab = json.load(f)

# ================================================================
# PART 1: MANUAL LOOKUP FOR SHORT FUNCTION WORDS
# These ~80 words cover the most frequent Roman Urdu variants
# Short words cannot be handled by automated rules safely
# ================================================================
MANUAL_NORM = {
    # hai (is/are)
    'ha': 'hai', 'hy': 'hai', 'hae': 'hai', 'hey': 'hai',
    'hain': 'hai', 'hen': 'hai', 'hein': 'hai', 'haen': 'hai',

    # nahi (no/not)
    'nhi': 'nahi', 'ni': 'nahi', 'nhe': 'nahi', 'nhy': 'nahi',
    'nahin': 'nahi', 'nahn': 'nahi', 'nehi': 'nahi', 'nai': 'nahi',

    # mein (in/I)
    'me': 'mein', 'mn': 'mein', 'mien': 'mein',

    # main (I - first person)  
    'mai': 'main',

    # mein (in) and main (I) are DISTINCT - do not merge
    # 'mein' stays as its own canonical

    # kya (what)
    'kia': 'kya', 'kiya': 'kya', 'kia': 'kya',

    # yeh (this)
    'ye': 'yeh', 'yh': 'yeh', 'yee': 'yeh',

    # woh (he/she/that)
    'wo': 'woh', 'voh': 'woh', 'vo': 'woh',

    # aap (you - formal)
    'ap': 'aap', 'aap': 'aap',

    # hum (we)
    'hm': 'hum',

    # tum (you - informal)
    'tm': 'tum',

    # koi (someone/any)
    'koe': 'koi', 'koie': 'koi',

    # kuch (something/some)
    'kch': 'kuch', 'kuch': 'kuch', 'kch': 'kuch',

    # sab (all)
    'sub': 'sab', 'sb': 'sab',

    # ab (now)
    'abb': 'ab',

    # aaj (today)
    'aj': 'aaj', 'aaj': 'aaj',

    # kal (yesterday/tomorrow)
    'kl': 'kal',

    # phir (then/again)
    'fer': 'phir', 'fir': 'phir', 'phr': 'phir',

    # bhi (also)
    'bi': 'bhi', 'v': 'bhi',

    # toh (so/then)
    'to': 'toh',  # careful - 'to' is also English

    # aur (and)
    'or': 'aur',  # careful - 'or' is also English

    # per/par (on/but)  - keep separate, both valid
    'pey': 'par', 'py': 'par',

    # se (from/with)
    'say': 'se', 'sey': 'se',

    # ke/ka/ki/ko - these are DISTINCT, do not merge
    'k': 'ka',   # most common shortening is ka
    'ki': 'ki',  # keep as is
    'ke': 'ke',  # keep as is
    'ko': 'ko',  # keep as is

    # tha/thi/the (was/were - gender forms) - keep distinct
    'tha': 'tha', 'thi': 'thi',

    # hoga/hogi (will be - gender forms)
    'hoga': 'hoga', 'hogi': 'hogi',

    # bohat (very/much) - important content word, manual add
    'boht': 'bohat', 'bht': 'bohat', 'bhot': 'bohat',
    'buhat': 'bohat', 'bouhat': 'bohat', 'bhohat': 'bohat',
    'bohat': 'bohat',

    # bilkul (absolutely)
    'blkl': 'bilkul', 'blkul': 'bilkul', 'bilkol': 'bilkul',
    'belkul': 'bilkul', 'bulkul': 'bilkul',

    # bakwas (nonsense)
    'bkwas': 'bakwas', 'bakwaas': 'bakwas', 'baqwas': 'bakwas',
    'bukwas': 'bakwas', 'bkws': 'bakwas',

    # theek (okay/correct) - add as canonical too
    'theek': 'theek',  # ensure it exists
    'thik': 'theek', 'theak': 'theek',

    # zaroor (definitely/must)
    'zarur': 'zaroor', 'zaror': 'zaroor', 'zroor': 'zaroor',

    # matlab (meaning)
    'mtlb': 'matlab', 'matlb': 'matlab',

    # waise (by the way/like that)
    'wese': 'waise', 'waisy': 'waise', 'wasy': 'waise',

    # zyada (more/too much)
    'ziada': 'zyada', 'ziyada': 'zyada', 'jyada': 'zyada',

    # pehle (before/first)
    'pehlay': 'pehle', 'pahle': 'pehle', 'pehly': 'pehle',

    # baad (after)
    'baad': 'baad', 'bad': 'baad',

    # saath (with/together)
    'sath': 'saath', 'sat': 'saath',

    # raat (night)
    'rat': 'raat',

    # baat (talk/matter)
    'bat': 'baat', 'bt': 'baat',

    # abhi (right now)
    'abhi': 'abhi', 'abi': 'abhi',

    # sirf (only)
    'srf': 'sirf', 'sirf': 'sirf',

    # kyun (why)
    'kyun': 'kyun', 'kiun': 'kyun', 'kyn': 'kyun',

    # kaisa (how/what kind)
    'kaisa': 'kaisa', 'kesa': 'kaisa', 'kaesa': 'kaisa',

    # warna (otherwise)
    'wrna': 'warna', 'varna': 'warna',

    # acha/achha/accha (good/okay) - all valid, pick one
    'achha': 'acha', 'accha': 'acha', 'achcha': 'acha',
    'aachaa': 'acha', 'achaa': 'acha',

    # theek (okay/correct)
    'thk': 'theek', 'thek': 'theek', 'tik': 'theek',

    # dekh (see/look)
    'dkh': 'dekh',

    # kar (do)
    'kr': 'kar',

    # baat (talk/thing)
    'bat': 'baat', 'bt': 'baat',

    # waqt (time)
    'wqt': 'waqt', 'vaqt': 'waqt',
}

# Only apply manual norm if word is in vocab
manual_applied = {w: c for w, c in MANUAL_NORM.items()
                  if w in urdu_vocab and c != w}
print(f"Manual rules applicable to vocab: {len(manual_applied)}")

# ================================================================
# PART 2: AUTOMATED MERGE FOR LONG WORDS ONLY (6+ chars)
# UrduPhone + edit distance, but ONLY for words >= 6 characters
# ================================================================

URDUPHONE_MAP = {
    'aa': 'a', 'ae': 'a', 'ai': 'a', 'ay': 'a',
    'ee': 'i', 'ei': 'i', 'ey': 'i',
    'oo': 'u', 'ou': 'u',
    'q': 'k', 'z': 'z', 'ph': 'f',
    'tt': 't', 'dd': 'd', 'ss': 's', 'nn': 'n',
    'mm': 'm', 'll': 'l',
}

def urduphone_encode(word):
    w = word.lower()
    for pattern in sorted(URDUPHONE_MAP.keys(), key=len, reverse=True):
        w = w.replace(pattern, URDUPHONE_MAP[pattern])
    w = w.rstrip('aeiou') if len(w) > 3 else w
    result = w[0] if w else ''
    for char in w[1:]:
        if char != result[-1]:
            result += char
    return result

def levenshtein(s1, s2):
    if abs(len(s1) - len(s2)) > 3:
        return 999
    m, n = len(s1), len(s2)
    dp = list(range(n + 1))
    for i in range(1, m + 1):
        prev, dp[0] = dp[0], i
        for j in range(1, n + 1):
            temp = dp[j]
            dp[j] = prev if s1[i-1] == s2[j-1] else 1 + min(prev, dp[j], dp[j-1])
            prev = temp
    return dp[n]

def shares_substring(w1, w2, min_len=3):
    for i in range(len(w1) - min_len + 1):
        if w1[i:i+min_len] in w2:
            return True
    return False

# Get current canonicals that are LONG words (6+ chars)
# and not already in manual norm
long_canonicals = sorted(
    [w for w in urdu_vocab
     if len(w) >= 6
     and w not in norm_dict          # already a canonical
     and w not in manual_applied],   # not in manual rules
    key=lambda w: -urdu_vocab.get(w, 0)
)
print(f"Long-word canonicals to process: {len(long_canonicals)}")

# Find merges among long canonicals only
long_merge_map = {}
phone_groups = defaultdict(list)

# Group by phonetic code first for efficiency
for w in long_canonicals:
    code = urduphone_encode(w)
    phone_groups[code].append(w)

auto_merges = 0
for code, group in phone_groups.items():
    if len(group) < 2:
        continue
    # Sort by frequency - highest freq = canonical
    group_sorted = sorted(group, key=lambda w: -urdu_vocab.get(w, 0))
    canonical = group_sorted[0]

    for variant in group_sorted[1:]:
        if variant in long_merge_map:
            continue
        # Verify with edit distance too
        if levenshtein(canonical, variant) <= 2:
            long_merge_map[variant] = canonical
            auto_merges += 1

print(f"Auto merges for long words: {auto_merges}")

# ================================================================
# PART 3: COMBINE EVERYTHING
# Priority: manual > clustering > auto long-word merge
# ================================================================
final_dict = {}

for word in urdu_vocab:
    # Priority 1: manual rules
    if word in manual_applied:
        final_dict[word] = manual_applied[word]
    # Priority 2: clustering results
    elif word in norm_dict:
        canonical = norm_dict[word]
        # Check if that canonical itself needs remapping
        if canonical in manual_applied:
            canonical = manual_applied[canonical]
        elif canonical in long_merge_map:
            canonical = long_merge_map[canonical]
        if canonical != word:
            final_dict[word] = canonical
    # Priority 3: auto long-word merge
    elif word in long_merge_map:
        final_dict[word] = long_merge_map[word]
    # else: word is its own canonical, not stored

print(f"\nFinal normalization rules: {len(final_dict)}")
print(f"Coverage: {100*len(final_dict)/len(urdu_vocab):.1f}%")

# ================================================================
# SPOT CHECKS
# ================================================================
print("\n" + "="*60)
print("SPOT CHECKS")
print("="*60)
checks = [
    'nhi', 'nahi', 'ha', 'hy', 'hai',
    'boht', 'bht', 'bhot', 'bohat',
    'acha', 'achha', 'accha',
    'ko', 'ka', 'ki', 'ke',        # these must stay distinct
    'bhai',                          # must NOT become hai
    'wo', 'woh', 'yo',
    'theek', 'thk', 'thek',
    'bilkul', 'blkl', 'blkul',
    'phir', 'fer', 'fir',
    'alhamdulillah', 'alhamdulilah',
    'bakwas', 'bkwas',
    'shukriya', 'shukrya',
]

for word in dict.fromkeys(checks):
    freq = urdu_vocab.get(word, 0)
    if word not in urdu_vocab:
        print(f"  {word}: not in vocab")
        continue
    canonical = final_dict.get(word, word)
    marker = f"→ {canonical}" if word != canonical else "[CANONICAL]"
    print(f"  {word}({freq}) {marker}")

# Verify ka/ki/ke/ko are still distinct
print("\nGrammar word check (must all be distinct canonicals):")
grammar = ['ka', 'ki', 'ke', 'ko', 'se', 'ne', 'par', 'mein', 'tha', 'thi']
for w in grammar:
    c = final_dict.get(w, w)
    status = "OK" if c == w else f"WRONG → {c}"
    print(f"  {w}: {status}")

# Save
with open("normalization_dict_final.json", "w", encoding="utf-8") as f:
    json.dump(final_dict, f, ensure_ascii=False, indent=2)
print(f"\nSaved normalization_dict_final.json")