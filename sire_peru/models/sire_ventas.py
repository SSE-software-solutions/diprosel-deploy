from odoo import models, fields

class SIREVentas(models.Model):
    _name = 'sire.ventas'
    _description = 'Registro de Ventas para SIRE'

    periodo_id = fields.Many2one('sire.periodo', string="Período", required=True, ondelete="cascade")
    fecha_emision = fields.Date(string="Fecha de Emisión", required=True)
    tipo_comprobante = fields.Selection([
        ('01', 'Factura'),
        ('out_invoice', 'Factura de Venta'),
        ('entry', 'Boleta de Venta'),
        ('07', 'Nota de Crédito'),
        ('08', 'Nota de Débito'),
    ], string="Tipo de Comprobante", required=True)
    serie = fields.Char(string="Serie", required=True)
    numero_comprobante = fields.Char(string="Número", required=True)
    tipo_documento_cliente = fields.Selection([
        ('1', 'DNI'),
        ('6', 'RUC'),
        ('0', 'Sin Documento'),
    ], string="Tipo Doc. Cliente", required=True)
    numero_documento_cliente = fields.Char(string="Número Doc. Cliente", required=True)
    nombre_cliente = fields.Char(string="Nombre o Razón Social", required=True)
    base_imponible = fields.Float(string="Base Imponible", required=True)
    igv = fields.Float(string="IGV", required=True)
    exonerado = fields.Float(string="Exonerado")
    inafecto = fields.Float(string="Inafecto")
    total = fields.Float(string="Total Venta", required=True)
    moneda = fields.Selection([
        ('PEN', 'Soles'),
        ('USD', 'Dólares'),
    ], string="Moneda", default='PEN')
