# Load environment variables from .env file
# Run this script to activate environment variables before running your application

# PowerShell version
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^#][^=]*)=(.*)$') {
        $name = $matches[1].Trim()
        $value = $matches[2].Trim()
        [Environment]::SetEnvironmentVariable($name, $value, "Process")
        Write-Host "Set $name" -ForegroundColor Green
    }
}

Write-Host "Environment variables loaded from .env file" -ForegroundColor Cyan