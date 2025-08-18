"""
Pydantic models for AIFR form data.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator


class UnknownAISystem(BaseModel):
    """Schema for unknown AI systems described by users."""
    description: str = Field(..., min_length=1, description="User description of unknown AI system")


class RawAIFlawReport(BaseModel):
    """Raw form input - simple validation only."""
    
    ai_systems: List[str] = Field(default=[], description="List of known AI system slugs from dropdown")
    ai_systems_unknown: List[UnknownAISystem] = Field(default=[], description="List of unknown systems with descriptions")
    flaw_description: str = Field(..., min_length=10, description="Description of the flaw or issue")
    flaw_severity: str = Field(..., description="Severity level of the flaw")
    
    @validator('flaw_severity')
    def validate_severity(cls, v):
        valid_severities = {'Low', 'Medium', 'High', 'Critical'}
        if v not in valid_severities:
            raise ValueError(f'Severity must be one of: {valid_severities}')
        return v
    
    @validator('ai_systems', 'ai_systems_unknown')
    def validate_at_least_one_system(cls, v, values):
        # Check if we have at least one system (known or unknown)
        ai_systems = values.get('ai_systems', []) if 'ai_systems' in values else v
        ai_systems_unknown = values.get('ai_systems_unknown', []) if 'ai_systems_unknown' in values else v
        
        if not ai_systems and not ai_systems_unknown:
            raise ValueError('Must specify at least one AI system (known or unknown)')
        return v


class AISystem(BaseModel):
    """AI System information - clean business data without JSON-LD semantics."""
    
    # Core system data
    id: str = Field(..., description="System identifier/URL")
    name: str = Field(..., description="System name")
    version: str = Field(..., description="System version")
    slug: str = Field(..., description="Internal slug for lookups")
    display_name: str = Field(..., description="Human-friendly display name")
    
    # System type
    system_type: str = Field(default="known", description="'known' or 'unknown'")
    description: Optional[str] = Field(None, description="For unknown systems")

    @validator('system_type')
    def validate_system_type(cls, v):
        if v not in {'known', 'unknown'}:
            raise ValueError("System type must be either 'known' or 'unknown'")
        return v


class ProcessedAIFlawReport(BaseModel):
    """Fully processed flaw report - rich data suitable as end product."""
    
    # Processing metadata
    report_id: str = Field(..., description="Generated report ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Report creation timestamp")
  
    ai_systems: List[AISystem] = Field(..., description="Fully enriched system data")
    flaw_description: str = Field(..., description="Flaw description")
    flaw_severity: str = Field(..., description="Severity level")
    
    
    class Config:
        # Allow arbitrary field assignment during processing
        validate_assignment = True

    @validator('ai_systems')
    def validate_at_least_one_system(cls, v, values):
        # Check if we have at least one system
        ai_systems = values.get('ai_systems', []) if 'ai_systems' in values else v

        if not ai_systems:
            raise ValueError('Must specify at least one AI system')
        return v