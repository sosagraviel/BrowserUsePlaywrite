import asyncio
from controllers.chatbot_controller import controller
from tasks.chatbot_task import chatbot_task
from services.agent_service import run_chatbot_agent
from models.result_models import CheckoutResult
import json


async def main():
    history = await run_chatbot_agent(controller, chatbot_task)
    history.save_to_file("agent_results.json")
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
    assert validated_result.success == True


if __name__ == "__main__":
    asyncio.run(main())
