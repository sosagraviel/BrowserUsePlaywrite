# AI Test Automation with browser-use & LangChain + Playwrite + Langfuse Observability

## Overview
This project demonstrates browser automation and UI validation using the `browser-use` agent with multiple LLM providers via LangChain. It supports both **Google Gemini** and **Anthropic Claude** for intelligent web automation tasks, with **Langfuse observability** for comprehensive LLM monitoring and validation. The project is designed for UI automation testers to validate web tasks using LLMs with a modular, scalable architecture.

## Features

### 🤖 Multi-LLM Support
- **Google Gemini**: Using `langchain_google_genai` for Gemini 2.0 Flash
- **Anthropic Claude**: Using `langchain_anthropic` for Claude 3 Haiku
- **Modular Architecture**: Clean separation of concerns with controllers, services, tasks, and models

### 📊 Langfuse Observability & Validation
- **LLM Tracing**: Complete observability of all LLM interactions using `@observe()` decorators
- **Validation System**: Domain-specific conversation quality assessment and scoring
- **Real-time Monitoring**: Live tracking of agent performance and validation metrics
- **Custom Trace IDs**: Easy filtering and correlation of traces in Langfuse dashboard

### 🏗️ Project Structure
```
BrowserUsePlaywrite/
├── main.py                          # Basic Gemini implementation
├── main_playwrite.py                # Advanced Gemini with custom actions
├── main_playwrite_claude.py         # Claude implementation with custom actions
├── main_playwrite_claude_moduled.py # Modular Claude implementation
├── main_playwrite_claude_moduled_Judge.py # Claude with validation & Langfuse
├── controllers/
│   └── chatbot_controller.py        # Custom browser actions
├── services/
│   ├── agent_service.py             # Agent service with LLM configuration
│   ├── validation_service.py        # LLM-powered validation service
│   ├── conversation_validation_service.py # Conversation extraction & validation
│   ├── langfuse_validation_service.py # Langfuse-specific validation
│   └── langsmith_validation_service.py # LangSmith validation integration
├── tasks/
│   └── chatbot_task.py              # Task definitions
├── models/
│   ├── result_models.py             # Pydantic models for results
│   └── validation_models.py         # Validation data models
├── utils/
│   └── validation_helper.py         # Validation utility functions
├── test_langfuse_observability.py  # Langfuse observability test
└── requirements.txt                  # Project dependencies
```

### 🎯 Use Cases
- **Chatbot Testing**: Automated interaction with web-based chatbots
- **Form Validation**: Intelligent form filling and validation
- **UI Flow Testing**: Complex user journey automation
- **Custom Action Support**: Extensible browser automation actions
- **LLM Observability**: Complete monitoring and debugging of LLM interactions
- **Conversation Validation**: Quality assessment of chatbot conversations

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
   
   # Langfuse Observability (Required for LLM tracing)
   LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
   LANGFUSE_SECRET_KEY=your_langfuse_secret_key
   LANGFUSE_HOST=http://localhost:3000
   
   # Optional: Custom chatbot URL
   CHATBOT_URL=https://your-chatbot-url.com
   
   # Optional: Validation field type
   VALIDATION_FIELD_TYPE=insurance
   ```

## Validation Field Types

The `VALIDATION_FIELD_TYPE` environment variable determines which domain-specific validation rules and criteria are applied to your chatbot conversations. This ensures that the validation system evaluates conversations according to the appropriate domain context.

### Available Field Types

| Field Type | Description | Relevant Topics | Validation Focus |
|------------|-------------|-----------------|------------------|
| `baseball` | Sports and baseball-related conversations | Baseball, sports, teams, players, games, scores, statistics, rules, equipment, training, coaching | Ensures questions stay within sports domain, avoids personal/financial topics |
| `insurance` | Insurance and financial conversations | Insurance, coverage, policies, claims, premiums, deductibles, benefits, risk assessment, liabilities | Validates insurance-specific terminology and logical flow |
| `healthcare` | Medical and health-related conversations | Health, medical, doctor, patient, treatment, symptoms, diagnosis, medications, appointments | Ensures medical appropriateness and patient safety |
| `finance` | General financial conversations | Finance, money, investment, bank, loan, credit, account, payment, budgeting | Validates financial advice accuracy and compliance |
| `financial_advisor` | Professional financial advisory conversations | Retirement planning, investment strategies, portfolio management, tax planning, estate planning, risk management | Ensures professional financial advice standards and regulatory compliance |
| `real_estate` | Real estate and property conversations | Property, real estate, buying, selling, mortgages, home inspection, market analysis | Validates real estate transaction accuracy |
| `education` | Educational and learning conversations | Education, courses, learning, students, teachers, curriculum, academic performance | Ensures educational content appropriateness |
| `retirement` | Retirement planning conversations | Retirement, pensions, 401k, social security, retirement age, savings, planning | Validates retirement planning advice accuracy |
| `general` | Generic conversation validation | General topics, no specific domain restrictions | Basic conversation quality and coherence |

### Setting Validation Field Type

**Option 1: Environment Variable**
```env
VALIDATION_FIELD_TYPE=financial_advisor
```

**Option 2: In Code**
```python
from models.validation_models import FieldType
from services.validation_service import ChatbotValidationService

# Initialize with specific field type
validation_service = ChatbotValidationService(field_type=FieldType.FINANCIAL_ADVISOR)
```

### Financial Advisor Validation Example

When `VALIDATION_FIELD_TYPE=financial_advisor` is set, the validation system:

**✅ Validates For:**
- Retirement planning questions
- Investment strategy discussions
- Portfolio management advice
- Tax planning considerations
- Estate planning guidance
- Risk assessment and management
- Financial goal setting
- Regulatory compliance

**❌ Flags As Issues:**
- Personal relationship questions (unrelated to finances)
- Medical advice (outside financial domain)
- Sports or entertainment topics
- Questions that could lead to non-compliant financial advice

**Example Validation Output:**
```
Field Type: financial_advisor
Relevance Score: 8.5/10
Logical Consistency: 9.0/10
Overall Score: 8.75/10

✅ Good: "What are your retirement goals?"
✅ Good: "How much risk are you comfortable with?"
❌ Issue: "Are you married?" (not financial-related)
```

### Domain-Specific Validation Rules

Each field type has custom validation rules:

**Baseball Domain:**
- Forbidden questions: "Are you married?", "Do you own a house?"
- Logical rules: No personal questions unrelated to baseball

**Insurance Domain:**
- Logical rules: Consistent insurance status throughout conversation
- Required flow: Establish coverage before discussing claims

**Financial Advisor Domain:**
- Regulatory compliance: Avoid giving specific investment advice without proper context
- Professional standards: Maintain advisory relationship boundaries
- Risk assessment: Ensure proper risk tolerance evaluation

### Automatic Domain Detection

If `VALIDATION_FIELD_TYPE` is not set, the system automatically detects the domain based on conversation content:

```python
# Keywords for different domains
baseball_keywords = ["baseball", "game", "team", "player", "score"]
insurance_keywords = ["insurance", "policy", "coverage", "claim", "premium"]
financial_keywords = ["finance", "investment", "retirement", "portfolio", "advisor"]
```

The system counts keyword matches and selects the most relevant domain for validation.

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

### Claude with Validation & Langfuse Observability (Production Ready)
```bash
python main_playwrite_claude_moduled_Judge.py
```

### Test Langfuse Observability
```bash
python test_langfuse_observability.py
```

## Langfuse Observability Setup

### 1. Install Langfuse
```bash
pip install langfuse==2.60.9
```

### 2. Set up Langfuse Server
**Option A: Self-hosted (Recommended)**
```bash
# Using Docker
docker run -p 3000:3000 langfuse/langfuse:latest
```

**Option B: Cloud-hosted**
- Sign up at [cloud.langfuse.com](https://cloud.langfuse.com)
- Get your public and secret keys

### 3. Configure Environment Variables
```env
LANGFUSE_PUBLIC_KEY=pk-lf-your-public-key
LANGFUSE_SECRET_KEY=sk-lf-your-secret-key
LANGFUSE_HOST=http://localhost:3000  # or https://cloud.langfuse.com
```

### 4. Add @observe() Decorators
All LLM interaction functions are automatically traced:
```python
from langfuse.decorators import observe

@observe()
async def validate_conversation(self, conversation):
    # This function will be traced in Langfuse
    pass
```

## Validation System

### Domain-Specific Validation
The system supports validation for different domains:
- **Baseball**: Sports-related conversations
- **Insurance**: Insurance and financial conversations
- **Healthcare**: Medical and health-related conversations
- **General**: Generic conversation validation

### Validation Metrics
- **Relevance Score**: How relevant questions are to the domain (0-10)
- **Logical Consistency**: Flow and logical coherence (0-10)
- **Overall Score**: Combined quality assessment (0-10)

### Validation Process
1. **Conversation Extraction**: Extracts actual chatbot interactions from agent results
2. **Domain Detection**: Automatically determines the conversation domain
3. **Question Validation**: Each question is validated for relevance and logic
4. **Flow Analysis**: Overall conversation flow is assessed
5. **Recommendations**: Specific improvements are suggested

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
@observe()
def run_chatbot_agent(controller, task):
    load_dotenv()
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    llm = ChatAnthropic(model='claude-3-haiku-20240307', api_key=api_key)
    agent = Agent(task, llm, use_vision=True, controller=controller)
    return agent.run()
```

### 📊 Validation Services
Domain-specific validation with Langfuse integration:
```python
@observe()
async def validate_conversation(self, conversation):
    # Validates conversation quality
    # Logs results to Langfuse
    pass
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

class ValidationResult(BaseModel):
    conversation_id: str
    field_type: FieldType
    relevance_score: float
    logical_consistency_score: float
    overall_score: float
    issues: List[str]
    recommendations: List[str]
```

## Environment Variables

### Required Variables
- `GEMINI_API_KEY`: Your Google Gemini API key
- `ANTHROPIC_API_KEY`: Your Anthropic Claude API key
- `LANGFUSE_PUBLIC_KEY`: Your Langfuse public key
- `LANGFUSE_SECRET_KEY`: Your Langfuse secret key

### Optional Variables
- `CHATBOT_URL`: Custom chatbot URL (defaults to Landbot demo)
- `LANGFUSE_HOST`: Langfuse server URL (defaults to localhost:3000)
- `VALIDATION_FIELD_TYPE`: Domain for validation (baseball, insurance, healthcare, etc.)

### Setting Environment Variables

**Option 1: Using .env file (Recommended)**
```env
GEMINI_API_KEY=your_gemini_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
LANGFUSE_PUBLIC_KEY=pk-lf-your-public-key
LANGFUSE_SECRET_KEY=sk-lf-your-secret-key
LANGFUSE_HOST=http://localhost:3000
CHATBOT_URL=https://your-chatbot-url.com
VALIDATION_FIELD_TYPE=insurance
```

**Option 2: Export in shell**
```bash
export GEMINI_API_KEY=your_gemini_api_key_here
export ANTHROPIC_API_KEY=your_anthropic_api_key_here
export LANGFUSE_PUBLIC_KEY=pk-lf-your-public-key
export LANGFUSE_SECRET_KEY=sk-lf-your-secret-key
export LANGFUSE_HOST=http://localhost:3000
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

## Langfuse Dashboard

### Accessing Traces
1. Open your Langfuse dashboard: `http://localhost:3000`
2. Navigate to your project
3. View traces in real-time as your scripts run

### Filtering Traces
- **By Function Name**: Search for function names like `validate_conversation`
- **By Custom ID**: Filter using metadata `trace_id:main_playwright_claude_judge_run_001`
- **By Domain**: Filter by validation field type

### Trace Information
Each trace includes:
- **Input/Output**: Function arguments and return values
- **Metadata**: Custom trace IDs and domain information
- **Scores**: Validation scores and quality metrics
- **Timing**: Performance metrics and latency
- **Nested Operations**: Hierarchical view of all LLM calls

## Troubleshooting

### Common Issues

1. **API Key Errors**
   - Ensure your API keys are correctly set in the `.env` file
   - Verify the keys are valid and have sufficient credits

2. **Langfuse Connection Issues**
   - Check if Langfuse server is running: `http://localhost:3000`
   - Verify environment variables are loaded: `echo $LANGFUSE_PUBLIC_KEY`
   - Restart your terminal after updating `.env`

3. **Browser Issues**
   - Make sure Playwright browsers are installed: `playwright install`
   - Check if the target website is accessible

4. **Validation Issues**
   - Check if `VALIDATION_FIELD_TYPE` is set correctly
   - Verify agent results file exists: `results/agent_results.json`

### Debug Mode
Add debug prints to understand the agent's behavior:
```python
print(">>> Custom action called!")
```

### Langfuse Debugging
Check if Langfuse is working:
```bash
python test_langfuse_observability.py
```

## Dependencies

- `browser-use==0.1.36`: Browser automation framework
- `langchain-openai==0.3.1`: LangChain OpenAI integration
- `langchain-anthropic==0.1.0`: LangChain Anthropic integration
- `pydantic==2.11.0a2`: Data validation
- `google-ai-generativelanguage==0.6.10`: Google AI integration
- `python-dotenv==1.1.1`: Environment variable management
- `langfuse==2.60.9`: LLM observability and tracing
- `langsmith==0.2.11`: LangSmith integration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your custom actions in `controllers/`
4. Define new tasks in `tasks/`
5. Update models in `models/` if needed
6. Add `@observe()` decorators to new LLM functions
7. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 