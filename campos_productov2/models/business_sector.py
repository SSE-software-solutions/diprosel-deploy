# -*- coding: utf-8 -*-
from odoo import api, fields, models

class BusinessSector(models.Model):
    _name = 'business.sector'
    _description = "Giro de Negocios"

    name = fields.Char(string="Nombre del Giro de Negocios", required=True, help="Nombre del Giro de Negocios")
    sector_image = fields.Binary(string="Imagen del Giro", help="Imagen representativa del Giro de Negocios")
    product_ids = fields.One2many('product.template', 'sector_id', string="Productos")
    product_count = fields.Integer(string='Número de Productos', compute='_compute_product_count', store=True)

    @api.depends('product_ids')
    def _compute_product_count(self):
        """Calcula el número de productos asociados a este giro"""
        for record in self:
            record.product_count = len(record.product_ids)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sector_id = fields.Many2one('business.sector', string='Giro de Negocios', help="Giro de Negocios del Producto")
