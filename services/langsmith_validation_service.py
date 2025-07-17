import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from langsmith import Client
from langsmith.evaluation import EvaluationResult, EvaluationResultType
from models.validation_models import (
    FieldType, ValidationResult, ConversationFlowValidation, 
    QuestionValidation, FieldValidationConfig
)

class LangSmithValidationService:
    def __init__(self, field_type: FieldType):
        load_dotenv()
        self.field_type = field_type
        
        # Initialize LangSmith client
        self.client = Client(
            api_url=os.environ.get("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com"),
            api_key=os.environ.get("LANGSMITH_API_KEY")
        )
        
        self.field_config = self._get_field_config(field_type)
    
    def _get_field_config(self, field_type: FieldType) -> FieldValidationConfig:
        """Get validation configuration for specific field type"""
        # Same configuration as before
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
        """Validate conversation using LangSmith evaluation"""
        
        # Create a dataset for this validation
        dataset_name = f"{self.field_type.value}_chatbot_validation"
        
        try:
            # Create evaluation dataset
            dataset = self.client.create_dataset(
                dataset_name=dataset_name,
                description=f"Validation dataset for {self.field_type.value} chatbot"
            )
            
            # Evaluate each question using LangSmith
            question_validations = []
            overall_score = 0.0
            
            for i, msg in enumerate(conversation_history):
                if "question" in msg:
                    question = msg["question"]
                    response = msg.get("response", "")
                    
                    # Create evaluation example
                    example = self.client.create_example(
                        inputs={"question": question, "response": response},
                        outputs={"field_type": self.field_type.value},
                        dataset_id=dataset.id
                    )
                    
                    # Evaluate using LangSmith
                    evaluation = await self._evaluate_question_with_langsmith(
                        question, response, i, conversation_history[:i], example
                    )
                    
                    question_validations.append(evaluation)
                    overall_score += evaluation.relevance_score
            
            # Calculate average score
            overall_score = overall_score / len(question_validations) if question_validations else 0.0
            
            # Evaluate conversation flow
            flow_validation = await self._evaluate_conversation_flow_with_langsmith(
                conversation_history, dataset
            )
            
            # Generate recommendations
            recommendations = await self._generate_recommendations_with_langsmith(
                question_validations, flow_validation, dataset
            )
            
            result = ValidationResult(
                field_type=self.field_type,
                conversation_flow=flow_validation,
                question_validations=question_validations,
                overall_score=overall_score,
                recommendations=recommendations,
                passed=overall_score >= 0.8
            )
            
            return result
            
        except Exception as e:
            print(f"LangSmith validation error: {str(e)}")
            raise
    
    async def _evaluate_question_with_langsmith(
        self, question: str, response: str, question_index: int, 
        previous_conversation: List[Dict[str, Any]], example
    ) -> QuestionValidation:
        """Evaluate question using LangSmith evaluation"""
        
        # Create evaluation criteria
        evaluation_criteria = {
            "relevance": {
                "description": f"Question relevance to {self.field_type.value} domain",
                "score": 0.0
            },
            "logical_consistency": {
                "description": "Logical consistency with previous responses",
                "score": 0.0
            },
            "appropriateness": {
                "description": "Appropriateness for the context",
                "score": 0.0
            }
        }
        
        # Evaluate relevance
        relevant_topics = self.field_config.relevant_topics
        irrelevant_topics = self.field_config.irrelevant_topics
        
        relevance_score = 0.0
        if any(topic in question.lower() for topic in relevant_topics):
            relevance_score = 0.9
        elif any(topic in question.lower() for topic in irrelevant_topics):
            relevance_score = 0.1
        else:
            relevance_score = 0.5
        
        # Create evaluation result
        evaluation_result = EvaluationResult(
            key="question_relevance",
            score=relevance_score,
            comment=f"Question relevance to {self.field_type.value} domain",
            result_type=EvaluationResultType.SCORE
        )
        
        # Log evaluation to LangSmith
        self.client.create_feedback(
            example_id=example.id,
            key="relevance_score",
            score=relevance_score,
            comment=f"Question: {question}, Score: {relevance_score}"
        )
        
        return QuestionValidation(
            question_text=question,
            is_relevant=relevance_score > 0.5,
            relevance_score=relevance_score,
            validation_issues=[] if relevance_score > 0.5 else ["Question not relevant to domain"],
            suggested_improvements=[] if relevance_score > 0.5 else ["Make question more relevant to domain"]
        )
    
    async def _evaluate_conversation_flow_with_langsmith(
        self, conversation_history: List[Dict[str, Any]], dataset
    ) -> ConversationFlowValidation:
        """Evaluate conversation flow using LangSmith"""
        
        questions = [msg["question"] for msg in conversation_history if "question" in msg]
        responses = [msg["response"] for msg in conversation_history if "response" in msg]
        
        # Calculate metrics
        relevant_count = sum(1 for q in questions if any(topic in q.lower() for topic in self.field_config.relevant_topics))
        total_questions = len(questions)
        
        # Create flow evaluation
        flow_score = relevant_count / total_questions if total_questions > 0 else 0.0
        
        # Log flow evaluation
        self.client.create_feedback(
            dataset_id=dataset.id,
            key="conversation_flow_score",
            score=flow_score,
            comment=f"Overall conversation flow score: {flow_score}"
        )
        
        return ConversationFlowValidation(
            conversation_id=f"{self.field_type.value}_conversation",
            field_type=self.field_type,
            total_questions=total_questions,
            relevant_questions=relevant_count,
            irrelevant_questions=total_questions - relevant_count,
            logical_inconsistencies=[],
            validation_score=flow_score,
            overall_assessment="Evaluated using LangSmith"
        )
    
    async def _generate_recommendations_with_langsmith(
        self, question_validations: List[QuestionValidation], 
        flow_validation: ConversationFlowValidation, dataset
    ) -> List[str]:
        """Generate recommendations using LangSmith"""
        
        recommendations = []
        
        # Analyze using LangSmith data
        irrelevant_count = sum(1 for qv in question_validations if not qv.is_relevant)
        if irrelevant_count > 0:
            recommendations.append(f"Remove or modify {irrelevant_count} irrelevant questions")
        
        if flow_validation.validation_score < 0.8:
            recommendations.append("Improve overall conversation quality and relevance")
        
        # Log recommendations
        self.client.create_feedback(
            dataset_id=dataset.id,
            key="recommendations",
            score=1.0 if not recommendations else 0.0,
            comment=f"Recommendations: {', '.join(recommendations)}"
        )
        
        return recommendations
    
    def get_validation_dashboard_url(self, dataset_id: str) -> str:
        """Get URL to view validation results in LangSmith dashboard"""
        return f"https://smith.langchain.com/datasets/{dataset_id}"
    
    def create_validation_test_suite(self, field_type: FieldType) -> str:
        """Create a comprehensive test suite for the field type"""
        
        test_suite_name = f"{field_type.value}_validation_tests"
        
        # Create test cases
        test_cases = [
            {
                "input": {"question": "What's your favorite baseball team?", "response": "Yankees"},
                "expected": {"relevance": 0.9, "is_relevant": True}
            },
            {
                "input": {"question": "Are you married?", "response": "Yes"},
                "expected": {"relevance": 0.1, "is_relevant": False}
            }
        ]
        
        # Create test suite
        test_suite = self.client.create_test_suite(
            name=test_suite_name,
            description=f"Validation tests for {field_type.value} chatbot"
        )
        
        # Add test cases
        for test_case in test_cases:
            self.client.create_example(
                inputs=test_case["input"],
                outputs=test_case["expected"],
                dataset_id=test_suite.id
            )
        
        return test_suite.id 