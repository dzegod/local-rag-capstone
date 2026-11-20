import json
import sys

from generate import generate_answer
from retrieve import retrieve_chunks

TEST_QUESTIONS_FILE = "test_questions.json"
OUTPUT_FILE = "pipeline_outputs.json"


def answer_question(query: str) -> dict:
    retrieval_result = retrieve_chunks(query)
    generation_result = generate_answer(
        query=query,
        chunks=retrieval_result["retrieved_chunks"]
    )
    return {
        **generation_result,
        "retrieval": retrieval_result,
    }


def to_output_row(question: dict, result: dict) -> dict:
    chunks = result["retrieval"]["retrieved_chunks"]
    return {
        "id": question["id"],
        "question": question["question"],
        "expected_answer": question["expected_answer"],
        "actual_answer": result["answer"],
        "retrieved_context": [c["content"] for c in chunks],
        "context_sources": [{"source": c["source"], "page": c["page"], "score": c["relevance_score"]} for c in chunks],
        "model": result["model"],
        "thinking": result["thinking"],
        "finish_reason": result["finish_reason"],
        "embedding_model": result["retrieval"]["embedding_model"],
        "prompt_tokens": result["prompt_tokens"],
        "tokens_generated": result["tokens_generated"],
        "retrieval_time_ms": result["retrieval"]["retrieval_time_ms"],
        "generation_time_ms": result["generation_time_ms"],
        "passed": None,
        "rating_note": "",
    }


def run_all(output_file: str = OUTPUT_FILE) -> None:
    with open(TEST_QUESTIONS_FILE, encoding="utf-8") as f:
        questions = json.load(f)

    rows = []
    for n, question in enumerate(questions, start=1):
        result = answer_question(question["question"])
        rows.append(to_output_row(question, result))
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2, ensure_ascii=False)
        print(f"[{n}/{len(questions)}] {question['id']} finish={result['finish_reason']} "
              f"{result['generation_time_ms']} ms | {result['answer'][:80]!r}")
    print(f"Wrote {len(rows)} rows to {output_file}. Fill in 'passed' and 'rating_note' by hand.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test-set":
        # --test-set <file>: write to a labelled file so the hand-rated pipeline_outputs.json survives
        run_all(sys.argv[2] if len(sys.argv) > 2 else OUTPUT_FILE)
    elif len(sys.argv) > 1:
        out = answer_question(" ".join(sys.argv[1:]))
        print(out["answer"])
        for c in out["retrieval"]["retrieved_chunks"]:
            print(f"  {c['relevance_score']:.3f}  {c['source']} p{c['page']}")
    else:
        run_all()
