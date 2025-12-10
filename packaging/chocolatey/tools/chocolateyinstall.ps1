$ErrorActionPreference = 'Stop'

$packageName = 'black'
$toolsDir = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"
$url = 'https://github.com/hollowsunhc/black/releases/download/v0.1.0/black.pyz'
$checksum = 'REPLACE_WITH_SHA256_FROM_RELEASE'
$checksumType = 'sha256'

# Download the .pyz file
$pyzFile = Join-Path $toolsDir 'black.pyz'
Get-ChocolateyWebFile -PackageName $packageName `
                      -FileFullPath $pyzFile `
                      -Url $url `
                      -Checksum $checksum `
                      -ChecksumType $checksumType

# Create a wrapper batch file
$batFile = Join-Path $toolsDir 'black.bat'
@"
@echo off
python "%~dp0black.pyz" %*
"@ | Out-File -FilePath $batFile -Encoding ASCII

# Add to PATH
Install-ChocolateyPath -PathToInstall $toolsDir -PathType 'User'

Write-Host "Provenance Demo has been installed successfully!"
Write-Host "Run 'black --version' to verify installation"
Write-Host "Run 'black verify' to validate security attestations"
