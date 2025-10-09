# Facturación Electrónica SUNAT - NubeFact

Módulo de integración con NubeFact para envío de comprobantes electrónicos a SUNAT en Odoo 18.

## Características

✅ **Secuencias automáticas** con formato SUNAT (F001-000001, B001-000001)  
✅ **Detección automática** de Factura/Boleta según tipo de documento del cliente  
✅ Envío de Facturas, Boletas, Notas de Crédito y Débito  
✅ Consulta de estado en SUNAT  
✅ Descarga de PDF, XML y CDR  
✅ Registro completo de respuestas de SUNAT  

## Instalación

1. Copiar el módulo a la carpeta de addons de Odoo
2. Actualizar lista de aplicaciones
3. Instalar el módulo "Facturación Electrónica SUNAT - NubeFact"

## Configuración Inicial

### 1. Configurar Credenciales de NubeFact

1. Ir a: **Contabilidad → Configuración → NubeFact**
2. Crear una nueva configuración con:
   - **RUC**: RUC de tu empresa
   - **Token NubeFact**: Token proporcionado por NubeFact
   - **URL API**: URL completa de tu cuenta (ej: `https://api.nubefact.com/api/v1/12345678901/xxxxx`)
3. Hacer clic en **"Probar Conexión"** para verificar

### 2. Configurar Series de Documentos Electrónicos

El módulo crea automáticamente las siguientes series por defecto:
- **F001**: Facturas Electrónicas
- **B001**: Boletas de Venta
- **FC01**: Notas de Crédito
- **FD01**: Notas de Débito

Para modificar o agregar nuevas series:

1. Ir a: **Contabilidad → Configuración → Series Electrónicas**
2. Editar la secuencia deseada
3. Modificar el **Prefijo** (debe ser formato SUNAT: F001, B001, etc.)
4. Configurar el **Siguiente Número** según tu correlativo actual

### 3. Configurar Tipo de Documento en Clientes

Para que el sistema detecte automáticamente si emitir Factura o Boleta:

1. Ir al registro del cliente
2. En la pestaña **"Ventas y Compras"**:
   - Cliente con **RUC** (11 dígitos) → Se emitirá **Factura**
   - Cliente con **DNI** (8 dígitos) → Se emitirá **Boleta**

## Uso

### Enviar Comprobante a SUNAT

1. Crear y confirmar una factura/boleta
2. El sistema asignará automáticamente la serie correcta:
   - Clientes con RUC → Serie F001-000001 (Factura)
   - Clientes con DNI → Serie B001-000001 (Boleta)
3. Hacer clic en **"Enviar a SUNAT"**
4. El sistema enviará el comprobante a NubeFact
5. Verificar el estado en el badge superior derecho

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
