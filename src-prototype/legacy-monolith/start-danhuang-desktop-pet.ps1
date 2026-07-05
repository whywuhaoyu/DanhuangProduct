$ErrorActionPreference = "Stop"

$pythonw = "C:\Users\27176\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\pythonw.exe"
$python = "C:\Users\27176\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$script = Join-Path $PSScriptRoot "run-danhuang-desktop-pet.py"
$legacyScript = "C:\Users\27176\.codex\pets\danhuang\run-danhuang-desktop-pet.py"

$existing = Get-CimInstance Win32_Process | Where-Object {
    ($_.Name -in @("python.exe", "pythonw.exe")) -and (
        ($_.CommandLine -like "*$script*") -or
        ($_.CommandLine -like "*$legacyScript*")
    )
}
foreach ($process in $existing) {
    Stop-Process -Id $process.ProcessId -Force
}

if (Test-Path $pythonw) {
    Start-Process -FilePath $pythonw -ArgumentList @($script) -WindowStyle Hidden
} else {
    Start-Process -FilePath $python -ArgumentList @($script) -WindowStyle Hidden
}
