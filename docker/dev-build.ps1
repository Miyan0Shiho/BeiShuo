Param(
  [string]$EnvFile = "",
  [switch]$NoCache
)

$RepoRoot = (Split-Path $PSScriptRoot -Parent)
$ComposeFile = Join-Path $RepoRoot 'docker/compose.dev.yml'
if ([string]::IsNullOrWhiteSpace($EnvFile)) { $EnvFile = Join-Path $RepoRoot '.env.dev' }
if (-not (Test-Path $EnvFile)) { $EnvFile = Join-Path $RepoRoot '.env.sample' }

Write-Host "[STEP] Pre-pulling base images"
foreach ($img in @('maven:3.9.6-eclipse-temurin-17','eclipse-temurin:17-jre','node:20-alpine')) { try { docker pull $img | Out-Host } catch { Write-Warning "Pull failed for $img" } }

Write-Host "[STEP] Rebuilding backend"
if ($NoCache) { docker compose -f $ComposeFile --env-file $EnvFile build --no-cache backend | Out-Host } else { docker compose -f $ComposeFile --env-file $EnvFile build backend | Out-Host }

Write-Host "[STEP] Rebuilding frontend"
if ($NoCache) { docker compose -f $ComposeFile --env-file $EnvFile build --no-cache frontend | Out-Host } else { docker compose -f $ComposeFile --env-file $EnvFile build frontend | Out-Host }

Write-Host "[DONE] Build refreshed. Restart services if needed:"
Write-Host "docker compose -f `"$ComposeFile`" --env-file `"$EnvFile`" up -d backend frontend"