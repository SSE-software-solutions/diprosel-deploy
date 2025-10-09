# Integración con Punto de Venta (POS)

## 🎯 Resumen

Este módulo **SÍ funciona con POS**, pero necesitas **2 módulos** trabajando juntos:

| Módulo | Función |
|--------|---------|
| `nubefact_sunat` | Crea diarios "Factura" y "Boleta" con secuencias SUNAT correctas |
| `custom_pos_journal_v3` | Selecciona automáticamente el diario según el tipo de documento del cliente |

## 📋 Checklist de Instalación

- [ ] Instalar `nubefact_sunat`
- [ ] Instalar `custom_pos_journal_v3`
- [ ] Configurar credenciales de NubeFact
- [ ] Verificar que se crearon los diarios "Factura" y "Boleta"
- [ ] Probar en POS con cliente RUC (debe usar Factura)
- [ ] Probar en POS con cliente DNI (debe usar Boleta)

## 🔄 Flujo de Trabajo

### 1. Venta en POS

```
🛒 Venta en POS
    ↓
👤 Seleccionar Cliente
    ↓
📄 Facturar
    ↓
🤖 custom_pos_journal_v3 detecta:
    • RUC → Diario "Factura"
    • DNI → Diario "Boleta"
    ↓
📝 Factura creada con serie correcta:
    • Factura: F001-000001
    • Boleta: B001-000001
```

### 2. Envío a SUNAT

```
📋 Ir a la factura generada
    ↓
🚀 Click en "Enviar a SUNAT"
    ↓
📡 nubefact_sunat envía a NubeFact
    ↓
✅ Recibe PDF, XML, CDR
```

## ⚙️ Configuración Automática

Al instalar `nubefact_sunat`, se crean automáticamente:

### Diario: Factura (FE)
```
Nombre: Factura
Código: FE
Tipo: Venta
Secuencia: F001-000001
```

### Diario: Boleta (BE)
```
Nombre: Boleta
Código: BE
Tipo: Venta
Secuencia: B001-000001
```

## ✅ Verificación de Instalación

### Paso 1: Verificar Diarios

1. Ir a: **Contabilidad → Configuración → Diarios**
2. Buscar:
   - ✅ Diario **"Factura"** (código FE)
   - ✅ Diario **"Boleta"** (código BE)

### Paso 2: Verificar Secuencias

1. Abrir diario **"Factura"**
2. Ir a pestaña **"Configuración Avanzada"**
3. Verificar:
   - ✅ Tiene secuencia configurada
   - ✅ El siguiente número debe empezar en tu correlativo actual

### Paso 3: Probar en POS

1. Abrir **Punto de Venta**
2. Crear venta para cliente con **RUC**
3. Facturar
4. Verificar que la factura se cree con serie **F001-**
5. Repetir con cliente **DNI** → Debe crear **B001-**

## 🚨 Problemas Comunes

### ❌ El POS no selecciona el diario correcto

**Causa:** El módulo `custom_pos_journal_v3` no está instalado.

**Solución:**
```bash
# Instalar custom_pos_journal_v3
cd /ruta/odoo
./odoo-bin -u custom_pos_journal_v3 -d tu_base_datos
```

### ❌ Las facturas desde POS usan serie incorrecta

**Causa:** Los diarios no tienen las secuencias correctas.

**Solución:**
1. Ir a: **Contabilidad → Configuración → Diarios**
2. Editar diario **"Factura"**
3. En **"Configuración Avanzada"**:
   - Verificar que la secuencia tenga prefijo **F001-**
4. Hacer lo mismo para diario **"Boleta"** → Debe ser **B001-**

### ❌ Los diarios "Factura" y "Boleta" no existen

**Causa:** El hook de instalación no se ejecutó.

**Solución:**
```bash
# Reinstalar el módulo
./odoo-bin -u nubefact_sunat -d tu_base_datos --stop-after-init
```

Si persiste el problema, crear los diarios manualmente:

#### Crear Diario "Factura"
1. Ir a: **Contabilidad → Configuración → Diarios → Nuevo**
2. Llenar:
   - **Nombre**: Factura
   - **Código**: FE
   - **Tipo**: Venta
3. En **"Configuración Avanzada"**:
   - Marcar **"Secuencias Dedicadas"**
   - En **"Secuencia de facturas"**: Seleccionar **"Facturas Electrónicas PE"**

#### Crear Diario "Boleta"
1. Repetir los pasos anteriores con:
   - **Nombre**: Boleta
   - **Código**: BE
   - **Secuencia de facturas**: **"Boletas de Venta PE"**

## 📊 Ejemplo Práctico

### Cliente Empresa (RUC)

```
Cliente: ACME SAC
RUC: 20123456789
    ↓
Venta en POS: S/ 118.00
    ↓
custom_pos_journal_v3 → Diario "Factura"
    ↓
Factura: F001-000001
    ↓
Enviar a SUNAT → ✅ Aceptado
```

### Cliente Persona (DNI)

```
Cliente: Juan Pérez
DNI: 12345678
    ↓
Venta en POS: S/ 50.00
    ↓
custom_pos_journal_v3 → Diario "Boleta"
    ↓
Boleta: B001-000001
    ↓
Enviar a SUNAT → ✅ Aceptado
```

## 🎓 Preguntas Frecuentes

### ¿Necesito `custom_pos_journal_v3` si solo uso facturas normales?

**No.** Solo es necesario si usas el Punto de Venta (POS).

### ¿Puedo usar series diferentes para POS y facturación normal?

**Sí.** Puedes crear diarios adicionales:
- Factura POS → F002
- Factura Normal → F001

### ¿Los diarios se crean para todas las compañías?

**Sí**, pero solo para compañías peruanas (country_code = 'PE').

### ¿Puedo cambiar los códigos FE y BE por otros?

**Sí**, pero asegúrate de que sean únicos y no conflictivos con otros diarios.

## 🔗 Documentación Relacionada

- [README.md](README.md) - Documentación completa
- [ACTUALIZAR.md](ACTUALIZAR.md) - Guía de actualización
- [CONFIGURACION.md](../nubefact_sunat/CONFIGURACION.md) - Configuración de NubeFact

---

**Versión**: 18.0.1.0.0  
**Compatible con**: Odoo 18.0 + POS  
**Autor**: SSE

