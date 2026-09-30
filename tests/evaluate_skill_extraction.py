"""
Skill Extraction Evaluation

Runs the deterministic skill extraction pipeline (no LLM) on the labelled
cases in tests/skill_extraction_cases.py and reports recall, precision,
missed skills and false positives.

Two inputs are evaluated for every resume:
- "raw":     text exactly as returned by the PDF extraction pipeline
- "cleaned": text after preprocessing.text_cleaner.advanced_clean_text

Usage (from the repository root):
    python tests/evaluate_skill_extraction.py
    python tests/evaluate_skill_extraction.py --markdown > report.md
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from preprocessing.text_cleaner import advanced_clean_text
from preprocessing.skill_extraction_pipeline import extract_skills
from tests.skill_extraction_cases import SYNTHETIC_CASES, PDF_CASES


def load_cases():
    cases = []
    for case in SYNTHETIC_CASES:
        cases.append({**case, "raw_text": case["text"]})

    for case in PDF_CASES:
        if not case["pdf"].exists():
            continue
        from pdf_parser.pdf_reader import extract_text_from_pdf
        extraction = extract_text_from_pdf(str(case["pdf"]), enable_ocr=False)
        cases.append({
            **case,
            "raw_text": extraction["text"],
            "parser_used": extraction.get("parser_used"),
        })
    return cases


def score_case(expected, acceptable, extracted):
    extracted = set(extracted)
    true_positives = extracted & expected
    false_positives = extracted - expected - acceptable
    missed = expected - extracted
    counted = len(true_positives) + len(false_positives)

    recall = len(true_positives) / len(expected) if expected else 1.0
    precision = len(true_positives) / counted if counted else 1.0
    return {
        "recall": round(recall * 100, 1),
        "precision": round(precision * 100, 1),
        "true_positives": sorted(true_positives),
        "false_positives": sorted(false_positives),
        "missed": sorted(missed),
        "extracted_count": len(extracted),
    }


def evaluate():
    results = []
    for case in load_cases():
        inputs = {
            "raw": case["raw_text"],
            "cleaned": advanced_clean_text(case["raw_text"]),
        }
        for input_name, text in inputs.items():
            extracted = extract_skills(text, enable_llm=False)["extracted_skills"]
            results.append({
                "case": case["name"],
                "input": input_name,
                **score_case(case["expected"], case["acceptable"], extracted),
            })
    return results


def summarize(results, input_name):
    rows = [r for r in results if r["input"] == input_name]
    tp = sum(len(r["true_positives"]) for r in rows)
    fp = sum(len(r["false_positives"]) for r in rows)
    fn = sum(len(r["missed"]) for r in rows)
    recall = tp / (tp + fn) if tp + fn else 1.0
    precision = tp / (tp + fp) if tp + fp else 1.0
    return {
        "input": input_name,
        "recall": round(recall * 100, 1),
        "precision": round(precision * 100, 1),
        "true_positives": tp,
        "false_positives": fp,
        "missed": fn,
    }


def print_markdown(results):
    print("| Case | Input | Recall % | Precision % | Extracted | Missed | False positives |")
    print("|---|---|---|---|---|---|---|")
    for r in results:
        print(
            f"| {r['case']} | {r['input']} | {r['recall']} | {r['precision']} | "
            f"{r['extracted_count']} | {', '.join(r['missed']) or '-'} | "
            f"{', '.join(r['false_positives']) or '-'} |"
        )
    print()
    print("| Input | Micro recall % | Micro precision % | TP | FP | Missed |")
    print("|---|---|---|---|---|---|")
    for input_name in ("raw", "cleaned"):
        s = summarize(results, input_name)
        print(
            f"| {s['input']} | {s['recall']} | {s['precision']} | "
            f"{s['true_positives']} | {s['false_positives']} | {s['missed']} |"
        )


def print_plain(results):
    for r in results:
        print(f"\n=== {r['case']} [{r['input']}]")
        print(f"recall={r['recall']}%  precision={r['precision']}%  extracted={r['extracted_count']}")
        print(f"missed:          {r['missed']}")
        print(f"false positives: {r['false_positives']}")
    print()
    for input_name in ("raw", "cleaned"):
        print(summarize(results, input_name))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--markdown", action="store_true")
    args = parser.parse_args()

    results = evaluate()
    if args.markdown:
        print_markdown(results)
    else:
        print_plain(results)
