import json
from datetime import datetime, timezone
from typing import Dict, Any

from models import RawAIFlawReport, ProcessedAIFlawReport, AISystem
from kb import KnowledgeBase


def process_raw_report(raw_report: RawAIFlawReport) -> ProcessedAIFlawReport:
    """Convert raw form data to processed report by resolving AI systems and other data."""
    kb = KnowledgeBase()

    # Process known systems
    ai_systems = []
    for slug in raw_report.ai_systems:
        system_data = kb.find_system_by_slug(slug)
        if system_data:
            internal_data = system_data.get("_aifr_internal", {})
            ai_system = AISystem(
                id=system_data.get("@id", ""),
                name=system_data.get("name", ""),
                version=system_data.get("version", ""),
                slug=internal_data.get("slug", slug),
                display_name=internal_data.get(
                    "displayName", system_data.get("name", "")
                ),
                description=None,
                system_type="known",
            )
            ai_systems.append(ai_system)

    # Generate report ID first, make it stable hashed rather than random
    report_id = f"{hash(raw_report.model_dump_json()) % 100000}"

    # Process unknown systems - generate stable IDs based on report ID
    for idx, unknown in enumerate(raw_report.ai_systems_unknown):
        temp_id = f"https://aifr.org/reports/{report_id}/unknown-system-{idx + 1}"
        ai_system = AISystem(
            id=temp_id,
            name="Unknown System",
            version="",
            slug="",
            display_name="Unknown System",
            system_type="unknown",
            description=unknown.description,
        )
        ai_systems.append(ai_system)

    # Create processed report
    processed_report = ProcessedAIFlawReport(
        report_id=report_id,
        created_at=datetime.now(timezone.utc),
        ai_systems=ai_systems,
        flaw_description=raw_report.flaw_description,
        flaw_severity=raw_report.flaw_severity,
    )

    return processed_report


def serialize_to_jsonld(processed_report: ProcessedAIFlawReport) -> Dict[str, Any]:
    """Convert processed report to JSON-LD with real-world IDs and linked data semantics."""
    kb = KnowledgeBase()

    # Process systems for JSON-LD output
    jsonld_systems = []
    system_names = []

    for system in processed_report.ai_systems:
        if system.system_type == "unknown":
            # Unknown system with temporary ID
            jsonld_systems.append(
                {
                    "@type": "schema:SoftwareApplication",
                    "@id": system.id,
                    "description": system.description,
                }
            )
            system_names.append("Unknown System")
        else:
            # Known system - get clean JSON-LD from knowledge base
            jsonld_system = kb.get_system_jsonld(system.slug)
            if not jsonld_system:
                raise ValueError(
                    f"System slug '{system.slug}' not found in knowledge base"
                )

            jsonld_systems.append(jsonld_system)
            system_names.append(system.display_name)

    # Create JSON-LD structure
    return {
        "@context": [
            "https://schema.org/",
            {
                "aifr": "urn:aifr:vocab:",
                "aiSystem": "aifr:aiSystem",
                "severity": "aifr:severity",
            },
        ],
        "@type": "aifr:AIFlawReport",
        "@id": f"https://aifr.org/reports/{processed_report.report_id}",
        "name": f"AI Flaw Report: {', '.join(system_names)}",
        "description": processed_report.flaw_description,
        "aiSystem": jsonld_systems,
        "severity": processed_report.flaw_severity,
    }


def main():
    # Load the example form data from the file
    with open("example_form_report_data.json") as f:
        raw_form_data = json.load(f)

    print("\n=== Example Form Data ===")
    print("Raw Form Data:")
    print(json.dumps(raw_form_data, indent=2))

    # Validate form data with Pydantic
    try:
        validated_form_data = RawAIFlawReport(**raw_form_data)
        print(f"\nForm validation passed")
    except Exception as e:
        print(f"\nForm validation failed: {e}")
        return

    # Stage 1: Raw Form data -> Processed
    # This turns slugs from the frontend into objects representing the systems.
    # This processed form can be considered complete, in some sense.
    processed_report = process_raw_report(validated_form_data)
    print(f"\nProcessed Report:")
    print(processed_report.model_dump_json(indent=2))

    # Stage 2: Processed -> JSON-LD
    # This is the extra step -- adding real-world IDs and linked data semantics.
    jsonld_report = serialize_to_jsonld(processed_report)
    print("\nGenerated JSON-LD Report:")
    print(json.dumps(jsonld_report, indent=2))


if __name__ == "__main__":
    main()
