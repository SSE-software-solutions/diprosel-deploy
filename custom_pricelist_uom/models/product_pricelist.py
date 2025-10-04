from odoo import api, fields, models


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    @api.onchange('product_tmpl_id', 'pricelist_id')
    def _onchange_product_tmpl_id(self):
        """Actualiza automáticamente la cantidad mínima en función del UoM master si la lista de precios es 'Mayorista'."""
        if self.product_tmpl_id and self.pricelist_id:
            # Verificar si la lista de precios es "Mayorista"
            if "Mayorista" in self.pricelist_id.name:  # Puedes ajustar según tu lógica
                # Obtener la unidad de medida de compra del producto
                purchase_uom = self.product_tmpl_id.uom_po_id

                if purchase_uom and purchase_uom.factor_inv:  # factor_inv = cantidad base (e.g., 12 para un paquete de 12)
                    self.min_quantity = purchase_uom.factor_inv  # Asignar el valor de la UoM como cantidad mínima
                else:
                    self.min_quantity = 0  # Default a 0 si no hay UoM definida
            else:
                # Si no es "Mayorista", no establecer cantidad mínima
                self.min_quantity = 0
