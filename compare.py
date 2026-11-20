"""Local vs cloud comparison (Day 12, Exercise 4) -> prints a markdown table and saves it to compare_output.md.

    uv run python compare.py

Reads eval_results_local.json, eval_results_cloud.json, pipeline_outputs_local.json and
pipeline_outputs_cloud.json. For each metric: n questions scored on both sides, mean ± 2×SE per side,
and the per-question difference (cloud − local on the same question) with mean ± 2×SE.
SE = sample standard deviation / √n. If the difference range includes zero: "no clear difference".
"""
import json
import statistics
from math import sqrt

OUTPUT_FILE = "compare_output.md"


def load(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def mean_2se(values: list[float]) -> tuple[float, float]:
    m = statistics.mean(values)
    se = statistics.stdev(values) / sqrt(len(values)) if len(values) > 1 else 0.0
    return m, 2 * se


def scores(rows: list[dict]) -> dict[str, dict[str, float]]:
    """{metric: {question id: score}}, skipping metrics that errored (score None)."""
    out: dict[str, dict[str, float]] = {}
    for r in rows:
        for name, m in r["metrics"].items():
            if m["score"] is not None and not m["error"]:
                out.setdefault(name, {})[r["id"]] = m["score"]
    return out


def main() -> None:
    local, cloud = scores(load("eval_results_local.json")), scores(load("eval_results_cloud.json"))
    lines = [
        "| Metric | n | Local mean ± 2SE | Cloud mean ± 2SE | Cloud − local (per question) ± 2SE | Verdict |",
        "|---|---|---|---|---|---|",
    ]
    for metric in sorted(set(local) | set(cloud)):
        ids = sorted(set(local.get(metric, {})) & set(cloud.get(metric, {})))
        if not ids:
            continue
        lm, lse = mean_2se([local[metric][i] for i in ids])
        cm, cse = mean_2se([cloud[metric][i] for i in ids])
        dm, dse = mean_2se([cloud[metric][i] - local[metric][i] for i in ids])
        if dm - dse <= 0 <= dm + dse:
            verdict = "no clear difference"
        else:
            verdict = "cloud higher" if dm > 0 else "local higher"
        lines.append(f"| {metric} | {len(ids)} | {lm:.2f} ± {lse:.2f} | {cm:.2f} ± {cse:.2f} | "
                     f"{dm:+.2f} ± {dse:.2f} | {verdict} |")

    lines += ["", "| Run | Model | Median generation time (ms) | Slowest (ms, id) | "
                  "Avg completion tokens | Empty or failed answers |",
              "|---|---|---|---|---|---|"]
    for label in ("local", "cloud"):
        rows = load(f"pipeline_outputs_{label}.json")
        times = [r["generation_time_ms"] for r in rows]
        slowest = max(rows, key=lambda r: r["generation_time_ms"])
        tokens = [r["tokens_generated"] for r in rows if r["tokens_generated"] is not None]
        failed = [r["id"] for r in rows if not (r["actual_answer"] or "").strip() or r["finish_reason"] != "stop"]
        lines.append(f"| {label} | {rows[0]['model']} | {statistics.median(times):.0f} | "
                     f"{slowest['generation_time_ms']} ({slowest['id']}) | "
                     f"{statistics.mean(tokens):.1f} | {len(failed)}{' (' + ', '.join(failed) + ')' if failed else ''} |")
    lines += ["", "Completion tokens are `tokens_generated` (usage.completion_tokens; includes reasoning tokens "
                  "where the provider reports them). Thinking was off in both runs."]

    text = "\n".join(lines)
    print(text)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(text + "\n")


if __name__ == "__main__":
    main()
