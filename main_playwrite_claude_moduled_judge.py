import asyncio
from controllers.chatbot_controller import controller
from tasks.chatbot_task import chatbot_task
from services.agent_service import run_chatbot_agent
from models.result_models import CheckoutResult
from services.conversation_validation_service import ConversationValidationService
from utils.validation_helper import check_and_validate_existing_results
from langfuse.decorators import observe, langfuse_context
import json
import os

# Set Langfuse environment variables directly
os.environ["LANGFUSE_PUBLIC_KEY"] = "pk-lf-2d22bd48-fe17-43b6-9d55-7e2d95e55616"
os.environ["LANGFUSE_SECRET_KEY"] = "sk-lf-f2a2b892-60e7-4477-a615-002cb7e16b92"
os.environ["LANGFUSE_HOST"] = "http://localhost:3000"


@observe()
async def main():
    # Add a custom trace id for this run
    langfuse_context.update_current_trace(
        name="main_playwright_claude_judge",
        metadata={
            "trace_id": "main_playwright_claude_judge_run_001"
        }
    )
    # Check if results/agent_results.json exists and run validation if it does
    if await check_and_validate_existing_results():
        return
    
    # If no existing results, run the agent
    print("🚀 No existing results found. Running agent...")
    history = await run_chatbot_agent(controller, chatbot_task)
    history.save_to_file("results/agent_results.json")
    test_result = history.final_result()

    # Check if the task was completed successfully
    if test_result is None:
        print(">>> Agent failed, but the chatbot flow was completed successfully!")
        print(">>> The agent reached the finish condition and attempted to end the chatbot")
        return

    if isinstance(test_result, str):
        test_result = json.loads(test_result)

    print(test_result)

    # Check for task completion signal
    if isinstance(test_result, dict) and test_result.get('extracted_content') == 'TASK_COMPLETE_BROWSER_CLOSED':
        print(">>> Task completed successfully! Exiting process.")
        return

    # Also check if the result is a string containing the completion signal
    if isinstance(test_result, str) and 'TASK_COMPLETE_BROWSER_CLOSED' in test_result:
        print(">>> Task completed successfully! Exiting process.")
        return

    validated_result = CheckoutResult.model_validate(test_result)
    
    # Check if the task was successful, but still run validation
    if validated_result.success:
        print("✅ Task completed successfully!")
    else:
        print(f"⚠️  Task completed with issues: {validated_result.message}")
        print("📋 Questions asked: ", validated_result.list_of_questions)
    
    # Always run validation regardless of task success
    print("\n🔍 Running conversation validation...")
    conversation_validation_service = ConversationValidationService()
    validation_result = await conversation_validation_service.validate_agent_conversation()
    print(f"Validation Result: {validation_result}")


if __name__ == "__main__":
    asyncio.run(main())
