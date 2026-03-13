#!/usr/bin/env python3
"""LangExtract CLI helper — extract structured information from text or URLs.

Usage:
  python langextract_extract.py \\
    --input report.txt \\
    --prompt "Extract diagnoses and treatments." \\
    --examples examples.json \\
    --model gemini-2.5-flash \\
    --output results.jsonl \\
    --visualize

  python langextract_extract.py \\
    --input https://example.com/report.txt \\
    --prompt "Extract named entities." \\
    --examples examples.json

Examples JSON format (--examples):
  [
    {
      "text": "Patient takes aspirin 100mg daily.",
      "extractions": [
        {"extraction_class": "medication", "extraction_text": "aspirin 100mg",
         "attributes": {"frequency": "daily"}}
      ]
    }
  ]
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys


def load_examples(path: str) -> list:
    """Load ExampleData list from a JSON file."""
    try:
        import langextract as lx
    except ImportError:
        print("ERROR: langextract is not installed. Run: pip install langextract", file=sys.stderr)
        sys.exit(1)

    with open(path) as f:
        raw = json.load(f)

    examples = []
    for item in raw:
        extractions = [
            lx.data.Extraction(
                extraction_class=e["extraction_class"],
                extraction_text=e["extraction_text"],
                attributes=e.get("attributes"),
            )
            for e in item.get("extractions", [])
        ]
        examples.append(lx.data.ExampleData(text=item["text"], extractions=extractions))
    return examples


def main() -> None:
    parser = argparse.ArgumentParser(
        description="LangExtract CLI — extract structured information from text using LLMs."
    )
    parser.add_argument(
        "--input", "-i", required=True,
        help="Path to a text file OR a http(s):// URL to process."
    )
    parser.add_argument(
        "--prompt", "-p", required=True,
        help="Extraction instructions (what to extract)."
    )
    parser.add_argument(
        "--examples", "-e", required=True,
        help="Path to JSON file containing ExampleData (see module docstring)."
    )
    parser.add_argument(
        "--model", "-m", default="gemini-2.5-flash",
        help="Model ID (default: gemini-2.5-flash)."
    )
    parser.add_argument(
        "--output", "-o", default="extractions.jsonl",
        help="Output JSONL file name (default: extractions.jsonl)."
    )
    parser.add_argument(
        "--output-dir", default=".",
        help="Output directory (default: current directory)."
    )
    parser.add_argument(
        "--passes", type=int, default=1,
        help="Number of extraction passes for higher recall (default: 1)."
    )
    parser.add_argument(
        "--workers", type=int, default=10,
        help="Number of parallel LLM workers (default: 10)."
    )
    parser.add_argument(
        "--max-chars", type=int, default=1000,
        help="Max characters per chunk (default: 1000)."
    )
    parser.add_argument(
        "--api-key",
        help="API key (default: reads LANGEXTRACT_API_KEY env var)."
    )
    parser.add_argument(
        "--model-url",
        help="Custom model URL for Ollama (e.g., http://localhost:11434)."
    )
    parser.add_argument(
        "--fence-output", action="store_true", default=None,
        help="Expect fenced JSON/YAML output (required for OpenAI)."
    )
    parser.add_argument(
        "--no-schema-constraints", action="store_true",
        help="Disable schema constraints (required for OpenAI/Ollama)."
    )
    parser.add_argument(
        "--temperature", type=float, default=None,
        help="Sampling temperature (default: model default; 0.0 = deterministic)."
    )
    parser.add_argument(
        "--visualize", "-v", action="store_true",
        help="Also generate an HTML visualization file alongside the JSONL."
    )
    parser.add_argument(
        "--debug", action="store_true",
        help="Enable verbose debug logging."
    )

    args = parser.parse_args()

    try:
        import langextract as lx
    except ImportError:
        print("ERROR: langextract is not installed. Run: pip install langextract", file=sys.stderr)
        sys.exit(1)

    # Resolve input (file path vs URL)
    input_val = args.input
    if not input_val.startswith(("http://", "https://")):
        p = pathlib.Path(input_val)
        if not p.exists():
            print(f"ERROR: Input file not found: {input_val}", file=sys.stderr)
            sys.exit(1)
        with open(p) as f:
            input_val = f.read()

    examples = load_examples(args.examples)
    api_key = args.api_key or os.environ.get("LANGEXTRACT_API_KEY")

    kwargs: dict = dict(
        text_or_documents=input_val,
        prompt_description=args.prompt,
        examples=examples,
        model_id=args.model,
        extraction_passes=args.passes,
        max_workers=args.workers,
        max_char_buffer=args.max_chars,
        debug=args.debug,
        use_schema_constraints=not args.no_schema_constraints,
    )
    if api_key:
        kwargs["api_key"] = api_key
    if args.model_url:
        kwargs["model_url"] = args.model_url
    if args.fence_output is not None:
        kwargs["fence_output"] = args.fence_output
    if args.temperature is not None:
        kwargs["temperature"] = args.temperature

    print(f"Running extraction with model={args.model}, passes={args.passes}, workers={args.workers}...")
    result = lx.extract(**kwargs)

    results = result if isinstance(result, list) else [result]
    total = sum(len(r.extractions) for r in results)
    print(f"Extracted {total} entity/entities from {len(results)} document(s).")

    out_dir = pathlib.Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    lx.io.save_annotated_documents(results, output_dir=out_dir, output_name=args.output)
    jsonl_path = out_dir / args.output
    print(f"Saved: {jsonl_path}")

    if args.visualize:
        html = lx.visualize(str(jsonl_path))
        html_path = jsonl_path.with_suffix(".html")
        with open(html_path, "w") as f:
            f.write(html.data if hasattr(html, "data") else html)
        print(f"Visualization: {html_path}")


if __name__ == "__main__":
    main()
