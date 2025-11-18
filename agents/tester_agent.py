# TesterAgent generates test cases for the code produced by CoderAgent.

from typing import Dict, Any
from mcp_client import MCPClient
from logging_config import get_tester_agent_logger

logger = get_tester_agent_logger()

class TesterAgent:
    """
    TesterAgent is responsible for:
      - Generating at least 10 test cases for the produced code.
      - Ensuring that tests are runnable via pytest or unittest.
      - Including clear comments explaining each test case.
    """

    def __init__(self, mcp_client: MCPClient, model_name: str = "tester-model") -> None:
        logger.info(f"Initializing TesterAgent with model: {model_name}")
        self.mcp_client = mcp_client
        self.model_name = model_name

    def generate_tests(self, requirements_text: str, code_text: str) -> str:
        """
        Ask the model to produce a Python test file (e.g., pytest style)
        that imports the generated module and tests at least 10 behaviors.
        """
        logger.info(f"=== Generating test with TesterAgent ===")

        system_prompt = (
            "You are a senior QA engineer writing unit tests in Python. "
            "Generate at least 10 tests for the provided module. "
            "Use pytest style functions (test_*). "
            "Assume the main module file is named 'generated_app.py'."
        )

        user_prompt = (
            "=== REQUIREMENTS ===\n"
            f"{requirements_text}\n\n"
            "=== GENERATED IMPLEMENTATION ===\n"
            f"{code_text}\n\n"
            "Please output ONLY valid Python test code for pytest, "
            "with at least 10 tests."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
