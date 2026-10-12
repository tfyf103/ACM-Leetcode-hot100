"""Load authored statements and fixed extra fixtures; never execute solutions."""

import json
from pathlib import Path


def apply_enrichment(problems):
    entries = json.loads(Path(__file__).with_name("enrichment.json").read_text(encoding="utf-8"))
    if set(entries) != {str(problem["id"]) for problem in problems}:
        raise ValueError("Enrichment must cover the complete catalog exactly")
    for problem in problems:
        entry = entries[str(problem["id"])]
        problem["description"] = entry["description"]
        problem["clarifications"] = entry["clarifications"]
        problem["examples"] = entry["examples"]
        seen = {case["input"] for case in problem["tests"]}
        for case in entry["tests"]:
            if case["input"] not in seen:
                problem["tests"].append(dict(case))
                seen.add(case["input"])
    return problems
