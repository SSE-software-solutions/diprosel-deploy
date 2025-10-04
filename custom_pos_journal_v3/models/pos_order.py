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
            _logger.error("El cliente %s no tiene un tipo de identificación configurado.", self.partner_id.name)
            raise ValueError("El cliente no tiene un tipo de identificación configurado.")

        # Selecciona el diario según el ID del tipo de identificación
        if identification_type.id == 4:  # RUC
            journal = self.env['account.journal'].search([('name', '=', 'Factura')], limit=1)
            _logger.info("Cliente con RUC. Diario asignado: Factura (ID: %s)", journal.id if journal else "No encontrado")
        elif identification_type.id == 5:  # DNI
            journal = self.env['account.journal'].search([('name', '=', 'Boleta')], limit=1)
            _logger.info("Cliente con DNI. Diario asignado: Boleta (ID: %s)", journal.id if journal else "No encontrado")
        else:
            _logger.error("Tipo de identificación no soportado para el cliente: %s", self.partner_id.name)
            raise ValueError("Tipo de identificación no soportado para el cliente.")

        # Valida que se haya encontrado un diario
        if not journal:
            _logger.error("No se encontró un diario válido para el cliente: %s", self.partner_id.name)
            raise ValueError("No se encontró un diario válido para el cliente.")

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

                if identification_type.id == 4:  # RUC
                    journal = self.env['account.journal'].search([('name', '=', 'Factura')], limit=1)
                elif identification_type.id == 5:  # DNI
                    journal = self.env['account.journal'].search([('name', '=', 'Boleta')], limit=1)
                else:
                    journal = None

                if journal:
                    order.invoice_id.write({'journal_id': journal.id})
                    _logger.info("Factura actualizada con el diario: %s (ID: %s)", journal.name, journal.id)
                else:
                    _logger.error("No se encontró un diario válido para el cliente en el pedido: %s", order.name)

        return res
