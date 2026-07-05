param(
  [string]$Owner = "whywuhaoyu",
  [string]$Repo = "danhuang-desktop-pet-tauri-vue",
  [switch]$Public
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
  throw "GitHub CLI is not installed. Install it first: winget install --id GitHub.cli -e"
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  throw "Git is not available on PATH."
}

gh auth status
if ($LASTEXITCODE -ne 0) {
  throw "GitHub CLI is not logged in. Run: gh auth login --hostname github.com --git-protocol https --web"
}

$visibility = if ($Public) { "--public" } else { "--private" }
$repoFullName = "$Owner/$Repo"
$remoteUrl = "https://github.com/$repoFullName.git"

if (-not (git remote | Select-String -SimpleMatch "origin")) {
  git remote add origin $remoteUrl
} else {
  git remote set-url origin $remoteUrl
}

$exists = $true
gh repo view $repoFullName *> $null
if ($LASTEXITCODE -ne 0) {
  $exists = $false
}

if (-not $exists) {
  gh repo create $repoFullName $visibility --description "Danhuang desktop pet Tauri Vue app"
  if ($LASTEXITCODE -ne 0) {
    throw "Failed to create GitHub repository $repoFullName"
  }
}

git push -u origin main

Write-Host "Published $repoFullName"
