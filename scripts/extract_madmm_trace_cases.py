#!/usr/bin/env python3
import argparse
import json
import math
import re
from collections import Counter
from pathlib import Path


METHOD_FILES = {
    "cot": "cot_seed41.json",
    "naive": "mad_3agents_2rounds_seed41.json",
    "objective": "mad_objective_3agents_2rounds_seed41.json",
    "subjective": "mad_subjective_3agents_2rounds_seed41.json",
}


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def normalize_number(value):
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


def ground_truth(value):
    text = str(value)
    if "####" in text:
        text = text.split("####")[-1]
    return normalize_number(text)


def is_correct(pred, gt):
    return normalize_number(pred) == ground_truth(gt)


def summarize_mask(results):
    stats = Counter()
    selected_wrong_with_correct = []
    selected_correct_with_wrong = []

    for item in results:
        round_1 = item["debate_history"][0]
        answers = [agent.get("answer") for agent in round_1]
        correct = [is_correct(answer, item["ground_truth"]) for answer in answers]
        mask = item["mask_history"][1]
        kept_indexes = [idx for idx, keep in enumerate(mask) if keep]

        stats["items"] += 1
        stats["memories"] += len(mask)
        stats["kept"] += len(kept_indexes)
        stats["kept_correct"] += sum(correct[idx] for idx in kept_indexes)
        stats["kept_wrong"] += sum(not correct[idx] for idx in kept_indexes)
        stats["dropped_correct"] += sum((not mask[idx]) and correct[idx] for idx in range(len(mask)))
        stats["dropped_wrong"] += sum((not mask[idx]) and (not correct[idx]) for idx in range(len(mask)))

        if any(correct) and kept_indexes and not any(correct[idx] for idx in kept_indexes):
            selected_wrong_with_correct.append(item["id"])
        if any(not flag for flag in correct) and kept_indexes and any(correct[idx] for idx in kept_indexes):
            selected_correct_with_wrong.append(item["id"])

    return {
        **dict(stats),
        "selected_wrong_when_correct_available": selected_wrong_with_correct,
        "selected_correct_when_wrong_available": selected_correct_with_wrong,
    }


def initial_distribution(results):
    distribution = Counter()
    for item in results:
        correct_count = sum(
            is_correct(agent.get("answer"), item["ground_truth"])
            for agent in item["debate_history"][0]
        )
        distribution[correct_count] += 1
    return dict(sorted(distribution.items()))


def case_summary(case_id, by_method):
    cot_item = by_method["cot"][case_id]
    methods = {}
    for method in ["cot", "naive", "objective", "subjective"]:
        item = by_method[method][case_id]
        row = {
            "pred": normalize_number(item.get("pred")),
            "correct": is_correct(item.get("pred"), item.get("ground_truth")),
        }
        if method != "cot":
            row["round_1_answers"] = [
                agent.get("answer") for agent in item["debate_history"][0]
            ]
            row["round_2_answers"] = [
                agent.get("answer") for agent in item["debate_history"][1]
            ]
            row["round_1_confidence_scores"] = item["perplexity_history"][0]
            row["round_2_confidence_scores"] = item["perplexity_history"][1]
            row["mask"] = item["mask_history"][1]
        methods[method] = row

    return {
        "id": case_id,
        "question": cot_item["question"],
        "ground_truth": ground_truth(cot_item["ground_truth"]),
        "methods": methods,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", required=True)
    parser.add_argument("--cases", nargs="+", default=["335", "562", "214", "1227"])
    args = parser.parse_args()

    base = Path(args.results_dir)
    loaded = {
        method: load_json(base / filename)["results"]
        for method, filename in METHOD_FILES.items()
    }
    by_method = {
        method: {str(item["id"]): item for item in results}
        for method, results in loaded.items()
    }

    output = {
        "initial_round_correct_distribution": initial_distribution(loaded["naive"]),
        "mask_stats": {
            "objective": summarize_mask(loaded["objective"]),
            "subjective": summarize_mask(loaded["subjective"]),
        },
        "cases": [case_summary(case_id, by_method) for case_id in args.cases],
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
