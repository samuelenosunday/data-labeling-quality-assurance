"""
Data Labeling QA
================
Quality assurance for annotation data:
- Cohen's Kappa (pairwise inter-annotator agreement)
- Per-annotator label distribution
- Per-annotator average agreement (outlier detection)
- Per-item disagreement (adjudication candidates)

Author: Samuel Eno Sunday
License: MIT
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations


# ---------------------------------------------------------
# LOADING
# ---------------------------------------------------------

def load_data(filepath):
    """Load annotation data from a JSON file."""
    path = Path(filepath)
    if not path.exists():
        print(f"Error: File not found -> {filepath}")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "items" not in data or not isinstance(data["items"], list):
        print("Error: JSON must contain an 'items' list.")
        sys.exit(1)

    return data["items"]


# ---------------------------------------------------------
# COHEN'S KAPPA
# ---------------------------------------------------------

def cohen_kappa(labels_a, labels_b):
    """
    Compute Cohen's Kappa between two annotators.
    labels_a and labels_b are lists of the same length.
    Returns kappa (float) or None if undefined (e.g., both annotators used one label).
    """
    n = len(labels_a)
    if n == 0:
        return None

    # Observed agreement (Po)
    agreements = sum(1 for a, b in zip(labels_a, labels_b) if a == b)
    po = agreements / n

    # Expected agreement (Pe) by chance
    counts_a = Counter(labels_a)
    counts_b = Counter(labels_b)
    all_labels = set(labels_a) | set(labels_b)

    pe = sum((counts_a[l] / n) * (counts_b[l] / n) for l in all_labels)

    # Avoid division by zero (both annotators used only one label)
    if pe == 1.0:
        return None

    return (po - pe) / (1 - pe)


def interpret_kappa(k):
    """Human-readable interpretation of a kappa value (Landis & Koch scale)."""
    if k is None:
        return "undefined"
    if k < 0:
        return "poor (worse than chance)"
    if k < 0.20:
        return "slight"
    if k < 0.40:
        return "fair"
    if k < 0.60:
        return "moderate"
    if k < 0.80:
        return "substantial"
    return "almost perfect"


# ---------------------------------------------------------
# ANALYSIS
# ---------------------------------------------------------

def get_annotator_list(items):
    """Collect all annotator names across all items."""
    annotators = set()
    for item in items:
        annotators.update(item["annotations"].keys())
    return sorted(annotators)


def build_label_lists(items, annotators):
    """
    Build per-annotator lists of labels, aligned by item.
    If an annotator is missing an item, we skip that item for that annotator pair
    during kappa calculation (handled below).
    """
    label_lists = defaultdict(list)
    for item in items:
        for ann in annotators:
            if ann in item["annotations"]:
                label_lists[ann].append((item["item_id"], item["annotations"][ann]))
    return label_lists


def pairwise_kappa(items, annotators):
    """Compute Cohen's Kappa for each pair of annotators."""
    results = []
    for a, b in combinations(annotators, 2):
        # Only use items where BOTH annotators labeled
        labels_a = []
        labels_b = []
        for item in items:
            ann = item["annotations"]
            if a in ann and b in ann:
                labels_a.append(ann[a])
                labels_b.append(ann[b])

        if len(labels_a) < 2:
            results.append((a, b, None, "insufficient data"))
            continue

        k = cohen_kappa(labels_a, labels_b)
        results.append((a, b, k, interpret_kappa(k)))

    return results


def label_distribution(items, annotators):
    """Count how often each annotator used each label."""
    dist = {ann: Counter() for ann in annotators}
    for item in items:
        for ann, label in item["annotations"].items():
            if ann in dist:
                dist[ann][label] += 1
    return dist


def average_agreement(items, annotators):
    """
    For each annotator, compute their average agreement with the group.
    'Agreement' here = fraction of items where their label matches the majority label.
    """
    per_annotator = {ann: {"matches": 0, "total": 0} for ann in annotators}

    for item in items:
        ann = item["annotations"]
        if len(ann) < 2:
            continue
        labels = list(ann.values())
        majority_label, majority_count = Counter(labels).most_common(1)[0]

        for annotator, label in ann.items():
            if annotator in per_annotator:
                per_annotator[annotator]["total"] += 1
                if label == majority_label:
                    per_annotator[annotator]["matches"] += 1

    averages = {}
    for annotator, counts in per_annotator.items():
        if counts["total"] == 0:
            averages[annotator] = None
        else:
            averages[annotator] = round(counts["matches"] / counts["total"], 2)

    return averages


def disagreement_items(items):
    """List items where annotators disagree, sorted by most disagreement."""
    rows = []
    for item in items:
        ann = item["annotations"]
        if len(ann) < 2:
            continue
        labels = list(ann.values())
        majority_label, majority_count = Counter(labels).most_common(1)[0]
        disagree_count = len(labels) - majority_count
        if disagree_count > 0:
            rows.append({
                "item_id": item["item_id"],
                "disagree": disagree_count,
                "total": len(labels),
            })
    rows.sort(key=lambda r: r["disagree"], reverse=True)
    return rows


# ---------------------------------------------------------
# REPORTING
# ---------------------------------------------------------

def print_report(items, annotators):
    """Print the full QA report to the console."""
    print("=" * 50)
    print("ANNOTATION QA REPORT")
    print("=" * 50)
    print(f"Total items: {len(items)}")
    print(f"Annotators: {', '.join(annotators)}\n")

    # --- 1. Pairwise Cohen's Kappa ---
    print("--- INTER-ANNOTATOR AGREEMENT (Cohen's Kappa) ---")
    kappa_results = pairwise_kappa(items, annotators)
    for a, b, k, interpretation in kappa_results:
        if k is None:
            print(f"{a} vs {b}: N/A ({interpretation})")
        else:
            print(f"{a} vs {b}: {k:.2f}  ({interpretation})")
    print()

    # --- 2. Per-annotator label distribution ---
    print("--- PER-ANNOTATOR LABEL DISTRIBUTION ---")
    dist = label_distribution(items, annotators)
    for ann in annotators:
        counts = dist[ann]
        parts = [f"{label}={count}" for label, count in counts.most_common()]
        print(f"{ann}: {', '.join(parts) if parts else '(no data)'}")
    print()

    # --- 3. Per-annotator average agreement ---
    print("--- PER-ANNOTATOR AVERAGE AGREEMENT ---")
    averages = average_agreement(items, annotators)
    valid_averages = [v for v in averages.values() if v is not None]
    overall_avg = round(sum(valid_averages) / len(valid_averages), 2) if valid_averages else None

    for ann in annotators:
        avg = averages[ann]
        if avg is None:
            print(f"{ann}: N/A")
        else:
            flag = ""
            if overall_avg is not None and avg < overall_avg - 0.15:
                flag = "  ⚠️ (potential outlier)"
            print(f"{ann}: {avg}{flag}")
    print()

    # --- 4. Per-item disagreement ---
    print("--- PER-ITEM DISAGREEMENT ---")
    dis = disagreement_items(items)
    if not dis:
        print("No disagreement — all annotators agreed on every item.")
    else:
        for row in dis:
            print(f"{row['item_id']}: {row['disagree']}/{row['total']} disagree")
    print("=" * 50)


# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------

def main():
    filepath = "sample_annotations.json"
    if len(sys.argv) > 1:
        filepath = sys.argv[1]

    print(f"Loading annotations from: {filepath}\n")
    items = load_data(filepath)
    annotators = get_annotator_list(items)

    if len(annotators) < 2:
        print("Error: Need at least 2 annotators to compute agreement.")
        sys.exit(1)

    print_report(items, annotators)


if __name__ == "__main__":
    main()
