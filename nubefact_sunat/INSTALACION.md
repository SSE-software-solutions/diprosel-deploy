# Instrucciones de Instalación - NubeFact SUNAT para Odoo 18

## Cambios Realizados para Compatibilidad Odoo 18

### ✅ Correcciones Aplicadas:

1. **Vistas XML:**
   - ✅ Cambio de `<tree>` a `<list>` en todas las vistas
   - ✅ Cambio de `view_mode="tree,form"` a `view_mode="list,form"`
   - ✅ Cambio de xpath `//tree` a `//list`
   - ✅ Simplificación de herencia de vistas para mayor compatibilidad

2. **Dependencias:**
   - ✅ Eliminada dependencia de `l10n_pe` (opcional)
   - ✅ Solo requiere módulo `account` (base de Odoo)

3. **Código Python:**
   - ✅ Detección automática de tipo de documento por VAT
   - ✅ Compatibilidad con y sin módulo de localización peruana
   - ✅ Fallback robusto para identificación de documentos

## Pasos de Instalación

### Método 1: Desde la Interfaz Web (Recomendado)

1. **Actualizar lista de aplicaciones:**
   - Ve a `Aplicaciones` (menú principal)
   - Haz clic en el icono de tres puntos (⋮) arriba a la derecha
   - Selecciona "Actualizar Lista de Aplicaciones"
   - Confirma la actualización

2. **Buscar e instalar:**
   - En el buscador, escribe: **"NubeFact"** o **"SUNAT"**
   - Encuentra el módulo: "Facturación Electrónica SUNAT - NubeFact"
   - Haz clic en **"Instalar"**
   - Espera a que termine la instalación (puede tardar 1-2 minutos)

3. **Verificar instalación:**
   - Ve a `Contabilidad > Configuración`
   - Deberías ver el menú **"NubeFact"**
   - Si lo ves, ¡la instalación fue exitosa! ✅

### Método 2: Desde Terminal (Si tienes acceso SSH)

```bash
# Conectarse al servidor
ssh usuario@38.242.131.244

# Ir al directorio de Odoo
cd /path/to/odoo

# Actualizar el módulo
./odoo-bin -c odoo.conf -d nombre_base_datos -u nubefact_sunat --stop-after-init

# O instalarlo directamente
./odoo-bin -c odoo.conf -d nombre_base_datos -i nubefact_sunat --stop-after-init

# Reiniciar el servicio
sudo systemctl restart odoo
```

### Método 3: Con Docker (Si usas contenedores)

```bash
# Entrar al contenedor
docker exec -it odoo_container bash

# Actualizar módulo
odoo -d nombre_base_datos -u nubefact_sunat --stop-after-init

# Salir y reiniciar contenedor
exit
docker restart odoo_container
```

## Solución de Problemas

### Error: "module not found"
**Causa:** El módulo no está en la ruta de addons
**Solución:**
1. Verifica que la carpeta `nubefact_sunat` esté en `/mnt/extra-addons/`
2. Verifica permisos: `chmod -R 755 /mnt/extra-addons/nubefact_sunat`
3. Reinicia Odoo

### Error: "l10n_latam_identification_type_id not found"
**Solución:** Ya está corregido. El módulo ahora funciona sin localización peruana.

### Error: ParseError en vistas XML
**Causa:** Caché del servidor
**Solución:**
1. Limpia el caché del navegador (Ctrl + Shift + R)
2. Desinstala el módulo si está parcialmente instalado
3. Reinstala desde cero

### Error: "view_invoice_tree not found"
**Solución:** El módulo ahora usa una herencia más simple y robusta.

## Verificación Post-Instalación

### 1. Verificar que el módulo esté instalado

```python
# Desde shell de Odoo
self.env['ir.module.module'].search([('name', '=', 'nubefact_sunat')])
# Debe mostrar el módulo con state='installed'
```

### 2. Verificar que los modelos existan

```python
# Verificar modelo de configuración
self.env['nubefact.config'].search([])

# Verificar campos en facturas
self.env['account.move']._fields.keys()
# Debe incluir: 'sunat_estado', 'sunat_enviado', etc.
```

### 3. Verificar que los menús existan

- Ve a `Contabilidad > Configuración > NubeFact`
- Debe aparecer el submenú "Configuración"

### 4. Verificar que los botones aparezcan en facturas

1. Ve a `Contabilidad > Clientes > Facturas`
2. Crea una factura de prueba
3. Confírmala
4. Debe aparecer el botón **"Enviar a SUNAT"**

## Actualización del Módulo

Si haces cambios al módulo:

```bash
# Actualizar sin perder datos
odoo-bin -c odoo.conf -d nombre_base_datos -u nubefact_sunat

# O desde la interfaz:
# Aplicaciones > NubeFact > Actualizar
```

## Desinstalación (Si es necesario)

1. Ve a `Aplicaciones`
2. Busca "NubeFact"
3. Haz clic en `Desinstalar`
4. Confirma (esto eliminará los datos del módulo)

## Logs y Depuración

### Ver logs en tiempo real

```bash
# Linux
tail -f /var/log/odoo/odoo.log

# Docker
docker logs -f odoo_container

# Filtrar errores de NubeFact
tail -f /var/log/odoo/odoo.log | grep -i nubefact
```

### Activar modo debug en Odoo

1. Ve a tu URL de Odoo
2. Agrega `?debug=1` al final de la URL
   - Ejemplo: `http://38.242.131.244:8069/web?debug=1`
3. Ahora verás más información técnica

## Configuración Inicial Rápida

Después de instalar:

1. **Configurar credenciales:**
   - `Contabilidad > Configuración > NubeFact > Configuración`
   - Crear nuevo registro con RUC y Token

2. **Probar conexión:**
   - Botón "Probar Conexión"
   - Verificar que sea exitosa

3. **Crear factura de prueba:**
   - Cliente con RUC o DNI
   - Confirmar y enviar a SUNAT

## Contacto y Soporte

- **Módulo creado por:** SSE
- **Versión:** 18.0.1.0.0
- **Compatible con:** Odoo 18.0 Community y Enterprise
- **Licencia:** LGPL-3

---

**Nota:** Este módulo ha sido testeado y optimizado específicamente para Odoo 18.
Todas las vistas usan `<list>` en lugar de `<tree>` según los cambios de Odoo 18.
