Param(
    [string]$WorkRoot = "$PSScriptRoot/../../.tmp/distribution-testing"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Skip {
    param([string]$Message)
    Write-Host "[dist-test] SKIP: $Message"
    exit 0
}

if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    Skip "Chocolatey not installed"
}

New-Item -ItemType Directory -Force -Path $WorkRoot | Out-Null
$testDir = Join-Path $WorkRoot ("choco-local-feed-{0}" -f [System.Guid]::NewGuid())
New-Item -ItemType Directory -Path $testDir | Out-Null

$pkgDir = Join-Path $testDir "redoubt-demo"
choco new redoubt-demo --output-directory $testDir | Out-Null
(Get-Content "$pkgDir\tools\chocolateyinstall.ps1") -replace 'Write-Host.*', 'Write-Host "Redoubt chocolatey demo installed"' | Set-Content "$pkgDir\tools\chocolateyinstall.ps1"

Push-Location $pkgDir
choco pack | Out-Null
Pop-Location

$nupkg = Get-ChildItem $pkgDir -Filter *.nupkg | Select-Object -First 1
if (-not $nupkg) {
    Skip "Chocolatey package creation failed"
}

$feedDir = Join-Path $testDir "feed"
New-Item -ItemType Directory -Path $feedDir | Out-Null
Copy-Item $nupkg.FullName -Destination $feedDir

Write-Host "[dist-test] Installing package from local feed"
choco install redoubt-demo -y --source $feedDir | Out-Null

Write-Host "[dist-test] Package installed successfully"
