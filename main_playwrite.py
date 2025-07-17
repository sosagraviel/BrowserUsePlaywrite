import asyncio
import os

from browser_use.agent.service import Agent
from browser_use.agent.views import ActionResult
from browser_use.browser.context import BrowserContext
from browser_use.controller.service import Controller
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, SecretStr
from playwright.async_api import async_playwright
from dotenv import load_dotenv
from langfuse.decorators import observe


# Define the model for the checkout result
class CheckoutResult(BaseModel):
    success: bool
    message: str
    list_of_questions: list[str]


controller = Controller(output_model=CheckoutResult)

@controller.action('skip the back button')
async def skip_back_button(browser: BrowserContext):
    page = await browser.get_current_page()
    print(">>> Custom skip_back_button action called!")
    back_button = page.get_by_role('button').get_by_label('Back')
    return ActionResult(extracted_content='back button skipped')

@controller.action('open base website')
async def open_base_website(browser: BrowserContext):
    print(">>> Custom open_base_website action called!")
    page = await browser.get_current_page()
    await page.goto("https://landbot.online/v3/H-2875416-SBUU90JD5GNZ910I/index.html")
    return ActionResult(extracted_content='base website opened')



@controller.action('Get the page url')
async def get_page_title(browser: BrowserContext):
    print(">>> Custom get_page_title action called!")
    page = await browser.get_current_page()
    current_url = page.url
    atr = await page.get_by_placeholder("Type here...").get_attribute("value")
    send_button = await page.get_by_role("button").text_content("input-icon-send-button")
    print(current_url, atr, send_button)
    return ActionResult(
        extracted_content=f'The page url is {current_url} and the input value is {atr} and the button text is {send_button}')


@observe()
async def siteValidation():
    load_dotenv()
    # Set the task for the agent
    task = (
        'Important: I am UI Automation tester validating the task'
        'Open the website'
        'Close the browser after validation.'
    )

    api_key = os.environ.get("GEMINI_API_KEY")
    llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp', api_key=SecretStr(api_key))
    agent = Agent(task, llm, use_vision=True, controller=controller)
    history = await agent.run()
    history.save_to_file("agent_results.json")
    test_result = history.final_result()
    import json
    if isinstance(test_result, str):
        test_result = json.loads(test_result)
    print(test_result)
    validated_result = CheckoutResult.model_validate(test_result)
    assert validated_result.success == True
    # assert test_result.message == "Checkout successful"
    # assert test_result.list_of_questions == ["What is your name?", "What is your email?", "What is your phone number?"]


asyncio.run(siteValidation())
