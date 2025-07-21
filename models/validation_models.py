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
    rule_id: str # Field(description="The unique identifier for the validation rule")
    description: str # Field(description "A description of the validation rule" "Don't ask personal questions in financial advisor field")
    field_type: FieldType # Field(description="The field type that the rule applies to", example="financial_advisor")
    severity: ValidationSeverity # Field(description="The severity of the validation rule", example="critical")
    condition: str  # Natural language description of the rule
    validation_logic: str  # How to validate this rule

class QuestionValidation(BaseModel):
    question_text: str # Field(description="The text of the question", example="What is your name?")
    is_relevant: bool # Field(description="Whether the question is relevant to the field type", example=True)
    relevance_score: float = Field(ge=0.0, le=1.0) # Field(description="The relevance score of the question", example=0.8)
    validation_issues: List[str] = [] # Field(description="The issues with the question", example=["The question is not relevant to the field type"])
    suggested_improvements: List[str] = [] # Field(description="The suggested improvements for the question", example=["Ask a question that is relevant to the field type"])

class ConversationFlowValidation(BaseModel):
    conversation_id: str # Field(description="The unique identifier for the conversation", example="123")
    field_type: FieldType # Field(description="The field type that the conversation applies to", example="financial_advisor")
    total_questions: int # Field(description="The total number of questions in the conversation", example=10)
    relevant_questions: int # Field(description="The number of relevant questions in the conversation", example=8)
    irrelevant_questions: int # Field(description="The number of irrelevant questions in the conversation", example=2)
    logical_inconsistencies: List[str] = [] # Field(description="The logical inconsistencies in the conversation", example=["The question is not relevant to the field type"])
    validation_score: float = Field(ge=0.0, le=1.0) # Field(description="The validation score of the conversation", example=0.8)
    overall_assessment: str # Field(description="The overall assessment of the conversation", example="The conversation is valid")

class FieldValidationConfig(BaseModel):
    field_type: FieldType # Field(description="The field type that the validation config applies to", example="financial_advisor")
    relevant_topics: List[str] # Field(description="The relevant topics for the field type", example=["Personal finance", "Investing", "Retirement"])
    irrelevant_topics: List[str] # Field(description="The irrelevant topics for the field type", example=["Healthcare", "Education", "Travel"])
    logical_rules: List[ValidationRule] # Field(description="The logical rules for the field type", example=[ValidationRule(rule_id="1", description="Don't ask personal questions in financial advisor field", field_type="financial_advisor", severity="critical", condition="The question is not relevant to the field type", validation_logic="The question is not relevant to the field type")])
    required_questions: List[str] = [] # Field(description="The required questions for the field type", example=["What is your name?", "What is your email?"])
    forbidden_questions: List[str] = [] # Field(description="The forbidden questions for the field type", example=["What is your social security number?", "What is your bank account number?"])

class ValidationResult(BaseModel):
    conversation_id: str # Field(description="The unique identifier for the conversation", example="123")
    field_type: FieldType # Field(description="The field type that the validation result applies to", example="financial_advisor")
    relevance_score: float = Field(ge=0.0, le=10.0) # Field(description="The relevance score of the conversation", example=0.8)
    logical_consistency_score: float = Field(ge=0.0, le=10.0) # Field(description="The logical consistency score of the conversation", example=0.8)
    overall_score: float = Field(ge=0.0, le=10.0) # Field(description="The overall score of the conversation", example=0.8)
    issues: List[str] = [] # Field(description="The issues with the conversation", example=["The question is not relevant to the field type"])
    recommendations: List[str] = [] # Field(description="The recommendations for the conversation", example=["Ask a question that is relevant to the field type"])
    metadata: Dict[str, Any] = {} # Field(description="The metadata for the conversation", example={"conversation_id": "123", "field_type": "financial_advisor"})