# Overview
Project implements a multi-agent AI system that generates Python applications and a test suites from natural language requirements. The system uses three specialized agents - a PlannerAgent for architectural design, a CoderAgent for implementation, and a TesterAgent for quality assurance. Users interact with the system using Gradio web GUI.

## Project Prompt
BudgetMaster is a budgeting software application that helps individuals effectively manage their finances by providing comprehensive budgeting features. It allows users to input their income and expenses, categorize them, and set budget goals. The software provides visual representations of budget breakdowns and generates reports to track spending patterns. With BudgetMaster, users can make informed financial decisions and stay on track to achieve their financial goals.

# Setup Instructions

## Quick Start Guide
1. Clone the repository and navigate to the project directory
2. Create venv `python -m venv venv`. Activate venv environment `venv/Scripts/activate` (windows)
3. Install dependencies: `pip install -r requirements.txt`
4. Configure your API key in `.env`
5. Load environment variables: `scripts\load-env.bat` (Command Prompt) or `.\load-env.ps1` (PowerShell)
6. Run application by calling `python app.py` in command line. 
7. Access Gradio UI through url `http://127.0.0.1:7860/`

## Step-by-step Setup
### Cloning Repository
Run the following to command to clone the project repository to current directory.
```
git clone https://github.com/zackthomas1/inf119-final-project.git
```

### Setting up and using venv
To manage required python packages setup an environment using venv.
First, create the environment by running the following command `python -m venv venv`.
Next, activate environment by running command `venv/Scripts/activate`.

## Dependencies

Run `pip install -r requirements.txt` to install all required packages, including:
- google-generativeai
- gradio

## Google Gemini API Configuration

To use the Google Gemini API integration in `mcp_client.py`, you need to:

1. Get a Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

2. **Option 1: Use the .env file (Recommended)**
   - Edit the `.env` file in the project root
   - Replace `your-api-key-here` with your actual API key:
     ```
     GEMINI_API_KEY=your-actual-api-key-here
     ```
   - Load the environment variables using one of these commands:
     
     **PowerShell:**
     ```powershell
     .\load-env.ps1
     ```
     
     **Command Prompt:**
     ```cmd
     scripts\load-env.bat
     ```

3. **Option 2: Set environment variable manually**
   ```bash
   # Windows PowerShell
   $env:GEMINI_API_KEY = "your-api-key-here"
   
   # Windows Command Prompt
   set GEMINI_API_KEY=your-api-key-here
   
   # Linux/Mac
   export GEMINI_API_KEY=your-api-key-here
   ```
## Running Test
Project test suit can be run using the command `python run_test.py`.

## Security Notes
- The `.env` file is automatically ignored by Git to protect your API keys
- Never commit your actual API key to version control
- The loader scripts set environment variables only for the current session