"""
LLM Benchmark Report Generator

Does not run Ollama.
Reads results/scores.json and benchmark result JSON files and generates
results/report.md.
"""

import json
from pathlib import Path

RESULTS_DIR = Path("results")
SCORES_FILE = RESULTS_DIR / "scores.json"
REPORT_FILE = RESULTS_DIR / "report.md"

EXPECTED_TEST_COUNT = 12
MAX_SCORE = EXPECTED_TEST_COUNT * 2


def load(path):
    """Load and return JSON data from a file."""
    return json.loads(path.read_text(encoding="utf-8"))


def model_outputs():
    """
    Load benchmark result JSON files from the results directory.

    scores.json is excluded because it contains scoring data rather than
    raw benchmark output.
    """
    data = {}

    for path in sorted(RESULTS_DIR.glob("*.json")):
        if path.name == SCORES_FILE.name:
            continue

        try:
            item = load(path)

            if "model" in item and "results" in item:
                data[item["model"]] = item

        except (OSError, json.JSONDecodeError, TypeError, KeyError) as exc:
            print(f"Warning: Could not read {path}: {exc}")

    return data


def performance(data):
    """Calculate average completion time and generation speed."""
    rows = [
        result
        for result in data.get("results", [])
        if result.get("status") == "success"
    ]

    times = [
        result["elapsed_seconds"]
        for result in rows
        if isinstance(result.get("elapsed_seconds"), (int, float))
    ]

    speeds = [
        result["tokens_per_second"]
        for result in rows
        if isinstance(result.get("tokens_per_second"), (int, float))
    ]

    return {
        "completed": len(rows),
        "avg_time": sum(times) / len(times) if times else None,
        "avg_speed": sum(speeds) / len(speeds) if speeds else None,
    }


def scored_tests(info):
    """Return only valid manually scored test entries."""
    return [
        test
        for test in info.get("tests", [])
        if test.get("score") in (0, 1, 2)
    ]


def model_score(info):
    """Return total score, maximum score, percentage, and review count."""
    tests = scored_tests(info)
    total = sum(test["score"] for test in tests)
    maximum = len(tests) * 2

    percentage = (total / maximum * 100) if maximum else None

    return {
        "total": total,
        "maximum": maximum,
        "percentage": percentage,
        "reviewed": len(tests),
        "complete": len(tests) == EXPECTED_TEST_COUNT,
    }


def format_score(score_info):
    """Format a model's current qualitative score."""
    if not score_info["reviewed"]:
        return "Pending"

    return f"{score_info['total']}/{score_info['maximum']}"


def format_percentage(score_info):
    """Format a model's current percentage."""
    if score_info["percentage"] is None:
        return "Pending"

    return f"{score_info['percentage']:.1f}%"


def main():
    if not SCORES_FILE.exists():
        print("scores.json not found. Run scorer.py first.")
        return

    try:
        scores = load(SCORES_FILE)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Could not read {SCORES_FILE}: {exc}")
        return

    outputs = model_outputs()

    lines = [
        "# LLM Suitability Benchmark Report",
        "",
        "## Objective",
        "",
        "Determine which local LLM is the best fit to act as the brain of the Agentic Recon Assistant.",
        "",
        "## Benchmark",
        "",
        f"All candidate models are evaluated using the same {EXPECTED_TEST_COUNT} tests.",
        "",
        "## Scoring",
        "",
        "| Score | Meaning |",
        "|---:|---|",
        "| 2 | Correct |",
        "| 1 | Partial |",
        "| 0 | Failed |",
        "",
        f"**Maximum qualitative score: {MAX_SCORE} points.**",
        "",
        "Percentages are calculated from the tests that have actually been reviewed.",
        "A model is included in the final ranking only after all 12 tests have been scored.",
        "",
        "## Overall Results",
        "",
        "| Model | Score | Percentage | Tests Reviewed | Avg Time (s) | Avg tok/s |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    ranked = []

    for model, info in scores.get("models", {}).items():
        score_info = model_score(info)
        perf = performance(outputs.get(model, {}))

        score_text = format_score(score_info)
        pct_text = format_percentage(score_info)
        reviewed_text = f"{score_info['reviewed']}/{EXPECTED_TEST_COUNT}"

        time_text = (
            f"{perf['avg_time']:.2f}"
            if perf["avg_time"] is not None
            else "—"
        )

        speed_text = (
            f"{perf['avg_speed']:.2f}"
            if perf["avg_speed"] is not None
            else "—"
        )

        lines.append(
            f"| `{model}` | {score_text} | {pct_text} | "
            f"{reviewed_text} | {time_text} | {speed_text} |"
        )

        # Only fully reviewed models are eligible for final ranking.
        if score_info["complete"] and score_info["percentage"] is not None:
            ranked.append((score_info["percentage"], model))

    lines += ["", "## Test-by-Test Review", ""]

    for model, info in scores.get("models", {}).items():
        lines += [
            f"### {model}",
            "",
            "| Test | Score | Reviewer Notes |",
            "|---|---:|---|",
        ]

        for row in info.get("tests", []):
            score = row.get("score")
            score_text = str(score) if score in (0, 1, 2) else "Pending"

            notes = str(row.get("reviewer_notes", ""))
            notes = notes.replace("|", "\\|").replace("\n", " ")

            test_id = row.get("test_id", "Unknown")
            lines.append(
                f"| {test_id} | {score_text} | {notes} |"
            )

        reviewer_summary = info.get("reviewer_summary") or "Pending"

        lines += [
            "",
            f"**Reviewer summary:** {reviewer_summary}",
            "",
        ]

    lines += [
        "## Evaluation Dimensions",
        "",
        "- TTP reasoning",
        "- Hallucination resistance",
        "- Nuclei template generation",
        "- Structured output",
        "- Instruction following",
        "- Human-approval compliance",
        "- Tool/agent suitability",
        "- Inference speed",
        "- Hardware requirements",
        "- Local/offline suitability",
        "",
        "## Ranking",
        "",
    ]

    if ranked:
        ranked.sort(key=lambda item: (-item[0], item[1]))

        for i, (pct, model) in enumerate(ranked, 1):
            lines.append(f"{i}. **{model}** — {pct:.1f}%")
    else:
        lines.append(
            "Pending: no model has completed all 12 manually scored tests."
        )

    lines += [
        "",
        "## Final Model Selection",
        "",
        "**Selected model:** Pending benchmark review",
        "",
        "The final choice should consider both qualitative benchmark performance "
        "and practical local/offline deployment requirements.",
        "",
        "The ranking above is score-based only and does not automatically select "
        "the final model.",
        "",
    ]

    try:
        REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")
    except OSError as exc:
        print(f"Could not write {REPORT_FILE}: {exc}")
        return

    print(f"Created: {REPORT_FILE}")


if __name__ == "__main__":
    main()
