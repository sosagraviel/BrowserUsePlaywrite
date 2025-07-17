from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum

class FieldType(str, Enum):
    BASEBALL = "baseball"
    INSURANCE = "insurance"
    RETIREMENT = "retirement"
    REAL_ESTATE = "real_estate"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    FINANCE = "finance"
    GENERAL = "general"
    FINANCIAL_ADVISOR = "financial_advisor"

class Conversation(BaseModel):
    """Represents a conversation for validation"""
    id: str
    field_type: FieldType
    messages: List[Dict[str, Any]]
    metadata: Dict[str, Any] = {}

class ValidationSeverity(str, Enum):
    CRITICAL = "critical"    # Flow-breaking inconsistency
    WARNING = "warning"      # Minor inconsistency
    INFO = "info"           # Suggestion for improvement

class ValidationRule(BaseModel):
    rule_id: str
    description: str
    field_type: FieldType
    severity: ValidationSeverity
    condition: str  # Natural language description of the rule
    validation_logic: str  # How to validate this rule

class QuestionValidation(BaseModel):
    question_text: str
    is_relevant: bool
    relevance_score: float = Field(ge=0.0, le=1.0)
    validation_issues: List[str] = []
    suggested_improvements: List[str] = []

class ConversationFlowValidation(BaseModel):
    conversation_id: str
    field_type: FieldType
    total_questions: int
    relevant_questions: int
    irrelevant_questions: int
    logical_inconsistencies: List[str] = []
    validation_score: float = Field(ge=0.0, le=1.0)
    overall_assessment: str

class FieldValidationConfig(BaseModel):
    field_type: FieldType
    relevant_topics: List[str]
    irrelevant_topics: List[str]
    logical_rules: List[ValidationRule]
    required_questions: List[str] = []
    forbidden_questions: List[str] = []

class ValidationResult(BaseModel):
    conversation_id: str
    field_type: FieldType
    relevance_score: float = Field(ge=0.0, le=10.0)
    logical_consistency_score: float = Field(ge=0.0, le=10.0)
    overall_score: float = Field(ge=0.0, le=10.0)
    issues: List[str] = []
    recommendations: List[str] = []
    metadata: Dict[str, Any] = {} 