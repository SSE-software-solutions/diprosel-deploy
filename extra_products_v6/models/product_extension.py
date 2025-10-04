from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Primera columna
    negocio = fields.Many2one('product.business', string='Negocio')
    sub_negocio = fields.Many2one('product.subbusiness', string='Sub Negocio')
    familia = fields.Many2one('product.family', string='Familia')
    categoria_productos = fields.Many2one('product.products.category', string='Categoría Productos', index=True)
    sub_categoria_productos = fields.Many2one(
        'product.sub.category',
        string='Sub Categoría',
        domain="[('categoria_productos', '=', categoria_productos)]",
        index=True
    )
    presentacion = fields.Many2one('product.presentation', string='Presentación')
    tier = fields.Many2one('product.tier', string='Tier')

    # Segunda columna
    condicion_almacenaje = fields.Many2one('product.storage.condition', string='Condición de Almacenaje')
    grupo_articulo = fields.Many2one('product.article.group', string='Grupo de Artículo')
    conversion_paleta = fields.Integer(string='Conversión de Paleta')
    cama_conversion = fields.Integer(string='Cama Conversión')
    unidades_por_nivel = fields.Integer(string='Unidades por Nivel')
    tiempo_vida_dias = fields.Integer(string='Tiempo de Vida (Días)')
    
    # Campo calculado para el tiempo de vida en meses
    tiempo_vida_en_meses = fields.Float(
        string='Tiempo de Vida (Meses)',
        compute='_compute_tiempo_vida_en_meses',
        store=True
    )

    @api.depends('tiempo_vida_dias')
    def _compute_tiempo_vida_en_meses(self):
        for record in self:
            record.tiempo_vida_en_meses = record.tiempo_vida_dias / 30 if record.tiempo_vida_dias else 0

    @api.onchange('categoria_productos')
    def _onchange_categoria_productos(self):
        """ Limita las subcategorías disponibles según la categoría seleccionada """
        if self.categoria_productos:
            return {'domain': {'sub_categoria_productos': [('categoria_productos', '=', self.categoria_productos.id)]}}


class ProductProductsCategory(models.Model):
    _name = 'product.products.category'
    _description = 'Product Category'

    name = fields.Char(string='Nombre de la Categoría', required=True)
    description = fields.Text(string='Descripción')
    sub_category_ids = fields.One2many('product.sub.category', 'categoria_productos', string='Sub Categorías')


class ProductSubCategory(models.Model):
    _name = 'product.sub.category'
    _description = 'Sub Category'

    name = fields.Char(string="Nombre de la Sub Categoría", required=True)
    categoria_productos = fields.Many2one(
        'product.products.category',
        string="Categoría Productos",
        required=True
    )


class ProductFamily(models.Model):
    _name = 'product.family'
    _description = 'Product Family'

    name = fields.Char(string='Nombre de la Familia', required=True)


class ProductPresentation(models.Model):
    _name = 'product.presentation'
    _description = 'Product Presentation'

    name = fields.Char(string='Presentación', required=True)


class ProductStorageCondition(models.Model):
    _name = 'product.storage.condition'
    _description = 'Storage Condition'

    name = fields.Char(string='Condición de Almacenaje', required=True)


class ProductArticleGroup(models.Model):
    _name = 'product.article.group'
    _description = 'Article Group'

    name = fields.Char(string='Grupo de Artículo', required=True)


class Tier(models.Model):
    _name = 'product.tier'
    _description = 'Tier'

    name = fields.Char(string='Nombre de tier', required=True)


class ProductBusiness(models.Model):
    _name = 'product.business'
    _description = 'Business'

    name = fields.Char(string="Nombre del Negocio", required=True)


class ProductSubBusiness(models.Model):
    _name = 'product.subbusiness'
    _description = 'Sub Business'

    name = fields.Char(string="Nombre del Sub Negocio", required=True)
