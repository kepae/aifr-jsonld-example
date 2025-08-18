# aifr-jsonld-example

Example on how to add richer data to AI systems that are collected in a reporting form, and then convert that to JSON-LD with real-world identifiers/URLs.

An example flaw report from a frontend form using slug-ified data is:
* loaded into an initial PyDantic model (`RawAIFlawReport`) for validation
* processed further to resolve slugs/internal IDs into expanded objects (`ProcessedAIFlawReport`), using an internal lookup knowledge base
* and further processed and dumped to JSON-LD (`@type: AIFlawReport`) along with example organization data

The result is a JSON-LD object representing the flaw report, but enriched with linked data to the publishers of the AI systems. The validated `ProcessedAIFlawReport` is also suitable for sharing if JSON-LD isn't desired/is too complex.

NOTE: the example `aifr` vocabulary is a stand-in, which defines the JSON-LD type `AIFlawReport` that describes the output JSON-LD.

This process can be repeated for other fields where the frontend form needs only to know a display name, but during processing is resolved to a more rich object to attach to the report. For example, values for severities could be resolved and their definitions attached to the report.


## Example

```shell
uv run main.py
```

Raw Form Data:
```json
{
  "ai_systems": [
    "claude-sonnet-4",
    "deepseek-r1"
  ],
  "ai_systems_unknown": [
    {
      "description": "free text description of unknown system by user"
    }
  ],
  "flaw_description": "The AI sometimes generates incorrect information about recent events.",
  "flaw_severity": "Medium"
}
```

Processed Report:
```json
{
  "report_id": "63957",
  "created_at": "2025-08-18T19:13:09.414024Z",
  "ai_systems": [
    {
      "id": "https://www.anthropic.com/claude/sonnet",
      "name": "Claude",
      "version": "Sonnet 4.0",
      "slug": "claude-sonnet-4",
      "display_name": "Claude Sonnet 4.0",
      "system_type": "known",
      "description": null
    },
    {
      "id": "https://huggingface.co/deepseek-ai/DeepSeek-R1",
      "name": "DeepSeek-R1",
      "version": "R1",
      "slug": "deepseek-r1",
      "display_name": "DeepSeek-R1",
      "system_type": "known",
      "description": null
    },
    {
      "id": "https://aifr.org/reports/63957/unknown-system-1",
      "name": "Unknown System",
      "version": "",
      "slug": "",
      "display_name": "Unknown System",
      "system_type": "unknown",
      "description": "free text description of unknown system by user"
    }
  ],
  "flaw_description": "The AI sometimes generates incorrect information about recent events.",
  "flaw_severity": "Medium"
}
```

Generated JSON-LD Report:
```json
{
  "@context": [
    "https://schema.org/",
    {
      "aifr": "urn:aifr:vocab:",
      "aiSystem": "aifr:aiSystem",
      "severity": "aifr:severity"
    }
  ],
  "@type": "aifr:AIFlawReport",
  "@id": "https://aifr.org/reports/73652",
  "name": "AI Flaw Report: Claude Sonnet 4.0, DeepSeek-R1, Unknown System",
  "description": "The AI sometimes generates incorrect information about recent events.",
  "aiSystem": [
    {
      "@type": "schema:SoftwareApplication",
      "@id": "https://www.anthropic.com/claude/sonnet",
      "name": "Claude",
      "version": "Sonnet 4.0",
      "publisher": {
        "@type": "schema:Organization",
        "@id": "https://www.anthropic.com/",
        "name": "Anthropic",
        "url": "https://www.anthropic.com/",
        "sameAs": [
          "https://en.wikipedia.org/wiki/Anthropic",
          "https://www.crunchbase.com/organization/anthropic"
        ]
      }
    },
    {
      "@type": "schema:SoftwareApplication",
      "@id": "https://huggingface.co/deepseek-ai/DeepSeek-R1",
      "name": "DeepSeek-R1",
      "version": "R1",
      "publisher": {
        "@type": "schema:Organization",
        "@id": "https://www.deepseek.com/",
        "name": "DeepSeek AI",
        "url": "https://www.deepseek.com/",
        "sameAs": [
          "https://huggingface.co/deepseek-ai"
        ]
      }
    },
    {
      "@type": "schema:SoftwareApplication",
      "@id": "https://aifr.org/reports/73652/unknown-system-1",
      "description": "free text description of unknown system by user"
    }
  ],
  "severity": "Medium"
}
```