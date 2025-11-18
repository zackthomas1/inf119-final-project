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
from logging_config import get_orchestrator_logger
from agents.coder_agent import CoderAgent
from agents.tester_agent import TesterAgent

logger = get_orchestrator_logger()

def run_pipeline(requirements_text: str) -> tuple[str, str, str]:
    """
    Run the full multi-agent pipeline on a single set of requirements. 

    Returns: 
        - genreated_code: Python soure code for app
        - genreated_tests: Python source code for tests
        - usage_report: Dict matching JSON structure
    """
    logger.info("=== Starting multi-agent pipeline ===")
    logger.debug(f"Requirements preview: {requirements_text[:200]}...")

    logger.info("Initializing UsageTracker")
    usage_tracker = UsageTracker()
    
    logger.info("Initializing MCPClient")
    try:
        mcp_client = MCPClient(usage_tracker)
        logger.info("MCPClient initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize MCPClient: {str(e)}", exc_info=True)
        raise

    planner = PlannerAgent(mcp_client)
    coder = CoderAgent(mcp_client)
    tester = TesterAgent(mcp_client)

    # PlannerAgent: create implementation plan
    logger.info("running PlannerAgent")
    try:
        plan = planner.create_plan(requirements_text)
        logger.info("PlannerAgent completed successfully")
    except Exception as e:
        logger.error(f"PlannerAgent failed: {str(e)}", exc_info=True)
        raise

    # CodeAgent: generate application code
    generated_code = coder.generate_code(requirements_text, plan)

    # TesterAgent: generate test suite
    generated_tests = tester.generate_tests(requirements_text, generated_code)

    # persist artifacts
    logger.info("Persisting python code and test")
    os.makedirs("generated", exist_ok=True)
    with open("generated/generated_app.py", "w", encoding="utf-8") as f:
        f.write(generated_code)

    with open("generated/test_generated_app.py", "w", encoding="utf-8") as f:
        f.write(generated_tests)

    # Prepare JSON-serializable usage report
    logger.info("Preparing usage report")
    try:
        usage_report = usage_tracker.to_dict()
        logger.info(f"Usage report generated with {len(usage_report)} models tracked")
    except Exception as e:
        logger.error(f"Failed to generate usage report: {str(e)}", exc_info=True)
        usage_report = {}

    logger.info("=== Multi-agent pipeline completed ===")
    return generated_code, generated_tests, usage_report