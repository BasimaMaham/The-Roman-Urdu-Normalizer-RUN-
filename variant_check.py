import pandas as pd
from collections import Counter
import re

df = pd.read_csv("consolidated_roman.csv")

# Clean tokenization - strip punctuation properly
def tokenize(text):
    if not isinstance(text, str):
        return []
    text = text.lower()
    # remove urls
    text = re.sub(r'http\S+', '', text)
    # remove numbers
    text = re.sub(r'\b\d+\b', '', text)
    # strip punctuation from word boundaries but keep hyphens inside words
    tokens = re.findall(r'\b[a-z][a-z\-\']*[a-z]\b|\b[a-z]\b', text)
    return tokens

all_tokens = []
for text in df['text'].dropna():
    all_tokens.extend(tokenize(text))

freq = Counter(all_tokens)
qualified = {w: c for w, c in freq.items() if c >= 5}

print(f"After proper tokenization:")
print(f"Unique tokens (5+ freq): {len(qualified)}")

# Now find likely variant groups by shared prefix
# Words sharing first 3 chars are candidate variants
from collections import defaultdict
prefix_groups = defaultdict(list)
for word in qualified:
    if len(word) >= 4:
        prefix_groups[word[:3]].append((word, qualified[word]))

# Show groups with 3+ members - these are your variant clusters
print(f"\nLikely variant groups (same first 3 letters, 3+ members):")
count = 0
for prefix, words in sorted(prefix_groups.items()):
    if len(words) >= 3:
        words_sorted = sorted(words, key=lambda x: -x[1])
        print(f"  [{prefix}*] " + ", ".join(f"{w}({c})" for w,c in words_sorted[:6]))
        count += 1
    if count >= 40:
        break