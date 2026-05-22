import json

with open("eval_data.json", "r", encoding="utf-8") as f:
    eval_data = json.load(f)

with open("claude_baseline_input.txt", "w", encoding="utf-8") as f:
    f.write("ROMAN URDU NORMALIZATION TASK\n")
    f.write("="*60 + "\n\n")
    f.write("Instructions for Claude:\n")
    f.write("Normalize each Roman Urdu sentence below.\n")
    f.write("Rules:\n")
    f.write("- Fix Roman Urdu spelling variants to standard forms\n")
    f.write("- Examples: bht→bohat, nhi→nahi, me→mein, ap→aap, ye→yeh, wo→woh, or→aur, to→toh, ha→hai, kr→kar, rha→raha\n")
    f.write("- Keep ALL English words exactly as they are\n")
    f.write("- Do NOT translate to Urdu script\n")
    f.write("- Do NOT add or remove words\n")
    f.write("- Do NOT change meaning\n")
    f.write("- Return ONLY the normalized sentence, nothing else\n\n")
    f.write("="*60 + "\n\n")
    f.write("For each sentence, output exactly:\n")
    f.write("ID: [number]\n")
    f.write("OUTPUT: [normalized sentence]\n\n")
    f.write("="*60 + "\n\n")

    for item in eval_data:
        f.write(f"ID: {item['id']}\n")
        f.write(f"INPUT: {item['original']}\n\n")

print("Saved claude_baseline_input.txt")
print(f"Total sentences: {len(eval_data)}")