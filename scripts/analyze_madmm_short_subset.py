#!/usr/bin/env python3
import argparse
import json
import math
import re
from pathlib import Path


METHOD_FILES = {
    "cot": "cot_seed41.json",
    "mad_naive": "mad_3agents_2rounds_seed41.json",
    "mad_objective": "mad_objective_3agents_2rounds_seed41.json",
    "mad_subjective": "mad_subjective_3agents_2rounds_seed41.json",
}


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def extract_ground_truth(value):
    text = str(value)
    if "####" in text:
        text = text.split("####")[-1]
    matches = re.findall(r"-?\d+(?:\.\d+)?", text.replace(",", ""))
    if not matches:
        return str(value).strip()
    try:
        number = float(matches[-1])
        return int(number) if number.is_integer() else number
    except ValueError:
        return matches[-1]


def normalize_pred(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        if isinstance(value, float) and math.isnan(value):
            return None
        return int(value) if float(value).is_integer() else float(value)
    text = str(value).replace(",", "")
    matches = re.findall(r"-?\d+(?:\.\d+)?", text)
    if not matches:
        return text.strip()
    number = float(matches[-1])
    return int(number) if number.is_integer() else number


def is_correct(pred, gt):
    pred_norm = normalize_pred(pred)
    gt_norm = extract_ground_truth(gt)
    if isinstance(pred_norm, (int, float)) and isinstance(gt_norm, (int, float)):
        return abs(float(pred_norm) - float(gt_norm)) < 1e-9
    return str(pred_norm).strip() == str(gt_norm).strip()


def summarize_mask_history(results):
    total = 0
    kept = 0
    examples = []
    for item in results:
        mask_history = item.get("mask_history")
        if not mask_history:
            continue
        # Usually [initial_round_masks, pruning_round_masks] after zip per sample.
        for round_index, round_masks in enumerate(mask_history):
            if round_index == 0:
                continue
            flat = []
            stack = [round_masks]
            while stack:
                cur = stack.pop()
                if isinstance(cur, bool):
                    flat.append(cur)
                elif isinstance(cur, list):
                    stack.extend(cur)
            if flat:
                total += len(flat)
                kept += sum(1 for x in flat if x)
                if len(examples) < 8:
                    examples.append(
                        {
                            "id": item.get("id"),
                            "round_index": round_index,
                            "kept": sum(1 for x in flat if x),
                            "total": len(flat),
                            "mask": flat,
                        }
                    )
    return {
        "mask_entries": total,
        "kept_entries": kept,
        "keep_rate": None if total == 0 else kept / total,
        "examples": examples,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", required=True)
    parser.add_argument("--max-cases", type=int, default=8)
    args = parser.parse_args()

    base = Path(args.results_dir)
    loaded = {name: load_json(base / filename) for name, filename in METHOD_FILES.items()}

    method_rows = {}
    result_by_method = {}
    correct_by_method = {}
    for name, data in loaded.items():
        results = data["results"]
        result_by_method[name] = {str(item["id"]): item for item in results}
        correct_by_method[name] = {
            str(item["id"]): is_correct(item.get("pred"), item.get("ground_truth"))
            for item in results
        }
        usage = data.get("token_usage_summary", {})
        method_rows[name] = {
            "accuracy": data.get("accuracy"),
            "total_tokens": usage.get("total_tokens"),
            "eval_results": len(results),
            "correct_count": sum(correct_by_method[name].values()),
            "call_count": usage.get("call_count"),
        }

    all_ids = sorted(result_by_method["cot"].keys(), key=lambda x: int(x) if x.isdigit() else x)
    cot_correct = correct_by_method["cot"]

    comparisons = {}
    for name in ["mad_naive", "mad_objective", "mad_subjective"]:
        other = correct_by_method[name]
        comparisons[f"cot_wrong_{name}_right"] = [qid for qid in all_ids if not cot_correct[qid] and other[qid]]
        comparisons[f"cot_right_{name}_wrong"] = [qid for qid in all_ids if cot_correct[qid] and not other[qid]]

    pairwise = {}
    for left, right in [
        ("mad_naive", "mad_objective"),
        ("mad_naive", "mad_subjective"),
        ("mad_objective", "mad_subjective"),
    ]:
        lmap, rmap = correct_by_method[left], correct_by_method[right]
        pairwise[f"{left}_right_{right}_wrong"] = [qid for qid in all_ids if lmap[qid] and not rmap[qid]]
        pairwise[f"{left}_wrong_{right}_right"] = [qid for qid in all_ids if not lmap[qid] and rmap[qid]]

    def case(qid):
        item = result_by_method["cot"][qid]
        return {
            "id": qid,
            "question": item.get("question"),
            "ground_truth": extract_ground_truth(item.get("ground_truth")),
            "preds": {
                name: normalize_pred(result_by_method[name][qid].get("pred"))
                for name in METHOD_FILES
            },
            "correct": {
                name: correct_by_method[name][qid]
                for name in METHOD_FILES
            },
        }

    case_examples = {}
    for key, ids in {**comparisons, **pairwise}.items():
        case_examples[key] = [case(qid) for qid in ids[: args.max_cases]]

    cot_tokens = method_rows["cot"]["total_tokens"]
    cot_correct_count = method_rows["cot"]["correct_count"]
    cost_vs_cot = {}
    for name in ["mad_naive", "mad_objective", "mad_subjective"]:
        extra_correct = method_rows[name]["correct_count"] - cot_correct_count
        extra_tokens = method_rows[name]["total_tokens"] - cot_tokens
        cost_vs_cot[name] = {
            "extra_correct": extra_correct,
            "extra_tokens": extra_tokens,
            "tokens_per_extra_correct": None if extra_correct <= 0 else extra_tokens / extra_correct,
        }

    output = {
        "methods": method_rows,
        "cost_vs_cot": cost_vs_cot,
        "comparison_counts": {k: len(v) for k, v in comparisons.items()},
        "pairwise_counts": {k: len(v) for k, v in pairwise.items()},
        "case_examples": case_examples,
        "mask_stats": {
            name: summarize_mask_history(loaded[name]["results"])
            for name in ["mad_naive", "mad_objective", "mad_subjective"]
        },
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
