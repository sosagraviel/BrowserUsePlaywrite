#!/usr/bin/env python3
"""
Standalone script to validate agent conversations using ConversationValidationService
"""

import sys
import os
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.conversation_validation_service import ConversationValidationService

async def main():
    """Main function to validate agent conversation"""
    print("🤖 Agent Conversation Validator")
    print("=" * 50)
    
    # Initialize the service
    conversation_validation_service = ConversationValidationService()
    
    # Get conversation summary first
    print("\n📊 Conversation Summary:")
    summary = conversation_validation_service.get_conversation_summary("results/agent_results.json")
    
    if "error" in summary:
        print(f"❌ Error: {summary['error']}")
        return
    
    print(f"   Conversation ID: {summary['conversation_id']}")
    print(f"   Field Type: {summary['field_type']}")
    print(f"   Total Messages: {summary['total_messages']}")
    print(f"   Total Steps: {summary['total_steps']}")
    print(f"   Extraction Method: {summary['extraction_method']}")
    
    if summary['messages_sample']:
        print(f"   Sample Messages: {len(summary['messages_sample'])} messages extracted")
    
    # Run validation (await the async call)
    print("\n🔍 Running Validation...")
    validation_result = await conversation_validation_service.validation_service.validate_conversation(
        conversation_validation_service.extract_conversation_from_agent_results("results/agent_results.json")
    )
    
    # Display results
    print("\n📋 Validation Results:")
    print(f"   Conversation ID: {validation_result.conversation_id}")
    print(f"   Field Type: {validation_result.field_type.value}")
    print(f"   Relevance Score: {validation_result.relevance_score:.2f}/10")
    print(f"   Logical Consistency: {validation_result.logical_consistency_score:.2f}/10")
    print(f"   Overall Score: {validation_result.overall_score:.2f}/10")
    
    if validation_result.issues:
        print(f"\n⚠️  Issues Found:")
        for issue in validation_result.issues:
            print(f"   • {issue}")
    
    if validation_result.recommendations:
        print(f"\n💡 Recommendations:")
        for rec in validation_result.recommendations:
            print(f"   • {rec}")
    
    # Overall assessment
    print(f"\n🎯 Overall Assessment:")
    if validation_result.overall_score >= 8.0:
        print("   ✅ EXCELLENT - High quality conversation")
    elif validation_result.overall_score >= 6.0:
        print("   ✅ GOOD - Acceptable conversation quality")
    elif validation_result.overall_score >= 4.0:
        print("   ⚠️  FAIR - Some issues detected")
    else:
        print("   ❌ POOR - Significant issues found")
    
    print(f"\n📈 Score Breakdown:")
    print(f"   • Relevance: {validation_result.relevance_score:.1f}/10")
    print(f"   • Logic: {validation_result.logical_consistency_score:.1f}/10")
    print(f"   • Overall: {validation_result.overall_score:.1f}/10")

if __name__ == "__main__":
    asyncio.run(main()) 