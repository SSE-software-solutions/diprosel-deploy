# Facturación Electrónica SUNAT - NubeFact

Módulo de integración con NubeFact para envío de comprobantes electrónicos a SUNAT en Odoo 18.

## Características

✅ **Secuencias automáticas** con formato SUNAT (F001-000001, B001-000001)  
✅ **Diarios pre-configurados** para Factura y Boleta (funciona con POS)  
✅ **Detección automática** de Factura/Boleta según tipo de documento del cliente  
✅ Envío de Facturas, Boletas, Notas de Crédito y Débito  
✅ Consulta de estado en SUNAT  
✅ Descarga de PDF, XML y CDR  
✅ Registro completo de respuestas de SUNAT  
✅ **Compatible con Punto de Venta (POS)**  

## Instalación

1. Copiar el módulo a la carpeta de addons de Odoo
2. Actualizar lista de aplicaciones
3. Instalar el módulo "Facturación Electrónica SUNAT - NubeFact"

**Al instalar, el módulo creará automáticamente:**
- ✅ Diario **"Factura"** (código FE) con secuencia F001-000001
- ✅ Diario **"Boleta"** (código BE) con secuencia B001-000001
- ✅ Secuencias para Notas de Crédito y Débito
- ✅ Menú de configuración de series

## Configuración Inicial

### 1. Configurar Credenciales de NubeFact

1. Ir a: **Contabilidad → Configuración → NubeFact**
2. Crear una nueva configuración con:
   - **RUC**: RUC de tu empresa
   - **Token NubeFact**: Token proporcionado por NubeFact
   - **URL API**: URL completa de tu cuenta (ej: `https://api.nubefact.com/api/v1/12345678901/xxxxx`)
3. Hacer clic en **"Probar Conexión"** para verificar

### 2. Configurar Series de Documentos Electrónicos

El módulo crea automáticamente las siguientes series y diarios:

**Diarios Creados:**
- 📄 **Factura (FE)**: Para clientes con RUC → Serie F001-000001
- 📄 **Boleta (BE)**: Para clientes con DNI → Serie B001-000001

**Secuencias Creadas:**
- **F001**: Facturas Electrónicas
- **B001**: Boletas de Venta
- **FC01**: Notas de Crédito
- **FD01**: Notas de Débito

Para modificar series o correlativos:

1. Ir a: **Contabilidad → Configuración → Series Electrónicas**
2. Editar la secuencia deseada
3. Modificar el **Prefijo** (debe ser formato SUNAT: F001, B001, etc.)
4. Configurar el **Siguiente Número** según tu correlativo actual

**Nota:** Los diarios de Factura y Boleta ya están vinculados a las secuencias correctas, por lo que **funcionan automáticamente en POS y facturación normal**.

### 3. Configurar Tipo de Documento en Clientes

Para que el sistema detecte automáticamente si emitir Factura o Boleta:

1. Ir al registro del cliente
2. En la pestaña **"Ventas y Compras"**:
   - Cliente con **RUC** (11 dígitos) → Se emitirá **Factura**
   - Cliente con **DNI** (8 dígitos) → Se emitirá **Boleta**

## Uso

### Enviar Comprobante a SUNAT (Facturación Normal)

1. Crear y confirmar una factura/boleta desde **Contabilidad → Clientes → Facturas**
2. Seleccionar el diario según el cliente:
   - Clientes con RUC → Diario **"Factura"** → Serie F001-000001
   - Clientes con DNI → Diario **"Boleta"** → Serie B001-000001
3. Hacer clic en **"Enviar a SUNAT"**
4. El sistema enviará el comprobante a NubeFact
5. Verificar el estado en el badge superior derecho

### Enviar Comprobante desde POS

**Requisito:** Instalar también el módulo `custom_pos_journal_v3` para selección automática de diarios en POS.

1. Crear venta en **Punto de Venta**
2. Al facturar:
   - Si cliente tiene **RUC** → Usa diario "Factura" (F001)
   - Si cliente tiene **DNI** → Usa diario "Boleta" (B001)
3. La factura se crea automáticamente con la serie correcta
4. Ir a la factura generada y hacer clic en **"Enviar a SUNAT"**

### Consultar Estado en SUNAT

- Hacer clic en **"Consultar en SUNAT"** para actualizar el estado
- Los enlaces de descarga aparecerán automáticamente

### Descargar Documentos

Una vez aceptado por SUNAT, estarán disponibles:
- **Descargar PDF**: Comprobante impreso
- **Descargar XML**: Archivo XML firmado
- **Descargar CDR**: Constancia de Recepción

### Ver Detalles de Facturación Electrónica

Ir a la pestaña **"Facturación Electrónica"** para ver:
- Estado de envío y respuesta de SUNAT
- Serie y número del comprobante
- Enlaces de descarga
- Mensajes de error (si los hay)

## Formato de Series SUNAT

### Facturas
- **F001**, **F002**, **F003**, etc.

### Boletas de Venta
- **B001**, **B002**, **B003**, etc.

### Notas de Crédito
- **FC01**, **FC02** (Notas de crédito de facturas)
- **BC01**, **BC02** (Notas de crédito de boletas)

### Notas de Débito
- **FD01**, **FD02** (Notas de débito de facturas)
- **BD01**, **BD02** (Notas de débito de boletas)

## Detección Automática de Tipo de Comprobante

El módulo detecta automáticamente el tipo de comprobante a emitir:

| Tipo de Documento Cliente | Comprobante | Serie |
|---------------------------|-------------|-------|
| RUC (11 dígitos)          | Factura     | F001  |
| DNI (8 dígitos)           | Boleta      | B001  |
| Otros                     | Boleta      | B001  |

## Estados de SUNAT

- 🔵 **No Enviado**: Comprobante no ha sido enviado
- 🟡 **Enviado a SUNAT**: Enviado pero pendiente de confirmación
- 🟢 **Aceptado por SUNAT**: Comprobante válido y aceptado
- 🔴 **Rechazado por SUNAT**: Revisar mensaje de error
- ⚫ **Error al Enviar**: Error en la comunicación

## Integración con Punto de Venta (POS)

### Módulos Necesarios

Para que funcione correctamente con POS, necesitas **ambos módulos**:

1. ✅ **nubefact_sunat** (este módulo) - Crea diarios y secuencias
2. ✅ **custom_pos_journal_v3** - Selecciona automáticamente el diario según cliente

### Flujo Completo en POS

```
Cliente entra al POS
    ↓
Cliente tiene RUC?
    ├─ SÍ  → custom_pos_journal_v3 selecciona diario "Factura"
    │         ↓
    │         Diario "Factura" usa secuencia F001-000001
    │         ↓
    │         nubefact_sunat envía a SUNAT
    │
    └─ NO  → custom_pos_journal_v3 selecciona diario "Boleta"
              ↓
              Diario "Boleta" usa secuencia B001-000001
              ↓
              nubefact_sunat envía a SUNAT
```

### Verificación de Configuración

Después de instalar ambos módulos:

1. Ir a: **Contabilidad → Configuración → Diarios**
2. Verificar que existan:
   - ✅ Diario **"Factura"** (código FE)
   - ✅ Diario **"Boleta"** (código BE)
3. Abrir cada diario y verificar en **"Configuración Avanzada"**:
   - Debe tener secuencia configurada
   - El prefijo debe ser F001- o B001- respectivamente

## Solución de Problemas

### Error: "No se pudo determinar la serie del comprobante"

**Solución**: Verificar que las secuencias estén correctamente configuradas en **Contabilidad → Configuración → Series Electrónicas**

### Error de autenticación con NubeFact

**Solución**: 
1. Verificar el Token en la configuración de NubeFact
2. Verificar que la URL sea la correcta
3. Usar el botón **"Probar Conexión"** para diagnóstico

### Las facturas se numeran con formato antiguo (F3/2025/00001)

**Solución**: 
1. Actualizar el módulo a la última versión
2. Verificar que las secuencias PE estén activas
3. Reiniciar el servicio de Odoo

### Cliente con RUC recibe Boleta en lugar de Factura

**Solución**:
1. Verificar que el campo VAT/RUC del cliente tenga exactamente 11 dígitos
2. Verificar que el RUC comience con 10 o 20
3. El sistema detecta automáticamente según la longitud

## Soporte

Para soporte técnico:
- Email: soporte@sse.pe
- NubeFact: https://www.nubefact.com/soporte

## Licencia

LGPL-3

---

**Versión**: 18.0.1.0.0  
**Autor**: SSE  
**Compatible con**: Odoo 18.0
