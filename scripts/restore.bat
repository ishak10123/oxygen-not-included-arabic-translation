@echo off
setlocal EnableExtensions EnableDelayedExpansion

echo ============================================================
echo Oxygen Not Included - Arabic Translation Uninstaller
echo ============================================================
echo.
echo Restoring original settings (removing Arabic translation mod)...
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command "& { $doc = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::MyDocuments); $target = Join-Path $doc 'Klei\OxygenNotIncluded\mods\local\arabic_translation'; if (Test-Path $target) { Remove-Item -Path $target -Recurse -Force; write-host '[SUCCESS] Mod removed successfully!' } else { write-host '[INFO] Mod is not installed.' } }"

exit /b %ERRORLEVEL%
