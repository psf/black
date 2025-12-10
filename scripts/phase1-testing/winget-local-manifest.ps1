Param(
    [string]$ManifestPath = "$PSScriptRoot/../../packaging/winget/manifests/OWNER.redoubt.yaml"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Skip {
    param([string]$Message)
    Write-Host "[dist-test] SKIP: $Message"
    exit 0
}

if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Skip "winget not installed"
}

if (-not (Get-Command wingetcreate -ErrorAction SilentlyContinue)) {
    Skip "wingetcreate CLI not installed"
}

if (-not (Test-Path $ManifestPath)) {
    Skip "Manifest file not found: $ManifestPath"
}

Write-Host "[dist-test] Validating manifest with wingetcreate"
wingetcreate validate --manifest $ManifestPath

Write-Host "[dist-test] Manifest validated successfully"
