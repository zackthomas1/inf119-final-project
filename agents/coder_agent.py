"""
File: coder_agent.py
Authors: 
    - [Zachery Thomas] ([47642149])
    - [Collin Vinh Tran] ([47304556])
    - [Jenny Thao Ly] ([83605957])
    - [Lina Nguyen] ([70703520])
Description: [What this file does (functions/methods used)]
"""

# CoderAgent takes structured requirements generatedby PlannerAgent
# and produces code for the application.

from typing import Dict, Any
from mcp_client import MCPClient
from logging_config import get_coder_agent_logger

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

    return self.mcp_client.call_model(self.model_name, messages)
