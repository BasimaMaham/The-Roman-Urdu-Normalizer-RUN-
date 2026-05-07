import json
import numpy as np
from collections import defaultdict
import re
from gensim.models import FastText

print("Loading data...")
with open("urdu_vocab_v2.json", "r", encoding="utf-8") as f:
    urdu_vocab = json.load(f)

with open("cleaned_sentences.txt", "r", encoding="utf-8") as f:
    sentences = [line.strip().split() for line in f if line.strip()]

words_list = list(urdu_vocab.keys())
print(f"Words to embed: {len(words_list)}")
print(f"Sentences: {len(sentences)}")

# Train FastText using gensim - pure Python, no C++ needed
# Character n-grams (min_n=2, max_n=5) capture Roman Urdu variant patterns
print("\nTraining FastText model (this takes 5-10 minutes)...")
model = FastText(
    sentences=sentences,
    vector_size=100,
    window=5,
    min_count=3,
    sg=1,              # skipgram
    min_n=2,           # min char n-gram
    max_n=5,           # max char n-gram
    epochs=10,
    workers=4,
    seed=42
)
print("Model trained.")

# Get normalized embeddings for all vocab words
print("Extracting word vectors...")
word_embeddings = {}
for word in words_list:
    try:
        vec = model.wv[word]
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        word_embeddings[word] = vec
    except KeyError:
        pass

words_with_emb = list(word_embeddings.keys())
words_array = np.array([word_embeddings[w] for w in words_with_emb])
print(f"Embedding matrix shape: {words_array.shape}")

# Save
np.save("word_embeddings_v2.npy", words_array)
with open("words_list_v2.json", "w", encoding="utf-8") as f:
    json.dump(words_with_emb, f, ensure_ascii=False)
model.save("fasttext_roman_urdu.model")

print("Saved word_embeddings_v2.npy, words_list_v2.json, fasttext_roman_urdu.model")

# Sanity check - nearest neighbors
print("\nSanity check - nearest neighbors:")
test_words = ['bohat', 'nahi', 'bhai', 'acha', 'kal', 'karna', 'achha']
word_idx = {w: i for i, w in enumerate(words_with_emb)}

for test_word in test_words:
    if test_word not in word_idx:
        print(f"  {test_word}: not in vocab")
        continue
    idx = word_idx[test_word]
    query = words_array[idx]
    sims = words_array @ query
    top_indices = np.argsort(sims)[::-1][1:10]
    neighbors = [(words_with_emb[i], round(float(sims[i]), 3)) for i in top_indices]
    print(f"  {test_word}: {neighbors}")

# OOV test - fastText handles these via character n-grams
print("\nOOV variant test:")
oov_tests = ['bht', 'boht', 'bhot', 'nhi', 'accha', 'achha', 'krnا']
for oov in oov_tests:
    try:
        vec = model.wv[oov]
        vec = vec / np.linalg.norm(vec)
        sims = words_array @ vec
        top_indices = np.argsort(sims)[::-1][:6]
        neighbors = [(words_with_emb[i], round(float(sims[i]), 3)) for i in top_indices]
        print(f"  '{oov}' -> {neighbors}")
    except Exception as e:
        print(f"  '{oov}' -> error: {e}")

print("\nDone.")