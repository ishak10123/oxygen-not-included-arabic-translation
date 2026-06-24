@echo off
setlocal EnableExtensions EnableDelayedExpansion

echo ============================================================
echo Oxygen Not Included - Arabic Translation Installer
echo ============================================================
echo.
echo Installing translation files...
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command "& { $doc = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::MyDocuments); $target = Join-Path $doc 'Klei\OxygenNotIncluded\mods\local\arabic_translation'; if (Test-Path $target) { Remove-Item -Path $target -Recurse -Force }; New-Item -ItemType Directory -Path $target -Force | Out-Null; Copy-Item -Path '%~dp0..\files\arabic_translation\*' -Destination $target -Recurse -Force; write-host '[SUCCESS] Mod installed successfully!' }"

exit /b %ERRORLEVEL%
