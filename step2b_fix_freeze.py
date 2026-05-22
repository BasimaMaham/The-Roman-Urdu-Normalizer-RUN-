import json
import re
from collections import defaultdict, Counter

# Load files
with open("vocab_freq.json", "r", encoding="utf-8") as f:
    vocab = json.load(f)

# These are unambiguously Urdu grammar words that must never be frozen
# regardless of what the English dictionary says
URDU_PROTECTED = {
    # core grammar
    'hai', 'hain', 'ha', 'hy', 'hen',           # is/are
    'tha', 'thi', 'the', 'thy',                   # was/were  
    'mein', 'me', 'main',                          # in/I
    'ka', 'ki', 'ke', 'k',                         # of/possessive
    'ko', 'se', 'ne', 'na', 'ni',                 # case markers
    'aur', 'or',                                   # and
    'par', 'per', 'pey',                           # on/but
    'to', 'toh',                                   # so/then
    'bhi', 'bi',                                   # also
    'nahi', 'nhi', 'ni', 'nahin',                 # no/not
    'koi', 'kuch', 'kuch',                        # some/any
    'sab', 'sub',                                  # all
    'jo', 'jو',                                    # who/which
    'wo', 'woh', 'voh',                            # he/she/that
    'ye', 'yeh', 'yh',                             # this
    'ap', 'aap',                                   # you (formal)
    'hum', 'ham',                                  # we
    'in', 'un', 'en',                              # these/those
    'is', 'us',                                    # this/that (oblique)
    'ho', 'hou',                                   # be/become
    'kar', 'kr',                                   # do/doing
    'log', 'loog',                                 # people
    'say', 'sey',                                  # from (Urdu se variant)
    'kay', 'key',                                  # of (Urdu ke variant)
    'allah', 'allaah',                             # God
    'bhai', 'bhi',                                 # brother
    'ap', 'aap',                                   # you
    'hy', 'hai',                                   # is
}

# Unambiguously English - always freeze these
ALWAYS_ENGLISH = {
    'the', 'and', 'but', 'for', 'with', 'from', 'have', 'been', 'will',
    'would', 'could', 'should', 'very', 'really', 'actually', 'basically',
    'obviously', 'seriously', 'already', 'always', 'never', 'every',
    'people', 'good', 'bad', 'just', 'even', 'also', 'only', 'then',
    'than', 'they', 'them', 'their', 'there', 'here', 'when', 'what',
    'which', 'you', 'your', 'our', 'my', 'his', 'her', 'its', 'we',
    'this', 'that', 'these', 'those', 'not', 'yes', 'no', 'okay', 'ok',
    'please', 'thanks', 'thank', 'sorry', 'hello', 'lol', 'omg',
    'because', 'about', 'after', 'before', 'through', 'between',
    'phone', 'mobile', 'school', 'college', 'university', 'class',
    'exam', 'test', 'result', 'marks', 'degree', 'job', 'work', 'office',
    'government', 'police', 'army', 'court', 'party', 'media', 'news',
    'family', 'friend', 'life', 'love', 'heart', 'mind', 'body', 'money',
    'today', 'tomorrow', 'yesterday', 'morning', 'night', 'day', 'time',
    'year', 'month', 'week', 'hour', 'minute', 'second',
    'quality', 'product', 'price', 'service', 'delivery', 'order',
    'like', 'share', 'post', 'comment', 'follow', 'update',
    'pakistan', 'karachi', 'lahore', 'islamabad', 'punjab', 'sindh',
}

import nltk
nltk.download('words', quiet=True)
from nltk.corpus import words as nltk_words
english_dict = set(w.lower() for w in nltk_words.words())

def classify_token(word, freq):
    # Rule 1: protected Urdu words - never freeze
    if word in URDU_PROTECTED:
        return 'urdu'
    
    # Rule 2: always-English list
    if word in ALWAYS_ENGLISH:
        return 'english'
    
    # Rule 3: clearly Urdu patterns
    # Words with these patterns are almost certainly Roman Urdu
    urdu_patterns = [
        r'.*[^aeiou]{3,}.*',     # 3+ consonants in a row (common in Roman Urdu)
        r'^[^aeiou]{2}',          # starts with 2 consonants
    ]
    
    # Rule 4: short ambiguous words (2-3 chars) - treat as Urdu unless in ALWAYS_ENGLISH
    if len(word) <= 3 and word not in ALWAYS_ENGLISH:
        return 'urdu'
    
    # Rule 5: longer words - use dictionary but only if NOT in Urdu protected
    if len(word) >= 5 and word in english_dict and word not in URDU_PROTECTED:
        return 'english'
    
    # Rule 6: 4-char words are ambiguous - default to Urdu (safer for normalization)
    if len(word) == 4:
        if word in ALWAYS_ENGLISH:
            return 'english'
        return 'urdu'
    
    return 'urdu'

frozen = {}
urdu_vocab = {}
ambiguous = {}

for word, freq in vocab.items():
    label = classify_token(word, freq)
    if label == 'english':
        frozen[word] = freq
    else:
        urdu_vocab[word] = freq

print(f"Total vocab: {len(vocab)}")
print(f"Frozen English: {len(frozen)}")
print(f"Urdu (to normalize): {len(urdu_vocab)}")

print(f"\nSample frozen English:")
for w, c in sorted(frozen.items(), key=lambda x: -x[1])[:25]:
    print(f"  {w}({c})", end="  ")

print(f"\n\nSample Urdu vocab (high freq):")
for w, c in sorted(urdu_vocab.items(), key=lambda x: -x[1])[:25]:
    print(f"  {w}({c})", end="  ")

# Sanity check - make sure key Urdu words are in urdu_vocab
print(f"\n\nSanity check - key Urdu words in urdu_vocab:")
check_words = ['hai', 'mein', 'tha', 'nahi', 'ka', 'ki', 'aur', 
               'bhai', 'ap', 'koi', 'sab', 'log', 'par', 'say']
for w in check_words:
    loc = 'URDU' if w in urdu_vocab else 'FROZEN' if w in frozen else 'NOT IN VOCAB'
    print(f"  {w}: {loc}")

# Save
with open("frozen_english_v2.json", "w", encoding="utf-8") as f:
    json.dump(frozen, f, ensure_ascii=False, indent=2)

with open("urdu_vocab_v2.json", "w", encoding="utf-8") as f:
    json.dump(urdu_vocab, f, ensure_ascii=False, indent=2)

print(f"\nSaved frozen_english_v2.json and urdu_vocab_v2.json")