<#
borrar-carpetas-vacias.ps1  (PowerShell 5.1+)

Borra SOLO las carpetas de fanout VACIAS dentro de .git/objects
(00, 01, ... ff). Nunca borra 'info', 'pack' ni una carpeta con
contenido. Git recrea estas carpetas cuando las necesita.

Uso:
  powershell -NoProfile -ExecutionPolicy Bypass -File ".\borrar-carpetas-vacias.ps1" -Repo "C:\ruta\al\repo"
  powershell -NoProfile -ExecutionPolicy Bypass -File ".\borrar-carpetas-vacias.ps1" -Repo "C:\ruta\al\repo" -DryRun   (solo lista)
Si lo ejecutas desde dentro del repo, puedes omitir -Repo.
#>
param(
    [string]$Repo = "",
    [switch]$DryRun
)

if (-not $Repo) { $Repo = (Get-Location).Path }

$gitDir = git -C $Repo rev-parse --absolute-git-dir 2>$null
if (-not $gitDir) {
    Write-Host "ERROR: '$Repo' no es un repositorio git (o git no esta en el PATH)."
    exit 1
}

$objects = Join-Path $gitDir "objects"
Write-Host "Repositorio: $gitDir"
Write-Host ""

$borradas = 0
$fallos = 0

$candidatas = Get-ChildItem -LiteralPath $objects -Directory -Force -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -match '^[0-9a-f]{2}$' }

foreach ($dir in $candidatas) {
    $hijos = @(Get-ChildItem -LiteralPath $dir.FullName -Force -ErrorAction SilentlyContinue)

    if ($hijos.Count -gt 0) { continue }   # con contenido: no se toca

    if ($DryRun) {
        Write-Host "[DryRun] se borraria: $($dir.Name)"
        $borradas++
        continue
    }

    try {
        Remove-Item -LiteralPath $dir.FullName -Force -ErrorAction Stop
        Write-Host "Borrada: $($dir.Name)"
        $borradas++
    } catch {
        Write-Host "No se pudo borrar '$($dir.Name)': $($_.Exception.Message)"
        $fallos++
    }
}

Write-Host ""
if ($DryRun) {
    Write-Host ("Carpetas vacias encontradas: {0} (nada borrado: era -DryRun)" -f $borradas)
} else {
    Write-Host ("Carpetas vacias borradas: {0} | Fallos: {1}" -f $borradas, $fallos)
}