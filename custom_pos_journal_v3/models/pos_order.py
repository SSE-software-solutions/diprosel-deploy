from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = "pos.order"

    def _prepare_invoice_vals(self):
        """
        Sobrescribe la preparación de valores para la factura, asignando
        dinámicamente el diario según el tipo de identificación del cliente.
        """
        vals = super(PosOrder, self)._prepare_invoice_vals()

        # Verifica si el cliente tiene un tipo de identificación asignado
        identification_type = self.partner_id.l10n_latam_identification_type_id

        if not identification_type:
            _logger.warning("El cliente %s no tiene un tipo de identificación. Usando diario por defecto.", self.partner_id.name)
            return vals

        # Determinar el nombre del tipo de documento
        tipo_doc_name = identification_type.name if identification_type else ''
        
        # Buscar diario según el tipo de documento
        journal = False
        
        if 'RUC' in tipo_doc_name.upper():
            # Buscar diario para facturas (RUC)
            # Primero por nombre exacto, luego por nombre parcial, luego por tipo
            journal = self.env['account.journal'].search([
                ('name', '=', 'Factura'),
                ('type', '=', 'sale')
            ], limit=1)
            
            if not journal:
                journal = self.env['account.journal'].search([
                    ('name', 'ilike', 'Factura'),
                    ('type', '=', 'sale')
                ], limit=1)
            
            _logger.info("Cliente con RUC. Diario asignado: %s (ID: %s)", journal.name if journal else "No encontrado", journal.id if journal else "N/A")
            
        elif 'DNI' in tipo_doc_name.upper() or 'IDENTIDAD' in tipo_doc_name.upper():
            # Buscar diario para boletas (DNI)
            journal = self.env['account.journal'].search([
                ('name', '=', 'Boleta'),
                ('type', '=', 'sale')
            ], limit=1)
            
            if not journal:
                journal = self.env['account.journal'].search([
                    ('name', 'ilike', 'Boleta'),
                    ('type', '=', 'sale')
                ], limit=1)
            
            _logger.info("Cliente con DNI. Diario asignado: %s (ID: %s)", journal.name if journal else "No encontrado", journal.id if journal else "N/A")
        
        # Si no se encontró diario específico, usar el primero de ventas disponible
        if not journal:
            journal = self.env['account.journal'].search([
                ('type', '=', 'sale')
            ], limit=1)
            _logger.warning("No se encontró diario específico. Usando diario de ventas: %s", journal.name if journal else "Ninguno")

        # Valida que se haya encontrado un diario
        if not journal:
            _logger.error("No se encontró ningún diario de ventas para el cliente: %s", self.partner_id.name)
            raise ValueError("No se encontró un diario válido para el cliente. Configure al menos un diario de ventas en Contabilidad > Configuración > Diarios.")

        # Asigna el diario en los valores de la factura
        vals['journal_id'] = journal.id
        return vals

    def action_pos_order_invoice(self):
        """
        Genera la factura y asegura que el diario dinámico se respete.
        """
        res = super(PosOrder, self).action_pos_order_invoice()

        for order in self:
            if order.invoice_id:
                identification_type = order.partner_id.l10n_latam_identification_type_id
                
                if not identification_type:
                    continue
                
                tipo_doc_name = identification_type.name if identification_type else ''
                journal = False

                if 'RUC' in tipo_doc_name.upper():
                    journal = self.env['account.journal'].search([
                        ('name', 'ilike', 'Factura'),
                        ('type', '=', 'sale')
                    ], limit=1)
                elif 'DNI' in tipo_doc_name.upper():
                    journal = self.env['account.journal'].search([
                        ('name', 'ilike', 'Boleta'),
                        ('type', '=', 'sale')
                    ], limit=1)

                if journal:
                    order.invoice_id.write({'journal_id': journal.id})
                    _logger.info("Factura actualizada con el diario: %s (ID: %s)", journal.name, journal.id)
                else:
                    _logger.warning("No se encontró un diario específico para el pedido: %s", order.name)

        return res
