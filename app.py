import gradio as gr
import json

from orchestrator import run_pipeline

def process_requirements(requirements_file, requirements_text: str) -> tuple[str, str, str, str]: 
    """
    gradio callback.
    Takes either an uploaded file or text area input and runs the pipline

    Returns: 
        - generated code (string)
        - generated tests (string)
        - usage report as pretty-printed JSON
        - textual instructions on how to run code/tests
    """
    if requirements_file is not None:
        requirements = requirements_file.read().decode("utf-8")
    else:
        requirements = requirements_text or ""

    if not requirements.strip():
        return (
            "ERROR: No requirements provided.",
            "",
            "{}",
            "Please upload a file or paste the requirements into the text box.",
        )

    generated_code, generated_tests, usage_report = run_pipeline(requirements)

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

    return generated_code, generated_tests, usage_json_str, instructions

def main(): 
    """
    Create and launch Gradio UI. 
    """
    with gr.Blocks(title="IN4MATX 119 - AI Coder") as demo: 
        gr.Markdown(
            "# AI Coder (N4MATX 119 Final Project)\n"
            "Upload the chosen software description or paste the requirements below"
            "System will generate Python code, tests, and a model usage report."
        )

        with gr.Row():
            requirements_file = gr.File(
                label = "Upload reqruiements file (.txt, .md, etc.)", 
                file_types=["text"], 
                type="binary",
            )

            requirements_text = gr.Textbox(
                label = "or paste requirements here", 
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
            inputs=[requirements_file, requirements_text],
            outputs=[
                generated_code_output,
                generate_tests_output,
                usage_json_output,
                instructions_output,
            ],
        )

    demo.launch()

if __name__ == '__main__': 
    main()