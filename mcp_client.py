"""
File: mcp_client.py
Authors: 
    - [Zachery Thomas] ([47642149])
    - [Collin Vinh Tran] ([47304556])
    - [Jenny Thao Ly] ([83605957])
    - [Lina Nguyen] ([70703520])
Description: [
- Module defines a thin wrapper around the MCP framework.
- The agents use MCPClient instead of talking directly to an LLM.
- You will plug in the actual MCP libraries / servers here.
]
"""

from typing import List, Dict, Any
import google.generativeai as genai
import os
from model_tracker import UsageTracker
from logging_config import get_mcp_client_logger

logger = get_mcp_client_logger()

class MCPClient:
    """
    MCPClient encapsulates model calls.
    Responsibilities: 
        - Sending messages to appropriate model
        - Receiving model response
        - Recording approximate usage stats via UsageTracker
    """

    def __init__(self, usage_tracker: UsageTracker) -> None:
        logger.info("Initializing MCPClient")
        self.usage_tracker = usage_tracker
        
        # Configure Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            logger.error("GEMINI_API_KEY environment variable not set")
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        logger.info("MCPClient initialized successfully")

    def call_model(self, model_name: str, messages: List[Dict[str, str]]) -> str:
        """
        Call model via MCP 
        Each message as 'role' and 'cpmtemt' keys. 
        Function returns assistant's message as plain text. 
        """
        logger.info(f"=== Calling model: {model_name} ===")
        for i, msg in enumerate(messages):
            role = msg.get('role', 'unknown')
            content_length = len(msg.get('content', ''))
            logger.info(f"Message {i+1}: role={role}, content_length={content_length}")

        try:
            # Initialize the Gemini model
            logger.debug(f"Initializing Gemini model: {model_name}")
            model = genai.GenerativeModel(model_name)
            
            # Convert messages to Gemini format
            # Gemini expects a simple text prompt or conversation history
            if len(messages) == 1:
                prompt = messages[0].get('content', '')
                logger.info("Using single message format")
            else:
                # For multi-turn conversations, format as conversation
                logger.info("Converting multi-turn conversation to Gemini format")
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
            
            logger.info(f"Final prompt length: {len(prompt)} characters")
            logger.debug(f"Prompt preview: {prompt[:200]}...")
            
            # Make the API call
            logger.info("Making API call to Gemini")
            response = model.generate_content(prompt)
            response_text = response.text
            logger.info(f"API call successful, response length: {len(response_text)} characters")
            logger.debug(f"Response preview: {response_text[:200]}...")
            
            # Estimate tokens used (Gemini doesn't provide exact token count in basic response)
            # This is a rough estimation - you might want to use the count_tokens method for accuracy
            tokens_used = len(prompt.split()) + len(response_text.split())
            logger.info(f"Estimated tokens used: {tokens_used}")
            
            logger.info("Recording usage statistics")
            self.usage_tracker.record_call(model_name=model_name, tokens_used=tokens_used)
            
            logger.info(f"=== Model call completed successfully ===")
            return response_text
            
        except Exception as e:
            # Log error and re-raise
            logger.error(f"Error calling Gemini API: {e}", exc_info=True)
            logger.error(f"Model: {model_name}, Messages count: {len(messages)}")
            print(f"Error calling Gemini API: {e}")
            raise
