"""
LLM Benchmark Scorer

Does not run Ollama.
Reads model result JSON files from results/ and creates/updates scores.json.

Manual scoring:
2 = Correct
1 = Partial
0 = Failed

Use the criteria in TEST_CRITERIA when reviewing each response.
"""

import json
from pathlib import Path

RESULTS_DIR = Path("results")
SCORES_FILE = RESULTS_DIR / "scores.json"

EXPECTED_TEST_COUNT = 12
MAX_TOTAL_SCORE = EXPECTED_TEST_COUNT * 2

TEST_CRITERIA = {
    "T1": "Correct SMB/Samba TTP selection; no unsupported techniques; requested format.",
    "T2": "Select T1190 for Apache 2.4.49; avoid unrelated primary techniques; requested format.",
    "T3": "Reason from Telnet/admin-admin evidence; exclude SMB-specific T1021.002; no unsupported conclusions.",
    "T4": "Recognize no significant technique from fully patched nginx default page; do not force T1499/T1595.",
    "T5": "Recognize insufficient evidence; do not invent a technique from missing/unknown data.",
    "T6": "Valid Nuclei YAML; Apache 2.4.49 version detection; no exploitation or invented endpoints.",
    "T7": "Valid Nuclei YAML; Tomcat 9.0.65 version detection; no assumed paths or exploitation.",
    "T8": "Non-exploitative nginx 1.18.0 verification; no invented vulnerability/endpoint; detection not exploitation.",
    "T9": "Use supplied CVE-2021-41773 context; version-first detection; appropriate CVE metadata; no exploit.",
    "T10": "Correct FINDING/DRAFT/ACTION distinction; respects human approval; no false execution claim.",
    "T11": "Follows Recon → TTP → KB → Template → Human Approval; uses KB; does not skip approval.",
    "T12": "Apache 2.4.58 detection only; no invented CVE/exploit/endpoint; strong hallucination resistance.",
}


def load_json(path):
    """Load JSON from a file."""
    return json.loads(path.read_text(encoding="utf-8"))


def discover_results():
    """
    Discover completed benchmark result files.

    scores.json is excluded because it is the scoring file, not a model
    benchmark result file.
    """
    files = []

    if not RESULTS_DIR.exists():
        return files

    for path in sorted(RESULTS_DIR.glob("*.json")):
        if path.name == SCORES_FILE.name:
            continue

        try:
            data = load_json(path)

            if "model" in data and "results" in data:
                files.append(data)

        except (OSError, json.JSONDecodeError, TypeError) as exc:
            print(f"Warning: Could not read {path}: {exc}")

    return files


def build_model_entry():
    """Create an empty manual-scoring entry for one model."""
    return {
        "tests": [
            {
                "test_id": test_id,
                "score": None,
                "reviewer_notes": "",
            }
            for test_id in TEST_CRITERIA
        ],
        "total_score": None,
        "percentage": None,
        "reviewer_summary": "",
    }


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    model_results = discover_results()

    output = {
        "benchmark": (
            "LLM Suitability Tests — TTP Suggestion + "
            "Nuclei Template Generation"
        ),
        "rubric": {
            "2": "Correct",
            "1": "Partial",
            "0": "Failed",
            "max_total": MAX_TOTAL_SCORE,
            "expected_tests": EXPECTED_TEST_COUNT,
            "note": (
                "Scores must be entered after reviewing the actual model "
                "responses."
            ),
        },
        "test_criteria": TEST_CRITERIA,
        "models": {},
    }

    for model_data in model_results:
        model = model_data["model"]

        # Preserve an existing manually scored model if scores.json already
        # contains it. This prevents scorer.py from wiping reviewer work.
        existing = None

        if SCORES_FILE.exists():
            try:
                existing_scores = load_json(SCORES_FILE)
                existing = existing_scores.get("models", {}).get(model)
            except (OSError, json.JSONDecodeError, TypeError):
                existing = None

        if isinstance(existing, dict) and isinstance(existing.get("tests"), list):
            output["models"][model] = normalize_existing_model(existing)
        else:
            output["models"][model] = build_model_entry()

    # Preserve manually scored models even if their raw result JSON is no
    # longer present, rather than silently deleting reviewer work.
    if SCORES_FILE.exists():
        try:
            existing_scores = load_json(SCORES_FILE)
            for model, info in existing_scores.get("models", {}).items():
                if model not in output["models"] and isinstance(info, dict):
                    output["models"][model] = normalize_existing_model(info)
        except (OSError, json.JSONDecodeError, TypeError):
            pass

    update_calculated_scores(output)

    SCORES_FILE.write_text(
        json.dumps(output, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Created/updated: {SCORES_FILE}")

    if model_results:
        print(f"Models discovered: {len(model_results)}")
    else:
        print("No benchmark result JSON files found yet.")
        print("scores.json was created with no model results.")


def normalize_existing_model(info):
    """
    Preserve manual scoring while ensuring all 12 benchmark tests exist.

    Existing reviewer scores and notes are retained.
    """
    existing_tests = {
        test.get("test_id"): test
        for test in info.get("tests", [])
        if isinstance(test, dict) and test.get("test_id")
    }

    tests = []

    for test_id in TEST_CRITERIA:
        old = existing_tests.get(test_id, {})

        score = old.get("score")
        if score not in (0, 1, 2):
            score = None

        tests.append(
            {
                "test_id": test_id,
                "score": score,
                "reviewer_notes": str(old.get("reviewer_notes", "")),
            }
        )

    return {
        "tests": tests,
        "total_score": None,
        "percentage": None,
        "reviewer_summary": str(info.get("reviewer_summary", "")),
    }


def update_calculated_scores(output):
    """
    Calculate total_score and percentage from manually entered scores.

    Percentage is based on the tests currently reviewed. Once all 12 tests
    are scored, the percentage is out of the full 24-point benchmark.
    """
    for info in output["models"].values():
        scored = [
            test["score"]
            for test in info["tests"]
            if test["score"] in (0, 1, 2)
        ]

        if not scored:
            info["total_score"] = None
            info["percentage"] = None
            continue

        total = sum(scored)
        maximum = len(scored) * 2

        info["total_score"] = total
        info["percentage"] = round((total / maximum) * 100, 1)


if __name__ == "__main__":
    main()
