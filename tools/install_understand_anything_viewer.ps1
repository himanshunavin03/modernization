[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$vendorRoot = Join-Path $repositoryRoot 'tools/vendor/understand-anything-viewer'
$archive = Join-Path $env:TEMP 'understand-anything-viewer-2.9.0.tgz'
$url = 'https://github.com/Egonex-AI/Understand-Anything/releases/download/v2.9.0/understand-anything-viewer.tgz'

if (-not (Get-Command npm.cmd -ErrorAction SilentlyContinue)) { throw 'Node.js 18+ and npm are required for the one-time viewer installation.' }
New-Item -ItemType Directory -Force -Path $vendorRoot | Out-Null
Invoke-WebRequest -Uri $url -OutFile $archive
& npm.cmd install --ignore-scripts --no-audit --no-fund --prefix $vendorRoot $archive
if ($LASTEXITCODE -ne 0) { throw 'Pinned viewer installation failed.' }
Write-Host "Installed pinned viewer under $vendorRoot"
