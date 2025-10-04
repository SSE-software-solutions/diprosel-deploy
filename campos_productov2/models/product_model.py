# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ProductModel(models.Model):
    _name = 'product.model'
    _description = "Modelo"

    name = fields.Char(string="Nombre del Modelo", required=True, help="Nombre del Modelo")
    model_image = fields.Binary(string="Imagen del Modelo", help="Imagen representativa del Modelo")
    product_ids = fields.One2many('product.template', 'model_id', string="Productos")
    product_count = fields.Integer(string='Número de Productos', compute='_compute_product_count', store=True)

    @api.depends('product_ids')
    def _compute_product_count(self):
        for record in self:
            record.product_count = len(record.product_ids)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    model_id = fields.Many2one('product.model', string='Modelo', help="Modelo del Producto")
