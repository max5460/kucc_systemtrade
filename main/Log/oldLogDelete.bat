CD %~dp0
forfiles /p %~dp0 /d -30 /m "*.log" /c "cmd /c del @file"