import gradio as gr
import json

def process_requirements(requirements_file, requirements_text): 
    """
    gradio callback.
    Takes either an uploaded file or text area input and runs the pipline

    Returns: 
        - generated code (string)
        - generated tests (string)
        - usage report as pretty-printed JSON
        - textual instructions on how to run code/tests
    """
    return ["hello", "world", "test", "this"]


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