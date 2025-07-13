# AI Test Automation with browser-use & LangChain

## Overview
This project demonstrates browser automation and UI validation using the `browser-use` agent with multiple LLM providers via LangChain. It supports both **Google Gemini** and **Anthropic Claude** for intelligent web automation tasks. The project is designed for UI automation testers to validate web tasks using LLMs with a modular, scalable architecture.

## Features

### 🤖 Multi-LLM Support
- **Google Gemini**: Using `langchain_google_genai` for Gemini 2.0 Flash
- **Anthropic Claude**: Using `langchain_anthropic` for Claude 3 Haiku
- **Modular Architecture**: Clean separation of concerns with controllers, services, tasks, and models

### 🏗️ Project Structure
```
BrowserUsePlaywrite/
├── main.py                          # Basic Gemini implementation
├── main_playwrite.py                # Advanced Gemini with custom actions
├── main_playwrite_claude.py         # Claude implementation with custom actions
├── main_playwrite_claude_moduled.py # Modular Claude implementation
├── controllers/
│   └── chatbot_controller.py        # Custom browser actions
├── services/
│   └── agent_service.py             # Agent service with LLM configuration
├── tasks/
│   └── chatbot_task.py              # Task definitions
├── models/
│   └── result_models.py             # Pydantic models for results
└── requirements.txt                  # Project dependencies
```

### 🎯 Use Cases
- **Chatbot Testing**: Automated interaction with web-based chatbots
- **Form Validation**: Intelligent form filling and validation
- **UI Flow Testing**: Complex user journey automation
- **Custom Action Support**: Extensible browser automation actions

## Supported LLM Providers

### 1. Google Gemini
- **Model**: `gemini-2.0-flash-exp`
- **Provider**: `langchain_google_genai`
- **Files**: `main.py`, `main_playwrite.py`

### 2. Anthropic Claude
- **Model**: `claude-3-haiku-20240307`
- **Provider**: `langchain_anthropic`
- **Files**: `main_playwrite_claude.py`, `main_playwrite_claude_moduled.py`

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd BrowserUsePlaywrite
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   # For Gemini
   GEMINI_API_KEY=your_gemini_api_key_here
   
   # For Claude/Anthropic
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   
   # Optional: Custom chatbot URL
   CHATBOT_URL=https://your-chatbot-url.com
   ```

## Usage

### Basic Implementation (Gemini)
```bash
python main.py
```

### Advanced Implementation with Custom Actions (Gemini)
```bash
python main_playwrite.py
```

### Claude Implementation with Custom Actions
```bash
python main_playwrite_claude.py
```

### Modular Claude Implementation (Recommended)
```bash
python main_playwrite_claude_moduled.py
```

## Architecture

### 🎮 Controllers
Define custom browser actions using the `@controller.action` decorator:
```python
@controller.action('skip the back button')
async def skip_back_button(browser: BrowserContext):
    page = await browser.get_current_page()
    back_button = page.get_by_role('button').get_by_label('Back')
    return ActionResult(extracted_content='back button skipped')
```

### 🔧 Services
Handle LLM configuration and agent setup:
```python
def run_chatbot_agent(controller, task):
    load_dotenv()
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    llm = ChatAnthropic(model='claude-3-haiku-20240307', api_key=api_key)
    agent = Agent(task, llm, use_vision=True, controller=controller)
    return agent.run()
```

### 📋 Tasks
Define the automation task in natural language:
```python
chatbot_task = (
    'Important: I am UI Automation tester validating the task. '
    'Open the website and then get the page URL information. '
    'Respond to the chatbot questions with the correct answers. '
    # ... more task instructions
)
```

### 📊 Models
Define result structures using Pydantic:
```python
class CheckoutResult(BaseModel):
    success: bool
    message: str
    list_of_questions: list[str]
    extracted_content: Optional[str] = None
```

## Environment Variables

### Required Variables
- `GEMINI_API_KEY`: Your Google Gemini API key
- `ANTHROPIC_API_KEY`: Your Anthropic Claude API key

### Optional Variables
- `CHATBOT_URL`: Custom chatbot URL (defaults to Landbot demo)

### Setting Environment Variables

**Option 1: Using .env file (Recommended)**
```env
GEMINI_API_KEY=your_gemini_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
CHATBOT_URL=https://your-chatbot-url.com
```

**Option 2: Export in shell**
```bash
export GEMINI_API_KEY=your_gemini_api_key_here
export ANTHROPIC_API_KEY=your_anthropic_api_key_here
export CHATBOT_URL=https://your-chatbot-url.com
```

## Custom Actions

The project includes several custom browser actions:

- `skip the back button`: Avoids clicking back buttons
- `open base website`: Navigates to the target URL
- `get the page url`: Extracts page information
- `end the chatbot`: Detects completion conditions
- `click yes button`: Clicks the first button
- `click no button`: Clicks the second button
- `close browser`: Closes the browser session

## Troubleshooting

### Common Issues

1. **API Key Errors**
   - Ensure your API keys are correctly set in the `.env` file
   - Verify the keys are valid and have sufficient credits

2. **Browser Issues**
   - Make sure Playwright browsers are installed: `playwright install`
   - Check if the target website is accessible

3. **Task Completion Issues**
   - Review the task definition in `tasks/chatbot_task.py`
   - Check if the completion conditions are met

### Debug Mode
Add debug prints to understand the agent's behavior:
```python
print(">>> Custom action called!")
```

## Dependencies

- `browser-use==0.1.36`: Browser automation framework
- `langchain-openai==0.3.1`: LangChain OpenAI integration
- `pydantic==2.11.0a2`: Data validation
- `google-ai-generativelanguage==0.6.10`: Google AI integration
- `python-dotenv==1.1.1`: Environment variable management

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your custom actions in `controllers/`
4. Define new tasks in `tasks/`
5. Update models in `models/` if needed
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 