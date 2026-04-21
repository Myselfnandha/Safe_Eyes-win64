$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location "$ScriptDir\.."

Write-Host "Installing dependencies..."
pip install -r safeeyes_windows\requirements.txt

Write-Host "Starting SafeEyes..."
Start-Process pythonw -ArgumentList "-m safeeyes_windows" -NoNewWindow
