import json

with open("normalization_dict_final.json", "r", encoding="utf-8") as f:
    d = json.load(f)

print(f"Rules before: {len(d)}")

REMOVE_R3 = [
    # Catastrophic semantic collisions
    'joota',        # shoe→looted
    'chalan',       # behavior→run plural
    'dihari',       # daily wage→nihari dish
    'shararat',     # mischief→alcohol
    'karra',        # solid/dense→cauldron
    'laein',        # bring→go
    'simran',       # name→different name
    'musa',         # name→imposed
    'laay',         # bring→shade
    'bahta',        # flows→says
    'chiknay',      # smooth→for selling
    'maali',        # gardener→one who
    'daley',        # cast/put→ones who
    'latoon',       # kicks→words
    'bezameer',     # without conscience→conscience
    'benishan',     # without trace→trace
    'males',        # males→females
    'madari',       # circus person→mother
    'matalab',      # meaning→desire

    # Names wrongly changed
    'jamiat',       # political party→seminary
    'shehnaazgill', # celebrity name→fanbase name

    # English words wrongly changed
    'functioning',  # functioning→functions
    'putting',      # putting→hitting
    'packed',       # packed→packing
    'handles',      # handles→candles
    'strings',      # music group→jewelry
    'wanna',        # want to→going to
    'desktop',      # computer type→table

    # Correct spellings wrongly changed — confirmed by manual review
    # (removing only ones NOT confirmed as correct by you)
    'filmsaaz',     # filmmaker→films
    'mauseeqar',    # musician→music
    'wafadari',     # loyalty→loyal
    'muqable',      # competitions plural→singular
    'mashware',     # advice plural→singular
    'kutty',        # dogs/puppy→singular (confirmed wrong)
    'hakoomati',    # governmental adj→noun
    'mahngi',       # expensive adj→inflation noun
    'kharcha',      # expense noun→less letters
    'pucho',        # ask plural→singular
    'rakhyn',       # keep plural→singular
    'dikhae',       # showed plural→singular
    'khandano',     # families plural→singular

    # Form/tense wrongly changed
    'chalne',       # of breathing genitive→infinitive
    'chalyga',      # future→subjunctive
    'bhonka',       # barked past→base
    'nakami',       # failure noun→adjective
    'muqadar',      # fate→sacred (catastrophic)
    'chahte',       # want plural→singular
    'jayee',        # may go→went past
    'harna',        # losing→falling
    'laein',        # bring plural→go

    # Other confirmed wrong
    'naqool',       # copies→reasonable
    'nizaam',       # historical title→adjective
    'chaheay',      # shortening→different shortening (correct: chahiye)
]

# Words confirmed CORRECT by you — remove from REMOVE list above if present
# These are kept in dict: naslo, khushiyon (wrong direction confirmed),
# wajuhaat, tabiat, aayegi, tehelka, farmaa, taadaad, aorat, bachii,
# krdo, hahahahahha, bugz, hta, meharbani, taklif, ittifaq, utaarny,
# hojai, oasat, mutarrif, hogyaa, firdous, zalmon, barbaad,
# khoubsurat, taqreeban, mutassir, aagye, hahaha

# Also add correct mapping for chaheay
CORRECTIONS = {
    'chaheay': 'chahiye',   # confirmed by you
    'khushiyon': 'khushiyan',  # confirmed correct direction
    'wajuhaat': 'wajohaat',    # confirmed correct
}

removed = []
for word in REMOVE_R3:
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

NEW_ANCHORS_R3 = [
    'joota', 'dihari', 'shararat', 'karra',
    'laay', 'bahta', 'chiknay', 'maali', 'daley',
    'latoon', 'bezameer', 'benishan', 'madari', 'matalab',
    'jamiat', 'filmsaaz', 'mauseeqar',
    'wafadari', 'hakoomati', 'mahngi',
    'khandano', 'chalne', 'chahte',
    'naqool', 'nizaam',
]

anchored = 0
for word in NEW_ANCHORS_R3:
    if word not in d:
        d[word] = word
        anchored += 1

print(f"New anchors: {anchored}")
print(f"Final rules: {len(d)}")

with open("normalization_dict_final.json", "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print("Saved.")