"""Load authored statements and fixed extra fixtures; never execute solutions."""

import json
from pathlib import Path


def apply_enrichment(problems):
    entries = json.loads(Path(__file__).with_name("enrichment.json").read_text(encoding="utf-8"))
    tutorials = json.loads(Path(__file__).with_name("tutorials.json").read_text(encoding="utf-8"))
    solutions = json.loads(Path(__file__).with_name("optimal_solutions.json").read_text(encoding="utf-8"))
    guides = json.loads(Path(__file__).with_name("guides.json").read_text(encoding="utf-8"))
    hot100 = [problem for problem in problems if problem.get("track") != "acm_io"]
    io_problems = [problem for problem in problems if problem.get("track") == "acm_io"]
    ids = {str(problem["id"]) for problem in hot100}
    if set(entries) != ids or set(tutorials) != ids or set(guides) != ids or not set(solutions) <= ids:
        raise ValueError("Enrichment must cover the complete catalog exactly")
    for problem in hot100:
        entry = entries[str(problem["id"])]
        tutorial = tutorials[str(problem["id"])]
        tutorial["guide"] = guides[str(problem["id"])]
        problem["tutorial"] = tutorial
        problem["explanation"] = "\n\n".join(
            section["title"] + "\n" + section["text"] for section in tutorial["sections"])
        if str(problem["id"]) in solutions:
            problem["solution"] = solutions[str(problem["id"])]
        problem["description"] = entry["description"]
        problem["clarifications"] = entry["clarifications"]
        problem["examples"] = entry["examples"]
        seen = {case["input"] for case in problem["tests"]}
        for case in entry["tests"]:
            if case["input"] not in seen:
                problem["tests"].append(dict(case))
                seen.add(case["input"])
    if io_problems:
        io_guides = json.loads(Path(__file__).with_name("io_guides.json").read_text(encoding="utf-8"))
        if set(io_guides) != {str(problem["id"]) for problem in io_problems}:
            raise ValueError("IO guides must cover the complete IO topic exactly")
        for problem in io_problems:
            guide = io_guides[str(problem["id"])]
            titles = ("识别输入协议", "逐步推导读取方法", "为什么不会多读或漏读", "手算读取过程",
                      "时间复杂度", "空间复杂度", "边界与自测", "方法取舍")
            table = guide["walkthrough"]
            bodies = (guide["recognition"]["why"],
                      "\n\n".join(item["question"]+"\n"+item["answer"] for item in guide["dialogue"]),
                      guide["invariant"]["statement"]+"\n"+guide["invariant"]["reason"],
                      table["input"]+"\n"+"\n".join(" | ".join(row) for row in table["rows"])+"\n"+table["conclusion"],
                      guide["complexity"]["time"]+"\n"+guide["complexity"]["reason"],
                      guide["complexity"]["space"],
                      "\n\n".join(item["question"]+"\n"+item["answer"] for item in guide["self_check"]),
                      guide["complexity"]["optimality"])
            sections = [{"title": title, "text": body} for title, body in zip(titles, bodies)]
            problem["tutorial"] = {"approach": guide["recognition"]["pattern"], "guide": guide, "sections": sections}
            problem["explanation"] = "\n\n".join(s["title"]+"\n"+s["text"] for s in sections)
    return problems
