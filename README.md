# RUN — Roman Urdu Normalizer
- **Context-Aware Unsupervised Normalization for Code-Switched Pakistani Digital Text** 
- CSCS-366: Introduction to Natural Language Processing, Spring 2026


## What This Is

Pakistani social media text mixes Urdu (written in Latin script) with English — this is called Roman Urdu. The same Urdu word gets spelled dozens of different ways: "bohat", "bht", "boht", "bhot" all mean "very/much". Standard NLP tools treat these as completely different words, breaking search, sentiment analysis, and chatbot intent detection.

**RUN** is an unsupervised preprocessing pipeline that standardizes Roman Urdu
spelling variants into consistent canonical forms, while leaving English tokens
completely untouched via a sentence-level language detection layer.

```
Input:  "bhaii bht zyada tension mt lo university mein"
Output: "bhai bohat zyada tension mt lo university mein"

Input:  "am very happy to receive it the quality was good"
Output: "am very happy to receive it the quality was good"  ← English frozen

Input:  "bohat acha tha yar or bhi"
Output: "bohat acha tha yaar aur bhi"  ← code-switched: or→aur in Urdu context
```

## Key Results

| Metric | Initial System | Final System |
|--------|---------------|--------------|
| Sentence-level precision | 41.2% | **72.3%** |
| Token-level precision | 30.8% | **54.8%** |
| F1 score | — | **83.9%** |
| Normalization rules | ~8,200 | **7,354** |

### Comparative Analysis (F1 Score)

| System | Precision | Recall | F1 |
|--------|-----------|--------|-----|
| No normalization | N/A | N/A | N/A |
| Baseline 1: Manual rules (60 rules) | 75.1% | 81.1% | 78.0% |
| Baseline 2: Edit distance | 72.5% | 0.0% | 0.0% |
| Baseline 3: Claude | 73.9% | 70.9% | 72.3% |
| Baseline 3: Gemini | 73.4% | 84.8% | 78.7% |
| Baseline 3: DeepSeek | 72.6% | 63.0% | 67.5% |
| **RUN (our system)** | **72.3%** | **100.0%** | **83.9%** |

RUN achieves the highest F1 score, outperforming all baselines, including
three large language models (Claude, Gemini, DeepSeek).

---

## How It Works

### Pipeline

| Stage | Script | What it does |
|-------|--------|--------------|
| 1 | `step1_clean.py` | Tokenize, remove noise, build frequency vocabulary |
| 2 | `step2b_fix_freeze.py` | Separate English tokens from Urdu candidates |
| 3 | `step3b_gensim.py` | Train FastText embeddings on Roman Urdu corpus |
| 4 | `step4b_cluster_fix.py` | Centroid-based clustering of variant words |
| 5 | `step5b_safe_merge.py` | Canonicalization via frequency + UrduPhone + manual rules |
| 6 | `normalizer.py` | **Main inference module** — use this for normalization |
| 7 | `step7_create_eval.py` | Build 200-sentence human evaluation set |
| 8 | `final_eval.py` | Compute precision, recall, F1 metrics |

### Key Design Decisions

**Sentence-level language detection:** If >65% of tokens in a sentence are
English signals, ambiguous words (to, or, me, is) are frozen as English.
This prevents "to→toh" in English sentences while correctly normalizing
"to" in Urdu-dominant sentences.

**FastText character n-grams:** Trained on the Roman Urdu corpus itself
(min_n=2, max_n=5). Better than pretrained multilingual models for this
low-resource, inconsistently spelled text.

**Iterative error-guided refinement:** 4 rounds of development set annotation
(899 sentences total) to identify and remove bad mappings from the dictionary.

---

## Evaluation Methodology

- **Test set:** 200 human-annotated sentences held out throughout development (seed=42)
- **Dev sets:** 4 rounds × ~200 sentences each (seeds 100, 200, 300, 400) — disjoint from test set
- **Annotation:** Each sentence judged OK (fully correct) or FIX (has errors)
- **Metrics:** Sentence precision, token precision, recall, F1

---

## Quick Start

```bash
pip install gensim nltk numpy
```

```python
from normalizer import normalize_text

# Basic usage
result = normalize_text("bhai bht zyada tension mt lo")
print(result)  # "bhai bohat zyada tension mt lo"

# English preserved
result = normalize_text("I want to go to school")
print(result)  # "I want to go to school"

# Code-switching handled
result = normalize_text("bohat acha tha yar or bhi aya")
print(result)  # "bohat acha tha yaar aur bhi aya"
```

---

## Repository Structure

- `normalization_dict_final.json`   ← Main artifact: 7,354 normalization rules
- `normalizer.py`                   ← Main module: import this for normalization
- `eval_data.json`                  ← 200-sentence human-annotated test set
- `final_annotation_sheet.txt`      ← Human-readable annotation judgments
- `final_eval_results.json`         ← Final evaluation metrics
- `all_baseline_results.json`       ← All comparative analysis results
- `step1_clean.py`                  ← Pipeline stage 1
- `step2b_fix_freeze.py`            ← Pipeline stage 2
- `step3b_gensim.py`                ← Pipeline stage 3 (FastText training)
- `step4b_cluster_fix.py`           ← Pipeline stage 4
- `step5b_safe_merge.py`            ← Pipeline stage 5
- `step6_inference.py`              ← Pipeline stage 6 (test runner)
- `final_eval.py`                   ← Evaluation script
- `baseline_b1_b2.py`               ← Baseline 1 and 2 evaluation
- `baseline_all_llms.py`            ← LLM baseline evaluation
- `round1_eval_data.json`          ← Dev set round 1 (seed=100)
- `round2_eval_data.json`          ← Dev set round 2 (seed=200)
- `round3_eval_data.json`           ← Dev set round 3 (seed=300)
- `round4_eval_data.json`           ← Dev set round 4 (seed=400)
- `round_eval_sheet.txt`           ← Human annotation sheets per round
- `patch_dict_r.py`                ← Dictionary patch scripts per round
- `claude_baseline_raw.txt`         ← Claude normalization outputs
- `gemini_baseline_raw.txt`         ← Gemini normalization outputs
- `deepseek_baseline_raw.txt`       ← DeepSeek normalization outputs

**Note:** Large files not in repository (add to `.gitignore`):
- `consolidated_roman.csv` (239K sentences raw corpus)
- `cleaned_sentences.txt` (220K sentences)
- `fasttext_roman_urdu.model` (trained model)
- `word_embeddings_v2.npy` (embeddings matrix)

---

## Main Artifact

`normalization_dict_final.json` — 7,354 rules mapping Roman Urdu variants
to canonical forms. Can be used as a standalone lookup table for any Roman
Urdu preprocessing task without running the full pipeline.

---

## Research Contribution

No published paper provides an end-to-end, unsupervised, code-switch-aware
normalizer for Roman Urdu. Key novelties:

- FastText character n-gram embeddings trained on Roman Urdu specifically
- Centroid-based clustering with threshold-based canonicalization
- Sentence-level English freeze layer protecting code-switched tokens
- Iterative error-guided dictionary refinement methodology
- Comprehensive evaluation against manual rules, edit distance, and LLM baselines

---

## Team

- Basima Maham — 261031499
- Soban Khan — 261039078
- Tahreem Fatima — 261042129
