from browser_use.controller.service import Controller
from browser_use.browser.context import BrowserContext
from browser_use.agent.views import ActionResult
from models.result_models import CheckoutResult

controller = Controller(output_model=CheckoutResult)

@controller.action('skip the back button')
async def skip_back_button(browser: BrowserContext):
    page = await browser.get_current_page()
    print(">>> Custom skip_back_button action called!")
    back_button = page.get_by_role('button').get_by_label('Back')
    return ActionResult(extracted_content='back button skipped')

import os
from dotenv import load_dotenv

@controller.action('open base website')
async def open_base_website(browser: BrowserContext):
    print(">>> Custom open_base_website action called!")
    page = await browser.get_current_page()
    
    # Load environment variables and get the chatbot URL
    load_dotenv()
    chatbot_url = os.environ.get("CHATBOT_URL", "https://landbot.online/v3/H-2875416-SBUU90JD5GNZ910I/index.html")
    
    await page.goto(chatbot_url)
    return ActionResult(extracted_content='base website opened')

@controller.action('Get the page url')
async def get_page_title(browser: BrowserContext):
    print(">>> Custom get_page_title action called!")
    page = await browser.get_current_page()
    current_url = page.url
    atr = await page.get_by_placeholder("Type here...").get_attribute("value")
    endOption = await page.get_by_text("Feel free to share this landbot on:")
    send_button = await page.locator("button.input-icon-send-button").text_content()
    print(">>> Custom get_page_title action called! current_url:", current_url, "atr:", atr, "send_button:", send_button, "endOption:", endOption)
    return ActionResult(
        extracted_content=f'The page url is {current_url} and the input value is {atr} and the button text is {send_button} and the endOption is {endOption}')

@controller.action('end the chatbot')
async def end_the_chatbot(browser: BrowserContext):
    print(">>> Custom end_the_chatbot action called!")
    page = await browser.get_current_page()
    thank_you = page.get_by_text("Thank you Assistant for providing the details.")
    share_text = page.get_by_text("Feel free to share this landbot on:")
    thank_you_found = await thank_you.count() > 0
    share_found = await share_text.count() > 0
    input_field = page.get_by_placeholder("Type here...")
    input_present = await input_field.count() > 0
    input_enabled = False
    if input_present:
        input_enabled = await input_field.is_enabled()
    if thank_you_found and share_found and (not input_present or not input_enabled):
        print(">>> Robust finish condition met: thank you + share text + no input field")
        await page.close()
        return ActionResult(extracted_content='end the chatbot - robust finish condition met and browser closed')
    else:
        print(f">>> Robust finish condition NOT met: thank_you_found={thank_you_found}, share_found={share_found}, input_present={input_present}, input_enabled={input_enabled}")
        return ActionResult(extracted_content='end the chatbot - robust finish condition NOT met')

@controller.action('click yes button')
async def click_yes_button(browser: BrowserContext):
    print(">>> Custom click_yes_button action called!")
    page = await browser.get_current_page()
    await page.locator("button").first.click()
    return ActionResult(extracted_content='clicked yes button')

@controller.action('click no button')
async def click_no_button(browser: BrowserContext):
    print(">>> Custom click_no_button action called!")
    page = await browser.get_current_page()
    await page.locator("button").nth(1).click()
    return ActionResult(extracted_content='clicked no button')

@controller.action('close browser')
async def close_browser(browser: BrowserContext):
    print(">>> Custom close_browser action called!")
    await browser.close()
    print(">>> Browser context closed. Task completed successfully.")
    # Return a result that signals completion
    return ActionResult(
        extracted_content='TASK_COMPLETE_BROWSER_CLOSED',
        success=True,
        message="Chatbot flow completed successfully",
        list_of_questions=[]
    ) 