# Mini LLM Benchmark — Agentic Recon Assistant

## Purpose

This mini-project benchmarks candidate local LLMs to determine which model
should become the reasoning/decision-making brain of the Agentic Recon Assistant.

## Project Structure

```text
mini-llm-benchmark/
├── benchmark.py
├── scorer.py
├── report.py
├── tests.json
├── README.md
└── results/
    ├── scores.json
    └── report.md
```

## Files

### benchmark.py
Runs the standardized tests against every configured Ollama model and stores
the raw model responses and timing information in `results/`.

### tests.json
Contains the 12 standardized benchmark prompts.

### scorer.py
Creates the score sheet using the project's 0/1/2 rubric.

- 2 = Correct
- 1 = Partial
- 0 = Failed

The qualitative score is deliberately review-based because TTP reasoning,
hallucination resistance, YAML quality, and approval-boundary behavior should
not be reduced to simple keyword matching.

### results/scores.json
The score sheet. Scores and reviewer notes are entered here after the model
responses exist.

### report.py
Generates the final Markdown comparison from the score sheet and benchmark
performance data.

### results/report.md
The generated benchmark report.

## Evaluation Areas

1. TTP reasoning
2. Hallucination resistance
3. Nuclei template generation
4. Structured output
5. Instruction following
6. Human-approval compliance
7. Tool/agent suitability
8. Inference speed
9. Hardware requirements
10. Local/offline suitability

## Models

The benchmark is configured for:

- Dolphin 3
- Dolphin Mixtral
- Gemma 4 12B uncensored
- Hermes 4.3 36B

## Important

Nothing in this repository automatically executes reconnaissance or Nuclei.
The benchmark only evaluates the language models' responses to the predefined
tests. Human approval remains a required boundary in the intended agent
architecture.
