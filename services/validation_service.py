import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langfuse.decorators import observe, langfuse_context
from models.validation_models import (
    FieldType, ValidationResult, ConversationFlowValidation, 
    QuestionValidation, FieldValidationConfig, ValidationRule
)

class ChatbotValidationService:
    def __init__(self, field_type: FieldType):
        load_dotenv()
        self.field_type = field_type
        
        # Check if API key is available
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found in environment variables. "
                "Please set it in your .env file or export it in your shell."
            )
        
        self.llm = ChatAnthropic(
            model='claude-3-haiku-20240307',
            api_key=api_key
        )
        self.field_config = self._get_field_config(field_type)
    
    def _get_field_config(self, field_type: FieldType) -> FieldValidationConfig:
        """Get validation configuration for specific field type"""
        configs = {
            FieldType.BASEBALL: FieldValidationConfig(
                field_type=FieldType.BASEBALL,
                relevant_topics=[
                    "baseball", "sports", "teams", "players", "games", "scores",
                    "statistics", "rules", "equipment", "training", "coaching"
                ],
                irrelevant_topics=[
                    "real estate", "house", "mortgage", "insurance", "healthcare",
                    "marriage", "divorce", "personal relationships"
                ],
                logical_rules=[
                    ValidationRule(
                        rule_id="baseball_no_personal_questions",
                        description="Baseball chatbot should not ask personal questions unrelated to baseball",
                        field_type=FieldType.BASEBALL,
                        severity="critical",
                        condition="If question is about personal life (marriage, house, etc.) and not baseball-related",
                        validation_logic="Flag as irrelevant if personal question not related to baseball"
                    )
                ],
                required_questions=[],
                forbidden_questions=["Are you married?", "Do you own a house?", "What's your relationship status?"]
            ),
            FieldType.INSURANCE: FieldValidationConfig(
                field_type=FieldType.INSURANCE,
                relevant_topics=[
                    "insurance", "coverage", "policies", "claims", "premiums",
                    "deductibles", "benefits", "risk assessment", "liabilities"
                ],
                irrelevant_topics=[
                    "baseball", "sports", "cooking", "entertainment", "hobbies"
                ],
                logical_rules=[
                    ValidationRule(
                        rule_id="insurance_logical_flow",
                        description="Insurance questions should follow logical flow",
                        field_type=FieldType.INSURANCE,
                        severity="critical",
                        condition="If user says they are married but next question asks about breakup",
                        validation_logic="Flag as logical inconsistency"
                    )
                ],
                required_questions=[],
                forbidden_questions=[]
            )
        }
        return configs.get(field_type, FieldValidationConfig(
            field_type=field_type,
            relevant_topics=[],
            irrelevant_topics=[],
            logical_rules=[]
        ))
    
    @observe()
    async def validate_conversation(self, conversation) -> ValidationResult:
        """Validate entire conversation flow from a Conversation object or message list"""
        # Accepts either a Conversation object or a list of messages
        if hasattr(conversation, 'messages'):
            messages = conversation.messages
        else:
            messages = conversation  # fallback for list input

        # Heuristic: treat 'assistant' role as questions, 'user' as responses
        questions = [msg["content"] for msg in messages if msg.get("role") == "assistant"]
        responses = [msg["content"] for msg in messages if msg.get("role") == "user"]

        # Validate each question
        question_validations = []
        for i, question in enumerate(questions):
            validation = await self._validate_question(question, i, responses[:i] if i > 0 else [])
            question_validations.append(validation)

        # Analyze conversation flow
        flow_validation = await self._validate_conversation_flow(questions, responses)

        # Calculate scores
        relevant_count = sum(1 for qv in question_validations if qv.is_relevant)
        total_questions = len(question_validations)
        relevance_score = (
            sum(qv.relevance_score for qv in question_validations) / total_questions * 10
            if total_questions > 0 else 0.0
        )
        logical_consistency_score = flow_validation.validation_score * 10 if hasattr(flow_validation, 'validation_score') else 0.0
        overall_score = (relevance_score + logical_consistency_score) / 2

        # Gather issues
        issues = []
        if hasattr(flow_validation, 'logical_inconsistencies'):
            issues.extend(flow_validation.logical_inconsistencies)
        for qv in question_validations:
            issues.extend(qv.validation_issues)

        # Generate recommendations
        recommendations = await self._generate_recommendations(question_validations, flow_validation)

        return ValidationResult(
            conversation_id=f"{self.field_type.value}_conversation",
            field_type=self.field_type,
            relevance_score=relevance_score,
            logical_consistency_score=logical_consistency_score,
            overall_score=overall_score,
            issues=issues,
            recommendations=recommendations,
            metadata={
                "total_questions": total_questions,
                "relevant_count": relevant_count,
                "flow_assessment": getattr(flow_validation, 'overall_assessment', None)
            }
        )
    
    @observe()
    async def _validate_question(self, question: str, question_index: int, previous_responses: List[str]) -> QuestionValidation:
        """Validate individual question for relevance and logic"""
        
        prompt = f"""
        You are a chatbot validation expert for {self.field_type.value} domain.
        
        Field Configuration:
        - Relevant topics: {', '.join(self.field_config.relevant_topics)}
        - Irrelevant topics: {', '.join(self.field_config.irrelevant_topics)}
        - Forbidden questions: {', '.join(self.field_config.forbidden_questions)}
        
        Question to validate: "{question}"
        Question position: {question_index + 1}
        
        Previous responses: {previous_responses}
        
        Please evaluate this question and provide:
        1. Is this question relevant to {self.field_type.value}? (true/false)
        2. Relevance score (0.0 to 1.0)
        3. Any validation issues
        4. Suggested improvements
        
        Respond in JSON format:
        {{
            "is_relevant": boolean,
            "relevance_score": float,
            "validation_issues": [string],
            "suggested_improvements": [string]
        }}
        """
        
        try:
            response = await self.llm.ainvoke(prompt)
            # Parse JSON response
            import json
            result = json.loads(response.content)
            
            return QuestionValidation(
                question_text=question,
                is_relevant=result.get("is_relevant", False),
                relevance_score=result.get("relevance_score", 0.0),
                validation_issues=result.get("validation_issues", []),
                suggested_improvements=result.get("suggested_improvements", [])
            )
        except Exception as e:
            # Fallback validation
            return QuestionValidation(
                question_text=question,
                is_relevant=False,
                relevance_score=0.0,
                validation_issues=[f"Validation error: {str(e)}"],
                suggested_improvements=["Review question manually"]
            )
    @observe
    async def _validate_conversation_flow(self, questions: List[str], responses: List[str]) -> ConversationFlowValidation:
        """Validate logical consistency of conversation flow"""
        
        prompt = f"""
        You are analyzing a {self.field_type.value} chatbot conversation for logical consistency.
        
        Questions: {questions}
        Responses: {responses}
        
        Analyze the conversation flow and identify:
        1. Logical inconsistencies (e.g., asking about breakup after user says they're married)
        2. Relevance of questions to {self.field_type.value} domain
        3. Overall conversation quality
        
        Respond in JSON format:
        {{
            "total_questions": int,
            "relevant_questions": int,
            "irrelevant_questions": int,
            "logical_inconsistencies": [string],
            "validation_score": float,
            "overall_assessment": string
        }}
        """
        
        try:
            response = await self.llm.ainvoke(prompt)
            import json
            result = json.loads(response.content)
            
            # Clamp validation_score to [0.0, 1.0]
            validation_score = result.get("validation_score", 0.0)
            validation_score = max(0.0, min(1.0, validation_score))
            
            return ConversationFlowValidation(
                conversation_id=f"{self.field_type.value}_conversation",
                field_type=self.field_type,
                total_questions=result.get("total_questions", len(questions)),
                relevant_questions=result.get("relevant_questions", 0),
                irrelevant_questions=result.get("irrelevant_questions", 0),
                logical_inconsistencies=result.get("logical_inconsistencies", []),
                validation_score=validation_score,
                overall_assessment=result.get("overall_assessment", "No assessment available")
            )
        except Exception as e:
            return ConversationFlowValidation(
                conversation_id=f"{self.field_type.value}_conversation",
                field_type=self.field_type,
                total_questions=len(questions),
                relevant_questions=0,
                irrelevant_questions=len(questions),
                logical_inconsistencies=[f"Validation error: {str(e)}"],
                validation_score=0.0,
                overall_assessment="Validation failed due to error"
            )
    
    async def _generate_recommendations(self, question_validations: List[QuestionValidation], flow_validation: ConversationFlowValidation) -> List[str]:
        """Generate improvement recommendations"""
        
        recommendations = []
        
        # Analyze question relevance
        irrelevant_questions = [qv for qv in question_validations if not qv.is_relevant]
        if irrelevant_questions:
            recommendations.append(f"Remove or modify {len(irrelevant_questions)} irrelevant questions")
        
        # Analyze logical inconsistencies
        if flow_validation.logical_inconsistencies:
            recommendations.append("Fix logical inconsistencies in conversation flow")
        
        # Overall score recommendations
        if flow_validation.validation_score < 0.8:
            recommendations.append("Improve overall conversation quality and relevance")
        
        return recommendations 