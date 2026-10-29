# Data Labeling QA

A Python tool for **quality assurance on annotation data**. Built for AI trainers, data annotators, and QA reviewers who need to measure inter-annotator agreement, detect label bias, and flag outliers in labeled datasets.

---

## What It Does

Given a dataset where **multiple annotators labeled the same items**, this tool produces a QA report covering:

| Check | What It Reveals |
|---|---|
| **Inter-Annotator Agreement (Cohen's Kappa)** | How consistently do two annotators agree? (Kappa accounts for chance agreement, unlike raw % match) |
| **Per-Annotator Label Distribution** | Is one annotator skewing toward a single label? (Bias detection) |
| **Per-Annotator Average Agreement** | Which annotator diverges most from the consensus? (Outlier flag) |
| **Per-Item Disagreement** | Which specific items caused the most disagreement? (These need adjudication) |

---

## Why I Built This

As an AI trainer working across platforms like Outlier, Handshake, Atlas, and RWS, I've seen how hard it is to catch bad annotations at scale. Low inter-annotator agreement, biased labeling, and outlier annotators are the biggest sources of noise in RLHF and supervised training data.

This tool automates the QA pass — giving project leads a clear signal of *data quality* before the data goes into model training.

It's the kind of check a senior annotator or QA reviewer runs to guarantee annotation quality on high-stakes projects.

---

## Input Format

The tool reads a JSON file structured like this:

```json
{
  "items": [
    {
      "item_id": "item_001",
      "annotations": {
        "annotator_A": "positive",
        "annotator_B": "positive",
        "annotator_C": "positive"
      }
    },
    {
      "item_id": "item_002",
      "annotations": {
        "annotator_A": "negative",
        "annotator_B": "negative",
        "annotator_C": "neutral"
      }
    }
  ]
}
