# Overview
Project implements a multi-agent AI system that generates Python applications and a test suites from natural language requirements. The system uses three specialized agents - a PlannerAgent for architectural design, a CoderAgent for implementation, and a TesterAgent for quality assurance. Users interact with the system using Gradio web GUI.

## Project Prompt
BudgetMaster is a budgeting software application that helps individuals effectively manage their finances by providing comprehensive budgeting features. It allows users to input their income and expenses, categorize them, and set budget goals. The software provides visual representations of budget breakdowns and generates reports to track spending patterns. With BudgetMaster, users can make informed financial decisions and stay on track to achieve their financial goals.

## Additional Requirements Specifications Prompts
User Interface:
- Command-line interface (CLI) with interactive menu system
- Clear menu options for all operations
- Input validation and error handling for all user inputs
- Confirmation prompts for destructive operations (delete, edit)

Data Persistence:
- Store all data in JSON format
- Save transactions to 'transactions.json'
- Save budget goals to 'budget_goals.json'
- Data must persist between program sessions
- Automatically create JSON files if they don't exist

Transaction Management:
- Each transaction must include:
  - Date (YYYY-MM-DD format)
  - Name/Description (string)
  - Amount (float, positive for income, can be negative for expenses)
  - Category (string from predefined or custom categories)
- Display all transactions in a formatted table

Categories
- Predefined categories: Food, Transport, Entertainment, Utilities, Healthcare, Shopping, Savings, Income

Budget Goals:
- Set monthly spending limits per category
- Display current spending vs. budget for each category

Visual Representations:
- ASCII art charts displayed directly in terminal
- Pie chart showing spending breakdown by category (using ASCII characters)
- Bar chart comparing spending across categories
- All visualizations should be clear and readable in terminal

Reports:
- Monthly summary showing:
  - Total income
  - Total expenses
  - Spending by category

User Experience Requirements:
- Menu-driven navigation with numbered options
- Clear prompts for user input
- Validation of all inputs (dates, amounts, categories)
- Helpful error messages
- Option to return to main menu from any screen
- Clean, organized output formatting

Required Features List:
1. Add income transaction
2. Add expense transaction
3. View all transactions
4. Edit existing transaction
5. Delete transaction
6. Set budget goal for category
7. View budget status for all categories
8. Generate monthly summary report
9. Filter transactions by category
10. Exit program

Testing Requirements:
- At least 10 test cases covering:
  - Adding transactions
  - Editing transactions
  - Deleting transactions
  - Setting budget goals
  - Calculating totals and summaries
  - Data persistence (save/load from JSON)
  - Input validation

# Setup Instructions

## Quick Start Guide
1. Clone the repository and navigate to the project directory
2. Create venv `python -m venv venv`. Activate venv environment `venv/Scripts/activate` (windows)
3. Install dependencies: `pip install -r requirements.txt`
4. Configure your API key in `.env`
5. Load environment variables: `scripts\load-env.bat` (Command Prompt) or `scripts\load-env.ps1` (PowerShell)
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
     scripts\load-env.ps1
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