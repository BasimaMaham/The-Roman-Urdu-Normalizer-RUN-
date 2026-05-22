import json
from collections import defaultdict
import re

with open("vocab_freq.json", "r", encoding="utf-8") as f:
    vocab = json.load(f)

# English word list for freeze layer
import nltk
nltk.download('words', quiet=True)
from nltk.corpus import words as nltk_words
english_set = set(w.lower() for w in nltk_words.words())

# Common English words that appear in Pakistani text - manual additions
common_loanwords = {
    'okay', 'ok', 'please', 'thanks', 'thank', 'sorry', 'hello', 'hi',
    'yes', 'no', 'not', 'very', 'much', 'more', 'good', 'bad', 'time',
    'done', 'come', 'going', 'like', 'just', 'even', 'also', 'only',
    'really', 'actually', 'basically', 'obviously', 'seriously', 'already',
    'always', 'never', 'every', 'other', 'some', 'same', 'then', 'than',
    'they', 'them', 'their', 'there', 'here', 'when', 'what', 'which',
    'will', 'would', 'could', 'should', 'have', 'been', 'being', 'want',
    'know', 'think', 'make', 'take', 'give', 'need', 'feel', 'seem',
    'become', 'keep', 'show', 'hear', 'play', 'turn', 'start', 'might',
    'paper', 'mobile', 'phone', 'school', 'college', 'university', 'class',
    'exam', 'test', 'result', 'marks', 'degree', 'job', 'work', 'office',
    'government', 'police', 'army', 'court', 'party', 'media', 'news',
    'people', 'family', 'friend', 'life', 'love', 'heart', 'mind', 'body'
}
english_set.update(common_loanwords)

# Separate frozen (English) from Urdu candidates
frozen = {}
urdu_vocab = {}

for word, freq in vocab.items():
    if word in english_set and len(word) >= 3:
        frozen[word] = freq
    else:
        urdu_vocab[word] = freq

print(f"Total vocab: {len(vocab)}")
print(f"Frozen English tokens: {len(frozen)}")
print(f"Urdu candidate tokens: {len(urdu_vocab)}")

# Sample of what got frozen
print(f"\nSample frozen English words:")
frozen_sample = sorted(frozen.items(), key=lambda x: -x[1])[:20]
for w, c in frozen_sample:
    print(f"  {w}: {c}")

print(f"\nSample Urdu candidates (high frequency):")
urdu_sample = sorted(urdu_vocab.items(), key=lambda x: -x[1])[:30]
for w, c in urdu_sample:
    print(f"  {w}: {c}")

# Now pre-filter candidate pairs using cheap signals before expensive embedding
# Two words are candidate pairs if:
# 1. Length difference <= 3
# 2. Share at least first 2 characters OR last 2 characters  
# 3. Neither is in frozen set

print(f"\nBuilding candidate pairs for embedding...")

# Group by first 2 chars
by_prefix = defaultdict(list)
by_suffix = defaultdict(list)
for word in urdu_vocab:
    if len(word) >= 3:
        by_prefix[word[:2]].append(word)
        by_suffix[word[-2:]].append(word)

# Build candidate set
candidate_words = set()
pair_count = 0

for prefix, words in by_prefix.items():
    if len(words) >= 2:
        for w in words:
            candidate_words.add(w)
        pair_count += len(words) * (len(words)-1) // 2

for suffix, words in by_suffix.items():
    if len(words) >= 2:
        for w in words:
            candidate_words.add(w)

print(f"Words that need embedding (have at least one candidate): {len(candidate_words)}")
print(f"Estimated candidate pairs to compare: {pair_count:,}")

# Save outputs
with open("frozen_english.json", "w", encoding="utf-8") as f:
    json.dump(frozen, f, ensure_ascii=False, indent=2)

with open("urdu_vocab.json", "w", encoding="utf-8") as f:
    json.dump(urdu_vocab, f, ensure_ascii=False, indent=2)

with open("candidate_words.json", "w", encoding="utf-8") as f:
    json.dump(list(candidate_words), f, ensure_ascii=False)

print(f"\nFiles saved: frozen_english.json, urdu_vocab.json, candidate_words.json")