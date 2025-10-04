# -*- coding: utf-8 -*-
from odoo import fields, models, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sector_id = fields.Many2one('business.sector', string='Giro de Negocios', help="Giro de Negocios del Producto")
    line_id = fields.Many2one('product.line', string='Línea de Producto', help="Línea de Producto del Producto")
    model_id = fields.Many2one('product.model', string='Modelo', help="Modelo del Producto")
    brand_id = fields.Many2one('product.brand', string='Marca', help="Marca del Producto")
    barcode_2 = fields.Char(string='Código de Barra 2', help="Código de Barra adicional para el producto")
    subfamily_id = fields.Many2one(
        'product.subfamily', 
        string='Sub Familia', 
        help="Sub Familia del Producto",
        domain="[('brand_id', '=', brand_id)]"  # Filtra subfamilias según la marca seleccionada
    )

    @api.onchange('brand_id')
    def _onchange_brand_id(self):
        """Limpiar subfamilia cuando se cambia la marca"""
        if not self.brand_id:
            self.subfamily_id = False
