# RUN — Roman Urdu Normalizer
Context-Aware Lexical Normalization for Code-Switched Pakistani Digital Text
CSCS-366: Introduction to Natural Language Processing 


## What This Is

Pakistani social media text mixes Urdu (written in English letters) with English. The same Urdu word gets spelled dozens of different ways — "bohat", "bht", "boht", "bhot" all mean "very/much". Standard NLP tools treat these as completely different words, breaking search, sentiment analysis, and chatbot intent detection.

RUN is an **unsupervised preprocessing pipeline** that standardizes Roman Urdu spelling variants into a consistent canonical form, while leaving English tokens untouched.

```
Input:  "bhaii bht zyada tension mt lo university mein"
Output: "bhai bohat zyada tension mt lo university mein"

Input:  "Paper boht tough tha yar"
Output: "Paper bohat tough tha yaar"   ← English tokens frozen correctly
```


## How It Works

The pipeline has six stages:

|Stage|Script|What it does|
|-|-|-|
|1|`step1_clean.py`|Tokenize, remove noise, build frequency vocabulary|
|2|`step2b_fix_freeze.py`|Separate English tokens (freeze) from Urdu candidates|
|3|`step3b_gensim.py`|Train FastText embeddings on Roman Urdu corpus|
|4|`step4b_cluster_fix.py`|Centroid-based clustering of variant words|
|5|`step5b_safe_merge.py`|Canonicalization via frequency + UrduPhone + manual rules|
|6|`normalizer.py`|Inference pipeline for new text|
|7|`step7_create_eval.py`|Build 200-sentence human evaluation set|
|8|`step8_evaluate.py`|Compute precision metrics and error analysis|


## Key Results

* **8,219 normalization rules** induced from raw corpus with zero human labeling
* **31.6% vocabulary coverage** — nearly a third of all Roman Urdu tokens have normalization rules
* **41.2% sentence-level precision** on 200 human-annotated sentences
* **13/13 test cases passing** including code-switching scenarios
* **12.6%** of tokens actively normalized per sentence on average


## Quick Start

```bash
pip install gensim nltk numpy pandas sentence-transformers

# Run the full pipeline in order
python step1\_clean.py
python step2b\_fix\_freeze.py
python step3b\_gensim.py        # Takes 5-10 min
python step4b\_cluster\_fix.py
python step5b\_safe\_merge.py
python step6\_inference.py      # Tests the full pipeline
```

Or use the normalizer directly:

```python
from normalizer import normalize_text

result = normalize_text("bhai bht zyada tension mt lo")
print(result)  # "bhai bohat zyada tension mt lo"
```


## Main Artifact

`outputs/normalization_dict_final.json` — 8,219 rules mapping Roman Urdu variants to canonical forms. Can be used as a standalone lookup table for any Roman Urdu preprocessing task.


## Research Contribution

No published paper provides an end-to-end, unsupervised, code-switch-aware normalizer for Roman Urdu. Key novelties:

1. FastText character n-gram embeddings trained on Roman Urdu specifically
2. Centroid-based clustering with substring constraints to prevent chaining errors
3. Dedicated English freeze layer protecting code-switched tokens
4. Hybrid canonicalization combining embeddings, UrduPhone phonetic rules, and frequency statistics


## Error Analysis

Four systematic error categories identified from evaluation:

* Proper noun mangling (no NER layer) — future work
* English context interference (word-level freeze misses English in Urdu-dominant context) — future work
* Morphological form confusion (gender/tense/number) — future work
* Semantic collision (phonetically similar words with different meanings) — rare but impactful


## Team

- Basima Maham — 261031499
- Soban Khan — 261039078
- Tahreem Fatima — 261042129
