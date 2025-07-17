#!/usr/bin/env python3
"""
Conversation Validation Service
Handles extraction of conversation data from agent results and validation
"""

import json
import os
import sys
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.validation_models import Conversation, ValidationResult, FieldType
from services.validation_service import ChatbotValidationService

class ConversationValidationService:
    """Service for extracting and validating conversations from agent results"""
    
    def __init__(self, field_type: Optional[FieldType] = None):
        # Load field type from environment variable or use provided parameter
        if field_type is None:
            field_type = self._get_field_type_from_env()
        
        # Initialize validation service with the specified field type
        self.validation_service = ChatbotValidationService(field_type=field_type)
        self.field_type = field_type
    
    def _get_field_type_from_env(self) -> FieldType:
        """Get field type from environment variable VALIDATION_FIELD_TYPE"""
        import os
        
        field_type_str = os.getenv("VALIDATION_FIELD_TYPE", "").lower()
        
        # Map environment variable values to FieldType enum
        field_type_mapping = {
            "baseball": FieldType.BASEBALL,
            "insurance": FieldType.INSURANCE,
            "retirement": FieldType.RETIREMENT,
            "real_estate": FieldType.REAL_ESTATE,
            "healthcare": FieldType.HEALTHCARE,
            "education": FieldType.EDUCATION,
            "finance": FieldType.FINANCE,
            "financial_advisor": FieldType.FINANCIAL_ADVISOR,
            "general": FieldType.GENERAL
        }
        
        if field_type_str in field_type_mapping:
            return field_type_mapping[field_type_str]
        else:
            print(f"⚠️  Warning: Invalid VALIDATION_FIELD_TYPE '{field_type_str}'. Using 'general' as default.")
            return FieldType.GENERAL
    
    def extract_conversation_from_agent_results(self, file_path: str = "results/agent_results.json") -> Conversation:
        """Extract conversation data from agent_results.json file"""
        try:
            with open(file_path, "r") as f:
                agent_data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Agent results file not found: {file_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in agent results file: {file_path}")
        
        # Extract conversation from agent history - focus on actual chatbot interaction
        messages = []
        conversation_step = 0
        
        for i, entry in enumerate(agent_data.get("history", [])):
            # Extract user inputs from actions
            if "model_output" in entry and "action" in entry["model_output"]:
                for action in entry["model_output"]["action"]:
                    if "input_text" in action:
                        user_input = action["input_text"]["text"]
                        
                        # Infer the chatbot question based on the user input and context
                        chatbot_question = self._infer_chatbot_question(user_input, conversation_step)
                        
                        # Add chatbot question first
                        if chatbot_question:
                            messages.append({
                                "role": "assistant",
                                "content": chatbot_question,
                                "timestamp": conversation_step
                            })
                        
                        # Add user response
                        messages.append({
                            "role": "user",
                            "content": user_input,
                            "timestamp": conversation_step + 1
                        })
                        
                        conversation_step += 2
                    
                    elif "click_yes_button" in action:
                        # User clicked yes button
                        chatbot_question = self._infer_yes_no_question(conversation_step)
                        
                        if chatbot_question:
                            messages.append({
                                "role": "assistant",
                                "content": chatbot_question,
                                "timestamp": conversation_step
                            })
                        
                        messages.append({
                            "role": "user",
                            "content": "Yes",
                            "timestamp": conversation_step + 1
                        })
                        
                        conversation_step += 2
                    
                    elif "click_no_button" in action:
                        # User clicked no button
                        chatbot_question = self._infer_yes_no_question(conversation_step)
                        
                        if chatbot_question:
                            messages.append({
                                "role": "assistant",
                                "content": chatbot_question,
                                "timestamp": conversation_step
                            })
                        
                        messages.append({
                            "role": "user",
                            "content": "No",
                            "timestamp": conversation_step + 1
                        })
                        
                        conversation_step += 2
        
        return Conversation(
            id="agent_conversation",
            field_type=self.field_type,  # Use the field type from constructor
            messages=messages,
            metadata={
                "source": file_path, 
                "total_steps": len(agent_data.get("history", [])),
                "extraction_method": "agent_results"
            }
        )
    
    def _infer_chatbot_question(self, user_input: str, step: int) -> str:
        """Infer the chatbot question based on user input and conversation step"""
        user_input_lower = user_input.lower()
        
        if step == 0:  # First interaction
            return "What is your name?"
        elif "auto" in user_input_lower or "homeowners" in user_input_lower or "life" in user_input_lower:
            return "What insurance policies do you have?"
        elif "savings" in user_input_lower or "retirement" in user_input_lower or "car" in user_input_lower or "$" in user_input:
            return "What are your assets?"
        else:
            return "Please provide more information."
    
    def _infer_yes_no_question(self, step: int) -> str:
        """Infer the yes/no question based on conversation step"""
        if step == 2:  # After name input
            return "Are you ready to discuss your retirement plan?"
        elif step == 4:  # After first yes
            return "Are you ready to discuss your insurance liabilities?"
        elif step == 6:  # After second yes
            return "Do you have any insurance?"
        else:
            return "Do you agree?"
    
    def _determine_field_type(self, messages: List[Dict[str, Any]]) -> FieldType:
        """Determine the field type based on conversation content"""
        content = " ".join([msg.get("content", "").lower() for msg in messages])
        
        # Keywords for different domains
        baseball_keywords = ["baseball", "game", "team", "player", "score", "inning", "pitch", "hit", "run"]
        insurance_keywords = ["insurance", "policy", "coverage", "claim", "premium", "deductible", "benefits"]
        healthcare_keywords = ["health", "medical", "doctor", "patient", "treatment", "symptoms", "diagnosis"]
        finance_keywords = ["finance", "money", "investment", "bank", "loan", "credit", "account", "payment"]
        
        # Count keyword matches
        baseball_count = sum(1 for keyword in baseball_keywords if keyword in content)
        insurance_count = sum(1 for keyword in insurance_keywords if keyword in content)
        healthcare_count = sum(1 for keyword in healthcare_keywords if keyword in content)
        finance_count = sum(1 for keyword in finance_keywords if keyword in content)
        
        # Return the field type with the highest match count
        max_count = max(baseball_count, insurance_count, healthcare_count, finance_count)
        
        if max_count == 0:
            return FieldType.GENERAL
        elif baseball_count == max_count:
            return FieldType.BASEBALL
        elif insurance_count == max_count:
            return FieldType.INSURANCE
        elif healthcare_count == max_count:
            return FieldType.HEALTHCARE
        elif finance_count == max_count:
            return FieldType.FINANCE
        else:
            return FieldType.GENERAL
    
    def validate_agent_conversation(self, file_path: str = "results/agent_results.json") -> ValidationResult:
        """Main method to extract and validate agent conversation"""
        try:
            # Extract conversation from agent results
            conversation = self.extract_conversation_from_agent_results(file_path)
            
            # Run validation
            validation_result = self.validation_service.validate_conversation(conversation)
            
            return validation_result
            
        except Exception as e:
            return ValidationResult(
                conversation_id=conversation.id if 'conversation' in locals() else "unknown",
                field_type=FieldType.GENERAL,
                relevance_score=0.0,
                logical_consistency_score=0.0,
                overall_score=0.0,
                issues=[f"Error during validation: {str(e)}"],
                recommendations=["Check agent_results.json file format and content"],
                metadata={"error": str(e)}
            )
    
    def get_conversation_summary(self, file_path: str = "results/agent_results.json") -> Dict[str, Any]:
        """Get a summary of the conversation without running validation"""
        try:
            conversation = self.extract_conversation_from_agent_results(file_path)
            
            return {
                "conversation_id": conversation.id,
                "field_type": conversation.field_type.value,
                "total_messages": len(conversation.messages),
                "total_steps": conversation.metadata.get("total_steps", 0),
                "extraction_method": conversation.metadata.get("extraction_method", "unknown"),
                "messages_sample": conversation.messages[:3] if conversation.messages else []
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "conversation_id": "unknown",
                "field_type": "unknown",
                "total_messages": 0,
                "total_steps": 0
            } 