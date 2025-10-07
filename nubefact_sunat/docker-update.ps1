# Script PowerShell para actualizar el módulo nubefact_sunat en Docker
# Ejecutar desde: .\docker-update.ps1

Write-Host "=== Actualizando módulo NubeFact en Docker ===" -ForegroundColor Cyan

# 1. Listar contenedores de Odoo
Write-Host "`n📦 Contenedores de Odoo en ejecución:" -ForegroundColor Yellow
docker ps --filter "name=odoo" --format "table {{.ID}}\t{{.Names}}\t{{.Status}}"

# 2. Solicitar nombre del contenedor
$containerName = Read-Host "`nIngresa el nombre del contenedor de Odoo (por ejemplo: odoo, odoo_web_1, etc.)"

if ([string]::IsNullOrWhiteSpace($containerName)) {
    Write-Host "❌ Debes ingresar un nombre de contenedor" -ForegroundColor Red
    exit 1
}

# 3. Verificar que el módulo esté en el contenedor
Write-Host "`n📁 Verificando módulo en el contenedor..." -ForegroundColor Yellow
docker exec $containerName ls -la /mnt/extra-addons/nubefact_sunat

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ No se encontró el módulo en /mnt/extra-addons/nubefact_sunat" -ForegroundColor Red
    Write-Host "Verifica que el volumen esté montado correctamente" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Módulo encontrado" -ForegroundColor Green

# 4. Preguntar nombre de la base de datos
$dbName = Read-Host "`nIngresa el nombre de la base de datos (por defecto: postgres)"
if ([string]::IsNullOrWhiteSpace($dbName)) {
    $dbName = "postgres"
}

# 5. Actualizar el módulo
Write-Host "`n🔄 Actualizando módulo en la base de datos: $dbName..." -ForegroundColor Yellow
docker exec -u odoo $containerName odoo -d $dbName -u nubefact_sunat --stop-after-init

# 6. Reiniciar contenedor
Write-Host "`n🔄 Reiniciando contenedor..." -ForegroundColor Yellow
docker restart $containerName

Write-Host "`n✅ ¡Actualización completada!" -ForegroundColor Green
Write-Host "Espera 10-15 segundos y recarga la página en tu navegador (Ctrl+Shift+R)" -ForegroundColor Cyan
