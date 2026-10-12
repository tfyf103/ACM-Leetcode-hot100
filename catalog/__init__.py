"""Load the trusted, bundled ACM problem catalog without running solutions."""

import importlib
import pkgutil


PROBLEMS = []
CHECKERS = {}
for module_info in sorted(pkgutil.iter_modules(__path__), key=lambda item: item.name):
    if module_info.name.startswith("part_"):
        module = importlib.import_module("." + module_info.name, __name__)
        PROBLEMS.extend(module.PROBLEMS)
        for problem_id, checker in getattr(module, "CHECKERS", {}).items():
            if problem_id in CHECKERS:
                raise ValueError("Duplicate checker: %s" % problem_id)
            CHECKERS[problem_id] = checker

HOT100_ORDER = (
    1, 49, 128, 283, 11, 15, 42, 3, 438, 560, 239, 76, 53, 56, 189, 238, 41,
    73, 54, 48, 240, 160, 206, 234, 141, 142, 21, 2, 19, 24, 25, 138, 148, 23,
    146, 94, 104, 226, 101, 543, 102, 108, 98, 230, 199, 114, 105, 437, 236, 124,
    200, 994, 207, 208, 46, 78, 17, 39, 22, 79, 131, 51, 35, 74, 34, 33, 153,
    4, 20, 155, 394, 739, 84, 215, 347, 295, 121, 55, 45, 763, 70, 118, 198,
    279, 322, 139, 300, 152, 416, 32, 62, 64, 5, 1143, 72, 136, 169, 75, 31, 287,
)
_ORDER_INDEX = {problem_id: index for index, problem_id in enumerate(HOT100_ORDER)}


def order_key(problem):
    return (_ORDER_INDEX.get(problem["id"], len(HOT100_ORDER)), problem["id"])


PROBLEMS.sort(key=order_key)
BY_ID = {problem["id"]: problem for problem in PROBLEMS}
if len(BY_ID) != len(PROBLEMS):
    raise ValueError("Duplicate problem IDs in catalog")

PUBLIC_FIELDS = (
    "id", "title", "slug", "difficulty", "category", "description",
    "input_format", "output_format", "constraints", "examples", "starter",
    "explanation", "compare",
)


def public_problem(problem):
    """Whitelist response fields so private tests never leak by accident."""
    result = {key: problem[key] for key in PUBLIC_FIELDS if key in problem}
    result["test_count"] = len(problem["tests"])
    return result


def summary(problem):
    result = {key: problem[key] for key in
              ("id", "title", "slug", "difficulty", "category")}
    result["test_count"] = len(problem["tests"])
    return result
