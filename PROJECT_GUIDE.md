# 🤖 Browser Automation + LLM Validation System

A comprehensive browser automation system that combines AI-powered chatbot interactions with multi-LLM validation and observability through Langfuse integration.

## 🎯 Project Purpose

This project provides:
1. **Automated chatbot interactions** using AI agents
2. **Multi-LLM conversation validation** for quality assessment
3mprehensive observability** through Langfuse integration
4. **Domain-specific validation** (financial advisor, insurance, healthcare, etc.)
5. **Performance monitoring** and quality scoring

## 🏗️ Architecture Overview

### Core Components

```
📁 Project Structure:
├── 🤖 Agent System (Browser Automation)
│   ├── controllers/chatbot_controller.py    # Browser actions
│   ├── tasks/chatbot_task.py               # Task definition
│   ├── services/agent_service.py           # Agent orchestration
│   └── main_playwrite_claude_moduled_judge.py  # Main execution
│
├── 🔍 Validation System (Quality Assessment)
│   ├── services/conversation_validation_service.py  # Core validation
│   ├── services/langfuse_validation_service.py      # Langfuse integration
│   ├── services/langsmith_validation_service.py     # LangSmith integration
│   ├── models/validation_models.py                 # Validation data models
│   └── utils/validation_helper.py                  # Validation utilities
│
└── 📊 Observability (Monitoring & Tracing)
    ├── Langfuse integration (@observe decorators)
    ├── Trace collection and scoring
    └── Performance monitoring
```

## 🔄 Step-by-Step Flow

### Phase 1 Agent Execution

#### Step 1: Task Definition
The agent receives detailed instructions for browser automation:

```python
# tasks/chatbot_task.py
chatbot_task = (
  Important: I am UI Automation tester validating the task. '
   Open the website and then get the page URL information.Respond to the chatbot questions with the correct answers. '
 If the chatbot asks for your name, respond with your name.
    r Yes/No questions, use the custom actions click yes button" orclickno button" instead of dropdown options.
    Follow the chatbot instructions and respond with the correct answers.    CRITICAL RULE: If you ever see a button labeled "Back", you must NEVER click it, under any circumstances. 
    If the Back button appears, use the custom action "skip the back button" to acknowledge it, but do not click it.IMPORTANT: When you see the text "Thank you Assistant for providing the details." and "Feel free to share this landbot on:" and there is no enabled input field, the chatbot conversation is COMPLETE. '
   DO NOT click any social media share buttons. Instead, call theend the chatbot" action immediately, then call "close browser" action. '
  After calling "close browser", the task is COMPLETE - STOP and do not call any other actions. 
    e task is finished when you see the sharing options - do not interact with them. '
 CRITICAL: Once you call "close browser, the task is100% complete and you must STOP all further actions.'
)
```

**What happens:**
- Defines the **task instructions** for the AI agent
- Specifies **rules and constraints** (never click "Back" button)
- Sets **completion criteria** (when to end the chatbot)
- Provides **action guidelines** (use custom actions for Yes/No)

#### Step 2: Browser Controller Setup
Defines custom browser actions that the agent can call:

```python
# controllers/chatbot_controller.py
@controller.action(open base website')
async def open_base_website(browser: BrowserContext):
    page = await browser.get_current_page()
    chatbot_url = os.environ.get("CHATBOT_URL", "https://landbot.online/v3H-287541690GNZ910I/index.html")
    await page.goto(chatbot_url)
    return ActionResult(extracted_content='base website opened')

@controller.action('click yes button)
async def click_yes_button(browser: BrowserContext):
    page = await browser.get_current_page()
    await page.locator("button").first.click()
    return ActionResult(extracted_content='clicked yes button')

@controller.action('close browser)
async def close_browser(browser: BrowserContext):
    await browser.close()
    return ActionResult(
        extracted_content=TASK_COMPLETE_BROWSER_CLOSED,      success=True,
        message="Chatbot flow completed successfully,
        list_of_questions=[]
    )
```

**What happens:**
- **Defines custom browser actions** that the agent can call
- **Handles specific UI interactions** (click yes/no, skip back button)
- **Manages browser lifecycle** (open, close, end chatbot)
- **Returns structured results** with extracted content

#### Step 3: Agent Service Orchestration
Initializes the AI agent with Claude 3 Haiku:

```python
# services/agent_service.py
@observe()
def run_chatbot_agent(controller, task):
    load_dotenv()
    api_key = os.environ.get(ANTHROPIC_API_KEY")
    llm = ChatAnthropic(model='claude-3iku-224307, api_key=api_key)
    agent = Agent(task, llm, use_vision=True, controller=controller)
    return agent.run()
```

**What happens:**
- **Initializes the AI agent** with Claude 3 Haiku
- **Connects the controller** (browser actions) with the task
- **Enables vision** for the agent to see the browser
- **Wraps with Langfuse observability** (@observe decorator)

#### Step4ain Execution Flow
Orchestrates the entire process:

```python
# main_playwrite_claude_moduled_judge.py
@observe()
async def main():
    # Check if results already exist
    if await check_and_validate_existing_results():
        return
    
    # Run the agent
    history = await run_chatbot_agent(controller, chatbot_task)
    history.save_to_file("results/agent_results.json")
    
    # Always run validation regardless of success/failure
    conversation_validation_service = ConversationValidationService()
    validation_result = await conversation_validation_service.validate_agent_conversation()
    print(fValidation Result: {validation_result}")
```

**What happens:**
1. **Checks for existing results** (if validation already ran)
2. **Runs the agent** if no results exist
3. **Saves agent history** to JSON file
4. **Validates task completion**
5. **Always runs validation** regardless of success/failure

### Phase 2: Validation

#### Step 5: Validation System
Extracts and validates conversation quality:

```python
# services/conversation_validation_service.py
class ConversationValidationService:
    def extract_conversation_from_agent_results(self, file_path: str = "results/agent_results.json) -> Conversation:
        # Extract conversation from agent history
        # Reconstruct the conversation from browser actions
        # Infer missing context (chatbot questions from user responses)
        
    def validate_agent_conversation(self, file_path: str = "results/agent_results.json") -> ValidationResult:
        # Validate conversation quality using LLM providers
        # Return structured validation results
```

**What happens:**
1. **Extracts conversation data** from agent results2**Reconstructs the conversation** from browser actions
3. **Infers missing context** (chatbot questions from user responses)
4. **Validates conversation quality** using LLM providers
5. **Returns structured validation results**

#### Step 6: Validation Models
Defines data structures for validation:

```python
# models/validation_models.py
class FieldType(str, Enum):
    BASEBALL = baseball"
    INSURANCE = "insurance    RETIREMENT = "retirement"
    REAL_ESTATE =real_estate    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    FINANCE = "finance"
    GENERAL =general   FINANCIAL_ADVISOR = financial_advisor"

class ValidationResult(BaseModel):
    conversation_id: str
    field_type: FieldType
    relevance_score: float = Field(ge=0.0, le=10)
    logical_consistency_score: float = Field(ge=0.0, le=10.0)
    overall_score: float = Field(ge=0.0, le=10.0)
    issues: List[str] = []
    recommendations: List[str] = []
    metadata: Dict[str, Any] = {}
```

**What happens:**
- **Defines data structures** for conversations and validation
- **Supports multiple domains** (financial advisor, insurance, etc.)
- **Structures validation results** with scores and recommendations
- **Enforces type safety** with Pydantic models

### Phase 3bservability

#### Langfuse Integration
Provides comprehensive monitoring and tracing:

```python
# All main functions are decorated with @observe()
@observe()
async def main():
    langfuse_context.update_current_trace(
        name="main_playwright_claude_judge",
        metadata={
            trace_id": "main_playwright_claude_judge_run_1       }
    )
    # ... rest of the function
```

**What happens:**
1. **Langfuse Integration** → Tracks all operations
2. **Trace Collection** → Records agent decisions and actions
3. **Performance Monitoring** → Measures execution time and success rates
4. **Scoring** → Adds quality scores to traces

## 🎯 Key Features

### ✅ Multi-LLM Support
- **Claude 3 Haiku** for agent execution
- **Google Gemini** for validation
- **Anthropic Claude** for validation

### ✅ Domain Flexibility
- **Financial Advisor** domain
- **Insurance** domain  
- **Healthcare** domain
- **General** domain

### ✅ Comprehensive Validation
- **Relevance scoring** (0-10)
- **Logical consistency** (0-10)
- **Overall quality** assessment
- **Detailed recommendations**

### ✅ Observability
- **Langfuse traces** for all operations
- **Performance metrics** collection
- **Quality scoring** integration
- **Debug information** logging

## 🚀 How to Use

### Prerequisites

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment variables:**
```bash
# Required
export ANTHROPIC_API_KEY="your_anthropic_api_key"
export VALIDATION_FIELD_TYPE=financial_advisor

# Optional (for Langfuse)
export LANGFUSE_PUBLIC_KEY="your_langfuse_public_key"
export LANGFUSE_SECRET_KEY="your_langfuse_secret_key"
export LANGFUSE_HOST=http://localhost:30`

### Basic Usage

#### Run with validation:
```bash
# Run with financial advisor validation
VALIDATION_FIELD_TYPE=financial_advisor python main_playwrite_claude_moduled_judge.py
```

#### Run with different domains:
```bash
# Insurance domain
VALIDATION_FIELD_TYPE=insurance python main_playwrite_claude_moduled_judge.py

# Healthcare domain
VALIDATION_FIELD_TYPE=healthcare python main_playwrite_claude_moduled_judge.py

# General domain
VALIDATION_FIELD_TYPE=general python main_playwrite_claude_moduled_judge.py
```

#### Validate existing results only:
```bash
# Validate existing results without running agent
python validate_agent_conversation.py
```

### Advanced Usage

#### Custom validation field types:
```python
# Add new domain in models/validation_models.py
class FieldType(str, Enum):
    # ... existing types
    CUSTOM_DOMAIN = custom_domain"

# Use in validation
VALIDATION_FIELD_TYPE=custom_domain python main_playwrite_claude_moduled_judge.py
```

#### Langfuse observability:
```bash
# Start Langfuse locally
docker run -p 300030 langfuse/langfuse:latest

# Run with observability
python main_playwrite_claude_moduled_judge.py
```

## 📊 Validation Results

The system provides comprehensive validation results:

### Sample Output:
```
🔍 Running conversation validation...
✅ Validation completed successfully!
📊 Validation Result:[object Object]  conversation_id": "agent_conversation,field_type": financial_advisor",
  relevance_score: 8.5ogical_consistency_score: 9.2,
  overall_score:885
 issues:Question 3 could be more specific to retirement planning"
  ],
  recommendations: [Consider asking about retirement timeline",
    Include questions about risk tolerance"
  ]
}
```

### Scoring System:
- **Relevance Score (0-10)**: How well questions align with domain
- **Logical Consistency (0-10)**: Flow and coherence of conversation
- **Overall Score (0-10)**: Combined quality assessment

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `ANTHROPIC_API_KEY` | Anthropic API key for agent | Yes | - |
| `VALIDATION_FIELD_TYPE` | Domain for validation | No | `general` |
| `LANGFUSE_PUBLIC_KEY` | Langfuse public key | No | - |
| `LANGFUSE_SECRET_KEY` | Langfuse secret key | No | - |
| `LANGFUSE_HOST` | Langfuse host URL | No | `http://localhost:3000` |
| `CHATBOT_URL` | Target chatbot URL | No | Landbot URL |

### Supported Field Types

- `financial_advisor` - Financial planning conversations
- `insurance` - Insurance-related conversations
- `healthcare` - Healthcare conversations
- `education` - Educational conversations
- `real_estate` - Real estate conversations
- `retirement` - Retirement planning
- `baseball` - Baseball-related conversations
- `finance` - General finance conversations
- `general` - General conversations

## 🏗️ Architecture Details

### Agent System Flow
```
Task Definition → Browser Controller → Agent Service → Browser Automation → Result Collection
```

### Validation System Flow
```
Data Extraction → Domain Detection → Quality Assessment → Scoring → Recommendations
```

### Observability Flow
```
Langfuse Integration → Trace Collection → Performance Monitoring → Quality Scoring
```

## 🔍 Troubleshooting

### Common Issues1. **Agent fails to start:**
   - Check `ANTHROPIC_API_KEY` is set
   - Verify internet connection
   - Check target website accessibility

2. **Validation not running:**
   - Ensure `results/agent_results.json` exists
   - Check `VALIDATION_FIELD_TYPE` is set
   - Verify LLM API keys for validation
3ngfuse not working:**
   - Check Langfuse server is running
   - Verify API keys are correct
   - Check network connectivity

### Debug Mode

Enable debug logging:
```bash
export DEBUG=1hon main_playwrite_claude_moduled_judge.py
```

## 📈 Performance Monitoring

### Langfuse Dashboard
- **Traces**: View all agent runs and decisions
- **Scores**: Quality metrics for each run
- **Performance**: Execution time and success rates
- **Errors**: Failed operations and debugging info

### Metrics Tracked
- Agent execution time
- Validation processing time
- Success/failure rates
- Quality scores
- Error rates and types

## 🤝 Contributing

### Adding New Domains
1 Add field type to `models/validation_models.py`
2. Update validation logic in `services/conversation_validation_service.py`
3. Add domain-specific rules and keywords
4. Test with sample conversations

### Adding New Validation Rules
1. Define rule in `models/validation_models.py`
2. Implement validation logic
3. Add to validation service
4. Test with various conversation types

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **BrowserUse** for browser automation framework
- **Langfuse** for observability platform
- **Anthropic** for Claude AI models
- **Google** for Gemini AI models

---

**This is a sophisticated system that combines AI-powered browser automation with multi-LLM validation and comprehensive observability for quality assessment across multiple domains.** 