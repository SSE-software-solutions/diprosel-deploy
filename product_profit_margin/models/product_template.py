from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    x_profit_percentage = fields.Float(string='Porcentaje de ganancia (%)')

    @api.onchange('x_profit_percentage', 'standard_price')
    def _update_sale_price(self):
        for product in self:
            if product.standard_price > 0 and product.x_profit_percentage >= 0:
                product.list_price = product.standard_price * (1 + (product.x_profit_percentage / 100))

    
    x_pricelist_id = fields.Many2one('product.pricelist', string='Lista de precios')
    x_margin_for_pricelist = fields.Float(string='Margen para lista (%)')

    @api.onchange('x_pricelist_id', 'x_margin_for_pricelist', 'standard_price')
    def _update_pricelist_price(self):
        for product in self:
            if product.x_pricelist_id and product.x_margin_for_pricelist and product.standard_price:
                new_price = product.standard_price * (1 + (product.x_margin_for_pricelist / 100))
                product_variant = product.product_variant_id

                # ✅ Obtener la UoM de compra
                purchase_uom = product.uom_po_id
                min_qty = purchase_uom.factor_inv if purchase_uom and purchase_uom.factor_inv else 1.0

                # Buscar si ya hay una regla
                existing_rule = self.env['product.pricelist.item'].search([
                    ('pricelist_id', '=', product.x_pricelist_id.id),
                    ('product_id', '=', product_variant.id),
                    ('applied_on', '=', '0_product_variant'),
                ], limit=1)

                if existing_rule:
                    existing_rule.fixed_price = new_price
                    existing_rule.min_quantity = min_qty
                else:
                    self.env['product.pricelist.item'].create({
                        'pricelist_id': product.x_pricelist_id.id,
                        'product_id': product_variant.id,
                        'applied_on': '0_product_variant',
                        'compute_price': 'fixed',
                        'fixed_price': new_price,
                        'min_quantity': min_qty,
                    })
