[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidatePattern('^[a-z0-9][a-z0-9-]{0,62}$')]
    [string]$ProjectId,

    [Parameter(Mandatory)]
    [ValidateRange(1, 65535)]
    [int]$Port,

    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$AccessToken
)

$ErrorActionPreference = 'Stop'
$repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$artifactRoot = Join-Path $repositoryRoot (Join-Path 'artifacts' $ProjectId)
$graphPath = Join-Path $artifactRoot 'knowledge-graph.json'
$exporterPath = Join-Path $repositoryRoot 'tools/export_understand_anything_visualization.py'
$viewerPackage = 'https://github.com/Egonex-AI/Understand-Anything/releases/download/v2.9.0/understand-anything-viewer.tgz'

if (-not (Test-Path -LiteralPath $graphPath -PathType Leaf)) {
    throw "Canonical graph artifact was not found for project '$ProjectId': $graphPath"
}
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw 'Python is required to run the deterministic visualization exporter.'
}
if (-not (Get-Command npx -ErrorAction SilentlyContinue)) {
    throw 'Node.js 18+ and npx are required to launch the local viewer.'
}
if (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue) {
    throw "Port $Port is already in use. Select an unused local port."
}

& python $exporterPath --graph $graphPath --output (Join-Path $artifactRoot 'visualization') --project-id $ProjectId
if ($LASTEXITCODE -ne 0) { throw 'Visualization export failed.' }

$env:UNDERSTAND_ACCESS_TOKEN = $AccessToken
$url = "http://127.0.0.1:$Port/?token=$AccessToken"
Write-Host "Open $url"
Write-Host 'The viewer is local and read-only. Press Ctrl+C to stop it.'
& npx --yes $viewerPackage (Join-Path $artifactRoot 'visualization') --port $Port --no-open
