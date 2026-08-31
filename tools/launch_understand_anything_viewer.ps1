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
$vendorRoot = Join-Path $repositoryRoot 'tools/vendor/understand-anything-viewer'
$packageJson = Join-Path $vendorRoot 'node_modules/understand-anything-viewer/package.json'
$viewerExecutable = Join-Path $vendorRoot 'node_modules/.bin/understand-anything-viewer.cmd'

if (-not (Test-Path -LiteralPath $graphPath -PathType Leaf)) {
    throw "Canonical graph artifact was not found for project '$ProjectId': $graphPath"
}
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw 'Python is required to run the deterministic visualization exporter.'
}
if (-not (Test-Path -LiteralPath $viewerExecutable -PathType Leaf) -or -not (Test-Path -LiteralPath $packageJson -PathType Leaf)) {
    throw 'Local pinned viewer is missing. Run .\tools\install_understand_anything_viewer.ps1 once before launching.'
}
$package = Get-Content -LiteralPath $packageJson -Raw | ConvertFrom-Json
if ($package.name -ne 'understand-anything-viewer' -or $package.version -ne '2.9.0' -or $package.license -ne 'MIT' -or $package.repository.url -notmatch 'Egonex-AI/Understand-Anything') {
    throw 'Local viewer verification failed. Run .\tools\install_understand_anything_viewer.ps1 to restore the pinned official package.'
}
if (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue) {
    throw "Port $Port is already in use. Select an unused local port."
}

& python $exporterPath --graph $graphPath --output (Join-Path $artifactRoot 'visualization') --project-id $ProjectId
if ($LASTEXITCODE -ne 0) { throw 'Visualization export failed.' }

$env:UNDERSTAND_ACCESS_TOKEN = $AccessToken
$url = ('http' + "://127.0.0.1:$Port/?token=$AccessToken")
Write-Host "Open $url"
Write-Host 'The viewer is local and read-only. Press Ctrl+C to stop it.'
& $viewerExecutable (Join-Path $artifactRoot 'visualization') --port $Port --no-open
