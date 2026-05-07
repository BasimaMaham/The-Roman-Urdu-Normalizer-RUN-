import json
import re
import numpy as np
from gensim.models import FastText
import nltk
nltk.download('words', quiet=True)
from nltk.corpus import words as nltk_words

# ================================================================
# LOAD ALL RESOURCES
# ================================================================
print("Loading resources...")

with open("normalization_dict_final.json", "r", encoding="utf-8") as f:
    norm_dict = json.load(f)

with open("urdu_vocab_v2.json", "r", encoding="utf-8") as f:
    urdu_vocab = json.load(f)

# Add known canonical words that are below frequency threshold
# These are real Urdu words that shouldn't be touched by OOV handler
KNOWN_URDU_WORDS = {
    'parcha', 'parchay', 'yaar', 'yar', 'baat', 'kaam', 'naam',
    'khabar', 'shakal', 'jawab', 'sawal', 'kitab', 'qalam',
    'dunya', 'duniya', 'aasman', 'zameen', 'paani', 'aag',
}
urdu_vocab.update({w: 1 for w in KNOWN_URDU_WORDS})

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

print(f"Normalization rules loaded: {len(norm_dict)}")

# ================================================================
# FREEZE LAYER
# ================================================================
def is_english(token, original):
    t = token.lower()
    if t in URDU_PROTECTED:
        return False
    if t in ALWAYS_ENGLISH:
        return True
    if len(t) <= 3:
        return False
    # Capitalized mid-sentence: only freeze if actually in English dict
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
        norm = np.linalg.norm(vec)
        if norm == 0:
            return token
        vec = vec / norm
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
def normalize_token(token, is_sentence_start=False):
    """
    Returns (normalized_token, status)
    status: 'frozen' | 'direct' | 'canonical' | 'oov' | 'unchanged'
    """
    original = token
    t = token.lower()

    # Step 1: Freeze check
    check_original = token if not is_sentence_start else token.lower()
    if is_english(t, check_original):
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
    # Never attempt OOV correction on capitalized words (proper nouns)
    # Never attempt on words already in URDU_PROTECTED
    if (original[0].islower() and
            len(t) >= 4 and
            any(c in t for c in 'aeiou') and
            t not in URDU_PROTECTED):
        nearest = find_nearest_canonical(t)
        if nearest != t:
            return nearest, 'oov'

    return original, 'unchanged'

# ================================================================
# SENTENCE NORMALIZER
# ================================================================
def normalize_text(text, verbose=False):
    if not isinstance(text, str) or not text.strip():
        return text

    tokens = text.split()
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

        normalized_core, status = normalize_token(core, is_sentence_start=is_first)

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

# ================================================================
# TESTS
# ================================================================
print("\n" + "="*60)
print("INFERENCE TESTS")
print("="*60)

test_sentences = [
    ("bht accha tha yar",                           "bohat acha tha yaar"),
    ("nhi karna mujhy yeh",                         "nahi karna mujhy yeh"),
    ("Paper bohat tough tha yaar",                  "Paper bohat tough tha yaar"),
    ("University mein exams bohat mushkil hain",    "University mein exams bohat mushkil hain"),
    ("mera phone bohat slow hai",                   "mera phone bohat slow hai"),
    ("bhai bht zyada tension mt lo",                "bhai bohat zyada tension mt lo"),
    ("blkl sahi keh raha hai tu",                   "bilkul sahi keh raha hai tu"),
    ("bkwas band karo yaar",                        "bakwas band karo yaar"),
    ("Parcha was tough yar",                        "Parcha was tough yaar"),
    ("hmry exams start hain",                       "hamaray exams start hain"),
    ("kya kar rha hai tu abhi",                     "kya kar raha hai tu abhi"),
    ("nhi pta mujhe",                               "nahi pata mujhe"),
    ("bohat mushkil hai yeh smjhna",                "bohat mushkil hai yeh samajhna"),
]

passed = 0
for input_sent, expected in test_sentences:
    output = normalize_text(input_sent)
    ok = "✓" if output == expected else "✗"
    if output == expected:
        passed += 1
    print(f"  {ok} IN:  {input_sent}")
    if output != expected:
        print(f"    GOT: {output}")
        print(f"    EXP: {expected}")

print(f"\nPassed: {passed}/{len(test_sentences)}")

# ================================================================
# VERBOSE EXAMPLE
# ================================================================
print("\n" + "="*60)
print("VERBOSE EXAMPLE")
print("="*60)
example = "bhai bht zyada tension mt lo university mein"
print(f"Input:  {example}")
print("Tokens: ", end='')
result = normalize_text(example, verbose=True)
print(f"\nOutput: {result}")

# ================================================================
# CORPUS STATISTICS
# ===============================