import json
import os
import time
from datetime import datetime

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
TESTS_FILE = "tests.json"
RESULTS_DIR = "results"

# Verified/current Ollama model tags.
# Hermes 4 is a community Ollama model, so keep the exact tag explicit.
MODELS = [
    "dolphin3",
    "dolphin-mixtral",
    "satgeze/gemma4-12b-uncensored-1m",
    "steelpuddles/hermes-4.3-36B",
]


def load_tests():
    with open(TESTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def run_test(model, test):
    payload = {
        "model": model,
        "prompt": test["prompt"],
        "stream": False,
        "options": {
            "temperature": 0
        }
    }

    start = time.perf_counter()

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=600
        )
        response.raise_for_status()
        data = response.json()

        elapsed = time.perf_counter() - start

        eval_count = data.get("eval_count", 0)
        eval_duration = data.get("eval_duration", 0)

        tokens_per_second = None
        if eval_count and eval_duration:
            tokens_per_second = eval_count / (eval_duration / 1e9)

        return {
            "status": "success",
            "model": model,
            "test_id": test["id"],
            "test_name": test["name"],
            "category": test.get("category"),
            "response": data.get("response", ""),
            "elapsed_seconds": round(elapsed, 3),
            "tokens_per_second": (
                round(tokens_per_second, 2)
                if tokens_per_second is not None else None
            ),
            "ollama_metadata": {
                "total_duration": data.get("total_duration"),
                "load_duration": data.get("load_duration"),
                "prompt_eval_count": data.get("prompt_eval_count"),
                "prompt_eval_duration": data.get("prompt_eval_duration"),
                "eval_count": data.get("eval_count"),
                "eval_duration": data.get("eval_duration"),
            },
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        return {
            "status": "error",
            "model": model,
            "test_id": test["id"],
            "test_name": test["name"],
            "category": test.get("category"),
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    tests = load_tests()

    print("LLM Benchmark")
    print("=" * 60)
    print(f"Models: {len(MODELS)}")
    print(f"Tests:  {len(tests)}")
    print()

    for model in MODELS:
        print(f"\nRunning model: {model}")
        print("-" * 60)

        results = []

        for i, test in enumerate(tests, start=1):
            print(f"[{i}/{len(tests)}] {test['id']} - {test['name']}")

            result = run_test(model, test)
            results.append(result)

            if result["status"] == "success":
                print(
                    f"  OK | {result['elapsed_seconds']}s | "
                    f"{result['tokens_per_second']} tok/s"
                )
            else:
                print(f"  ERROR | {result['error']}")

        safe_name = model.replace("/", "__").replace(":", "_")
        output_file = os.path.join(
            RESULTS_DIR,
            f"{safe_name}.json"
        )

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "model": model,
                    "run_timestamp": datetime.now().isoformat(),
                    "results": results
                },
                f,
                indent=2,
                ensure_ascii=False
            )

        print(f"Saved: {output_file}")


if __name__ == "__main__":
    main()
