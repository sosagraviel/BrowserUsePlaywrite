import asyncio
import os
from dotenv import load_dotenv

from browser_use.agent.service import Agent
from browser_use.controller.service import Controller
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, SecretStr


# Define the model for the checkout result
class Checkout(BaseModel):
    success: bool
    message: str
    list_of_questions: list[str]


controller = Controller(output_model=Checkout)


async def siteValidation():
    # Load environment variables from .env file
    load_dotenv()

    # Set the task for the agent
    task = (
        'Important: I am UI Automation tester validating the task'
        'Open the website https://landbot.online/v3/H-2875416-SBUU90JD5GNZ910I/index.html and validate that the page loads correctly.'
        'Close the browser after validation.'
    )

    api_key = os.environ.get("GEMINI_API_KEY")
    llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp', api_key=SecretStr(api_key))
    agent = Agent(task, llm, use_vision=True, controller=controller)
    history = await agent.run()
    test_result = history.final_result()
    print(test_result)
    assert test_result.success == True
    # assert test_result.message == "Checkout successful"
    # assert test_result.list_of_questions == ["What is your name?", "What is your email?", "What is your phone number?"]


asyncio.run(siteValidation())
