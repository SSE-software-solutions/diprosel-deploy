#!/bin/bash
# Script para actualizar el módulo nubefact_sunat en Docker

echo "=== Actualizando módulo NubeFact en Docker ==="

# 1. Encontrar el contenedor de Odoo
CONTAINER_NAME=$(docker ps --filter "ancestor=odoo" --format "{{.Names}}" | head -n 1)

if [ -z "$CONTAINER_NAME" ]; then
    echo "❌ No se encontró un contenedor de Odoo en ejecución"
    echo "Intenta con:"
    echo "  docker ps"
    exit 1
fi

echo "✅ Contenedor encontrado: $CONTAINER_NAME"

# 2. Verificar que el módulo esté en el contenedor
echo ""
echo "📁 Verificando módulo en el contenedor..."
docker exec $CONTAINER_NAME ls -la /mnt/extra-addons/nubefact_sunat

# 3. Actualizar el módulo
echo ""
echo "🔄 Actualizando módulo..."
docker exec -u odoo $CONTAINER_NAME odoo -d odoo -u nubefact_sunat --stop-after-init

# 4. Reiniciar contenedor
echo ""
echo "🔄 Reiniciando contenedor..."
docker restart $CONTAINER_NAME

echo ""
echo "✅ ¡Actualización completada!"
echo "Espera 10-15 segundos y recarga la página en tu navegador (Ctrl+Shift+R)"

