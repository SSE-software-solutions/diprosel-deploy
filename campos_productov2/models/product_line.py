# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ProductLine(models.Model):
    _name = 'product.line'
    _description = "Línea de Producto"

    name = fields.Char(string="Nombre de la Línea de Producto", required=True, help="Nombre de la Línea de Producto")
    line_image = fields.Binary(string="Imagen de la Línea", help="Imagen representativa de la Línea de Producto")
    product_ids = fields.One2many('product.template', 'line_id', string="Productos")
    product_count = fields.Integer(string='Número de Productos', compute='_compute_product_count', store=True)

    @api.depends('product_ids')
    def _compute_product_count(self):
        for record in self:
            record.product_count = len(record.product_ids)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    line_id = fields.Many2one('product.line', string='Línea de Producto', help="Línea de Producto del Producto")
