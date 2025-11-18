# Load environment variables from .env file
# Alternative batch script for Command Prompt

@echo off
for /f "usebackq delims== tokens=1,2" %%i in (`.env`) do (
    if not "%%i"=="" if not "%%i"=="rem" if not "%%i"=="#" (
        set %%i=%%j
        echo Set %%i
    )
)
echo Environment variables loaded from .env file