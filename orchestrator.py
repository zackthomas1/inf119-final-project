"""
File: orchestrator.py
Authors: 
    - [Zachery Thomas] ([47642149])
    - [Collin Vinh Tran] ([47304556])
    - [Jenny Thao Ly] ([83605957])
    - [Lina Nguyen] ([70703520])
Description: [Coordinates the multi-agent workflow:
1. PlannerAgent -> produce plan.
2. CoderAgent   -> generate application code.
3. TesterAgent  -> generate test code.
Also writes the generated code to disk and returns all artifacts.
]
"""

from typing import Tuple, Dict, Any
import os
from datetime import datetime

from model_tracker import UsageTracker
from mcp_client import MCPClient
from agents.planner_agent import PlannerAgent
from logging_config import get_orchestrator_logger
from agents.coder_agent import CoderAgent
from agents.tester_agent import TesterAgent
from utils import strip_markdown_formatting, run_generated_tests

logger = get_orchestrator_logger()

def run_pipeline(requirements_text: str) -> tuple[str, str, str, str, str]:
    """
    Run the full multi-agent pipeline on a single set of requirements. 

    Returns: 
        - genreated_code: Python soure code for app
        - genreated_tests: Python source code for tests
        - usage_report: Dict matching JSON structure
        - app_filename: Name of generated app file
        - test_filename: Name of generated test file
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

    # Specialist Architecture Configuration
    # Planner: Reasoning model for architecture and edge cases
    # Coder: High-quality coding model for implementation
    # Tester: Fast model for high-volume test generation
    PLANNER_MODEL = "gemini-2.0-flash-thinking-exp"
    CODER_MODEL = "gemini-2.5-pro"
    TESTER_MODEL = "gemini-2.0-flash"

    logger.info(f"Configuring Specialist Architecture: Planner={PLANNER_MODEL}, Coder={CODER_MODEL}, Tester={TESTER_MODEL}")

    planner = PlannerAgent(mcp_client, model_name=PLANNER_MODEL)
    coder = CoderAgent(mcp_client, model_name=CODER_MODEL)
    tester = TesterAgent(mcp_client, model_name=TESTER_MODEL)

    # PlannerAgent: create implementation plan
    logger.info("running PlannerAgent")
    try:
        plan = planner.create_plan(requirements_text)
        logger.info("PlannerAgent completed successfully")
    except Exception as e:
        logger.error(f"PlannerAgent failed: {str(e)}", exc_info=True)
        raise

    # CodeAgent: generate application code
    raw_generated_code = coder.generate_code(requirements_text, plan)
    generated_code = strip_markdown_formatting(raw_generated_code)

    # Generate filenames with timestamp early so TesterAgent knows the module name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    app_module_name = f"generated_app_{timestamp}"
    app_filename = f"{app_module_name}.py"
    test_filename = f"test_{app_module_name}.py"
    
    app_filepath = os.path.join("generated", app_filename)
    test_filepath = os.path.join("generated", test_filename)

    # TesterAgent: generate test suite
    raw_generated_tests = tester.generate_tests(requirements_text, generated_code, app_module_name)
    generated_tests = strip_markdown_formatting(raw_generated_tests)

    # persist artifacts with timestamp
    logger.info("Persisting python code and test")
    os.makedirs("generated", exist_ok=True)
    
    logger.info(f"Writing app to: {app_filepath}")
    with open(app_filepath, "w", encoding="utf-8") as f:
        f.write(generated_code)

    logger.info(f"Writing tests to: {test_filepath}")
    with open(test_filepath, "w", encoding="utf-8") as f:
        f.write(generated_tests)

    # Self-Healing Loop: Run tests and fix code if they fail
    MAX_FIX_RETRIES = 3
    
    for attempt in range(MAX_FIX_RETRIES):
        logger.info(f"Running tests (Attempt {attempt + 1}/{MAX_FIX_RETRIES})")
        success, output = run_generated_tests(test_filepath)
        
        if success:
            logger.info("Tests passed successfully!")
            break
            
        logger.warning(f"Tests failed. Output preview:\n{output[:500]}...")
        
        if attempt < MAX_FIX_RETRIES - 1:
            logger.info("Requesting code fix from CoderAgent...")
            try:
                raw_fixed_code = coder.fix_code(generated_code, output, requirements_text)
                generated_code = strip_markdown_formatting(raw_fixed_code)
                
                # Update the file with fixed code
                logger.info(f"Overwriting {app_filepath} with fixed code")
                with open(app_filepath, "w", encoding="utf-8") as f:
                    f.write(generated_code)
            except Exception as e:
                logger.error(f"Failed to fix code: {str(e)}", exc_info=True)
                break # Stop loop if fixing fails
        else:
            logger.error("Max retries reached. Tests still failing.")

    # Prepare JSON-serializable usage report
    logger.info("Preparing usage report")
    try:
        usage_report = usage_tracker.to_dict()
        logger.info(f"Usage report generated with {len(usage_report)} models tracked")
    except Exception as e:
        logger.error(f"Failed to generate usage report: {str(e)}", exc_info=True)
        usage_report = {}

    logger.info("=== Multi-agent pipeline completed ===")
    return generated_code, generated_tests, usage_report, app_filename, test_filename
