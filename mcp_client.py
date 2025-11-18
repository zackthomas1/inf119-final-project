# Module defines a thin wrapper around the MCP framework.
# The agents use MCPClient instead of talking directly to an LLM.
# You will plug in the actual MCP libraries / servers here.

from typing import List, Dict, Any
import google.generativeai as genai
import os
from model_tracker import UsageTracker

class MCPClient:
    """
    MCPClient encapsulates model calls.
    Responsibilities: 
        - Sending messages to appropriate model
        - Receiving model response
        - Recording approximate usage stats via UsageTracker
    """

    def __init__(self, usage_tracker: UsageTracker) -> None:
        self.usage_tracker = usage_tracker
        # Configure Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        genai.configure(api_key=api_key)

    def call_model(self, model_name: str, messages: List[Dict[str, str]]) -> str:
        """
        Call model via MCP 
        Each message as 'role' and 'cpmtemt' keys. 
        Function returns assistant's message as plain text. 
        """

        try:
            # Initialize the Gemini model
            model = genai.GenerativeModel(model_name)
            
            # Convert messages to Gemini format
            # Gemini expects a simple text prompt or conversation history
            if len(messages) == 1:
                prompt = messages[0].get('content', '')
            else:
                # For multi-turn conversations, format as conversation
                formatted_messages = []
                for msg in messages:
                    role = msg.get('role', 'user')
                    content = msg.get('content', '')
                    if role == 'system':
                        formatted_messages.append(f"System: {content}")
                    elif role == 'user':
                        formatted_messages.append(f"User: {content}")
                    elif role == 'assistant':
                        formatted_messages.append(f"Assistant: {content}")
                prompt = "\n".join(formatted_messages)
            
            # Make the API call
            response = model.generate_content(prompt)
            response_text = response.text
            
            # Estimate tokens used (Gemini doesn't provide exact token count in basic response)
            # This is a rough estimation - you might want to use the count_tokens method for accuracy
            tokens_used = len(prompt.split()) + len(response_text.split())
            self.usage_tracker.record_call(model_name=model_name, tokens_used=tokens_used)
            
            return response_text
            
        except Exception as e:
            # Log error and re-raise
            print(f"Error calling Gemini API: {e}")
            raise