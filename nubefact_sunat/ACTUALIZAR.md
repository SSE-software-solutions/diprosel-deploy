# Guía de Actualización - Series Formato SUNAT

Esta guía te ayudará a actualizar tu módulo de NubeFact para usar el formato de series correcto de SUNAT.

## ⚠️ IMPORTANTE - Antes de Actualizar

1. **Hacer backup de la base de datos**
2. **Anotar el último número usado** de cada serie (F3/2025/00001 → anotar "1")
3. **Modo de prueba**: Primero probar en un ambiente de desarrollo

## Pasos de Actualización

### 1. Actualizar el Módulo

```bash
# Opción A: Actualizar desde Odoo (Recomendado)
# Ir a: Aplicaciones → Buscar "NubeFact" → Actualizar

# Opción B: Actualizar desde terminal
cd /ruta/a/odoo
./odoo-bin -u nubefact_sunat -d nombre_base_datos --stop-after-init
```

### 2. Verificar Secuencias Creadas

1. Ir a: **Contabilidad → Configuración → Series Electrónicas**
2. Deberías ver las nuevas secuencias:
   - Facturas Electrónicas PE (F001-)
   - Boletas de Venta PE (B001-)
   - Notas de Crédito PE (FC01-)
   - Notas de Débito PE (FD01-)

### 3. Ajustar Numeración Inicial

Si ya tenías comprobantes emitidos en NubeFact, ajusta el correlativo:

**Ejemplo**: Si tu última factura en NubeFact fue F001-000045:

1. Ir a la secuencia "Facturas Electrónicas PE"
2. Editar el campo **"Siguiente Número"**: poner **46**
3. Guardar

Hacer lo mismo para cada tipo de documento (Boletas, NC, ND).

### 4. Configurar Series Personalizadas (Opcional)

Si en NubeFact usas series diferentes (F002, F003, etc.):

#### Para Facturas:
1. Duplicar la secuencia "Facturas Electrónicas PE"
2. Cambiar:
   - **Nombre**: "Facturas Electrónicas PE - F002"
   - **Prefijo**: F002-
   - **Siguiente Número**: Correlativo actual + 1

#### Asignar serie a un diario específico:
1. Ir a: **Contabilidad → Configuración → Diarios**
2. Abrir el diario de ventas
3. En **"Secuencias Dedicadas"** → Marcar la opción
4. Seleccionar tu nueva secuencia para facturas

### 5. Configurar Clientes

Asegúrate de que tus clientes tengan el tipo de documento correcto:

**Empresas (RUC)**:
```
Nombre: ACME SAC
VAT: 20123456789 (11 dígitos, empieza con 20)
→ Se emitirá FACTURA (F001)
```

**Personas (DNI)**:
```
Nombre: Juan Pérez
VAT: 12345678 (8 dígitos)
→ Se emitirá BOLETA (B001)
```

### 6. Probar la Emisión

1. Crear una factura de prueba
2. Seleccionar un cliente con RUC
3. Confirmar la factura
4. **Verificar el número**: Debe ser `F001-000046` (o el correlativo que configuraste)
5. Hacer clic en **"Enviar a SUNAT"**
6. Verificar que NubeFact la acepte

## Migración de Facturas Antiguas

### Si tienes facturas con formato antiguo (F3/2025/00001)

Las facturas antiguas **NO se re-numeran automáticamente**. Solo las nuevas facturas usarán el formato correcto.

Para enviar facturas antiguas a SUNAT:

**Opción 1 (Recomendada)**: Crear nueva factura
1. Cancelar la factura antigua
2. Crear una nueva factura (tendrá el formato correcto)
3. Enviar a SUNAT

**Opción 2**: Re-numerar manualmente (solo si no se ha enviado a SUNAT)
1. Borrar la factura (debe estar en borrador)
2. Crearla nuevamente
3. El nuevo número será con formato SUNAT

## Verificación Final

Checklist de verificación:

- [ ] Las nuevas facturas se numeran como `F001-000001`
- [ ] Las boletas se numeran como `B001-000001`
- [ ] El cliente con RUC recibe Factura (F001)
- [ ] El cliente con DNI recibe Boleta (B001)
- [ ] Se puede enviar correctamente a NubeFact
- [ ] Se reciben los PDFs, XMLs y CDRs

## Problemas Comunes

### ❌ Las facturas siguen con formato antiguo (F3/2025/00001)

**Causa**: El diario de ventas tiene secuencias propias configuradas.

**Solución**:
1. Ir a: **Contabilidad → Configuración → Diarios → Ventas**
2. Pestaña **"Configuración Avanzada"**
3. Si hay secuencias dedicadas, desmarcar y volver a marcar
4. Asignar manualmente la secuencia "Facturas Electrónicas PE"

### ❌ Error: "No se pudo determinar la serie del comprobante"

**Causa**: Las secuencias no están correctamente asociadas.

**Solución**:
```bash
# Reinstalar el módulo para recrear las secuencias
./odoo-bin -u nubefact_sunat -d nombre_bd --stop-after-init
```

### ❌ Todas las facturas usan B001 (Boleta) en lugar de F001

**Causa**: El campo VAT del cliente no está en formato correcto.

**Solución**:
- RUC debe tener exactamente 11 dígitos
- DNI debe tener exactamente 8 dígitos
- Verificar que no haya espacios o guiones en el VAT

## Rollback (Volver Atrás)

Si hay problemas y necesitas volver a la versión anterior:

1. Restaurar el backup de la base de datos
2. Reemplazar el módulo con la versión anterior
3. Reiniciar Odoo

## Soporte

Si necesitas ayuda:
- Revisar el archivo `README.md`
- Revisar logs de Odoo: `/var/log/odoo/odoo-server.log`
- Contactar soporte: soporte@sse.pe

---

**Nota**: Esta actualización es **obligatoria** para poder enviar comprobantes a SUNAT, ya que SUNAT requiere el formato de series específico (4 caracteres) y numeración correlativa de 6 dígitos.

