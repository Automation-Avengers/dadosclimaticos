$exclude = @("venv", "dadosclimaticos.zip")
$files = Get-ChildItem -Path . -Exclude $exclude
Compress-Archive -Path $files -DestinationPath "dadosclimaticos.zip" -Force