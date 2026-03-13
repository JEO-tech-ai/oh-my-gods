# LangExtract API Reference

> Source: https://github.com/google/langextract | License: Apache-2.0

---

## Top-level functions

### `lx.extract()`

```python
lx.extract(
    text_or_documents,          # str | URL | Document | list[Document]
    prompt_description=None,    # str — extraction instructions
    examples=None,              # list[ExampleData]
    model_id="gemini-2.5-flash",
    api_key=None,               # or env var LANGEXTRACT_API_KEY
    format_type=None,           # FormatType.JSON | FormatType.YAML
    max_char_buffer=1000,       # int — chunk size in characters
    temperature=None,           # float | None — 0.0 = deterministic
    fence_output=None,          # bool | None — auto for Gemini; True required for OpenAI
    use_schema_constraints=True,# bool — False required for OpenAI/Ollama
    batch_length=10,            # int — items per batch
    max_workers=10,             # int — parallel LLM calls
    additional_context=None,    # str | None — appended to prompt
    resolver_params=None,       # dict | None
    language_model_params=None, # dict | None — e.g. {"vertexai": True, "batch": {...}}
    debug=False,                # bool
    model_url=None,             # str | None — Ollama: "http://localhost:11434"
    extraction_passes=1,        # int — repeat passes for higher recall
    context_window_chars=None,  # int | None
    config=None,                # ModelConfig | None
    model=None,                 # pre-built model instance
    fetch_urls=True,            # bool — auto-fetch http(s) URLs
    prompt_validation_level=PromptValidationLevel.WARNING,
    prompt_validation_strict=False,
    show_progress=True,
    tokenizer=None,             # Tokenizer | None
) -> AnnotatedDocument | list[AnnotatedDocument]
```

Returns a single `AnnotatedDocument` for a single input, or a `list[AnnotatedDocument]` for a list of `Document` objects.

---

### `lx.visualize()`

```python
lx.visualize(jsonl_path_or_data) -> str | HTML
```

Generates an interactive self-contained HTML visualization from a JSONL file.
Returns an `HTML` object in Jupyter/Colab (call `.data` for the string) or a plain string.

---

### `lx.io.save_annotated_documents()`

```python
lx.io.save_annotated_documents(
    annotated_documents,       # Iterator[AnnotatedDocument]
    output_dir=None,           # Path | str | None — defaults to "test_output/"
    output_name="data.jsonl",  # str
    show_progress=True,
) -> None
```

---

## Core data classes

### `lx.data.Extraction`

```python
lx.data.Extraction(
    extraction_class: str,                        # entity type label
    extraction_text: str,                         # verbatim text span
    *,
    char_interval: CharInterval | None = None,    # set by extract(), not manually
    alignment_status: AlignmentStatus | None = None,
    extraction_index: int | None = None,
    group_index: int | None = None,
    description: str | None = None,
    attributes: dict[str, str | list[str]] | None = None,
)
```

### `lx.data.ExampleData`

```python
lx.data.ExampleData(
    text: str,                    # example source text
    extractions: list[Extraction] # annotations for this example
)
```

### `lx.data.Document`

```python
lx.data.Document(
    text: str,
    *,
    document_id: str | None = None,      # auto-generated UUID if None
    additional_context: str | None = None,
)
```

### `lx.data.AnnotatedDocument`

Result object returned by `lx.extract()`:

```python
doc.text           # str — original source text
doc.document_id    # str — unique ID
doc.extractions    # list[Extraction] — all extracted entities
```

### `lx.data.CharInterval`

```python
interval.start_pos   # int | None — inclusive character start
interval.end_pos     # int | None — exclusive character end
```

---

## ModelConfig (explicit provider selection)

```python
from langextract.factory import ModelConfig

config = ModelConfig(
    model_id="gemini-2.5-flash",
    provider=None,             # str | None — explicit provider class name
    provider_kwargs={},        # dict — passed to provider __init__
)

result = lx.extract(..., config=config)
```

---

## Environment variables

| Variable | Description |
|----------|-------------|
| `LANGEXTRACT_API_KEY` | Gemini or fallback API key |
| `GEMINI_API_KEY` | Gemini-specific key (takes priority for Gemini models) |
| `OPENAI_API_KEY` | OpenAI-specific key |
| `OLLAMA_BASE_URL` | Ollama base URL (default: `http://localhost:11434`) |

---

## Supported models (built-in providers)

| Provider | Model pattern | Extra install |
|----------|--------------|---------------|
| Gemini | `gemini-*` | none |
| OpenAI | `gpt-*` | `pip install "langextract[openai]"` |
| Ollama | `ollama:*` or `gemma*`, `llama*`, etc. + `model_url` | Ollama running locally |
| Vertex AI | any Gemini model + `language_model_params={"vertexai": True}` | GCP auth configured |

---

## Custom provider registration

```python
from langextract import registry
from langextract.core import base_model

@registry.register("my_provider", pattern=r"myprovider/.*")
class MyProvider(base_model.BaseLanguageModel):
    def __init__(self, model_id: str, **kwargs):
        self.model_id = model_id

    def generate(self, prompt: str, **kwargs) -> str:
        # call your endpoint
        ...

    def get_schema_class(self):
        return None  # or a pydantic schema class

# Distribute as a package with entry_points:
# [project.entry-points."langextract.providers"]
# my_provider = "my_package.provider:MyProvider"
```

---

## Vertex AI batch processing

```python
result = lx.extract(
    ...,
    language_model_params={
        "vertexai": True,
        "batch": {
            "enabled": True,
            # optional overrides:
            # "gcs_input_uri": "gs://bucket/input",
            # "gcs_output_uri": "gs://bucket/output",
        },
        "project": "your-gcp-project",
        "location": "global",
    }
)
```

Falls back to real-time API automatically if batch fails.

---

## AlignmentStatus enum

| Value | Meaning |
|-------|---------|
| `MATCH_EXACT` | extraction_text found verbatim in source |
| `MATCH_GREATER` | aligned span is larger than extraction_text |
| `MATCH_LESSER` | aligned span is smaller than extraction_text |
| `MATCH_FUZZY` | approximate match |
