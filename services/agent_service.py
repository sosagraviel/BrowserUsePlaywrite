import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from browser_use.agent.service import Agent
from langfuse.decorators import observe

@observe()
def run_chatbot_agent(controller, task):
    # Load environment variables from .env file
    load_dotenv()
    
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
    
    llm = ChatAnthropic(model='claude-3-haiku-20240307', api_key=api_key)
    agent = Agent(task, llm, use_vision=True, controller=controller)
    return agent.run() 