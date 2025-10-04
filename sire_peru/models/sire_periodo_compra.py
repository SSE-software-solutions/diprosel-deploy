from odoo import models, fields, api
from odoo.exceptions import UserError
import calendar
import base64

class SIREPeriodoCompra(models.Model):
    _name = 'sire.periodo.compra'
    _description = 'Períodos de Registro de Compras SIRE'
    _rec_name = 'nombre_periodo'

    mes = fields.Selection([(str(i).zfill(2), calendar.month_name[i]) for i in range(1, 13)], string="Mes", required=True)
    anio = fields.Selection([(str(y), str(y)) for y in range(2020, fields.Date.today().year + 1)], string="Año", required=True)
    nombre_periodo = fields.Char(string="Nombre del Período", compute="_compute_nombre_periodo", store=True)
    estado = fields.Selection([
        ('borrador', 'Borrador'),
        ('validado', 'Validado'),
        ('reportado', 'Reportado')
    ], default='borrador', string="Estado")

    compras_ids = fields.One2many('sire.compras', 'periodo_id', string="Registros de Compras")
    archivo_sire = fields.Binary("Archivo TXT")
    archivo_nombre = fields.Char("Nombre del Archivo")

    @api.depends('mes', 'anio')
    def _compute_nombre_periodo(self):
        for record in self:
            if record.mes and record.anio:
                record.nombre_periodo = f"{calendar.month_name[int(record.mes)]} {record.anio}"
            else:
                record.nombre_periodo = "Sin Nombre"

    def generar_registros_compras(self):
        anio = int(self.anio)
        mes = int(self.mes)
        fecha_inicio = f"{anio}-{mes:02d}-01"
        fecha_fin = f"{anio}-{mes:02d}-{calendar.monthrange(anio, mes)[1]}"

        facturas = self.env['account.move'].search([
            ('move_type', '=', 'in_invoice'),
            ('state', '=', 'posted'),
            ('invoice_date', '>=', fecha_inicio),
            ('invoice_date', '<=', fecha_fin),
        ])

        if not facturas:
            raise UserError("No se encontraron compras para este período.")

        registros = []
        for factura in facturas:
            proveedor = factura.partner_id
            tipo_doc = proveedor.l10n_latam_identification_type_id.l10n_pe_vat_code if proveedor.l10n_latam_identification_type_id else '0'
            nro_doc = proveedor.vat or '-'
            nombre = proveedor.name or 'Proveedor Anónimo'

            registros.append({
                'periodo_id': self.id,
                'fecha_emision': factura.invoice_date,
                'tipo_comprobante': factura.move_type,
                'tipo_documento_proveedor': tipo_doc,
                'numero_documento_proveedor': nro_doc,
                'nombre_proveedor': nombre,
                'base_imponible': factura.amount_untaxed,
                'igv': factura.amount_tax,
                'total': factura.amount_total,
                'moneda': factura.currency_id.name or 'PEN',
            })

        self.env['sire.compras'].create(registros)

        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Registros de compras generados correctamente.',
                'type': 'rainbow_man',
            }
        }

    def generar_archivo_sire(self):
        """
        Genera y guarda el archivo TXT con los registros de COMPRAS del período.
        El nombre del archivo sigue el formato oficial SUNAT (RCE).
        """
        if not self.compras_ids:
            raise UserError("No hay registros de compras para este período.")

        # Datos del emisor
        company = self.env.user.company_id
        ruc_emisor = company.vat or ''
        nombre_emisor = company.name or ''
        periodo = f"{self.anio}{self.mes}"
        fecha_generacion = fields.Date.today().strftime('%d/%m/%Y')

        # Contenido del archivo .txt
        contenido = ""
        for compra in self.compras_ids:
            linea = [
                ruc_emisor,                                     # 1. RUC de la empresa
                nombre_emisor,                                  # 2. Razón social
                periodo,                                        # 3. Periodo en YYYYMM
                "", "",                                         # 4-5 vacíos
                fecha_generacion,                               # 6. Fecha de generación
                "",                                             # 7. vacío
                compra.tipo_comprobante or "",                  # 8. Tipo comprobante
                "", "",                                         # 9-10: Serie y número (no usados aquí)
                "",                                             # 11
                compra.tipo_documento_proveedor or "",          # 12. Tipo documento del proveedor
                compra.numero_documento_proveedor or "",        # 13. Número documento proveedor
                compra.nombre_proveedor or "",                  # 14. Nombre proveedor
                f"{compra.base_imponible:.2f}",                 # 15. Base imponible
                "0.00", "0.00", "0.00", "0.00", "0.00",          # 16-20 vacíos
                f"{compra.total:.2f}",                          # 21. Total compra
                "0.00", "0.00", "0.00", "0.00", "0.00", "0.00",  # 22-27 vacíos
                f"{compra.total:.2f}",                          # 28. Total final
                compra.moneda or "PEN",                         # 29. Moneda
                "", "", "", "", "", "", "", "", ""              # 30-38 vacíos
            ]
            contenido += "|".join(linea) + "\n"

        # ==== 📄 Generar nombre oficial SUNAT (RCE) ====
        ruc = ruc_emisor
        anio = self.anio
        mes = self.mes
        dia = "00"  # Siempre '00' en RCE/SIRE
        codigo_libro = "080100"  # Libro de Compras
        codigo_presentacion = "01"  # 01: Registro nuevo, 03: Ajuste posterior, etc.
        indicador_operacion = "1"  # 1: empresa activa
        indicador_contenido = "1" if self.compras_ids else "0"  # 0 si vacío
        indicador_moneda = "1" if company.currency_id.name == "PEN" else "2"
        indicador_sistema = "2"  # generado por SIRE
        correlativo_ajuste = "00"

        nombre_archivo = (
            f"LE{ruc}{anio}{mes}{dia}"
            f"{codigo_libro}{codigo_presentacion}"
            f"{indicador_operacion}{indicador_contenido}"
            f"{indicador_moneda}{indicador_sistema}"
            f"{correlativo_ajuste}.txt"
        )

        # Codificar contenido a base64
        archivo = base64.b64encode(contenido.encode('utf-8'))

        # Guardar en los campos del modelo
        self.write({
            'archivo_sire': archivo,
            'archivo_nombre': nombre_archivo,
        })

        return {
            'effect': {
                'fadeout': 'slow',
                'message': f'Archivo TXT \"{nombre_archivo}\" generado correctamente.',
                'type': 'rainbow_man',
            }
        }



    def download_sire_txt(self):
        return {
            'type': 'ir.actions.act_url',
            'url': f"/web/content/?model=sire.periodo.compra&id={self.id}&field=archivo_sire&download=true&filename={self.archivo_nombre}",
            'target': 'self',
        }


class SIRECompras(models.Model):
    _name = 'sire.compras'
    _description = 'Registro de Compras para SIRE'

    periodo_id = fields.Many2one('sire.periodo.compra', required=True, ondelete="cascade")
    fecha_emision = fields.Date(string="Fecha Emisión", required=True)
    tipo_comprobante = fields.Selection([
        ('in_invoice', 'Factura'),
        ('in_refund', 'Nota de Crédito'),
    ], string="Tipo Comprobante", required=True)

    tipo_documento_proveedor = fields.Selection([
        ('0', 'Sin Documento'),
        ('1', 'DNI'),
        ('6', 'RUC'),
    ], string="Tipo Doc. Proveedor", required=True)

    numero_documento_proveedor = fields.Char(string="Nro. Documento", required=True)
    nombre_proveedor = fields.Char(string="Nombre o Razón Social", required=True)

    base_imponible = fields.Float(string="Base Imponible", required=True)
    igv = fields.Float(string="IGV", required=True)
    exonerado = fields.Float(string="Exonerado")
    inafecto = fields.Float(string="Inafecto")
    total = fields.Float(string="Total Compra", required=True)

    moneda = fields.Selection([
        ('PEN', 'Soles'),
        ('USD', 'Dólares'),
    ], string="Moneda", default='PEN')
