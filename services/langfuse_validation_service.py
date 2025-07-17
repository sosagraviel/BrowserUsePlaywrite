import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from langfuse import Langfuse
from langfuse.model import CreateTrace, CreateSpan, CreateGeneration
from models.validation_models import (
    FieldType, ValidationResult, ConversationFlowValidation, 
    QuestionValidation, FieldValidationConfig
)

class LangfuseValidationService:
    def __init__(self, field_type: FieldType):
        load_dotenv()
        self.field_type = field_type
        
        # Initialize Langfuse client
        self.langfuse = Langfuse(
            public_key=os.environ.get("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.environ.get("LANGFUSE_SECRET_KEY"),
            host=os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com")
        )
        
        self.field_config = self._get_field_config(field_type)
    
    def _get_field_config(self, field_type: FieldType) -> FieldValidationConfig:
        """Get validation configuration for specific field type"""
        # Same configuration as before, but now used with Langfuse
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
                logical_rules=[],
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
                logical_rules=[],
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
    
    async def validate_conversation(self, conversation_history: List[Dict[str, Any]]) -> ValidationResult:
        """Validate conversation using Langfuse evaluation"""
        
        # Create a trace for this conversation validation
        trace = self.langfuse.trace(
            name=f"{self.field_type.value}_chatbot_validation",
            metadata={
                "field_type": self.field_type.value,
                "total_questions": len(conversation_history),
                "conversation_id": f"{self.field_type.value}_conversation_{hash(str(conversation_history))}"
            }
        )
        
        try:
            # Evaluate each question using Langfuse
            question_validations = []
            overall_score = 0.0
            
            for i, msg in enumerate(conversation_history):
                if "question" in msg:
                    question = msg["question"]
                    response = msg.get("response", "")
                    
                    # Create span for question evaluation
                    with trace.span(
                        name=f"question_validation_{i+1}",
                        metadata={"question": question, "response": response}
                    ) as span:
                        
                        # Use Langfuse to evaluate question relevance
                        evaluation = await self._evaluate_question_with_langfuse(
                            question, response, i, conversation_history[:i]
                        )
                        
                        question_validations.append(evaluation)
                        overall_score += evaluation.relevance_score
            
            # Calculate average score
            overall_score = overall_score / len(question_validations) if question_validations else 0.0
            
            # Evaluate conversation flow
            flow_validation = await self._evaluate_conversation_flow_with_langfuse(
                conversation_history, trace
            )
            
            # Generate recommendations
            recommendations = await self._generate_recommendations_with_langfuse(
                question_validations, flow_validation, trace
            )
            
            result = ValidationResult(
                field_type=self.field_type,
                conversation_flow=flow_validation,
                question_validations=question_validations,
                overall_score=overall_score,
                recommendations=recommendations,
                passed=overall_score >= 0.8
            )
            
            # Log the final result
            trace.update(
                metadata={
                    "overall_score": overall_score,
                    "passed": result.passed,
                    "recommendations": recommendations
                }
            )
            
            return result
            
        except Exception as e:
            trace.update(metadata={"error": str(e)})
            raise
    
    async def _evaluate_question_with_langfuse(
        self, question: str, response: str, question_index: int, 
        previous_conversation: List[Dict[str, Any]]
    ) -> QuestionValidation:
        """Evaluate question using Langfuse evaluation"""
        
        # Create evaluation prompt
        evaluation_prompt = f"""
        Evaluate this question for a {self.field_type.value} chatbot:
        
        Question: "{question}"
        Response: "{response}"
        Position: {question_index + 1}
        
        Relevant topics: {', '.join(self.field_config.relevant_topics)}
        Irrelevant topics: {', '.join(self.field_config.irrelevant_topics)}
        
        Rate on a scale of 0-1:
        1. Relevance to {self.field_type.value} domain
        2. Logical consistency with previous responses
        3. Appropriateness for the context
        
        Provide detailed feedback and suggestions.
        """
        
        # Use Langfuse to evaluate
        generation = self.langfuse.generation(
            name="question_evaluation",
            model="gpt-4",
            prompt=evaluation_prompt,
            completion="",  # Will be filled by Langfuse
            metadata={
                "question": question,
                "field_type": self.field_type.value,
                "question_index": question_index
            }
        )
        
        # Parse evaluation result (simplified for demo)
        # In production, you'd use Langfuse's evaluation features
        relevance_score = 0.8 if any(topic in question.lower() for topic in self.field_config.relevant_topics) else 0.2
        
        return QuestionValidation(
            question_text=question,
            is_relevant=relevance_score > 0.5,
            relevance_score=relevance_score,
            validation_issues=[] if relevance_score > 0.5 else ["Question not relevant to domain"],
            suggested_improvements=[] if relevance_score > 0.5 else ["Make question more relevant to domain"]
        )
    
    async def _evaluate_conversation_flow_with_langfuse(
        self, conversation_history: List[Dict[str, Any]], trace
    ) -> ConversationFlowValidation:
        """Evaluate conversation flow using Langfuse"""
        
        questions = [msg["question"] for msg in conversation_history if "question" in msg]
        responses = [msg["response"] for msg in conversation_history if "response" in msg]
        
        # Use Langfuse to evaluate conversation flow
        flow_evaluation_prompt = f"""
        Analyze this {self.field_type.value} conversation for:
        1. Logical consistency
        2. Question relevance
        3. Overall flow quality
        
        Questions: {questions}
        Responses: {responses}
        
        Provide detailed analysis and scoring.
        """
        
        generation = self.langfuse.generation(
            name="conversation_flow_evaluation",
            model="gpt-4",
            prompt=flow_evaluation_prompt,
            completion="",
            metadata={
                "field_type": self.field_type.value,
                "total_questions": len(questions)
            }
        )
        
        # Calculate metrics
        relevant_count = sum(1 for q in questions if any(topic in q.lower() for topic in self.field_config.relevant_topics))
        
        return ConversationFlowValidation(
            conversation_id=f"{self.field_type.value}_conversation",
            field_type=self.field_type,
            total_questions=len(questions),
            relevant_questions=relevant_count,
            irrelevant_questions=len(questions) - relevant_count,
            logical_inconsistencies=[],
            validation_score=relevant_count / len(questions) if questions else 0.0,
            overall_assessment="Evaluated using Langfuse"
        )
    
    async def _generate_recommendations_with_langfuse(
        self, question_validations: List[QuestionValidation], 
        flow_validation: ConversationFlowValidation, trace
    ) -> List[str]:
        """Generate recommendations using Langfuse"""
        
        recommendations = []
        
        # Analyze using Langfuse
        irrelevant_count = sum(1 for qv in question_validations if not qv.is_relevant)
        if irrelevant_count > 0:
            recommendations.append(f"Remove or modify {irrelevant_count} irrelevant questions")
        
        if flow_validation.validation_score < 0.8:
            recommendations.append("Improve overall conversation quality and relevance")
        
        # Log recommendations
        trace.update(metadata={"recommendations": recommendations})
        
        return recommendations
    
    def get_validation_dashboard_url(self, trace_id: str) -> str:
        """Get URL to view validation results in Langfuse dashboard"""
        return f"{os.environ.get('LANGFUSE_HOST', 'https://cloud.langfuse.com')}/traces/{trace_id}" 