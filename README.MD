```
python -m venv venv
```

```
venv/Scripts/activate
```

```
pip install -r requirements.txt
```

# Setup Instructions

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

## Quick Start

1. Clone the repository and navigate to the project directory
2. Install dependencies: `pip install -r requirements.txt`
3. Configure your API key in `.env`
4. Load environment variables: `scripts\load-env.bat` (Command Prompt) or `.\load-env.ps1` (PowerShell)
5. Run your application

## Dependencies

Run `pip install -r requirements.txt` to install all required packages, including:
- google-generativeai
- gradio

## Usage

The `MCPClient` class now supports calling Google Gemini models. Example usage:

```python
from mcp_client import MCPClient
from model_tracker import UsageTracker

tracker = UsageTracker()
client = MCPClient(tracker)

messages = [{"role": "user", "content": "Hello, how are you?"}]
response = client.call_model("gemini-pro", messages)
print(response)
```

## Security Notes

- The `.env` file is automatically ignored by Git to protect your API keys
- Never commit your actual API key to version control
- The loader scripts set environment variables only for the current session