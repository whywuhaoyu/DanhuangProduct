param(
  [string]$ProductRoot = $env:DANHUANG_PRODUCT_ROOT
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

function Write-Check($Name, $Ok, $Detail = "") {
  $status = if ($Ok) { "OK" } else { "WARN" }
  $line = "[$status] $Name"
  if ($Detail) {
    $line += " - $Detail"
  }
  Write-Host $line
}

$node = Get-Command node -ErrorAction SilentlyContinue
$npm = Get-Command npm -ErrorAction SilentlyContinue
$cargo = Get-Command cargo -ErrorAction SilentlyContinue
$git = Get-Command git -ErrorAction SilentlyContinue
$gh = Get-Command gh -ErrorAction SilentlyContinue
if (-not $gh) {
  $defaultGhDir = Join-Path $env:ProgramFiles "GitHub CLI"
  $defaultGh = Join-Path $defaultGhDir "gh.exe"
  if (Test-Path $defaultGh) {
    $env:Path = "$defaultGhDir;$env:Path"
    $gh = Get-Command gh -ErrorAction SilentlyContinue
  }
}

Write-Check "Node.js" ([bool]$node) ($(if ($node) { node --version } else { "not found" }))
Write-Check "npm" ([bool]$npm) ($(if ($npm) { npm --version } else { "not found" }))
Write-Check "Cargo" ([bool]$cargo) ($(if ($cargo) { cargo --version } else { "not found" }))
Write-Check "Git" ([bool]$git) ($(if ($git) { git --version } else { "not found" }))
Write-Check "GitHub CLI" ([bool]$gh) ($(if ($gh) { gh --version | Select-Object -First 1 } else { "not found" }))

if ($gh) {
  $previousErrorActionPreference = $ErrorActionPreference
  $ErrorActionPreference = "Continue"
  gh auth status *> $null
  $authOk = $LASTEXITCODE -eq 0
  $ErrorActionPreference = $previousErrorActionPreference
  Write-Check "GitHub auth" $authOk "run gh auth login if this is WARN"
}

$runtimeRoot = $null
if ($ProductRoot) {
  $runtimeRoot = Join-Path $ProductRoot "data-dev/current-runtime/danhuang"
  Write-Check "DANHUANG_PRODUCT_ROOT" (Test-Path $runtimeRoot) $runtimeRoot
} else {
  $cursor = (Resolve-Path ".").Path
  for ($i = 0; $i -lt 8; $i++) {
    $candidate = Join-Path $cursor "data-dev/current-runtime/danhuang"
    if (Test-Path $candidate) {
      $runtimeRoot = $candidate
      break
    }
    $parent = Split-Path -Parent $cursor
    if ($parent -eq $cursor -or -not $parent) { break }
    $cursor = $parent
  }
  Write-Check "Runtime mirror" ([bool]$runtimeRoot) ($(if ($runtimeRoot) { $runtimeRoot } else { "set DANHUANG_PRODUCT_ROOT" }))
}

if (Test-Path ".git") {
  $remote = git remote get-url origin 2>$null
  Write-Check "Git origin" ([bool]$remote) $remote
  $dirty = git status --short
  Write-Check "Git working tree" (-not $dirty) ($(if ($dirty) { "has local changes" } else { "clean" }))
}

Write-Host ""
Write-Host "Suggested checks:"
Write-Host "  npm install"
Write-Host "  npm run type-check"
Write-Host "  cargo check --manifest-path src-tauri/Cargo.toml"
