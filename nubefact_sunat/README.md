# Facturación Electrónica SUNAT - NubeFact

## Descripción

Módulo de Odoo 18 para la integración con NubeFact y envío de comprobantes electrónicos a SUNAT (Superintendencia Nacional de Aduanas y de Administración Tributaria de Perú).

## Características

- ✅ Envío de Facturas Electrónicas a SUNAT
- ✅ Envío de Boletas de Venta
- ✅ Envío de Notas de Crédito
- ✅ Descarga de PDF, XML y CDR (Constancia de Recepción)
- ✅ Seguimiento del estado de envío a SUNAT
- ✅ Configuración de entorno de pruebas y producción
- ✅ Integración con API REST de NubeFact

## Instalación

1. Copie el módulo `nubefact_sunat` en la carpeta de addons de Odoo
2. Actualice la lista de aplicaciones: `Aplicaciones > Actualizar Lista de Aplicaciones`
3. Busque "Facturación Electrónica SUNAT - NubeFact"
4. Haga clic en "Instalar"

## Configuración

### 1. Obtener credenciales de NubeFact

1. Regístrese en [NubeFact.com](https://www.nubefact.com/)
2. Acceda a su panel de control
3. Obtenga su **Token de API** y su **RUC**

### 2. Configurar el módulo en Odoo

1. Vaya a `Contabilidad > Configuración > NubeFact > Configuración`
2. Cree un nuevo registro
3. Complete los siguientes campos:
   - **RUC**: Su número de RUC
   - **Token NubeFact**: El token proporcionado por NubeFact
   - **Entorno**: Seleccione "Pruebas" para desarrollo o "Producción" para uso real
4. Haga clic en "Probar Conexión" para verificar la configuración
5. Guarde el registro

## Uso

### Enviar una Factura a SUNAT

1. Cree y confirme una factura en `Contabilidad > Clientes > Facturas`
2. En la factura confirmada, haga clic en el botón **"Enviar a SUNAT"**
3. El sistema enviará el comprobante a NubeFact/SUNAT
4. El estado se actualizará automáticamente:
   - **No Enviado**: El comprobante aún no se ha enviado
   - **Enviado a SUNAT**: En proceso de validación
   - **Aceptado por SUNAT**: El comprobante fue aceptado ✅
   - **Rechazado por SUNAT**: Hubo un error en el comprobante ❌
   - **Error al Enviar**: Error de conexión o configuración ⚠️

### Descargar documentos

Una vez que el comprobante sea aceptado por SUNAT, podrá:
- **Descargar PDF**: Archivo PDF del comprobante
- **Descargar XML**: Archivo XML firmado
- **Descargar CDR**: Constancia de Recepción de SUNAT

### Ver información de Facturación Electrónica

En cada factura, encontrará una pestaña "Facturación Electrónica" con:
- Estado del envío a SUNAT
- Fecha de envío
- Número de ticket
- Código hash
- Serie y número del comprobante
- Enlaces de descarga
- Respuesta completa de SUNAT
- Mensajes de error (si los hay)

## Filtros de búsqueda

En la lista de facturas, puede filtrar por:
- **Enviados a SUNAT**: Todos los comprobantes enviados
- **Aceptados por SUNAT**: Solo comprobantes aceptados
- **Rechazados por SUNAT**: Solo comprobantes rechazados
- **No Enviados**: Comprobantes pendientes de envío

## Requisitos

- Odoo 18.0
- Módulo `account` (Contabilidad)
- Módulo `l10n_pe` (Localización Peruana)
- Biblioteca Python `requests` (generalmente ya incluida en Odoo)
- Cuenta activa en NubeFact

## Estructura del módulo

```
nubefact_sunat/
├── __init__.py
├── __manifest__.py
├── README.md
├── models/
│   ├── __init__.py
│   ├── nubefact_config.py     # Configuración de credenciales
│   └── account_move.py         # Extensión de facturas
├── views/
│   ├── nubefact_config_views.xml
│   └── account_move_views.xml
└── security/
    └── ir.model.access.csv
```

## Soporte

Para soporte técnico:
- **NubeFact**: https://www.nubefact.com/soporte
- **Documentación API**: Disponible en el panel de NubeFact

## Notas importantes

⚠️ **Entorno de Pruebas vs Producción**
- En modo **Pruebas**: Los comprobantes NO se envían a SUNAT real
- En modo **Producción**: Los comprobantes SÍ se envían a SUNAT

⚠️ **Requisitos de los comprobantes**
- El cliente debe tener un número de documento (RUC o DNI)
- La factura debe estar confirmada (estado "Publicada")
- Los productos deben tener configurados correctamente los impuestos

## Licencia

LGPL-3

## Autor

SSE - Soluciones de Software Empresarial

## Versión

18.0.1.0.0
