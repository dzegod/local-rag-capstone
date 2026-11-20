"""Exercise 1: compare local models on speed and quality -> benchmark_results.json.

After the final run, fill in quality_rating (1-5) and rating_note by hand.
Re-running overwrites the file, so rate last.
"""
import json
import time

from openai import OpenAI

MODELS = ["qwen3.5:4b-q4_K_M", "qwen3.5:2b-q4_K_M"]
BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"
REASONING_EFFORT = "none"
OUTPUT_FILE = "benchmark_results.json"

PROMPTS = [
    {"category": "factual", "prompt": "What causes tides on Earth? Answer in 2-3 sentences."},
    {"category": "reasoning", "prompt": "If a train travels 120km in 1.5 hours, and then 80km in 1 hour, what is the average speed for the entire journey?"},
    {"category": "summarization", "prompt": "Summarize this paragraph in one sentence: Remote work has changed how software teams collaborate. Many companies moved from fixed office schedules to hybrid models. Supporters point to fewer commutes and better focus time, while critics worry about weaker mentoring for junior staff and slower knowledge sharing."},
    {"category": "structured", "prompt": 'List 3 European capitals. Respond ONLY with valid JSON: [{"city": ..., "country": ...}]'},
    {"category": "code", "prompt": "Write a Python function that checks whether a string is a palindrome, ignoring case and spaces."},
    {"category": "instruction_following", "prompt": "Give exactly 3 tips for writing clear emails as a numbered list, each tip at most 8 words, with no introduction."},
]


def run_benchmark(model: str, prompt_item: dict) -> dict:
    client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
    start = time.time()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt_item["prompt"]}],
        temperature=0.7,
        reasoning_effort=REASONING_EFFORT,
        max_tokens=1024,
    )
    elapsed = time.time() - start
    choice = response.choices[0]
    usage = response.usage

    return {
        "model": model,
        "category": prompt_item["category"],
        "prompt": prompt_item["prompt"],
        "response": choice.message.content,
        "thinking": REASONING_EFFORT != "none",
        "finish_reason": choice.finish_reason,
        "time_seconds": round(elapsed, 2),
        "prompt_tokens": usage.prompt_tokens if usage else None,
        "completion_tokens": usage.completion_tokens if usage else None,
        "tokens_per_second": round(usage.completion_tokens / elapsed, 1) if usage and usage.completion_tokens else None,
        "quality_rating": None,
        "rating_note": "",
    }


def main() -> None:
    results = []
    for model in MODELS:
        for item in PROMPTS:
            row = run_benchmark(model, item)
            if not (row["response"] or "").strip():
                print(f"WARNING: empty response from {model} on {item['category']} "
                      f"(finish_reason={row['finish_reason']})")
            print(f"{model} | {item['category']:<22} | {row['time_seconds']}s | "
                  f"{row['tokens_per_second']} tok/s | {row['finish_reason']}")
            results.append(row)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(results)} rows to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
