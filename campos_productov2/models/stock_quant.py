# -*- coding: utf-8 -*-
from odoo import fields, models


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    sector_id = fields.Many2one(related='product_id.sector_id', string='Business Sector', store=True, readonly=True,
                                help="Sector of the product")
