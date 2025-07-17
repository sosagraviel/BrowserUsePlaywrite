# Chatbot Validation System Setup Guide

## 🔧 Environment Setup

### 1. Create .env file
Create a `.env` file in your project root with the following content:

```env
# Anthropic Claude API Key (required for validation service)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Google Gemini API Key (for other chatbot implementations)
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Custom chatbot URL
CHATBOT_URL=https://your-chatbot-url.com
```

### 2. Get API Keys

**Anthropic Claude API Key:**
1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Create an account or sign in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-ant-api03-`)

**Google Gemini API Key:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create an account or sign in
3. Create a new API key
4. Copy the key (starts with `AIzaSy`)

## 🚀 Running the Validation System

### Test the Structure (No API Key Required)
```bash
python test_validation_structure.py
```

This will demonstrate the validation system structure and save sample results.

### Run Full Validation (API Key Required)
```bash
python main_validation_example.py
```

This will run actual LLM-powered validation of chatbot conversations.

## 📊 Understanding the Results

### Validation Output
```
=== BASEBALL CHATBOT VALIDATION ===
Field Type: baseball
Overall Score: 0.67
Passed: False
Recommendations: ['Remove or modify 2 irrelevant questions']

--- Question Validations ---
Q1: What's your favorite baseball team?
  Relevant: True
  Score: 0.95

Q2: Are you married?
  Relevant: False
  Score: 0.1
  Issues: ['Question is not relevant to baseball domain']
  Suggestions: ['Remove this question or make it baseball-related']
```

### Key Metrics
- **Overall Score**: Percentage of relevant questions (0.0-1.0)
- **Passed**: True if score ≥ 0.8 (80% threshold)
- **Recommendations**: Specific improvements needed
- **Question Validations**: Detailed analysis per question

## 🎯 Field-Specific Validation

### Baseball Chatbot
- ✅ Relevant: Teams, players, games, statistics
- ❌ Irrelevant: Marriage, real estate, personal relationships
- ❌ Forbidden: "Are you married?", "Do you own a house?"

### Insurance Chatbot
- ✅ Relevant: Coverage, policies, claims, premiums
- ❌ Irrelevant: Sports, entertainment, hobbies
- ❌ Logic Error: Married → "When did you get divorced?"

## 🔍 Integration with Your Existing Code

### Validate Agent Results
```python
from services.validation_service import ChatbotValidationService
from models.validation_models import FieldType

# After running your chatbot test
async def validate_agent_results():
    # Extract conversation from agent_results.json
    conversation_history = extract_from_agent_results()
    
    # Validate based on field type
    validator = ChatbotValidationService(FieldType.INSURANCE)
    result = await validator.validate_conversation(conversation_history)
    
    # Save results
    with open("validation_results.json", "w") as f:
        json.dump(result.model_dump(), f, indent=2)
```

### Add to Your Testing Pipeline
```python
# In your main chatbot test
async def run_chatbot_with_validation():
    # Run your existing chatbot test
    history = await run_chatbot_agent(controller, chatbot_task)
    
    # Add validation
    validator = ChatbotValidationService(FieldType.INSURANCE)
    validation_result = await validator.validate_conversation(conversation_history)
    
    # Report results
    print(f"Chatbot Test: {'✅ PASSED' if validation_result.passed else '❌ FAILED'}")
    print(f"Validation Score: {validation_result.overall_score:.2f}")
    print(f"Recommendations: {validation_result.recommendations}")
```

## 🛠️ Troubleshooting

### Common Issues

1. **API Key Error**
   ```
   ANTHROPIC_API_KEY not found in environment variables
   ```
   **Solution**: Set your API key in the `.env` file

2. **Import Error**
   ```
   ModuleNotFoundError: No module named 'langchain_anthropic'
   ```
   **Solution**: Install dependencies: `pip install -r requirements.txt`

3. **Validation Error**
   ```
   Validation error: JSON parsing failed
   ```
   **Solution**: Check your API key is valid and has sufficient credits

### Debug Mode
Add debug prints to understand validation behavior:
```python
print(f"Validating question: {question}")
print(f"Field type: {field_type}")
print(f"Previous responses: {previous_responses}")
```

## 📈 Next Steps

1. **Customize Field Configurations**: Add your specific domain rules
2. **Integrate with CI/CD**: Add validation to your testing pipeline
3. **Extend Validation Rules**: Add more sophisticated logic checks
4. **Create Custom Fields**: Add new field types for your specific use cases

## 🎯 Benefits

- **Quality Assurance**: Ensures chatbot questions are relevant
- **Logical Consistency**: Catches flow errors before deployment
- **Field-Specific**: Different rules for different domains
- **LLM-Powered**: Intelligent analysis using Claude
- **Comprehensive**: Detailed scoring and recommendations 