"""Rate results by hand, one row at a time.

uv run python rate.py pipeline     -> passed (y/n) + note in pipeline_outputs.json
uv run python rate.py benchmark    -> quality 1-5 + note in benchmark_results.json

Rows you already rated are skipped. Press Enter on an empty answer to skip a row,
type q to stop. Your answers are saved after every row.
"""
import json
import sys
import textwrap

FILES = {"pipeline": "pipeline_outputs.json", "benchmark": "benchmark_results.json"}


def show(label: str, text: str) -> None:
    print(f"\n{label}:")
    print(textwrap.indent(textwrap.fill(text or "(empty)", 100, replace_whitespace=False), "  "))


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode not in FILES:
        print(__doc__)
        return
    path = FILES[mode]
    rows = json.load(open(path, encoding="utf-8"))
    field = "passed" if mode == "pipeline" else "quality_rating"
    todo = [r for r in rows if r[field] is None]
    print(f"{len(todo)} of {len(rows)} rows still to rate in {path}")

    for n, row in enumerate(todo, start=1):
        print("\n" + "=" * 100)
        if mode == "pipeline":
            print(f"[{n}/{len(todo)}] {row['id']}")
            show("QUESTION", row["question"])
            show("EXPECTED", row["expected_answer"])
            show("ACTUAL", row["actual_answer"])
            answer = input("\nPassed? y / n (Enter = skip, q = quit): ").strip().lower()
            if answer == "q":
                break
            if answer not in ("y", "n"):
                continue
            row["passed"] = answer == "y"
        else:
            print(f"[{n}/{len(todo)}] {row['model']} | {row['category']}")
            show("PROMPT", row["prompt"])
            show("RESPONSE", row["response"])
            answer = input("\nQuality 1-5 (Enter = skip, q = quit): ").strip().lower()
            if answer == "q":
                break
            if answer not in ("1", "2", "3", "4", "5"):
                continue
            row["quality_rating"] = int(answer)
        row["rating_note"] = input("Short note (why): ").strip()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2, ensure_ascii=False)

    rated = [r for r in rows if r[field] is not None]
    if mode == "pipeline":
        print(f"\nRated {len(rated)} of {len(rows)}. Passed: {sum(r['passed'] for r in rated)} of {len(rated)}")
    else:
        print(f"\nRated {len(rated)} of {len(rows)}.")


if __name__ == "__main__":
    main()
