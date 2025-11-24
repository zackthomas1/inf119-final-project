"""
File: app.py
Authors: 
    - [Zachery Thomas] ([47642149])
    - [Collin Vinh Tran] ([47304556])
    - [Jenny Thao Ly] ([83605957])
    - [Lina Nguyen] ([70703520])
Description: [What this file does (functions/methods used)]
"""

import gradio as gr
import json
from typing import BinaryIO

from orchestrator import run_pipeline
from logging_config import setup_logging, get_app_logger, log_system_info

# Configure logging for the application
setup_logging(level="INFO")
logger = get_app_logger()
# Log system information at startup
log_system_info()

def process_requirements(requirements_text: str) -> tuple[str, str, str, str]: 
    """
    gradio callback.
    Takes text area input and runs the pipline

    Returns: 
        - generated code (string)
        - generated tests (string)
        - usage report as pretty-printed JSON
        - textual instructions on how to run code/tests
    """
    logger.info("=== Processing requirements started ===")
    
    requirements = requirements_text or ""
    logger.info(f"Using text input, length: {len(requirements)} characters")

    if not requirements.strip():
        logger.warning("No requirements provided - returning error")
        return (
            "ERROR: No requirements provided.",
            "",
            "{}",
            "Please upload a file or paste the requirements into the text box.",
        )

    logger.info("Starting pipeline execution")
    try:
        generated_code, generated_tests, usage_report = run_pipeline(requirements)
        logger.info("Pipeline execution completed successfully")
    except Exception as e:
        logger.error(f"Pipeline execution failed: {str(e)}", exc_info=True)
        return (
            f"ERROR: Pipeline failed - {str(e)}",
            "",
            "{}",
            "Pipeline execution encountered an error. Check logs for details."
        )

    usage_json_str = json.dumps(usage_report, indent=2)

    instructions = (
        "How to run the generated code and tests:\n\n"
        "1. After running this UI, the system writes files into the 'generated/' folder:\n"
        "   - generated/generated_app.py\n"
        "   - generated/test_generated_app.py\n\n"
        "2. To run the application (if it has a main function):\n"
        "   - python generated/generated_app.py\n\n"
        "3. To run the tests (requires pytest installed):\n"
        "   - python -m tests.run_tests\n"
        "   (Or simply: pytest generated/test_generated_app.py)\n"
    )

    logger.info("=== Processing requirements completed ===")
    return generated_code, generated_tests, usage_json_str, instructions

def main(): 
    """
    Create and launch Gradio UI. 
    """
    logger.info("Initializing Gradio interface")
    
    with gr.Blocks(title="IN4MATX 119 - AI Coder") as demo: 
        gr.Markdown(
            "# AI Coder (IN4MATX 119 Final Project)\n"
            "Upload the chosen software description or paste the requirements below."
            "System will generate Python code, tests, and a model usage report."
        )

        requirements_text = gr.Textbox(
            label = "Paste requirements here", 
            lines = 15, 
            placeholder="Paste software description and requirements..."
        )

        run_button = gr.Button("Generate Code & Tests")

        generated_code_output = gr.Code(
            label="Generated python Code (generated_app.py)", language="python"
        )
        generate_tests_output = gr.Code(
            label="Genreated Test code (test_generated_app.py)", language="python"
        )

        usage_json_output = gr.Code(
            label="Model usage JSON", language="json"
        )
        instructions_output = gr.Textbox(
            label="How to run the gernated code and tests", lines=10
        )

        run_button.click(
            fn=process_requirements,
            inputs=[requirements_text],
            outputs=[
                generated_code_output,
                generate_tests_output,
                usage_json_output,
                instructions_output,
            ],
        )

    logger.info("Launching Gradio demo")
    demo.launch()

if __name__ == '__main__': 
    logger.info("application starting up")
    main()
