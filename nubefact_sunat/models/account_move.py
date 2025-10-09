# -*- coding: utf-8 -*-

import logging
import json
import base64
import requests

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    # Campos de Facturación Electrónica
    l10n_pe_edi_serie = fields.Char(
        string='Serie Electrónica',
        help='Serie para el comprobante electrónico (ej: F001, B001)',
        copy=False
    )
    
    sunat_estado = fields.Selection([
        ('not_sent', 'No Enviado'),
        ('sent', 'Enviado a SUNAT'),
        ('accepted', 'Aceptado por SUNAT'),
        ('rejected', 'Rechazado por SUNAT'),
        ('error', 'Error al Enviar')
    ], string='Estado SUNAT', default='not_sent', copy=False, tracking=True)
    
    sunat_enviado = fields.Boolean(
        string='Enviado a SUNAT',
        default=False,
        copy=False
    )
    
    sunat_fecha_envio = fields.Datetime(
        string='Fecha de Envío SUNAT',
        readonly=True,
        copy=False
    )
    
    sunat_numero_ticket = fields.Char(
        string='Número de Ticket',
        readonly=True,
        copy=False,
        help='Número de ticket generado por NubeFact/SUNAT'
    )
    
    sunat_enlace_pdf = fields.Char(
        string='Enlace PDF',
        readonly=True,
        copy=False
    )
    
    sunat_enlace_xml = fields.Char(
        string='Enlace XML',
        readonly=True,
        copy=False
    )
    
    sunat_enlace_cdr = fields.Char(
        string='Enlace CDR',
        readonly=True,
        copy=False,
        help='Constancia de Recepción de SUNAT'
    )
    
    sunat_codigo_hash = fields.Char(
        string='Código Hash',
        readonly=True,
        copy=False
    )
    
    sunat_response = fields.Text(
        string='Respuesta SUNAT',
        readonly=True,
        copy=False
    )
    
    sunat_error_message = fields.Text(
        string='Mensaje de Error',
        readonly=True,
        copy=False
    )
    
    # Campos adicionales para documentos electrónicos
    serie_comprobante = fields.Char(
        string='Serie',
        compute='_compute_serie_numero',
        store=True
    )
    
    numero_comprobante = fields.Char(
        string='Número',
        compute='_compute_serie_numero',
        store=True
    )
    
    @api.depends('name', 'l10n_pe_edi_serie')
    def _compute_serie_numero(self):
        """Separa el número de factura en Serie y Número"""
        for record in self:
            if record.name and record.name != '/':
                # Formato esperado: SERIE-NUMERO (ej: F001-00000123)
                parts = record.name.split('-')
                if len(parts) >= 2:
                    record.serie_comprobante = parts[0]
                    record.numero_comprobante = parts[1] if len(parts) == 2 else '-'.join(parts[1:])
                elif record.l10n_pe_edi_serie:
                    # Si hay serie configurada pero el name no tiene el formato
                    record.serie_comprobante = record.l10n_pe_edi_serie
                    record.numero_comprobante = record.name
                else:
                    record.serie_comprobante = False
                    record.numero_comprobante = record.name
            else:
                record.serie_comprobante = False
                record.numero_comprobante = False
    
    def _get_or_create_pe_sequence(self, journal, tipo_doc):
        """Obtiene o crea la secuencia correcta para facturas/boletas peruanas"""
        if tipo_doc == '6':  # RUC - Factura
            # Buscar la secuencia de facturas del módulo
            sequence = self.env['ir.sequence'].search([
                ('code', '=', 'account.move.invoice.pe'),
                ('company_id', '=', self.env.company.id)
            ], limit=1)
            
            if not sequence:
                # Si no existe, buscar por nombre
                sequence = self.env.ref('nubefact_sunat.sequence_invoice_pe', raise_if_not_found=False)
            
            if not sequence:
                # Crear secuencia de facturas si no existe
                sequence = self.env['ir.sequence'].sudo().create({
                    'name': 'Facturas Electrónicas PE',
                    'code': 'account.move.invoice.pe',
                    'prefix': 'F001-',
                    'padding': 6,
                    'number_increment': 1,
                    'number_next': 1,
                    'implementation': 'standard',
                    'company_id': self.env.company.id,
                })
                _logger.info(f"✅ Secuencia de Facturas PE creada: {sequence.name}")
        else:  # DNI u otros - Boleta
            # Buscar la secuencia de boletas del módulo
            sequence = self.env['ir.sequence'].search([
                ('code', '=', 'account.move.boleta.pe'),
                ('company_id', '=', self.env.company.id)
            ], limit=1)
            
            if not sequence:
                # Si no existe, buscar por nombre
                sequence = self.env.ref('nubefact_sunat.sequence_boleta_pe', raise_if_not_found=False)
            
            if not sequence:
                # Crear secuencia de boletas si no existe
                sequence = self.env['ir.sequence'].sudo().create({
                    'name': 'Boletas de Venta PE',
                    'code': 'account.move.boleta.pe',
                    'prefix': 'B001-',
                    'padding': 6,
                    'number_increment': 1,
                    'number_next': 1,
                    'implementation': 'standard',
                    'company_id': self.env.company.id,
                })
                _logger.info(f"✅ Secuencia de Boletas PE creada: {sequence.name}")
        
        return sequence
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override para asignar el diario correcto según el tipo de cliente"""
        for vals in vals_list:
            # Solo aplicar para facturas de venta nuevas
            if vals.get('move_type') in ['out_invoice', 'out_refund'] and vals.get('partner_id'):
                # Obtener el partner
                partner = self.env['res.partner'].browse(vals['partner_id'])
                
                # Solo para compañías peruanas
                if self.env.company.country_code == 'PE':
                    # Determinar tipo de documento
                    tipo_doc = self._get_tipo_documento_identidad(partner)
                    
                    # Buscar el diario apropiado solo si no se especificó uno
                    if not vals.get('journal_id'):
                        if tipo_doc == '6':  # RUC - Factura
                            journal = self.env['account.journal'].search([
                                ('name', '=', 'Factura'),
                                ('type', '=', 'sale'),
                                ('company_id', '=', self.env.company.id)
                            ], limit=1)
                        else:  # DNI u otros - Boleta
                            journal = self.env['account.journal'].search([
                                ('name', '=', 'Boleta'),
                                ('type', '=', 'sale'),
                                ('company_id', '=', self.env.company.id)
                            ], limit=1)
                        
                        if journal:
                            vals['journal_id'] = journal.id
                    
                    # Asignar la secuencia correcta del módulo nubefact
                    # Obtener el diario (ya sea del vals o el que acabamos de asignar)
                    journal_id = vals.get('journal_id')
                    if journal_id:
                        journal = self.env['account.journal'].browse(journal_id)
                        # Obtener o crear la secuencia correcta
                        sequence = self._get_or_create_pe_sequence(journal, tipo_doc)
                        
                        # Asignar la secuencia al diario si no la tiene
                        if journal.sequence_id != sequence:
                            journal.sudo().write({'sequence_id': sequence.id})
                            _logger.info(f"✅ Diario {journal.name} actualizado con secuencia {sequence.name}")
        
        return super().create(vals_list)
    
    def _get_tipo_documento_identidad(self, partner):
        """Mapea el tipo de documento de identidad para SUNAT"""
        # Verificar si existe el campo de localización latam
        if hasattr(partner, 'l10n_latam_identification_type_id') and partner.l10n_latam_identification_type_id:
            # Mapeo según códigos SUNAT
            tipo_doc_map = {
                'DNI': '1',
                'RUC': '6',
                'Pasaporte': '7',
                'Carnet de Extranjería': '4',
            }
            return tipo_doc_map.get(partner.l10n_latam_identification_type_id.name, '0')
        
        # Fallback: determinar por el VAT si es RUC (11 dígitos) o DNI (8 dígitos)
        if partner.vat:
            vat_clean = partner.vat.strip()
            
            # RUC: 11 dígitos, empieza con 10 (persona) o 20 (empresa)
            if len(vat_clean) == 11 and (vat_clean.startswith('10') or vat_clean.startswith('20')):
                return '6'  # RUC (tipo de documento SUNAT)
            # DNI: 8 dígitos
            elif len(vat_clean) == 8:
                return '1'  # DNI
            # Carnet de Extranjería: 12 caracteres alfanuméricos
            elif len(vat_clean) == 12:
                return '4'  # Carnet de Extranjería
        
        return '0'  # Sin documento
    
    def _get_tipo_comprobante(self):
        """Retorna el tipo de comprobante según NubeFact: 1=FACTURA, 2=BOLETA, 3=NC, 4=ND"""
        self.ensure_one()
        
        # Mapeo según documentación de NubeFact (valores integer)
        if self.move_type == 'out_invoice':
            # Determinar si es factura (1) o boleta (2) según tipo de documento del cliente
            tipo_doc = self._get_tipo_documento_identidad(self.partner_id)
            if tipo_doc == '6':  # RUC
                return 1  # FACTURA
            else:
                return 2  # BOLETA DE VENTA
        elif self.move_type == 'out_refund':
            return 3  # NOTA DE CRÉDITO
        elif self.move_type == 'in_invoice':
            return 1  # Factura de compra
        elif self.move_type == 'in_refund':
            return 3  # Nota de crédito de compra
        else:
            return 1  # Por defecto factura
    
    def _get_sunat_uom_code(self, uom):
        """
        Mapea la unidad de medida de Odoo al código SUNAT (Catálogo 03)
        """
        if not uom:
            return 'NIU'
        
        # Mapeo de unidades comunes
        uom_map = {
            # Unidades
            'unit': 'NIU',
            'unidad': 'NIU',
            'unidades': 'NIU',
            'units': 'NIU',
            'u': 'NIU',
            
            # Peso
            'kg': 'KGM',
            'kilogramo': 'KGM',
            'kilogramos': 'KGM',
            'g': 'GRM',
            'gramo': 'GRM',
            'gramos': 'GRM',
            'ton': 'TNE',
            'tonelada': 'TNE',
            'lb': 'LBR',
            'libra': 'LBR',
            
            # Longitud
            'm': 'MTR',
            'metro': 'MTR',
            'metros': 'MTR',
            'cm': 'CMT',
            'centimetro': 'CMT',
            'centimetros': 'CMT',
            'mm': 'MMT',
            'milimetro': 'MMT',
            'milimetros': 'MMT',
            
            # Volumen
            'l': 'LTR',
            'litro': 'LTR',
            'litros': 'LTR',
            'ml': 'MLT',
            'mililitro': 'MLT',
            'mililitros': 'MLT',
            'gal': 'GLL',
            'galon': 'GLL',
            
            # Cantidad
            'docena': 'DZN',
            'docenas': 'DZN',
            'caja': 'BX',
            'cajas': 'BX',
            'paquete': 'PK',
            'paquetes': 'PK',
            'pack': 'PK',
            'bolsa': 'BG',
            'bolsas': 'BG',
            
            # Servicios
            'servicio': 'ZZ',
            'servicios': 'ZZ',
            'hora': 'HUR',
            'horas': 'HUR',
            'dia': 'DAY',
            'dias': 'DAY',
            'mes': 'MON',
            'meses': 'MON',
        }
        
        # Normalizar el nombre de la unidad
        uom_name = uom.name.lower().strip()
        
        # Buscar en el mapeo
        return uom_map.get(uom_name, 'NIU')  # Por defecto NIU si no se encuentra
    
    def _prepare_nubefact_invoice_data(self):
        """Prepara los datos de la factura para enviar a NubeFact"""
        self.ensure_one()
        
        # Validaciones
        if not self.partner_id:
            raise UserError(_('La factura debe tener un cliente asignado.'))
        
        if not self.partner_id.vat:
            raise UserError(_('El cliente debe tener un número de documento (RUC/DNI).'))
        
        # Validar que haya líneas de producto
        product_lines = self.invoice_line_ids.filtered(lambda l: l.display_type == 'product')
        if not product_lines:
            raise UserError(_('La factura debe tener al menos un producto o servicio.'))
        
        # Calcular totales separando líneas gravadas, exoneradas e inafectas
        total_gravada = 0.0
        total_exonerada = 0.0
        total_inafecta = 0.0
        total_igv = 0.0
        
        for line in self.invoice_line_ids.filtered(lambda l: l.display_type == 'product'):
            if line.tax_ids:
                # Obtener la tasa del primer impuesto
                tax_rate = line.tax_ids[0].amount if line.tax_ids else 0
                
                if tax_rate > 0:
                    # Línea con IGV (gravada) - tasa mayor a 0%
                    total_gravada += line.price_subtotal
                    total_igv += (line.price_total - line.price_subtotal)
                else:
                    # Línea con impuesto 0% (exonerada)
                    total_exonerada += line.price_subtotal
            else:
                # Línea sin impuestos (inafecta)
                total_inafecta += line.price_subtotal
        
        total = self.amount_total
        
        # Preparar items
        items = []
        for idx, line in enumerate(self.invoice_line_ids.filtered(lambda l: l.display_type == 'product'), start=1):
            # Calcular IGV de la línea
            igv_linea = line.price_total - line.price_subtotal
            
            # Determinar el tipo de afectación del IGV según el impuesto
            tipo_de_igv = 10  # Por defecto: Gravado - Operación Onerosa
            
            if line.tax_ids:
                tax_rate = line.tax_ids[0].amount if line.tax_ids else 0
                
                if tax_rate > 0:
                    # IGV 18% u otro porcentaje mayor a 0
                    tipo_de_igv = 10  # Gravado - Operación Onerosa
                else:
                    # Impuesto con tasa 0% - Exonerado
                    tipo_de_igv = 20  # Exonerado - Operación Onerosa
                    igv_linea = 0  # Asegurar que IGV sea 0
            else:
                # Sin impuestos - Inafecto
                tipo_de_igv = 30  # Inafecto - Operación Onerosa
                igv_linea = 0  # Asegurar que IGV sea 0
            
            item = {
                "unidad_de_medida": self._get_sunat_uom_code(line.product_uom_id),
                "codigo": line.product_id.default_code or str(line.product_id.id),
                "descripcion": line.name[:250],  # Máximo 250 caracteres
                "cantidad": round(line.quantity, 10),
                "valor_unitario": round(line.price_unit, 10),
                "precio_unitario": round(line.price_unit * (1 + (line.tax_ids[0].amount / 100 if line.tax_ids else 0)), 10),
                "descuento": "" if not line.discount else round(line.discount, 2),
                "subtotal": round(line.price_subtotal, 2),
                "tipo_de_igv": tipo_de_igv,
                "igv": round(igv_linea, 2),
                "total": round(line.price_total, 2),
                "anticipo_regularizacion": False,
                "anticipo_documento_serie": "",
                "anticipo_documento_numero": ""
            }
            items.append(item)
        
        # Mapear moneda según documentación (1=SOLES, 2=DÓLARES, 3=EUROS)
        moneda_map = {'PEN': 1, 'USD': 2, 'EUR': 3}
        moneda = moneda_map.get(self.currency_id.name, 1) if self.currency_id else 1
        
        # Validar serie y número
        if not self.serie_comprobante:
            raise UserError(_('No se pudo determinar la serie del comprobante. Verifique la configuración de secuencias.'))
        
        if not self.numero_comprobante:
            raise UserError(_('No se pudo determinar el número del comprobante.'))
        
        # Limpiar el número de comprobante (remover ceros a la izquierda si es necesario)
        numero_limpio = self.numero_comprobante.lstrip('0') or '1'
        try:
            numero = int(numero_limpio)
        except ValueError:
            raise UserError(_('El número de comprobante "%s" no es válido. Debe ser numérico.') % self.numero_comprobante)
        
        # Estructura de datos según documentación oficial de NubeFact
        data = {
            "operacion": "generar_comprobante",
            "tipo_de_comprobante": self._get_tipo_comprobante(),
            "serie": self.serie_comprobante,
            "numero": numero,
            "sunat_transaction": 1,  # 1 = Venta interna
            "cliente_tipo_de_documento": self._get_tipo_documento_identidad(self.partner_id),
            "cliente_numero_de_documento": self.partner_id.vat,
            "cliente_denominacion": self.partner_id.name[:100],
            "cliente_direccion": self.partner_id.street[:100] if self.partner_id.street else "",
            "cliente_email": self.partner_id.email or "",
            "cliente_email_1": "",
            "cliente_email_2": "",
            "fecha_de_emision": self.invoice_date.strftime('%d-%m-%Y') if self.invoice_date else fields.Date.today().strftime('%d-%m-%Y'),
            "fecha_de_vencimiento": self.invoice_date_due.strftime('%d-%m-%Y') if self.invoice_date_due else "",
            "moneda": moneda,
            "tipo_de_cambio": "",
            "porcentaje_de_igv": 18.00,
            "descuento_global": "",
            "total_descuento": "",
            "total_anticipo": "",
            "total_gravada": round(total_gravada, 2) if total_gravada > 0 else "",
            "total_inafecta": round(total_inafecta, 2) if total_inafecta > 0 else "",
            "total_exonerada": round(total_exonerada, 2) if total_exonerada > 0 else "",
            "total_igv": round(total_igv, 2) if total_igv > 0 else "",
            "total_gratuita": "",
            "total_otros_cargos": "",
            "total": round(total, 2),
            "percepcion_tipo": "",
            "percepcion_base_imponible": "",
            "total_percepcion": "",
            "total_incluido_percepcion": "",
            "detraccion": False,
            "observaciones": self.narration or "",
            "documento_que_se_modifica_tipo": "",
            "documento_que_se_modifica_serie": "",
            "documento_que_se_modifica_numero": "",
            "tipo_de_nota_de_credito": "",
            "tipo_de_nota_de_debito": "",
            "enviar_automaticamente_a_la_sunat": True,
            "enviar_automaticamente_al_cliente": False,
            "condiciones_de_pago": "",
            "medio_de_pago": "",
            "placa_vehiculo": "",
            "orden_compra_servicio": "",
            "formato_de_pdf": "",
            "items": items
        }
        
        # Si es nota de crédito, agregar referencia al documento modificado
        if self.move_type == 'out_refund' and self.reversed_entry_id:
            data["documento_que_se_modifica_tipo"] = self.reversed_entry_id._get_tipo_comprobante()
            data["documento_que_se_modifica_serie"] = self.reversed_entry_id.serie_comprobante or ""
            data["documento_que_se_modifica_numero"] = self.reversed_entry_id.numero_comprobante or ""
            data["tipo_de_nota_de_credito"] = "01"  # Anulación de la operación
        
        return data
    
    def action_send_to_sunat(self):
        """Acción para enviar el comprobante a SUNAT mediante NubeFact"""
        self.ensure_one()
        
        # Validaciones previas
        if self.state != 'posted':
            raise UserError(_('Solo se pueden enviar facturas confirmadas.'))
        
        if self.sunat_enviado and self.sunat_estado == 'accepted':
            raise UserError(_('Este comprobante ya fue aceptado por SUNAT. Use "Consultar en SUNAT" para actualizar la información.'))
        
        # Obtener configuración de NubeFact
        config = self.env['nubefact.config'].search([
            ('company_id', '=', self.company_id.id),
            ('active', '=', True)
        ], limit=1)
        
        if not config:
            raise UserError(_('No se ha configurado la conexión con NubeFact. '
                            'Por favor, configure las credenciales en Contabilidad > Configuración > NubeFact.'))
        
        try:
            # Preparar datos según documentación de NubeFact
            invoice_data = self._prepare_nubefact_invoice_data()
            
            # URL de la API de NubeFact (ya incluye el endpoint completo)
            url = config.get_api_url()
            
            # Headers según documentación oficial de NubeFact
            # Authorization solo contiene el token, sin prefijo
            headers = {
                'Authorization': config.token,
                'Content-Type': 'application/json'
            }
            
            _logger.info(f"Enviando factura {self.name} a NubeFact")
            _logger.debug(f"URL: {url}")
            _logger.debug(f"Datos: {json.dumps(invoice_data, indent=2)}")
            
            # Realizar petición POST a NubeFact
            response = requests.post(
                url,
                headers=headers,
                json=invoice_data,
                timeout=30
            )
            
            _logger.info(f"Respuesta de NubeFact: Status {response.status_code}, Body: {response.text}")
            
            # Procesar respuesta
            if response.status_code == 200:
                response_data = response.json()
                
                # Actualizar campos
                self.write({
                    'sunat_enviado': True,
                    'sunat_fecha_envio': fields.Datetime.now(),
                    'sunat_response': json.dumps(response_data, indent=2),
                })
                
                # Verificar si SUNAT aceptó el comprobante
                if response_data.get('aceptada_por_sunat'):
                    self.write({
                        'sunat_estado': 'accepted',
                        'sunat_enlace_pdf': response_data.get('enlace_del_pdf', ''),
                        'sunat_enlace_xml': response_data.get('enlace_del_xml', ''),
                        'sunat_enlace_cdr': response_data.get('enlace_del_cdr', ''),
                        'sunat_codigo_hash': response_data.get('codigo_hash', ''),
                        'sunat_numero_ticket': response_data.get('numero_ticket', ''),
                    })
                    
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': _('Éxito'),
                            'message': _('El comprobante fue aceptado por SUNAT correctamente.'),
                            'type': 'success',
                            'sticky': False,
                        }
                    }
                else:
                    # SUNAT rechazó el comprobante
                    error_msg = response_data.get('sunat_description', '') or response_data.get('errors', '')
                    self.write({
                        'sunat_estado': 'rejected',
                        'sunat_error_message': error_msg,
                    })
                    
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': _('Rechazado por SUNAT'),
                            'message': f"{_('El comprobante fue rechazado')}: {error_msg}",
                            'type': 'warning',
                            'sticky': True,
                        }
                    }
            else:
                # Error en la API
                error_msg = response.text
                self.write({
                    'sunat_estado': 'error',
                    'sunat_error_message': error_msg,
                    'sunat_response': error_msg,
                })
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Error'),
                        'message': f"{_('Error al enviar a NubeFact')}: {error_msg}",
                        'type': 'danger',
                        'sticky': True,
                    }
                }
                
        except Exception as e:
            _logger.error(f"Error al enviar comprobante a SUNAT: {str(e)}", exc_info=True)
            self.write({
                'sunat_estado': 'error',
                'sunat_error_message': str(e),
            })
            
            raise UserError(_('Error al enviar a SUNAT: %s') % str(e))
    
    def action_consultar_sunat(self):
        """Consulta el estado de un comprobante en NubeFact/SUNAT"""
        self.ensure_one()
        
        # Validaciones previas
        if self.state != 'posted':
            raise UserError(_('Solo se pueden consultar facturas confirmadas.'))
        
        # Obtener configuración de NubeFact
        config = self.env['nubefact.config'].search([
            ('company_id', '=', self.company_id.id),
            ('active', '=', True)
        ], limit=1)
        
        if not config:
            raise UserError(_('No se ha configurado la conexión con NubeFact.'))
        
        try:
            # Validar serie y número
            if not self.serie_comprobante:
                raise UserError(_('No se pudo determinar la serie del comprobante.'))
            
            if not self.numero_comprobante:
                raise UserError(_('No se pudo determinar el número del comprobante.'))
            
            # Limpiar el número de comprobante
            numero_limpio = self.numero_comprobante.lstrip('0') or '1'
            try:
                numero = int(numero_limpio)
            except ValueError:
                raise UserError(_('El número de comprobante "%s" no es válido.') % self.numero_comprobante)
            
            # Preparar datos de consulta según documentación
            consulta_data = {
                "operacion": "consultar_comprobante",
                "tipo_de_comprobante": self._get_tipo_comprobante(),
                "serie": self.serie_comprobante,
                "numero": numero
            }
            
            # URL de la API de NubeFact
            url = config.get_api_url()
            
            # Headers según documentación oficial
            headers = {
                'Authorization': config.token,
                'Content-Type': 'application/json'
            }
            
            _logger.info(f"Consultando factura {self.name} en NubeFact")
            
            # Realizar petición
            response = requests.post(
                url,
                headers=headers,
                json=consulta_data,
                timeout=30
            )
            
            _logger.info(f"Respuesta de consulta NubeFact: Status {response.status_code}, Body: {response.text}")
            
            # Procesar respuesta
            if response.status_code == 200:
                response_data = response.json()
                
                # Si el documento existe en NubeFact
                if 'errors' not in response_data or not response_data['errors']:
                    # Actualizar campos con la información de NubeFact
                    self.write({
                        'sunat_enviado': True,
                        'sunat_estado': 'accepted' if response_data.get('aceptada_por_sunat') else 'rejected',
                        'sunat_enlace_pdf': response_data.get('enlace_del_pdf', ''),
                        'sunat_enlace_xml': response_data.get('enlace_del_xml', ''),
                        'sunat_enlace_cdr': response_data.get('enlace_del_cdr', ''),
                        'sunat_codigo_hash': response_data.get('codigo_hash', ''),
                        'sunat_response': json.dumps(response_data, indent=2),
                    })
                    
                    if response_data.get('aceptada_por_sunat'):
                        return {
                            'type': 'ir.actions.client',
                            'tag': 'display_notification',
                            'params': {
                                'title': _('Consulta Exitosa'),
                                'message': _('El comprobante está aceptado por SUNAT. Se han actualizado los enlaces de descarga.'),
                                'type': 'success',
                                'sticky': False,
                            }
                        }
                    else:
                        return {
                            'type': 'ir.actions.client',
                            'tag': 'display_notification',
                            'params': {
                                'title': _('Comprobante Encontrado'),
                                'message': f"{_('Estado')}: {response_data.get('sunat_description', 'Rechazado')}",
                                'type': 'warning',
                                'sticky': True,
                            }
                        }
                else:
                    # El documento no existe en NubeFact
                    error_msg = response_data.get('errors', 'Documento no encontrado')
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': _('Comprobante No Encontrado'),
                            'message': f"{_('Este comprobante no existe en NubeFact')}: {error_msg}",
                            'type': 'warning',
                            'sticky': True,
                        }
                    }
            else:
                error_msg = response.text
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Error'),
                        'message': f"{_('Error al consultar')}: {error_msg}",
                        'type': 'danger',
                        'sticky': True,
                    }
                }
                
        except Exception as e:
            _logger.error(f"Error al consultar comprobante en SUNAT: {str(e)}", exc_info=True)
            raise UserError(_('Error al consultar en SUNAT: %s') % str(e))
    
    def action_download_pdf(self):
        """Descarga el PDF del comprobante desde NubeFact"""
        self.ensure_one()
        
        if not self.sunat_enlace_pdf:
            raise UserError(_('No hay un enlace de PDF disponible para este comprobante.'))
        
        return {
            'type': 'ir.actions.act_url',
            'url': self.sunat_enlace_pdf,
            'target': 'new',
        }
    
    def action_download_xml(self):
        """Descarga el XML del comprobante desde NubeFact"""
        self.ensure_one()
        
        if not self.sunat_enlace_xml:
            raise UserError(_('No hay un enlace de XML disponible para este comprobante.'))
        
        return {
            'type': 'ir.actions.act_url',
            'url': self.sunat_enlace_xml,
            'target': 'new',
        }
    
    def action_download_cdr(self):
        """Descarga el CDR del comprobante desde NubeFact"""
        self.ensure_one()
        
        if not self.sunat_enlace_cdr:
            raise UserError(_('No hay un enlace de CDR disponible para este comprobante.'))
        
        return {
            'type': 'ir.actions.act_url',
            'url': self.sunat_enlace_cdr,
            'target': 'new',
        }
