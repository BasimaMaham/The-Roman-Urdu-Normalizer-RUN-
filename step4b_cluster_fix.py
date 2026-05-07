import json
import numpy as np
from collections import defaultdict

print("Loading embeddings...")
words_array = np.load("word_embeddings_v2.npy")
with open("words_list_v2.json", "r", encoding="utf-8") as f:
    words_list = json.load(f)
with open("urdu_vocab_v2.json", "r", encoding="utf-8") as f:
    urdu_vocab = json.load(f)

word_idx = {w: i for i, w in enumerate(words_list)}
print(f"Vocab: {len(words_list)} words")

# ================================================================
# STRICT CLUSTERING - no chaining allowed
# 
# Instead of union-find, we use a centroid-based approach:
# A word can only join a cluster if it is similar to the CENTROID
# of that cluster, not just to one member.
# This prevents the chaining problem entirely.
#
# Additionally, we add hard linguistic constraints:
# Two words can only be variants if they share a common substring
# of length >= 3. This prevents phonetically similar but 
# semantically unrelated words from merging.
# ================================================================

SIMILARITY_THRESHOLD = 0.82   # raised from 0.75
MAX_LENGTH_DIFF = 3
MIN_SHARED_SUBSTR = 3          # must share at least 3 consecutive chars

def shares_substring(w1, w2, min_len=3):
    """Check if two words share a common substring of at least min_len chars."""
    if len(w1) < min_len or len(w2) < min_len:
        return len(w1) >= 2 and len(w2) >= 2  # short words get a pass
    for i in range(len(w1) - min_len + 1):
        substr = w1[i:i+min_len]
        if substr in w2:
            return True
    return False

def get_sim(i, j):
    return float(words_array[i] @ words_array[j])

# Step 1: Find all valid pairs with strict constraints
print(f"Finding strict candidate pairs (threshold={SIMILARITY_THRESHOLD})...")
BATCH_SIZE = 1000
valid_pairs = defaultdict(list)  # word_idx -> [(neighbor_idx, sim)]

for batch_start in range(0, len(words_list), BATCH_SIZE):
    batch_end = min(batch_start + BATCH_SIZE, len(words_list))
    batch_vecs = words_array[batch_start:batch_end]
    sims = batch_vecs @ words_array.T

    for i_local, (word, sim_row) in enumerate(
            zip(words_list[batch_start:batch_end], sims)):
        i_global = batch_start + i_local
        word_len = len(word)

        top_indices = np.argsort(sim_row)[::-1][1:20]
        for j in top_indices:
            sim = float(sim_row[j])
            if sim < SIMILARITY_THRESHOLD:
                break
            neighbor = words_list[j]

            # Hard constraint 1: length difference
            if abs(word_len - len(neighbor)) > MAX_LENGTH_DIFF:
                continue

            # Hard constraint 2: must share a common substring
            if not shares_substring(word, neighbor, MIN_SHARED_SUBSTR):
                continue

            if i_global < j:
                valid_pairs[i_global].append((j, sim))
                valid_pairs[j].append((i_global, sim))

total_pairs = sum(len(v) for v in valid_pairs.values()) // 2
print(f"Valid pairs after strict constraints: {total_pairs:,}")

# Step 2: Centroid-based greedy clustering
# Process words from highest frequency to lowest
# (so canonical forms tend to be the seeds)
print("Building clusters (centroid-based, no chaining)...")

word_order = sorted(range(len(words_list)),
                    key=lambda i: -urdu_vocab.get(words_list[i], 0))

assigned = {}   # word_idx -> cluster_id
clusters = {}   # cluster_id -> {"members": [], "centroid": vec, "sum_vec": vec}
cluster_id_counter = 0

for i in word_order:
    if i in assigned:
        continue

    word = words_list[i]
    neighbors = valid_pairs.get(i, [])

    if not neighbors:
        # Singleton
        assigned[i] = cluster_id_counter
        clusters[cluster_id_counter] = {
            "members": [i],
            "sum_vec": words_array[i].copy(),
            "centroid": words_array[i].copy()
        }
        cluster_id_counter += 1
        continue

    # Try to find an existing cluster to join
    # Must be similar to CENTROID (not just one member)
    best_cluster = None
    best_sim = SIMILARITY_THRESHOLD

    for existing_cid, cluster_data in clusters.items():
        centroid = cluster_data["centroid"]
        sim_to_centroid = float(words_array[i] @ centroid)
        if sim_to_centroid > best_sim:
            # Also check shared substring with canonical member
            canonical_idx = cluster_data["members"][0]
            canonical_word = words_list[canonical_idx]
            if shares_substring(word, canonical_word, MIN_SHARED_SUBSTR):
                best_sim = sim_to_centroid
                best_cluster = existing_cid

    if best_cluster is not None:
        # Join existing cluster
        assigned[i] = best_cluster
        clusters[best_cluster]["members"].append(i)
        # Update centroid
        n = len(clusters[best_cluster]["members"])
        clusters[best_cluster]["sum_vec"] += words_array[i]
        new_centroid = clusters[best_cluster]["sum_vec"] / n
        norm = np.linalg.norm(new_centroid)
        if norm > 0:
            clusters[best_cluster]["centroid"] = new_centroid / norm
        else:
            clusters[best_cluster]["centroid"] = new_centroid
    else:
        # Start new cluster
        assigned[i] = cluster_id_counter
        clusters[cluster_id_counter] = {
            "members": [i],
            "sum_vec": words_array[i].copy(),
            "centroid": words_array[i].copy()
        }
        cluster_id_counter += 1

# Step 3: Separate real clusters from singletons
real_clusters = {cid: data for cid, data in clusters.items()
                 if len(data["members"]) > 1}
singletons = {cid: data for cid, data in clusters.items()
              if len(data["members"]) == 1}

print(f"Total clusters: {len(clusters)}")
print(f"Multi-word clusters: {len(real_clusters)}")
print(f"Singletons: {len(singletons)}")

# Step 4: Canonicalization
print("\nSelecting canonical forms...")
normalization_dict = {}
cluster_info = []

for cid, data in real_clusters.items():
    member_indices = data["members"]
    members = [words_list[i] for i in member_indices]
    member_freqs = [(w, urdu_vocab.get(w, 0)) for w in members]
    canonical = max(member_freqs, key=lambda x: x[1])[0]

    for word in members:
        if word != canonical:
            normalization_dict[word] = canonical

    cluster_info.append({
        "canonical": canonical,
        "members": sorted(members, key=lambda w: -urdu_vocab.get(w, 0)),
        "size": len(members)
    })

cluster_info.sort(key=lambda x: -x["size"])

# Step 5: Display results
print(f"Normalization rules: {len(normalization_dict)}")
print(f"\nMax cluster size: {max(len(d['members']) for d in real_clusters.values())}")

print("\n" + "="*60)
print("SAMPLE CLUSTERS")
print("="*60)
for info in cluster_info[:40]:
    members_str = ", ".join(
        f"{w}({urdu_vocab.get(w,0)})" for w in info["members"][:8])
    print(f"  → {info['canonical']} | {members_str}")

print("\n" + "="*60)
print("CLUSTER SIZE DISTRIBUTION")
print("="*60)
sizes = [info["size"] for info in cluster_info]
print(f"  Size 2:    {sum(1 for s in sizes if s == 2)}")
print(f"  Size 3-5:  {sum(1 for s in sizes if 3 <= s <= 5)}")
print(f"  Size 6-10: {sum(1 for s in sizes if 6 <= s <= 10)}")
print(f"  Size 11+:  {sum(1 for s in sizes if s > 10)}")
print(f"  Largest:   {max(sizes)}")

# Step 6: Spot check specific word groups
print("\n" + "="*60)
print("SPOT CHECKS")
print("="*60)
spot_checks = ["bohat", "nahi", "acha", "bilkul",
               "bakwas", "duniya", "bhai", "karna"]
word_to_canonical = {v: v for v in urdu_vocab}
word_to_canonical.update(normalization_dict)

for word in spot_checks:
    canonical = word_to_canonical.get(word, "NOT IN VOCAB")
    # Find all words that map to this canonical
    variants = [w for w, c in normalization_dict.items()
                if c == canonical or (w == word and c == word)]
    variants_str = ", ".join(variants[:10])
    print(f"  {word} → {canonical} | variants: {variants_str}")

# Save
with open("normalization_dict_v2.json", "w", encoding="utf-8") as f:
    json.dump(normalization_dict, f, ensure_ascii=False, indent=2)
with open("cluster_info_v2.json", "w", encoding="utf-8") as f:
    json.dump(cluster_info[:500], f, ensure_ascii=False, indent=2)

print(f"\nSaved normalization_dict_v2.json ({len(normalization_dict)} rules)")