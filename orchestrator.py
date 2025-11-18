# Coordinates the multi-agent workflow:
#   1. PlannerAgent -> produce plan.
#   2. CoderAgent   -> generate application code.
#   3. TesterAgent  -> generate test code.
# Also writes the generated code to disk and returns all artifacts.

from typing import Tuple, Dict, Any
import os

from model_tracker import UsageTracker
from mcp_client import MCPClient
from agents.planner_agent import PlannerAgent
from agents.coder_agent import CoderAgent
from agents.tester_agent import TesterAgent

def run_pipeline(requirements_text: str) -> tuple[str, str, str]:
    """
    Run the full multi-agent pipeline on a single set of requirements. 

    Returns: 
        - genreated_code: Python soure code for app
        - genreated_tests: Python source code for tests
        - usage_report: Dict matching JSON structure
    """

    usage_tracker = UsageTracker()
    mcp_client = MCPClient(usage_tracker)

    planner = PlannerAgent(mcp_client)
    # coder = CoderAgent(mcp_client)
    # tester = TesterAgent(mcp_client)

    # PlannerAgent: create implementation plan
    plan = planner.create_plane(requirements_text)

    # CodeAgent: generate application code
    generated_code = ""

    # TesterAgent: generate test suite
    generated_tests = ""

    # persist artifacts

    # Prepare JSON-serializable usage report
    usage_report = {}

    return generated_code, generated_tests, usage_report