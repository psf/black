#!/usr/bin/env pwsh
# Build WinGet manifest files from .pyz artifact
# Usage: ./scripts/build_winget.ps1 [-Version v0.1.0] [-PyzPath dist/provenance-demo.pyz] [-OutputDir packaging/winget/manifests]

param(
    [Parameter(Mandatory=$false)]
    [string]$Version = "v0.0.1-alpha.10",

    [Parameter(Mandatory=$false)]
    [string]$PyzPath = "dist/provenance-demo.pyz",

    [Parameter(Mandatory=$false)]
    [string]$OutputDir = "packaging/winget/manifests"
)

$ErrorActionPreference = 'Stop'

Write-Host "Building WinGet manifests for version $Version" -ForegroundColor Blue

# Ensure .pyz file exists
if (!(Test-Path $PyzPath)) {
    Write-Error "PYZ file not found at: $PyzPath"
    Write-Host "Run ./scripts/build_pyz.sh first to build the .pyz file" -ForegroundColor Yellow
    exit 1
}

# Calculate SHA256 checksum
Write-Host "Calculating SHA256 checksum..." -ForegroundColor Cyan
$checksum = (Get-FileHash -Path $PyzPath -Algorithm SHA256).Hash.ToLower()
Write-Host "  SHA256: $checksum" -ForegroundColor Green

# Remove 'v' prefix from version if present
$versionNoV = $Version -replace '^v', ''

# Get release date (today in ISO format)
$releaseDate = Get-Date -Format "yyyy-MM-dd"

# Create output directory
$manifestDir = Join-Path $OutputDir $versionNoV
New-Item -ItemType Directory -Path $manifestDir -Force | Out-Null
Write-Host "Output directory: $manifestDir" -ForegroundColor Cyan

# Template directory
$templateDir = "packaging/winget/templates"

# Generate version manifest
Write-Host "Generating version manifest..." -ForegroundColor Cyan
$versionTemplate = Get-Content "$templateDir/version.yaml.template" -Raw
$versionContent = $versionTemplate -replace '{{VERSION_NO_V}}', $versionNoV

$versionContent | Out-File -FilePath "$manifestDir/hollowsunhc.ProvenanceDemo.yaml" -Encoding UTF8 -NoNewline

# Generate installer manifest
Write-Host "Generating installer manifest..." -ForegroundColor Cyan
$installerTemplate = Get-Content "$templateDir/installer.yaml.template" -Raw
$installerContent = $installerTemplate `
    -replace '{{VERSION_NO_V}}', $versionNoV `
    -replace '{{VERSION}}', $Version `
    -replace '{{SHA256}}', $checksum.ToUpper() `
    -replace '{{RELEASE_DATE}}', $releaseDate

$installerContent | Out-File -FilePath "$manifestDir/hollowsunhc.ProvenanceDemo.installer.yaml" -Encoding UTF8 -NoNewline

# Generate locale manifest
Write-Host "Generating locale manifest..." -ForegroundColor Cyan
$localeTemplate = Get-Content "$templateDir/locale.en-US.yaml.template" -Raw
$localeContent = $localeTemplate `
    -replace '{{VERSION_NO_V}}', $versionNoV `
    -replace '{{VERSION}}', $Version

$localeContent | Out-File -FilePath "$manifestDir/hollowsunhc.ProvenanceDemo.locale.en-US.yaml" -Encoding UTF8 -NoNewline

Write-Host "WinGet manifests created successfully!" -ForegroundColor Green
Write-Host "`nManifest files:" -ForegroundColor Blue
Get-ChildItem -Path $manifestDir | ForEach-Object {
    Write-Host "  - $($_.Name)" -ForegroundColor Cyan
}

Write-Host "`nTo test locally (requires winget):" -ForegroundColor Yellow
Write-Host "  winget validate --manifest $manifestDir" -ForegroundColor White
Write-Host "`nTo submit to WinGet repository:" -ForegroundColor Yellow
Write-Host "  1. Fork https://github.com/microsoft/winget-pkgs" -ForegroundColor White
Write-Host "  2. Copy $manifestDir to manifests/r/hollowsunhc/ProvenanceDemo/$versionNoV/" -ForegroundColor White
Write-Host "  3. Submit PR to microsoft/winget-pkgs" -ForegroundColor White
