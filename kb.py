"""
Knowledge Base abstraction layer for AIFR system.

Handles all lookups for info about systems and organizations needed for frontend,
as well as JSON-LD data lookups needed for serialization to real linked data.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List


def _clean_internal_fields(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove fields starting with underscore for clean JSON-LD output."""
    return {k: v for k, v in data.items() if not k.startswith("_")}


class KnowledgeBase:
    """Abstraction layer for AIFR knowledge base operations."""

    def __init__(self, kb_path: str = "knowledge-base"):
        """Initialize KB and load all knowledge base files."""
        self.kb_path = Path(kb_path)
        self.systems_data = None
        self.organizations_data = None
        self.slug_map = {}

        with open(self.kb_path / "ai-systems.jsonld") as f:
            self.systems_data = json.load(f)
            for system in self.systems_data["@graph"]:
                slug = system.get("_aifr_internal", {}).get("slug")
                if slug:
                    self.slug_map[slug] = system

        with open(self.kb_path / "organizations.jsonld") as f:
            self.organizations_data = json.load(f)
            for org in self.organizations_data["@graph"]:
                slug = org.get("_aifr_internal", {}).get("slug")
                if slug:
                    self.slug_map[slug] = org

    def find_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """Find system or organization by internal slug."""
        return self.slug_map.get(slug)

    def find_system_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """Find AI system by internal slug."""
        for system in self.systems_data["@graph"]:
            if system.get("_aifr_internal", {}).get("slug") == slug:
                return system
        return None

    def find_organization_by_id(self, org_id: str) -> Optional[Dict[str, Any]]:
        """Find organization by @id URI."""
        for org in self.organizations_data["@graph"]:
            if org.get("@id") == org_id:
                return org
        return None

    def get_system_jsonld(self, slug: str) -> Optional[Dict[str, Any]]:
        """Get clean JSON-LD representation of system with full publisher data."""
        system = self.find_system_by_slug(slug)
        if not system:
            return None

        # Create clean copy without internal fields
        jsonld_system = _clean_internal_fields(system)

        # Replace publisher reference with full organization data
        publisher_id = system.get("publisher", {}).get("@id")
        if publisher_id:
            org_data = self.find_organization_by_id(publisher_id)
            if org_data:
                # Clean organization data and use as publisher
                jsonld_system["publisher"] = _clean_internal_fields(org_data)

        return jsonld_system

    def get_all_system_slugs(self) -> List[str]:
        """Get list of all available system slugs for frontend dropdowns."""
        slugs_names = []
        for system in self.systems_data["@graph"]:
            slug = system.get("_aifr_internal", {}).get("slug")
            display_name = system.get("_aifr_internal", {}).get("displayName")
            if slug and display_name:
                slugs_names.append((slug, display_name))
        return sorted(slugs_names, key=lambda x: x[1].lower())
