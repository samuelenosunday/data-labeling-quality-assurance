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

Key structure:

items is a list

Each item has an item_id and an annotations dict

annotations maps annotator names → their label for that item

Labels can be any string: "positive", "negative", "cat", "dog", "relevant", "irrelevant", etc.

Running the Tool
python qa_report.py

Optionally pass a custom file:
bash
python qa_report.py my_annotations.json

Output Example
==================================================
ANNOTATION QA REPORT
==================================================
Total items: 5
Annotators: annotator_A, annotator_B, annotator_C

--- INTER-ANNOTATOR AGREEMENT (Cohen's Kappa) ---
annotator_A vs annotator_B: 0.83  (Almost perfect)
annotator_A vs annotator_C: 0.55  (Moderate)
annotator_B vs annotator_C: 0.60  (Moderate)

--- PER-ANNOTATOR LABEL DISTRIBUTION ---
annotator_A: positive=3, negative=2, neutral=0
annotator_B: positive=3, negative=2, neutral=0
annotator_C: positive=2, negative=1, neutral=2

--- PER-ANNOTATOR AVERAGE AGREEMENT ---
annotator_A: 0.69
annotator_B: 0.71
annotator_C: 0.57  ⚠️ (potential outlier)

--- PER-ITEM DISAGREEMENT ---
item_003: 2/3 disagree
item_005: 2/3 disagree
==================================================

Files in This Repo
File	Purpose
qa_report.py	Main QA analysis script
sample_annotations.json	Example annotation dataset
README.md	This documentation

Tech Stack
Language: Python 3

Dependencies: None (standard library only)

Data format: JSON

Future Improvements
Support for Fleiss' Kappa (3+ annotators at once)

Krippendorff's Alpha (for ordinal labels)

CSV export of the QA report

Streamlit dashboard for interactive exploration

About the Author
Samuel Eno Sunday — AI Training Specialist & LLM Quality Analyst

LinkedIn: linkedin.com/in/samuelenosunday001

GitHub: github.com/samuelenosunday

Email: samuelenosunday@gmail.com

Open to remote contract, part-time, and project-based AI training roles.
