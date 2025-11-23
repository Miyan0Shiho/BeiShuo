Param(
  [string]$EnvFile = "",
  [switch]$SetupMirrors,
  [switch]$Verbose
)

if ($Verbose) { $VerbosePreference = 'Continue' }

$RepoRoot = (Split-Path $PSScriptRoot -Parent)
$ComposeFile = Join-Path $RepoRoot 'docker/compose.dev.yml'
if ([string]::IsNullOrWhiteSpace($EnvFile)) { $EnvFile = Join-Path $RepoRoot '.env.dev' }
if (-not (Test-Path $EnvFile)) { Write-Host "[WARN] Env file '$EnvFile' not found. Fallback to .env.sample"; $EnvFile = Join-Path $RepoRoot '.env.sample' }

Write-Host "[INFO] Repo root: $RepoRoot"
Write-Host "[INFO] Compose file: $ComposeFile"
Write-Host "[INFO] Using env file: $EnvFile"

function Setup-RegistryMirrors {
  $DaemonJsonPath = Join-Path $env:USERPROFILE '.docker\daemon.json'
  New-Item -ItemType Directory -Path (Split-Path $DaemonJsonPath) -Force | Out-Null
  if (Test-Path $DaemonJsonPath) { Copy-Item $DaemonJsonPath "$DaemonJsonPath.bak.$(Get-Date -Format 'yyyyMMddHHmmss')" -Force }
  $json = '{"registry-mirrors":["https://docker.m.daocloud.io","https://hub-mirror.c.163.com","https://mirror.ccs.tencentyun.com"]}'
  Set-Content -Path $DaemonJsonPath -Value $json -Encoding UTF8
  Write-Host "[INFO] Wrote registry mirrors to $DaemonJsonPath"
  Write-Host "[INFO] Please restart Docker Desktop (Settings -> Docker Engine -> Apply & Restart)"
}

if ($SetupMirrors) { Setup-RegistryMirrors }

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { Write-Error "Docker not found in PATH"; exit 1 }
try { docker info | Out-Null } catch { Write-Error "Docker daemon not running. Start Docker Desktop and retry."; exit 1 }

New-Item -ItemType Directory -Path (Join-Path $RepoRoot 'data\faiss') -Force | Out-Null

Write-Host "[STEP] Pre-pulling base images (may take a few minutes)"
foreach ($img in @('maven:3.9.6-eclipse-temurin-17','eclipse-temurin:17-jre','node:20-alpine')) {
  Write-Host "[INFO] Pulling $img ..."
  try { docker pull $img | Out-Host } catch { Write-Warning "Pull failed for $img. Consider -SetupMirrors then restart Docker Desktop." }
}

Write-Host "[STEP] Building backend image"
docker compose -f $ComposeFile --env-file $EnvFile build backend | Out-Host

Write-Host "[STEP] Starting backend"
docker compose -f $ComposeFile --env-file $EnvFile up -d backend | Out-Host

Write-Host "[STEP] Building frontend image"
docker compose -f $ComposeFile --env-file $EnvFile build frontend | Out-Host

Write-Host "[STEP] Starting frontend"
docker compose -f $ComposeFile --env-file $EnvFile up -d frontend | Out-Host

Write-Host "[DONE] Services started"
Write-Host "[URL] Frontend:  http://localhost:5173"
Write-Host "[URL] Backend:   http://localhost:8080"
Write-Host "[TIP] View logs: docker compose -f `"$ComposeFile`" logs -f backend"
Write-Host "[TIP] Stop:      docker compose -f `"$ComposeFile`" down"