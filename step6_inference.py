from normalizer import normalize_text, detect_language_ratio, is_english_dominant

print("\n" + "="*60)
print("INFERENCE TESTS — including English context fix")
print("="*60)

test_sentences = [
    ("bht accha tha yar",                        "bohat acha tha yaar"),
    ("nhi karna mujhy yeh",                      "nahi karna mujhy yeh"),
    ("Paper bohat tough tha yaar",               "Paper bohat tough tha yaar"),
    ("University mein exams bohat mushkil hain", "University mein exams bohat mushkil hain"),
    ("mera phone bohat slow hai",                "mera phone bohat slow hai"),
    ("bhai bht zyada tension mt lo",             "bhai bohat zyada tension mt lo"),
    ("blkl sahi keh raha hai tu",                "bilkul sahi keh raha hai tu"),
    ("bkwas band karo yaar",                     "bakwas band karo yaar"),
    ("Parcha was tough yar",                     "Parcha was tough yaar"),
    ("hmry exams start hain",                    "hamaray exams start hain"),
    ("kya kar rha hai tu abhi",                  "kya kar raha hai tu abhi"),
    ("nhi pta mujhe",                            "nahi pata mujhe"),
    ("bohat mushkil hai yeh smjhna",             "bohat mushkil hai yeh samajhna"),
    ("am very happy to receive it",              "am very happy to receive it"),
    ("good or bad it does not matter",           "good or bad it does not matter"),
    ("it looks good to me",                      "it looks good to me"),
    ("for the price its really good or bad",     "for the price its really good or bad"),
    ("I want to go to school",                   "I want to go to school"),
    ("bohat acha tha yar or bhi",                "bohat acha tha yaar aur bhi"),
    ("nahi pata mein to ghar ja raha hun",       "nahi pata mein toh ghar ja raha hun"),
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

print("\n" + "="*60)
print("LANGUAGE DETECTION TEST")
print("="*60)

detection_tests = [
    "am very happy to receive it the quality was good",
    "bohat acha tha yaar bilkul sahi",
    "bhai bht zyada tension mt lo university mein",
    "Paper bohat tough tha yaar",
    "good or bad it does not matter to me",
    "nhi pta mujhe kya karna hai",
]

for sent in detection_tests:
    tokens = sent.split()
    ratio = detect_language_ratio(tokens)
    dominant = "ENGLISH" if is_english_dominant(tokens) else "URDU"
    print(f"  [{dominant} {ratio:.2f}] {sent}")

print("\n" + "="*60)
print("VERBOSE EXAMPLE")
print("="*60)
example = "bhai bht zyada tension mt lo university mein"
print(f"Input:  {example}")
print("Tokens: ", end='')
result = normalize_text(example, verbose=True)
print(f"\nOutput: {result}")