---
name: langextract
description: >
  Extract structured information from unstructured text using LLMs with source
  grounding, interactive HTML visualization, and multi-pass recall optimization.
  Use when extracting entities, relationships, or structured data from clinical
  notes, reports, legal documents, books, or any free-form text.
  Triggers on: "extract from text", "structured extraction", "NLP extraction",
  "entity extraction", "information extraction", "parse document", "extract
  entities", "extract relationships", "LLM extraction", "langextract",
  "clinical NLP", "medical extraction", "document parsing", "text mining".
allowed-tools: Bash Read Write Edit Glob Grep
compatibility: Python 3.10+. Cloud models require a Gemini or OpenAI API key. Local inference via Ollama needs Ollama running locally.
license: Apache-2.0
metadata:
  tags: nlp, extraction, llm, gemini, structured-output, document-processing
  version: "1.0"
  source: https://github.com/google/langextract
---

# LangExtract — LLM-Powered Structured Extraction

> Google open-source Python library (34.7k ⭐) for extracting structured information
> from unstructured text with source grounding, interactive visualization, and
> support for Gemini, OpenAI, Ollama, and custom providers.

## When to use this skill

- Extract entities, relationships, or attributes from clinical notes, reports, or any text
- Map every extraction back to its exact location in the source (source grounding)
- Process long documents via automatic chunking + parallel LLM calls
- Visualize thousands of extractions in an interactive, self-contained HTML file
- Run local inference without API keys using Ollama
- Define custom extraction schemas without fine-tuning — just a prompt + few examples

---

## Instructions

### Step 1: Install

```bash
# Basic (Gemini / Ollama)
pip install langextract

# With OpenAI support
pip install "langextract[openai]"

# With all dev/test tools
pip install -e ".[dev,test]"
```

### Step 2: Configure API key

```bash
# Option A — environment variable (recommended)
export LANGEXTRACT_API_KEY="your-gemini-api-key"

# Option B — .env file
echo "LANGEXTRACT_API_KEY=your-key" >> .env

# Option C — inline (testing only, never commit)
result = lx.extract(..., api_key="your-key")
```

Get keys from: [Google AI Studio](https://aistudio.google.com) (Gemini) | [OpenAI Platform](https://platform.openai.com) | [Vertex AI](https://cloud.google.com/vertex-ai)

### Step 3: Define extraction task

```python
import langextract as lx
import textwrap

# 1. Describe what to extract
prompt = textwrap.dedent("""\
    Extract characters, emotions, and relationships in order of appearance.
    Use exact text for extractions. Do not paraphrase or overlap entities.
    Provide meaningful attributes for each entity to add context.""")

# 2. Provide one high-quality few-shot example
examples = [
    lx.data.ExampleData(
        text="ROMEO. But soft! What light through yonder window breaks? It is the east, and Juliet is the sun.",
        extractions=[
            lx.data.Extraction(
                extraction_class="character",
                extraction_text="ROMEO",
                attributes={"emotional_state": "wonder"}
            ),
            lx.data.Extraction(
                extraction_class="emotion",
                extraction_text="But soft!",
                attributes={"feeling": "gentle awe"}
            ),
            lx.data.Extraction(
                extraction_class="relationship",
                extraction_text="Juliet is the sun",
                attributes={"type": "metaphor"}
            ),
        ]
    )
]
```

> **Tip**: `extraction_text` must be verbatim from the example text (no paraphrasing),
> listed in order of appearance. LangExtract raises prompt alignment warnings otherwise.

### Step 4: Run extraction

```python
# Short text
result = lx.extract(
    text_or_documents="Lady Juliet gazed longingly at the stars, her heart aching for Romeo",
    prompt_description=prompt,
    examples=examples,
    model_id="gemini-2.5-flash",
)

# Long document from URL (parallel processing, multi-pass recall)
result = lx.extract(
    text_or_documents="https://www.gutenberg.org/files/1513/1513-0.txt",
    prompt_description=prompt,
    examples=examples,
    model_id="gemini-2.5-flash",
    extraction_passes=3,   # repeat passes improve recall
    max_workers=20,        # parallel LLM calls
    max_char_buffer=1000,  # chunk size in characters
)
```

### Step 5: Save results and visualize

```python
# Save to JSONL
lx.io.save_annotated_documents(
    [result],
    output_name="extractions.jsonl",
    output_dir="."
)

# Generate interactive HTML visualization
html = lx.visualize("extractions.jsonl")
with open("visualization.html", "w") as f:
    f.write(html.data if hasattr(html, "data") else html)
# Open visualization.html in browser — entities highlighted in source context
```

### Step 6: Inspect results in code

```python
# result is an AnnotatedDocument (or list for batch)
for extraction in result.extractions:
    print(f"[{extraction.extraction_class}] '{extraction.extraction_text}'")
    if extraction.char_interval:
        print(f"  Position: {extraction.char_interval.start_pos}–{extraction.char_interval.end_pos}")
    if extraction.attributes:
        print(f"  Attrs: {extraction.attributes}")
```

---

## Model selection

| Model | Use case |
|-------|---------|
| `gemini-2.5-flash` | Default — best balance of speed, cost, quality |
| `gemini-2.5-pro` | Complex reasoning tasks requiring deeper analysis |
| `gpt-4o` | OpenAI alternative (`pip install langextract[openai]`) |
| `gemma2:2b` | Local inference via Ollama (no API key needed) |

**OpenAI extra flags:**
```python
result = lx.extract(
    ...,
    model_id="gpt-4o",
    api_key=os.environ["OPENAI_API_KEY"],
    fence_output=True,        # required for OpenAI
    use_schema_constraints=False,  # required for OpenAI
)
```

**Local Ollama:**
```bash
# One-time setup
curl -fsSL https://ollama.com/install.sh | sh
ollama pull gemma2:2b
ollama serve
```
```python
result = lx.extract(
    ...,
    model_id="gemma2:2b",
    model_url="http://localhost:11434",
    fence_output=False,
    use_schema_constraints=False,
)
```

---

## Batch document processing

```python
# Process multiple Documents in one call
documents = [
    lx.data.Document(text="Patient A: aspirin 100mg daily.", document_id="pt-001"),
    lx.data.Document(text="Patient B: metformin 500mg twice daily.", document_id="pt-002"),
]

results = lx.extract(
    text_or_documents=documents,
    prompt_description="Extract medication names and dosages.",
    examples=med_examples,
    model_id="gemini-2.5-flash",
    max_workers=10,
)
```

---

## Vertex AI batch (cost savings at scale)

```python
result = lx.extract(
    text_or_documents=input_text,
    prompt_description=prompt,
    examples=examples,
    model_id="gemini-2.5-flash",
    language_model_params={
        "vertexai": True,
        "batch": {"enabled": True},
        "project": "your-gcp-project-id",
        "location": "global",
    }
)
```

---

## Custom model providers

```python
from langextract import registry

@registry.register("my_provider", pattern=r"myprovider/.*")
class MyProvider(lx.core.base_model.BaseLanguageModel):
    def __init__(self, model_id, **kwargs):
        self.model_id = model_id

    def generate(self, prompt: str, **kwargs) -> str:
        # call your custom LLM endpoint
        ...

# Use it:
result = lx.extract(
    ...,
    model_id="myprovider/custom-model",
)
```

See: [Provider System Documentation](https://github.com/google/langextract/blob/main/docs/)

---

## Key `lx.extract()` parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `text_or_documents` | — | String, URL, `Document`, or list of `Document` |
| `prompt_description` | — | Natural language extraction instructions |
| `examples` | — | List of `ExampleData` for few-shot learning |
| `model_id` | `"gemini-2.5-flash"` | Model to use |
| `api_key` | env var | API key (or `LANGEXTRACT_API_KEY` env var) |
| `extraction_passes` | `1` | Repeat passes for higher recall (costs proportionally more) |
| `max_workers` | `10` | Parallel LLM calls (speed, no extra token cost) |
| `max_char_buffer` | `1000` | Chunk size in characters |
| `fence_output` | auto | `True` for OpenAI; auto for Gemini |
| `use_schema_constraints` | `True` | `False` for OpenAI/Ollama |
| `temperature` | model default | `0.0` for deterministic extraction |
| `additional_context` | `None` | Extra context appended to prompt |
| `language_model_params` | `{}` | Provider-specific dict (e.g., Vertex AI batch) |
| `model_url` | `None` | Custom endpoint URL (e.g., Ollama `http://localhost:11434`) |
| `debug` | `False` | Verbose debug logging |

---

## Examples

### Example 1: Medication extraction from clinical text

```python
import langextract as lx

prompt = "Extract medication names, dosages, and routes in order of appearance."
examples = [
    lx.data.ExampleData(
        text="Prescribe aspirin 100 mg orally once daily and lisinopril 10 mg PO QD.",
        extractions=[
            lx.data.Extraction("medication", "aspirin 100 mg", attributes={"route": "orally", "frequency": "once daily"}),
            lx.data.Extraction("medication", "lisinopril 10 mg", attributes={"route": "PO", "frequency": "QD"}),
        ]
    )
]

result = lx.extract(
    text_or_documents="Patient is on metformin 500mg twice daily for diabetes.",
    prompt_description=prompt,
    examples=examples,
    model_id="gemini-2.5-flash",
)
for e in result.extractions:
    print(e.extraction_class, e.extraction_text, e.attributes)
```

### Example 2: Long document processing from URL

```python
result = lx.extract(
    text_or_documents="https://www.gutenberg.org/files/1513/1513-0.txt",
    prompt_description=prompt,
    examples=examples,
    model_id="gemini-2.5-flash",
    extraction_passes=3,
    max_workers=20,
    max_char_buffer=1000,
)
lx.io.save_annotated_documents([result], output_name="romeo_juliet.jsonl")
html = lx.visualize("romeo_juliet.jsonl")
with open("viz.html", "w") as f:
    f.write(html.data if hasattr(html, "data") else html)
```

### Example 3: Local LLM with Ollama

```python
result = lx.extract(
    text_or_documents=my_text,
    prompt_description=prompt,
    examples=examples,
    model_id="gemma2:2b",
    model_url="http://localhost:11434",
    fence_output=False,
    use_schema_constraints=False,
)
```

---

## Best practices

1. **Example quality first** — one great verbatim example beats five vague ones
2. **Use `extraction_passes=3`** for long documents requiring high recall (3× API cost)
3. **`max_workers=20`** speeds up long docs at no extra token cost
4. **`temperature=0.0`** for reproducible, deterministic output
5. **JSONL + HTML visualization** — always save results before calling `visualize()`
6. **Vertex AI batch** for cost savings on large-scale production jobs
7. **Ollama** for offline/air-gapped environments or cost-free local testing

---

## Scripts

- **`scripts/langextract_extract.py`** — CLI wrapper: extract from a text file or URL and save JSONL + HTML

```bash
# Extract from a local file
python scripts/langextract_extract.py \
  --input report.txt \
  --prompt "Extract diagnoses and treatments." \
  --examples examples.json \
  --model gemini-2.5-flash \
  --output results.jsonl

# Extract from a URL
python scripts/langextract_extract.py \
  --input https://example.com/report.txt \
  --prompt "Extract entities." \
  --examples examples.json
```

---

## References

- [GitHub: google/langextract](https://github.com/google/langextract)
- [PyPI: langextract](https://pypi.org/project/langextract/)
- [RadExtract Demo (HuggingFace Spaces)](https://huggingface.co/spaces/google/radextract)
- [Community Provider Plugins](https://github.com/google/langextract/blob/main/COMMUNITY_PROVIDERS.md)
- [Provider System Documentation](https://github.com/google/langextract/blob/main/docs/)
- [Vertex AI Batch API Example](https://github.com/google/langextract/tree/main/examples)
- [Ollama Local LLM Example](https://github.com/google/langextract/tree/main/examples/ollama)
- [Contributing Guide](https://github.com/google/langextract/blob/main/CONTRIBUTING.md)
