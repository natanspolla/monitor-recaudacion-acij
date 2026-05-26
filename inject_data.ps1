# inject_data.ps1
# Copia BUNDLED_XLS y BUNDLED_IPC desde afip_dashboard_v3.html hacia recaudacion_v4.html

$src = ".\afip_dashboard_v3.html"
$dst = ".\index.html"

Write-Host "Leyendo $src..."
$lines = [System.IO.File]::ReadAllLines($src, [System.Text.Encoding]::UTF8)

# Buscar las líneas exactas de BUNDLED_XLS y BUNDLED_IPC
$xlsStart = -1; $xlsEnd = -1; $ipcLine = -1

for ($i = 0; $i -lt $lines.Length; $i++) {
    if ($lines[$i] -match '^const BUNDLED_XLS\s*=') { $xlsStart = $i }
    if ($xlsStart -ge 0 -and $xlsEnd -lt 0 -and $lines[$i] -match '^\};' ) { $xlsEnd = $i }
    if ($lines[$i] -match '^const BUNDLED_IPC\s*=') { $ipcLine = $i }
    if ($ipcLine -gt 0) { break }
}

if ($xlsStart -lt 0 -or $xlsEnd -lt 0) {
    Write-Error "No se encontró BUNDLED_XLS en $src"
    exit 1
}
if ($ipcLine -lt 0) {
    Write-Error "No se encontró BUNDLED_IPC en $src"
    exit 1
}

Write-Host "BUNDLED_XLS: líneas $($xlsStart+1) a $($xlsEnd+1)"
Write-Host "BUNDLED_IPC: línea $($ipcLine+1)"

$xlsBlock = ($lines[$xlsStart..$xlsEnd]) -join "`n"
$ipcBlock  = $lines[$ipcLine]

Write-Host "Inyectando en $dst..."
$content = [System.IO.File]::ReadAllText($dst, [System.Text.Encoding]::UTF8)

$content = $content -replace "if\(typeof BUNDLED_XLS===.undefined.\) var BUNDLED_XLS=\{\};", $xlsBlock
$content = $content -replace "if\(typeof BUNDLED_IPC===.undefined.\) var BUNDLED_IPC=\{\};", $ipcBlock

[System.IO.File]::WriteAllText($dst, $content, [System.Text.Encoding]::UTF8)
Write-Host "Listo. Datos inyectados en $dst"
