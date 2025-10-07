# Guía de Configuración - NubeFact SUNAT

## Paso a Paso para Configurar el Módulo

### 1. Registrarse en NubeFact

1. Visite https://www.nubefact.com/
2. Haga clic en "Prueba Gratis" o "Registro"
3. Complete el formulario con:
   - RUC de su empresa
   - Datos de contacto
   - Email
4. Confirme su cuenta por email

### 2. Obtener el Token de API

1. Inicie sesión en su cuenta de NubeFact
2. Vaya a `Configuración > API / Integración`
3. Copie su **Token de Autorización**
4. Guarde este token en un lugar seguro

### 3. Instalar el Módulo en Odoo

```bash
# Si está trabajando desde terminal
cd /ruta/a/odoo/addons
# El módulo ya debería estar en la carpeta
```

1. Reinicie el servidor de Odoo:
   ```bash
   # Linux/Mac
   ./odoo-bin -c odoo.conf -u all
   
   # Windows
   python odoo-bin -c odoo.conf -u all
   ```

2. O desde la interfaz:
   - Vaya a `Aplicaciones > Actualizar Lista de Aplicaciones`
   - Busque "NubeFact"
   - Haga clic en `Instalar`

### 4. Configurar Credenciales en Odoo

#### Opción A: Desde el Menú de Configuración

1. Vaya a `Contabilidad > Configuración > NubeFact > Configuración`
2. Haga clic en `Crear`
3. Complete:
   - **Compañía**: Se selecciona automáticamente
   - **RUC**: Su RUC (ej: 20123456789)
   - **Token NubeFact**: Pegue el token obtenido
   - **Entorno**: Seleccione `Pruebas` para empezar
4. Haga clic en `Guardar`
5. Haga clic en `Probar Conexión`

#### Ejemplo de Configuración

```
Compañía: Mi Empresa S.A.C.
RUC: 20123456789
Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... (su token real)
Entorno: Pruebas
```

### 5. Verificar la Configuración

Si la prueba de conexión es exitosa, verá:
- ✅ Estado de Conexión: **Exitosa**
- ✅ Mensaje: "Conexión exitosa con NubeFact"

Si hay un error:
- ❌ Verifique que el Token sea correcto
- ❌ Verifique su conexión a Internet
- ❌ Verifique que su cuenta de NubeFact esté activa

## Configuración de Diarios Contables

Para que el sistema identifique correctamente si debe emitir Factura o Boleta:

### 1. Configurar Tipos de Identificación

1. Vaya a `Contactos`
2. Para clientes con **RUC**:
   - Campo `Tipo de Identificación`: RUC
   - Campo `RUC`: 20XXXXXXXXX
3. Para clientes con **DNI**:
   - Campo `Tipo de Identificación`: DNI
   - Campo `DNI`: 12345678

### 2. Configurar Secuencias de Facturas

1. Vaya a `Contabilidad > Configuración > Diarios`
2. Seleccione su diario de ventas (ej: "Facturas de Clientes")
3. Configure la secuencia:
   - **Serie**: F001, B001, etc.
   - **Formato**: F001-%(range_y)s-%(y)s-%(seq)s
   - Ejemplo de numeración: F001-2025-00001

## Preparar su Primera Factura

### Requisitos previos

1. **Cliente configurado correctamente:**
   ```
   Nombre: Cliente de Prueba S.A.C.
   Tipo de Documento: RUC
   RUC: 20987654321
   Dirección: Av. Principal 123, Lima
   Email: cliente@ejemplo.com (opcional)
   ```

2. **Producto con impuestos:**
   ```
   Nombre: Producto de Prueba
   Precio: 100.00
   Impuesto: IGV 18%
   ```

### Crear y Enviar Factura

1. Vaya a `Contabilidad > Clientes > Facturas`
2. Haga clic en `Crear`
3. Complete:
   - **Cliente**: Seleccione el cliente
   - **Fecha de Factura**: Hoy
   - **Productos**: Agregue el producto
4. Haga clic en `Confirmar`
5. Una vez confirmada, haga clic en **`Enviar a SUNAT`**
6. Espere la respuesta (puede tardar 5-10 segundos)
7. Si es aceptada, verá:
   - Estado SUNAT: **Aceptado por SUNAT** ✅
   - Aparecerán los botones de descarga de PDF, XML y CDR

## Solución de Problemas Comunes

### Error: "No se ha configurado la conexión con NubeFact"
**Solución:** Configure las credenciales en `Contabilidad > Configuración > NubeFact`

### Error: "El cliente debe tener un número de documento"
**Solución:** Asigne un RUC o DNI al cliente en la ficha del contacto

### Error: "Solo se pueden enviar facturas confirmadas"
**Solución:** Confirme la factura antes de enviarla (botón "Confirmar")

### Error: Rechazado por SUNAT
**Posibles causas:**
- RUC del cliente inválido
- Fecha de emisión incorrecta
- Productos sin impuestos configurados
- Numeración duplicada

**Solución:** Revise el mensaje de error en la pestaña "Facturación Electrónica"

### Error de Conexión
**Solución:**
1. Verifique su conexión a Internet
2. Verifique que el token sea correcto
3. Pruebe la conexión desde `Configuración NubeFact`

## Cambiar de Pruebas a Producción

### ⚠️ IMPORTANTE
Antes de cambiar a producción:
1. ✅ Pruebe exhaustivamente en modo Pruebas
2. ✅ Verifique que todos los comprobantes se generen correctamente
3. ✅ Asegúrese de que su cuenta de NubeFact esté activa en producción
4. ✅ Haga un respaldo de su base de datos

### Pasos para cambiar a Producción

1. Vaya a `Contabilidad > Configuración > NubeFact > Configuración`
2. Edite su configuración
3. Cambie **Entorno** de `Pruebas` a `Producción`
4. Haga clic en `Guardar`
5. Haga clic en `Probar Conexión` para verificar

### Después del cambio

- ✅ Los comprobantes se enviarán a SUNAT real
- ✅ Se generarán documentos válidos fiscalmente
- ✅ Los clientes recibirán comprobantes válidos

## Mantenimiento

### Revisar Estado de Envíos

1. Vaya a `Contabilidad > Clientes > Facturas`
2. Use los filtros:
   - **Aceptados por SUNAT**: Ver comprobantes exitosos
   - **Rechazados por SUNAT**: Ver errores
   - **No Enviados**: Ver pendientes

### Monitorear Conexión

Periódicamente:
1. Vaya a `Configuración NubeFact`
2. Haga clic en `Probar Conexión`
3. Verifique que la conexión sea exitosa

## Contacto y Soporte

### Soporte NubeFact
- Web: https://www.nubefact.com/soporte
- Email: soporte@nubefact.com
- Teléfono: (01) 468-3535
- Sistema de Tickets: Disponible en su panel

### Documentación API
- Disponible en su cuenta de NubeFact
- Sección: Integración > Documentación

## Recursos Adicionales

- Manual de usuario de NubeFact
- FAQ de SUNAT sobre facturación electrónica
- Normativa vigente de comprobantes electrónicos

---

**Última actualización:** Octubre 2025  
**Versión del módulo:** 18.0.1.0.0
