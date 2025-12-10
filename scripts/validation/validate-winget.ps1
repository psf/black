#!/usr/bin/env pwsh
$ErrorActionPreference = 'Stop'

Write-Host "=== WinGet Installation Validation ==="

# Check if command exists
if (!(Get-Command provenance-demo -ErrorAction SilentlyContinue)) {
    Write-Host "❌ provenance-demo command not found"
    Write-Host "💡 Try restarting your terminal or adding to PATH"
    exit 1
}
Write-Host "✓ Command found"

# Check version
try {
    $version = provenance-demo --version 2>&1
    if ([string]::IsNullOrEmpty($version)) {
        Write-Host "❌ Version check failed"
        exit 1
    }
    Write-Host "✓ Version: $version"
} catch {
    Write-Host "❌ Version check failed: $_"
    exit 1
}

# Test basic functionality
try {
    $output = provenance-demo hello "Test" 2>&1
    if ($output -notlike "*hello, Test*") {
        Write-Host "❌ Basic functionality test failed"
        Write-Host "   Expected: 'hello, Test'"
        Write-Host "   Got: $output"
        exit 1
    }
    Write-Host "✓ Basic functionality works"
} catch {
    Write-Host "❌ Basic functionality test failed: $_"
    exit 1
}

# Check if verify command exists
try {
    $verifyHelp = provenance-demo verify --help 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Verify command not available"
        exit 1
    }
    Write-Host "✓ Verify command available"
} catch {
    Write-Host "❌ Verify command check failed: $_"
    exit 1
}

Write-Host ""
Write-Host "✅ All validation checks passed!"
Write-Host "Installation is working correctly."
