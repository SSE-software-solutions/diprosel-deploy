# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ProductBrand(models.Model):
    _name = 'product.brand'
    _description = "Marca"

    name = fields.Char(string="Nombre de la Marca", required=True, help="Nombre de la Marca")
    brand_image = fields.Binary(string="Imagen de la Marca", help="Imagen representativa de la Marca")
    product_ids = fields.One2many('product.template', 'brand_id', string="Productos")
    product_count = fields.Integer(string='Número de Productos', compute='_compute_product_count', store=True)

    @api.depends('product_ids')
    def _compute_product_count(self):
        for record in self:
            record.product_count = len(record.product_ids)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    brand_id = fields.Many2one('product.brand', string='Marca', help="Marca del Producto")
