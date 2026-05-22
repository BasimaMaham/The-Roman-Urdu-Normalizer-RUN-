import json

with open("normalization_dict_final.json", "r", encoding="utf-8") as f:
    d = json.load(f)

print(f"Rules before: {len(d)}")

# Bad mappings confirmed from Round 1 annotation (after manual corrections)
REMOVE_R1 = [
    # English words being wrongly modified
    'year', 'army', 'news', 'like', 'terminated',
    'responded', 'contacted', 'whom', 'replying',
    'moved', 'iphones',

    # Catastrophic semantic collisions
    'larnay',      # fight→kill
    'zariya',      # means→river (we anchor this below)
    'danty',       # scold→aunty
    'layen',       # bring→come
    'payen',       # get→come
    'wahein',      # right there→somewhere
    'farhami',     # understanding→name
    'bazariya',    # via→river
    'chapa',       # raid→sandal
    'farakh',      # spacious→difference
    'kharan',      # place name mangled

    # Morphological confusions confirmed wrong
    'khamoshi',    # silence noun→silent adjective
    'mushkilat',   # difficulties pl→singular
    'mushkilaat',  # difficulties pl→singular
    'tabdeel',     # changed→change noun
    'zimedar',     # responsible→responsibility
    'sochen',      # plural→singular
    'nikalen',     # plural subj→singular past
    'behtari',     # betterment→better
    'bunyadi',     # basic adj→foundation noun
    'qanuni',      # legal adj→law noun
    'aitraaf',     # confession→objection
    'dilchaspi',   # interest→interesting
    'tabahi',      # destruction→destroyed
    'kamiyabi',    # success→successful
    'pohanche',    # reached pl→base
    'jhoote',      # liars→lie noun
    'chooran',     # medicine→thief
    'pakara',      # past tense→base form
    'dehka',       # past→imperative
    'musalmanoo',  # vocative pl→singular
    'hinduon',     # Urdu pl→English pl
    'tarjuma',     # translation→translator
    'fazl',        # politician name truncated
    'chahat',      # desire→wants verb
    'kitnay',      # how many→this many
    'thnku',       # both valid shortenings
    'sochtay',     # present cont→subjunctive
    'waisay',      # like that→how (catastrophic)
    'neechay',     # below→behind
    'bhoki',       # hungry→not a word
    'nayee',       # new→came
    'parhne',      # genitive→infinitive
    'jarahay',     # going→coming
    'aadmiyon',    # men→daughters
    'jehat',       # direction→jihad
    'siyasi',      # political adj→politics noun
    'faraghat',    # leisure→not a word (already removed but ensure)
    'baatar',

    # Names being wrongly changed
    'bachan',      # Amitabh Bachchan
    'kakkar',      # Neha Kakkar
    'sharabi',     # film title
    'jinhoon',     # correct spelling being changed
]

# Correct canonical forms for words we were mapping wrongly
# These need to be updated not just removed
CORRECTIONS = {
    'banaaye':  'banaye',    # were made → made (correct plural past)
    'chooro':   'choron',    # thieves vocative → oblique plural
    'loogo':    'logon',     # people vocative → oblique plural
    'chahy':    'chahiye',   # wants subj → should/want (standard)
    'thii':     'thi',       # double vowel → single
    'paiso':    'paison',    # money → money oblique (correct)
    'muslimsto':'muslims',   # merged word → split correct
}

removed = []
for word in REMOVE_R1:
    if word in d:
        removed.append(f"{word} → {d[word]}")
        del d[word]

print(f"Removed {len(removed)} bad rules:")
for r in removed:
    print(f"  {r}")

corrected = []
for word, canonical in CORRECTIONS.items():
    old = d.get(word, 'not in dict')
    d[word] = canonical
    corrected.append(f"{word}: {old} → {canonical}")

print(f"\nCorrected {len(corrected)} rules:")
for c in corrected:
    print(f"  {c}")

# Identity anchors for words that keep getting wrongly changed
NEW_ANCHORS = [
    'zariya', 'chooran', 'mushkilat', 'mushkilaat',
    'tabahi', 'kamiyabi', 'aitraaf', 'dilchaspi',
    'khamoshi', 'farhami', 'bazariya', 'wahein',
    'larnay', 'danty', 'pakara', 'musalmanoo',
    'jinhoon', 'siyasi', 'zimedar', 'chapa',
    'farakh', 'kharan', 'sochen', 'nikalen',
    'behtari', 'bunyadi', 'qanuni',
]

anchored = 0
for word in NEW_ANCHORS:
    if word not in d:
        d[word] = word
        anchored += 1

print(f"\nNew identity anchors: {anchored}")
print(f"Final rules: {len(d)}")

with open("normalization_dict_final.json", "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print("Saved normalization_dict_final.json")