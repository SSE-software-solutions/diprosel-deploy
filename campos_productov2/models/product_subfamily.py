# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ProductSubFamily(models.Model):
    _name = 'product.subfamily'
    _description = "Sub Familia"

    name = fields.Char(string="Nombre de la Sub Familia", required=True, help="Nombre de la Sub Familia")
    subfamily_image = fields.Binary(string="Imagen de la Sub Familia", help="Imagen representativa de la Sub Familia")
    brand_id = fields.Many2one('product.brand', string='Marca', required=True, help="Marca asociada a esta Sub Familia")
    product_ids = fields.One2many('product.template', 'subfamily_id', string="Productos")
    product_count = fields.Integer(string='Número de Productos', compute='_compute_product_count', store=True)

    @api.depends('product_ids')
    def _compute_product_count(self):
        for record in self:
            record.product_count = len(record.product_ids)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    subfamily_id = fields.Many2one('product.subfamily', string='Sub Familia', help="Sub Familia del Producto")
    brand_id = fields.Many2one('product.brand', string='Marca', help="Marca del Producto")

    @api.onchange('brand_id')
    def _onchange_brand_id(self):
        """Filtra las subfamilias basadas en la marca seleccionada"""
        if self.brand_id:
            return {'domain': {'subfamily_id': [('brand_id', '=', self.brand_id.id)]}}
        else:
            return {'domain': {'subfamily_id': []}}
