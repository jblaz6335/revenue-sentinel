$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$hackathonRoot = (Resolve-Path (Join-Path $projectRoot "..")).Path
$stageRoot = Join-Path $hackathonRoot "package-staging-revenue-sentinel-final-20260825-v4"
$stageProject = Join-Path $stageRoot "revenue-sentinel"
$distRoot = Join-Path $hackathonRoot "dist"
$archive = Join-Path $distRoot "revenue-sentinel-submission-source-v4.zip"

if (Test-Path -LiteralPath $stageRoot) { throw "Staging path already exists: $stageRoot" }
if (Test-Path -LiteralPath $archive) { throw "Archive already exists: $archive" }

$files = @(
  ".dockerignore", ".gcloudignore", ".gitignore", ".python-version", "ARCHITECTURE.md", "DEMO_RUNBOOK.md",
  "Dockerfile", "LICENSE", "main.py", "PROJECT_CHECKLIST.md", "pyproject.toml", "README.md",
  "requirements.txt", "SECURITY.md", "SUBMISSION.md", "uv.lock", "VERIFICATION.md", "verify.ps1",
  "VIDEO_SCRIPT.md", "app/__init__.py", "app/agent.py", "app/runtime.py", "assets/architecture.png",
  "assets/architecture.svg", "fixtures/opportunities.json", "infra/deploy.ps1", "infra/service.yaml",
  "src/revenue_sentinel/__init__.py", "src/revenue_sentinel/cli.py", "src/revenue_sentinel/demo.py",
  "src/revenue_sentinel/engine.py", "src/revenue_sentinel/firestore_ledger.py",
  "src/revenue_sentinel/ledger.py", "src/revenue_sentinel/models.py",
  "src/revenue_sentinel/service.py", "tests/test_agent_definition.py", "tests/test_api.py",
  "tests/test_engine.py", "tests/test_firestore_ledger.py", "tests/test_ledger.py",
  "tests/test_runtime.py", "tests/test_service.py"
)

New-Item -ItemType Directory -Path $stageProject -Force | Out-Null
foreach ($relative in $files) {
  $source = Join-Path $projectRoot $relative
  if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw "Missing allowlisted file: $relative" }
  $destination = Join-Path $stageProject $relative
  New-Item -ItemType Directory -Path (Split-Path $destination -Parent) -Force | Out-Null
  Copy-Item -LiteralPath $source -Destination $destination
}

New-Item -ItemType Directory -Path $distRoot -Force | Out-Null
Compress-Archive -LiteralPath $stageProject -DestinationPath $archive -CompressionLevel Optimal

[pscustomobject]@{
  Archive = $archive
  FileCount = $files.Count
  Sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $archive).Hash
} | ConvertTo-Json
