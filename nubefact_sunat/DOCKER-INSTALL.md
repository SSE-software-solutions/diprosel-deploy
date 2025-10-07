# Instalación en Docker - NubeFact SUNAT

## Tu Situación Actual

- ✅ Odoo 18 corriendo en Docker
- ✅ Servidor: 38.242.131.244:8069
- ❌ Error de caché: Docker está usando archivos XML antiguos

## 🚀 Solución Rápida (Desde Windows)

### Método 1: Ejecutar Script PowerShell (Automático)

```powershell
# Desde PowerShell en la carpeta del módulo
cd c:\Repos\Odoo\diprosel-deploy\nubefact_sunat
.\docker-update.ps1
```

### Método 2: Comandos Manuales

#### Paso 1: Identificar el contenedor

```bash
docker ps
```

Busca el contenedor de Odoo, algo como:
- `odoo`
- `odoo_web_1`
- `diprosel_odoo_1`
- etc.

#### Paso 2: Verificar que el módulo esté en el contenedor

```bash
# Reemplaza 'odoo' con tu nombre de contenedor
docker exec odoo ls -la /mnt/extra-addons/nubefact_sunat
```

Deberías ver los archivos del módulo.

#### Paso 3: Actualizar el módulo

```bash
# Reemplaza 'odoo' con tu nombre de contenedor y 'postgres' con tu base de datos
docker exec -u odoo odoo odoo -d postgres -u nubefact_sunat --stop-after-init
```

#### Paso 4: Reiniciar el contenedor

```bash
docker restart odoo
```

#### Paso 5: Limpiar caché del navegador

En tu navegador: `Ctrl + Shift + R`

---

## 🔍 Diagnóstico del Problema

El error dice:
```
El elemento "<xpath expr="//tree">" no se puede localizar
```

Pero los archivos locales ya tienen `<list>`, no `<tree>`. Esto significa que:

1. ✅ Los archivos en tu PC (c:\Repos\Odoo\diprosel-deploy\nubefact_sunat) están **CORRECTOS**
2. ❌ Los archivos en el contenedor Docker están **DESACTUALIZADOS** (caché)

## 📋 Verificación de Archivos

### En tu PC (Local):
```bash
cd c:\Repos\Odoo\diprosel-deploy\nubefact_sunat\views
type account_move_views.xml | findstr "tree"
# No debería encontrar nada
```

### En Docker:
```bash
docker exec odoo cat /mnt/extra-addons/nubefact_sunat/views/account_move_views.xml | grep "tree"
# Si encuentra algo, el volumen no está sincronizado
```

## 🐳 Configuración de Docker-Compose

Tu `docker-compose.yml` debe tener algo como:

```yaml
services:
  web:
    image: odoo:18.0
    volumes:
      - ./addons:/mnt/extra-addons  # <-- Verifica esta línea
    ports:
      - "8069:8069"
```

### Si el volumen NO está montado correctamente:

1. **Copia el módulo al contenedor:**
```bash
docker cp nubefact_sunat odoo:/mnt/extra-addons/
```

2. **Reinicia el contenedor:**
```bash
docker restart odoo
```

3. **Actualiza el módulo:**
```bash
docker exec odoo odoo -d postgres -u nubefact_sunat --stop-after-init
```

---

## 🔧 Solución Definitiva

### Opción A: Con SSH al Servidor (Recomendado)

Si tienes acceso SSH a `38.242.131.244`:

```bash
# 1. Conectarse al servidor
ssh usuario@38.242.131.244

# 2. Ir a la carpeta de Docker
cd /ruta/donde/esta/docker-compose.yml

# 3. Ver contenedores
docker-compose ps

# 4. Desinstalar módulo (desde Odoo web primero)
# Ve a Aplicaciones > NubeFact > Desinstalar

# 5. Actualizar archivos (si están en un volumen)
# Los archivos deberían actualizarse automáticamente

# 6. Reiniciar contenedor
docker-compose restart web

# 7. Instalar módulo de nuevo (desde Odoo web)
# Ve a Aplicaciones > Actualizar Lista > Buscar NubeFact > Instalar
```

### Opción B: Sin SSH (Solo Web)

1. **Desinstalar el módulo:**
   - Ve a `Aplicaciones`
   - Busca "NubeFact"
   - Clic en `Desinstalar`

2. **Espera 5 minutos** (para que el caché expire)

3. **Limpia caché del navegador:**
   - `Ctrl + Shift + Delete`
   - Elimina todo el caché

4. **Actualiza lista de aplicaciones:**
   - `Aplicaciones > ⋮ > Actualizar Lista de Aplicaciones`

5. **Instala de nuevo:**
   - Busca "NubeFact"
   - `Instalar`

---

## 🆘 Si Sigue Sin Funcionar

### Verificar logs del contenedor:

```bash
docker logs odoo --tail 100
```

Busca errores relacionados con `nubefact_sunat`.

### Entrar al contenedor y verificar:

```bash
# Entrar al contenedor
docker exec -it odoo bash

# Ver archivos del módulo
cd /mnt/extra-addons/nubefact_sunat
ls -la

# Ver el contenido del XML
cat views/account_move_views.xml | grep -i tree

# Si dice "tree", los archivos NO se actualizaron
# Si dice "list", los archivos SÍ están actualizados

# Salir
exit
```

### Forzar recarga desde Python:

```bash
docker exec odoo python3 -c "
import odoo
odoo.cli.server.main(['-d', 'postgres', '-u', 'nubefact_sunat', '--stop-after-init'])
"
```

---

## 📞 Pasos Específicos para Tu Caso

Basado en tu error, te recomiendo:

1. **Desinstala el módulo desde la web** (Aplicaciones > NubeFact > Desinstalar)

2. **Ejecuta estos comandos:**
   ```bash
   docker ps
   # Anota el nombre del contenedor de Odoo
   
   docker restart nombre_del_contenedor
   # Espera 15 segundos
   ```

3. **Limpia caché del navegador** (Ctrl + Shift + R)

4. **Vuelve a instalar:**
   - Aplicaciones > Actualizar Lista
   - Buscar "NubeFact"
   - Instalar

5. **Si aún falla**, necesitarás acceso SSH o ejecutar:
   ```bash
   docker exec nombre_contenedor odoo -d nombre_bd --init=nubefact_sunat --stop-after-init
   docker restart nombre_contenedor
   ```

---

## ✅ Verificación Final

Una vez instalado correctamente, debes ver:

1. **Menú nuevo:** `Contabilidad > Configuración > NubeFact`
2. **Botones en facturas:** "Enviar a SUNAT"
3. **Nueva pestaña:** "Facturación Electrónica" en facturas
4. **Sin errores** en la consola del navegador

---

## 🎯 Alternativa: Instalación Limpia

Si nada funciona, reinstala Odoo:

```bash
# Detener contenedores
docker-compose down

# Eliminar volúmenes (CUIDADO: esto elimina datos)
docker-compose down -v

# Reconstruir
docker-compose up -d --build

# Restaurar backup de base de datos
# ...
```

**⚠️ IMPORTANTE:** Haz backup de tu base de datos antes de esto.

---

¿Necesitas ayuda con alguno de estos pasos?
