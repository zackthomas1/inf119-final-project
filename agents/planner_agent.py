# PlannerAgent analyzes  natural language requirements and produces
# a structured development plan for the application.

from typing import Dict, Any
from mcp_client import MCPClient
from logging_config import get_planner_agent_logger

logger = get_planner_agent_logger()

class PlannerAgent:
    """
    PlannerAgent is responsible for:
      - Parsing the input requirements.
      - Producing a high-level plan (components, functions, modules).
      - Listing testable behaviors for the TesterAgent.
    """
        
    def __init__(self, mcp_client: MCPClient, model_name: str = "gemini-2.0-flash"):
      logger.info(f"Initializing PlannerAgent with model: {model_name}")
      self.mcp_client = mcp_client
      self.model_name = model_name
      logger.info("PlannerAgent initialized successfully")

    def create_plan(self, requirement_text: str) -> Dict[str, Any]:
       """
       Given raw requirements text, ask model to return structured plan. 
       Model returns a JSON-like text, to parse later.
       """
       logger.info(f"=== Creating plan with PlannerAgent ===")
       logger.info(f"Requirements length: {len(requirement_text)} characters")
       logger.debug(f"Requirements preview: {requirement_text[:300]}...")

       system_prompt = (
            "You are a senior software architect. "
            "Given a set of requirements, you must produce a concise, "
            "structured plan describing:\n"
            "1) main modules/classes/functions,\n"
            "2) their responsibilities,\n"
            "3) key edge cases and test scenarios.\n"
            "Return the result as clearly labeled sections."
       )
       
       logger.info(f"System prompt length: {len(system_prompt)} characters")
       logger.debug(f"System prompt: {system_prompt}")

       messages = [
          {"role": "system", "content": system_prompt},
          {"role": "user", "content": requirement_text},
       ]
       
       logger.info(f"Calling model: {self.model_name}")
       
       try:
           plan_text = self.mcp_client.call_model(self.model_name, messages=messages)
           logger.info(f"Model call successful, plan text length: {len(plan_text)} characters")
       except Exception as e:
           logger.error(f"Model call failed: {str(e)}", exc_info=True)
           raise

       result = {"raw_plan": plan_text}
       logger.info(f"=== PlannerAgent create_plan completed ===")
       return result