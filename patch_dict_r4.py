import json

with open("normalization_dict_final.json", "r", encoding="utf-8") as f:
    d = json.load(f)

print(f"Rules before: {len(d)}")

REMOVE_R4 = [
    # Names catastrophically changed
    'kazmi',        # surname→different surname
    'sheharyar',    # name→city
    'armeena',      # name→different name
    'fazlur',       # full name→nickname
    'fiqar',        # worry→name (zulfiqar)
    'wakay',        # actually→came
    'hajji',        # pilgrim→female pilgrim

    # Catastrophic semantic collisions
    'muamla',       # matter→staff
    'shurka',       # participants→start
    'shoba',        # department→falcon
    'siyasiyat',    # politics→status
    'taiyariyan',   # preparations→cars
    'tarak',        # abandonment→progress
    'hukm',         # command→ruler
    'hasrat',       # longing→effects
    'shaqal',       # face→doubt
    'wujood',       # existence→present
    'sawaab',       # religious reward→question
    'baary',        # about→all
    'batanay',      # telling→going
    'chhati',       # chest→roof
    'kahien',       # somewhere→here
    'maliyat',      # finance→inclusion
    'sudhar',       # reform→there/loan
    'kamon',        # confirmed correct by you — KEEP IN DICT

    # English words wrongly changed
    'like',         # like→liked
    'dialog',       # dialog→dialogues
    'mints',        # minutes→colors
    'bat',          # cricket bat→baat

    # Correct spellings wrongly changed — confirmed WRONG by you
    # (removing only ones NOT confirmed as correct)
    'chaap',        # imprint→moon
    'waliden',      # parents plural→mother
    'bhaiyo',       # brothers plural→singular
    'karwae',       # got done plural→infinitive
    'chalate',      # driving plural→singular
    'insanon',      # humans plural→singular
    'sambhala',     # managed past→base
    'karsakte',     # can do plural→singular
    'lagani',       # to put feminine→masculine
    'jasakta',      # can go→can
    'dikhate',      # showing plural→singular
    'khareedo',     # buy plural→singular
    'anay',         # coming→going
    'sochte',       # think plural→singular
    'kamyabi',      # success noun→adjective
    'guzarna',      # to pass infinitive→base
    'shokh',        # fond adj→fondness noun
    'karobari',     # commercial adj→noun
    'qismati',      # fortunate→misfortune
    'progrm',       # program shortening→prog
    'tareekhi',     # historical adj→noun
    'riwayati',     # traditional adj→noun
    'inhyn',        # them with nasalization→inhy
    'bunyade',      # fundamental adj→noun
    'masail',       # problems plural→singular
    'isky',         # proximal→distal pronoun
    'ankho',        # eyes plural→singular
    'laptops',      # English plural→singular
    'btry',         # battery shortening→betry
]

removed = []
for word in REMOVE_R4:
    if word in d:
        removed.append(f"{word} → {d[word]}")
        del d[word]

print(f"Removed {len(removed)} bad rules:")
for r in removed:
    print(f"  {r}")

NEW_ANCHORS_R4 = [
    'muamla', 'shurka', 'shoba', 'siyasiyat', 'taiyariyan',
    'tarak', 'hukm', 'hasrat', 'wujood', 'sawaab',
    'chhati', 'maliyat', 'sudhar', 'kahien',
    'waliden', 'bhaiyo', 'kamyabi', 'insanon',
    'bunyade', 'masail', 'ankho', 'karobari',
    'guzarna', 'shokh', 'shaqal',
]

anchored = 0
for word in NEW_ANCHORS_R4:
    if word not in d:
        d[word] = word
        anchored += 1

print(f"New anchors: {anchored}")
print(f"Final rules: {len(d)}")

with open("normalization_dict_final.json", "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print("Saved.")