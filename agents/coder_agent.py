# CoderAgent takes structured requirements generatedby PlannerAgent
# and produces code for the application.

from typing import Dict, Any
from mcp_client import MCPClient
from logging_config import get_coder_agent_logger
from utils import strip_markdown_formatting, validate_python_syntax

logger = get_coder_agent_logger()

class CoderAgent:
  """
  CoderAgent is responsible for:
    - Taking the plan and original requirements.
    - Generating Python source code that satisfies the requirements.
    - Including docstrings and comments.
  """

  def __init__(self, mcp_client: MCPClient, model_name: str = "gemini-2.0-flash"):
    logger.info(f"Initializing CoderAgent with model: {model_name}")
    self.mcp_client = mcp_client
    self.model_name = model_name
    self.agent_name = "coder_agent"

  def generate_code(self, requirements_text: str, plan: Dict[str, any]) -> str:
    """
    Ask model to write Python code for described application.
    Return string will be written to .py file by orchestrator
    """
    logger.info(f"=== Generating code with CoderAgent ===")

    system_prompt = (
      "You are an expert Python developer. "
      "Write a single self-contained Python module that implements the "
      "specified application. Include clear function docstrings and comments. "
      "Focus on readability over optimization."
    )
      
    user_prompt = (
      "=== REQUIREMENTS ===\n"
      f"{requirements_text}\n\n"
      "=== IMPLEMENTATION PLAN ===\n"
      f"{plan.get('raw_plan', '')}\n\n"
      "Please output ONLY valid Python code, no explanations."
    )

    messages = [
      {"role": "system", "content": system_prompt},
      {"role": "user", "content": user_prompt},
    ]

    max_retries = 3
    
    for attempt in range(max_retries):
        logger.info(f"Generation attempt {attempt + 1}/{max_retries}")
        response_text = self.mcp_client.call_model(self.agent_name, self.model_name, messages)
        
        # Validate syntax
        cleaned_code = strip_markdown_formatting(response_text)
        is_valid, error_msg = validate_python_syntax(cleaned_code)
        
        if is_valid:
            logger.info("Generated code passed syntax validation")
            return response_text
            
        logger.warning(f"Generated code failed syntax validation: {error_msg}")
        
        if attempt < max_retries - 1:
            messages.append({"role": "assistant", "content": response_text})
            messages.append({
                "role": "user", 
                "content": f"The code you generated has a syntax error: {error_msg}\nPlease fix the syntax error and output the full corrected code."
            })
            
    logger.error("Failed to generate valid syntax after max retries")
    return response_text

  def fix_code(self, original_code: str, error_output: str, requirements_text: str) -> str:
    """
    Ask model to fix the code based on test failure output.
    """
    logger.info(f"=== Fixing code with CoderAgent ===")
    
    system_prompt = (
        "You are an expert Python developer. "
        "Your code failed the tests. You must fix the code to satisfy the requirements and pass the tests. "
        "Return the full fixed code module."
    )
    
    user_prompt = (
        "=== ORIGINAL REQUIREMENTS ===\n"
        f"{requirements_text}\n\n"
        "=== CURRENT CODE ===\n"
        f"{original_code}\n\n"
        "=== TEST FAILURE OUTPUT ===\n"
        f"{error_output}\n\n"
        "Please analyze the errors and output the FULL corrected Python code. "
        "Output ONLY valid Python code, no explanations."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    max_retries = 3
    
    for attempt in range(max_retries):
        logger.info(f"Fix attempt {attempt + 1}/{max_retries}")
        response_text = self.mcp_client.call_model(self.agent_name, self.model_name, messages)
        
        # Validate syntax
        cleaned_code = strip_markdown_formatting(response_text)
        is_valid, error_msg = validate_python_syntax(cleaned_code)
        
        if is_valid:
            logger.info("Fixed code passed syntax validation")
            return response_text
            
        logger.warning(f"Fixed code failed syntax validation: {error_msg}")
        
        if attempt < max_retries - 1:
            messages.append({"role": "assistant", "content": response_text})
            messages.append({
                "role": "user", 
                "content": f"The fixed code you generated has a syntax error: {error_msg}\nPlease fix the syntax error and output the full corrected code."
            })
            
    logger.error("Failed to generate valid syntax for fixed code after max retries")
    return response_text