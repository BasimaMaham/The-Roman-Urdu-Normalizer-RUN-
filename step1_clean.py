import pandas as pd
import re
from collections import Counter
import json

df = pd.read_csv("consolidated_roman.csv")

def tokenize(text):
    if not isinstance(text, str):
        return []
    text = text.lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'\b\d+\b', '', text)
    tokens = re.findall(r'\b[a-z][a-z\-\']*[a-z]\b|\b[a-z]\b', text)
    return tokens

# Noise filter: words with 3+ consecutive same letters are likely noise
def is_noise(word):
    for i in range(len(word) - 2):
        if word[i] == word[i+1] == word[i+2]:
            return True
    return False

# Build clean frequency table
all_tokens = []
for text in df['text'].dropna():
    all_tokens.extend(tokenize(text))

freq = Counter(all_tokens)

# Filter: min frequency 5, not noise, length 2-20
vocab = {
    w: c for w, c in freq.items()
    if c >= 5
    and not is_noise(w)
    and 2 <= len(w) <= 20
}

print(f"Raw unique tokens: {len(freq)}")
print(f"Clean vocab size: {len(vocab)}")
print(f"\nSample - removing noise:")
noise_examples = [w for w in freq if is_noise(w) and freq[w] >= 5][:15]
print(f"  Noise words filtered: {noise_examples}")

# Save clean vocab
with open("vocab_freq.json", "w", encoding="utf-8") as f:
    json.dump(vocab, f, ensure_ascii=False, indent=2)

# Save cleaned sentences (we need these for co-occurrence later)
cleaned_rows = []
for text in df['text'].dropna():
    tokens = [t for t in tokenize(text) if t in vocab]
    if len(tokens) >= 3:
        cleaned_rows.append(" ".join(tokens))

with open("cleaned_sentences.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(cleaned_rows))

print(f"\nClean sentences saved: {len(cleaned_rows)}")
print(f"Vocab saved to vocab_freq.json")
print(f"\nSample cleaned sentences:")
for s in cleaned_rows[:5]:
    print(f"  {s}")