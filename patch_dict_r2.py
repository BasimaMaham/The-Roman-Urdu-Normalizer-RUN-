import json

with open("normalization_dict_final.json", "r", encoding="utf-8") as f:
    d = json.load(f)

print(f"Rules before: {len(d)}")

REMOVE_R2 = [
    # Wrong word substitutions
    'oey',          # hey→happened
    'haiga',        # will be (Punjabi)→will come
    'isne',         # he/she did→who did
    'mahaan',       # great→monthly
    'beshumar',     # countless→count
    'anday',        # eggs→people
    'rayee',        # opinion→came
    'pursan',       # one who asks→not a word
    'lainay',       # taking→giving (opposite)
    'manty',        # accepting→knowing
    'bachao',       # save→saved/children
    'khawand',      # husband→dream (catastrophic)
    'dilanay',      # to get delivered→going

    # Proper nouns wrongly changed
    'nabila',       # name→name's
    'army',         # army→army's
    'maryum',       # name→different name

    # English words being wrongly changed
    'indicators',   # indicators→investors
    'gained',       # gained→listened
    'rumours',      # rumours→fours
    'instal',       # install shortening→Instagram
    'mobi',         # mobile short→qmobile brand
    'site',         # site→website
    'happened',     # happened→happens
    'mobiles',      # mobiles→qmobile

    # Correct spellings being wrongly changed
    'phoolon',      # flowers oblique pl→singular
    'gillani',      # PM's name
    'masrufiyat',   # busyness→wrong vowel
    'naghme',       # songs plural→singular
    'bataty',       # telling→not a word
    'poocha',       # asked→wiped (completely different)
    'janaze',       # funeral oblique→nominative
    'faysal',       # valid name spelling
    'nuqsanat',     # harms plural→singular (you said dytay is ok, nuqsanat wasn't mentioned so keep removing)
    'nafsiyat',     # psychology noun→adjective

    # Number/form wrongly changed
    'naujawano',    # youths oblique pl→singular
    'khandani',     # hereditary adj→noun
    'khelta',       # plays singular→plural
    'doosre',       # other masculine→feminine
    'bhejo',        # send plural→singular
    'rhny',         # stay→not a word
    'parhen',       # may read subjunctive→imperative
    'krwany',       # causative oblique→different form

    # Wrong word substitutions confirmed
    'zimadari',     # responsibility→adjective
]

removed = []
for word in REMOVE_R2:
    if word in d:
        removed.append(f"{word} → {d[word]}")
        del d[word]

print(f"Removed {len(removed)} bad rules:")
for r in removed:
    print(f"  {r}")

# New identity anchors for words that keep getting wrongly changed
NEW_ANCHORS_R2 = [
    'mahaan', 'beshumar', 'anday', 'rayee', 'pursan',
    'lainay', 'manty', 'bachao', 'khawand', 'dilanay',
    'phoolon', 'naujawano', 'nuqsanat',
    'haiga', 'isne', 'nabila',
]

anchored = 0
for word in NEW_ANCHORS_R2:
    if word not in d:
        d[word] = word
        anchored += 1

print(f"New anchors: {anchored}")
print(f"Final rules: {len(d)}")

with open("normalization_dict_final.json", "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print("Saved.")