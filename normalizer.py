import json
import re
import numpy as np
from gensim.models import FastText
import nltk
nltk.download('words', quiet=True)
from nltk.corpus import words as nltk_words

print("Loading normalizer...")

with open("normalization_dict_final.json", "r", encoding="utf-8") as f:
    norm_dict = json.load(f)
with open("urdu_vocab_v2.json", "r", encoding="utf-8") as f:
    urdu_vocab = json.load(f)

ft_model = FastText.load("fasttext_roman_urdu.model")
words_array = np.load("word_embeddings_v2.npy")
with open("words_list_v2.json", "r", encoding="utf-8") as f:
    words_list = json.load(f)

english_dict = set(w.lower() for w in nltk_words.words())

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
    'exam', 'test', 'result', 'marks', 'degree', 'job', 'work',
    'family', 'friend', 'life', 'love', 'heart', 'mind', 'money',
    'today', 'tomorrow', 'yesterday', 'morning', 'night', 'day', 'time',
    'quality', 'product', 'price', 'service', 'delivery', 'order',
    'paper', 'tough', 'easy', 'hard', 'fast', 'slow', 'big', 'small',
    'received', 'packaging', 'seller', 'recommended', 'satisfied',
    'review', 'rating', 'stars', 'shipping', 'item', 'worth', 'price',
    # Common English verbs and pronouns that are unambiguously English
    'it', 'its', 'am', 'are', 'was', 'were', 'be', 'been',
    'do', 'does', 'did', 'go', 'goes', 'went', 'gone',
    'want', 'wants', 'wanted', 'need', 'needs', 'needed',
    'look', 'looks', 'looked', 'see', 'seen', 'saw',
    'get', 'gets', 'got', 'give', 'gives', 'gave',
    'make', 'makes', 'made', 'take', 'takes', 'took',
    'come', 'comes', 'came', 'know', 'knows', 'knew',
    'think', 'thinks', 'thought', 'say', 'says', 'said',
    'use', 'used', 'using', 'show', 'shows', 'showed',
    'happy', 'sad', 'great', 'nice', 'best', 'worst',
    'new', 'old', 'long', 'short', 'high', 'low',
    'first', 'last', 'next', 'same', 'other', 'such',
    'how', 'who', 'why', 'where', 'all', 'any', 'both',
    'few', 'more', 'most', 'other', 'some', 'such',
    'into', 'over', 'under', 'again', 'further',
    'once', 'own', 'same', 'than', 'too', 'very',
    'can', 'will', 'just', 'don', 'should', 'now',
    'receive', 'received', 'matter', 'matters',
}

# Ambiguous words — exist in both English and Urdu
# In English-dominant sentences these should be frozen
# In Urdu-dominant sentences these should be normalized
AMBIGUOUS = {
    'to', 'or', 'me', 'is', 'in', 'on', 'at', 'do', 'go',
    'so', 'be', 'by', 'an', 'as', 'if', 'of', 'it', 'he',
    'we', 'us', 'am', 'are', 'was', 'were', 'has', 'had',
    'did', 'got', 'get', 'let', 'put', 'set', 'run', 'see',
}

URDU_PROTECTED = {
    'hai', 'ha', 'hy', 'hain', 'hen', 'tha', 'thi', 'the', 'thy',
    'mein', 'me', 'main', 'mai', 'ka', 'ki', 'ke', 'ko', 'k',
    'se', 'say', 'ne', 'na', 'ni', 'aur', 'or', 'par', 'per', 'pey',
    'to', 'toh', 'bhi', 'bi', 'nahi', 'nhi', 'nahin', 'koi', 'kuch',
    'sab', 'sub', 'jo', 'wo', 'woh', 'voh', 'ye', 'yeh', 'ap', 'aap',
    'hum', 'ham', 'in', 'un', 'is', 'us', 'ho', 'kar', 'log',
    'allah', 'bhai', 'ab', 'aaj', 'kal', 'phir', 'fir', 'fer',
    'raha', 'rahi', 'rahe', 'rha', 'rhi', 'rhe',
    'parcha', 'parchay', 'prcha',
    'hmry', 'hmra', 'hmri', 'hmare', 'hmary',
}

KNOWN_URDU_WORDS = {
    'parcha', 'parchay', 'yaar', 'yar', 'baat', 'kaam', 'naam',
    'khabar', 'shakal', 'jawab', 'sawal', 'kitab', 'qalam',
    'dunya', 'duniya', 'aasman', 'zameen', 'paani', 'aag',
}
urdu_vocab.update({w: 1 for w in KNOWN_URDU_WORDS})

print(f"Normalizer ready. Rules: {len(norm_dict)}")

# ================================================================
# SENTENCE-LEVEL LANGUAGE DETECTION
# ================================================================

def detect_language_ratio(tokens):
    """
    Returns the ratio of tokens that are clearly English.
    Used to decide how aggressively to freeze ambiguous words.
    """
    if not tokens:
        return 0.0

    english_count = 0
    urdu_count = 0

    for t in tokens:
        tl = t.lower()
        # Clear English signals
        if tl in ALWAYS_ENGLISH:
            english_count += 1
        # Clear Urdu signals
        elif tl in URDU_PROTECTED:
            urdu_count += 1
        # In English dictionary and not Urdu protected
        elif len(tl) >= 4 and tl in english_dict and tl not in URDU_PROTECTED:
            english_count += 0.5  # partial signal
        # In norm_dict = definitely Roman Urdu variant
        elif tl in norm_dict:
            urdu_count += 1

    total = english_count + urdu_count
    if total == 0:
        return 0.0
    return english_count / total

def is_english_dominant(tokens):
    """Returns True if sentence is predominantly English."""
    ratio = detect_language_ratio(tokens)
    return ratio > 0.65

# ================================================================
# FREEZE LAYER — now sentence-aware
# ================================================================

# Words that are ALWAYS Urdu regardless of sentence context
# These would never appear in a pure English sentence
ALWAYS_URDU = {
    'hai', 'hain', 'tha', 'thi', 'nahi', 'bohat', 'aur',
    'mein', 'main', 'ka', 'ki', 'ke', 'ko', 'se', 'ne',
    'kya', 'yeh', 'woh', 'aap', 'hum', 'bhi', 'phir',
    'raha', 'rahi', 'rahe', 'karo', 'karna', 'jana',
}

def is_english(token, original, sentence_is_english=False):
    t = token.lower()

    # Always-Urdu words: never freeze regardless of sentence
    if t in ALWAYS_URDU:
        return False

    # In English-dominant sentences: freeze ambiguous short words too
    if sentence_is_english and t in URDU_PROTECTED:
        return True

    # In Urdu-dominant sentences: protect all Urdu words
    if t in URDU_PROTECTED:
        return False
    if t in ALWAYS_ENGLISH:
        return True
    if len(t) <= 2:
        # Very short words: freeze if English-dominant sentence
        return sentence_is_english

    # Ambiguous words (to, or, me, is etc.)
    # In English-dominant sentences: freeze them
    # In Urdu-dominant sentences: let them through for normalization
    if t in AMBIGUOUS:
        return sentence_is_english

    # Capitalized mid-sentence = likely proper noun = freeze
    if original[0].isupper() and t in english_dict and t not in URDU_PROTECTED:
        return True

    if len(t) >= 5 and t in english_dict and t not in URDU_PROTECTED:
        return True

    return False

# ================================================================
# OOV HANDLER
# ================================================================

def find_nearest_canonical(token):
    try:
        vec = ft_model.wv[token]
        norm_val = np.linalg.norm(vec)
        if norm_val == 0:
            return token
        vec = vec / norm_val
        sims = words_array @ vec
        top_indices = np.argsort(sims)[::-1][:5]
        for idx in top_indices:
            candidate = words_list[idx]
            return norm_dict.get(candidate, candidate)
    except:
        pass
    return token

# ================================================================
# CORE TOKEN NORMALIZER
# ================================================================

def normalize_token(token, is_sentence_start=False, sentence_is_english=False):
    """
    Returns (normalized_token, status)
    status: 'frozen' | 'direct' | 'canonical' | 'oov' | 'unchanged'
    """
    original = token
    t = token.lower()

    # Step 1: Freeze check — now sentence-aware
    check_original = token if not is_sentence_start else token.lower()
    if is_english(t, check_original, sentence_is_english):
        return original, 'frozen'

    # Step 2: Direct lookup
    if t in norm_dict:
        canonical = norm_dict[t]
        if is_sentence_start and original[0].isupper():
            canonical = canonical.capitalize()
        return canonical, 'direct'

    # Step 3: Already canonical
    if t in urdu_vocab:
        return original, 'canonical'

    # Step 4: OOV - conservative
    if (original[0].islower() and
            len(t) >= 4 and
            any(c in t for c in 'aeiou') and
            t not in URDU_PROTECTED):
        nearest = find_nearest_canonical(t)
        if nearest != t:
            return nearest, 'oov'

    return original, 'unchanged'

# ================================================================
# SENTENCE NORMALIZER — updated with language detection
# ================================================================

def normalize_text(text, verbose=False):
    if not isinstance(text, str) or not text.strip():
        return text

    tokens = text.split()

    # Detect sentence language BEFORE normalizing
    sentence_is_english = is_english_dominant(tokens)

    normalized_tokens = []

    for i, token in enumerate(tokens):
        is_first = (i == 0)

        prefix = ''
        suffix = ''
        core = token
        while core and not core[0].isalpha():
            prefix += core[0]
            core = core[1:]
        while core and not core[-1].isalpha():
            suffix = core[-1] + suffix
            core = core[:-1]

        if not core:
            normalized_tokens.append(token)
            continue

        normalized_core, status = normalize_token(
            core,
            is_sentence_start=is_first,
            sentence_is_english=sentence_is_english
        )

        if verbose:
            if status == 'direct':
                print(f"  [{core}→{normalized_core}]", end=' ')
            elif status == 'frozen':
                print(f"  [EN:{core}]", end=' ')
            elif status == 'oov':
                print(f"  [OOV:{core}→{normalized_core}]", end=' ')
            else:
                print(f"  {core}", end=' ')

        normalized_tokens.append(prefix + normalized_core + suffix)

    return ' '.join(normalized_tokens)