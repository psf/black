#!/usr/bin/env pwsh
# Build Chocolatey package from .pyz artifact
# Usage: ./scripts/build_chocolatey.ps1 [-Version v0.1.0] [-PyzPath dist/provenance-demo.pyz]

param(
    [Parameter(Mandatory=$false)]
    [string]$Version = "v0.0.1-alpha.10",

    [Parameter(Mandatory=$false)]
    [string]$PyzPath = "dist/provenance-demo.pyz",

    [Parameter(Mandatory=$false)]
    [string]$OutputDir = "dist"
)

$ErrorActionPreference = 'Stop'

Write-Host "Building Chocolatey package for version $Version" -ForegroundColor Blue

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

# Create working directory
$workDir = Join-Path $env:TEMP "choco-build-$(Get-Date -Format 'yyyyMMddHHmmss')"
New-Item -ItemType Directory -Path $workDir -Force | Out-Null
Write-Host "Working directory: $workDir" -ForegroundColor Cyan

try {
    # Copy package structure
    $chocoDir = "packaging/chocolatey"
    Copy-Item -Path "$chocoDir/tools" -Destination $workDir -Recurse

    # Generate chocolateyInstall.ps1 from template
    Write-Host "Generating chocolateyInstall.ps1..." -ForegroundColor Cyan
    $installTemplate = Get-Content "$chocoDir/tools/chocolateyinstall.ps1.template" -Raw
    $installScript = $installTemplate `
        -replace '{{VERSION}}', $Version `
        -replace '{{CHECKSUM}}', $checksum

    $installScript | Out-File -FilePath "$workDir/tools/chocolateyinstall.ps1" -Encoding UTF8 -NoNewline

    # Generate nuspec from template
    Write-Host "Generating provenance-demo.nuspec..." -ForegroundColor Cyan
    $nuspecTemplate = Get-Content "$chocoDir/redoubt.nuspec.template" -Raw
    $nuspecContent = $nuspecTemplate `
        -replace '{{VERSION}}', $Version `
        -replace '{{VERSION_NO_V}}', $versionNoV

    $nuspecContent | Out-File -FilePath "$workDir/provenance-demo.nuspec" -Encoding UTF8 -NoNewline

    # Pack the Chocolatey package
    Write-Host "Packing Chocolatey package..." -ForegroundColor Cyan
    Push-Location $workDir
    try {
        $packOutput = choco pack provenance-demo.nuspec 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Chocolatey pack failed: $packOutput"
            exit 1
        }
        Write-Host $packOutput -ForegroundColor Gray
    } finally {
        Pop-Location
    }

    # Move .nupkg to output directory
    $nupkgFile = Get-ChildItem -Path $workDir -Filter "*.nupkg" | Select-Object -First 1
    if ($nupkgFile) {
        New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
        $destination = Join-Path $OutputDir $nupkgFile.Name
        Move-Item -Path $nupkgFile.FullName -Destination $destination -Force
        Write-Host "Chocolatey package created: $destination" -ForegroundColor Green

        # Display package info
        Write-Host "`nPackage Details:" -ForegroundColor Blue
        Write-Host "  File: $($nupkgFile.Name)" -ForegroundColor Cyan
        Write-Host "  Size: $([math]::Round($nupkgFile.Length / 1KB, 2)) KB" -ForegroundColor Cyan
        Write-Host "  Version: $versionNoV" -ForegroundColor Cyan
        Write-Host "  Checksum: $checksum" -ForegroundColor Cyan
    } else {
        Write-Error "No .nupkg file was created"
        exit 1
    }
} finally {
    # Cleanup
    if (Test-Path $workDir) {
        Remove-Item -Path $workDir -Recurse -Force
    }
}

Write-Host "`nChocolatey package build complete!" -ForegroundColor Green
Write-Host "`nTo test locally:" -ForegroundColor Yellow
Write-Host "  choco install $destination -y --source='.' --force" -ForegroundColor White
