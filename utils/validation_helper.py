import os
import asyncio
from services.conversation_validation_service import ConversationValidationService


async def check_and_validate_existing_results():
    """
    Check if agent_results.json exists and run validation on it.
    Returns True if validation was run, False if no existing results found.
    """
    if os.path.exists("results/agent_results.json"):
        print("📁 Found existing agent_results.json")
        print("🔍 Running validation on existing results...")
        
        # Only run validation on existing results
        conversation_validation_service = ConversationValidationService()
        validation_result = await conversation_validation_service.validate_agent_conversation("results/agent_results.json")
        
        print("\n" + "="*50)
        print("📊 VALIDATION RESULTS")
        print("="*50)
        print(f"Conversation ID: {validation_result.conversation_id}")
        print(f"Field Type: {validation_result.field_type}")
        print(f"Relevance Score: {validation_result.relevance_score}/10")
        print(f"Logical Consistency: {validation_result.logical_consistency_score}/10")
        print(f"Overall Score: {validation_result.overall_score}/10")
        
        if validation_result.issues:
            print(f"\n⚠️  Issues Found:")
            for issue in validation_result.issues:
                print(f"  • {issue}")
        
        if validation_result.recommendations:
            print(f"\n💡 Recommendations:")
            for rec in validation_result.recommendations:
                print(f"  • {rec}")
        
        # Determine overall assessment
        if validation_result.overall_score >= 8:
            assessment = "EXCELLENT"
        elif validation_result.overall_score >= 6:
            assessment = "GOOD"
        elif validation_result.overall_score >= 4:
            assessment = "FAIR"
        else:
            assessment = "POOR"
        
        print(f"\n🎯 Overall Assessment: {assessment}")
        return True
    
    return False 