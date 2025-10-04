import base64
import calendar
from odoo import models, fields, api
from datetime import datetime

from odoo.exceptions import UserError

class SIREPeriodo(models.Model):
    _name = 'sire.periodo'
    _description = 'Períodos de Registro de Ventas SIRE'
    _rec_name = 'nombre_periodo'

    def _get_year_selection(self):
        """ Retorna la lista de años desde 2020 hasta el actual """
        current_year = datetime.today().year
        return [(str(year), str(year)) for year in range(2020, current_year + 1)]

    def _get_month_selection(self):
        """ Retorna todos los meses del año (sin restricción) """
        return [
            ('01', 'Enero'), ('02', 'Febrero'), ('03', 'Marzo'),
            ('04', 'Abril'), ('05', 'Mayo'), ('06', 'Junio'),
            ('07', 'Julio'), ('08', 'Agosto'), ('09', 'Septiembre'),
            ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre'),
        ]

    mes = fields.Selection(
        selection=lambda self: self._get_month_selection(),
        string="Mes",
        required=True,
        help="Seleccione el mes (hasta el mes anterior al actual)."
    )

    anio = fields.Selection(
        selection=lambda self: self._get_year_selection(),
        string="Año",
        required=True,
        help="Seleccione el año (hasta el año actual)."
    )

    nombre_periodo = fields.Char(
        string="Período",
        compute="_compute_nombre_periodo",
        store=True,
        readonly=True
    )
    archivo_sire = fields.Binary(string="Archivo SIRE TXT")
    archivo_nombre = fields.Char(string="Nombre de Archivo")
    estado = fields.Selection([
        ('borrador', 'Borrador'),
        ('validado', 'Validado'),
        ('reportado', 'Reportado'),
    ], string="Estado", default="borrador")

    ventas_ids = fields.One2many(
        'sire.ventas',
        'periodo_id',
        string="Registros de Ventas"
    )

    _sql_constraints = [
        ('unique_mes_anio', 'unique(mes, anio)', 'El período ya existe. No se pueden duplicar meses y años.')
    ]

    @api.depends('mes', 'anio')
    def _compute_nombre_periodo(self):
        """ Genera automáticamente el nombre del período como 'Mes Año' """
        meses_dict = {
            '01': 'Enero', '02': 'Febrero', '03': 'Marzo',
            '04': 'Abril', '05': 'Mayo', '06': 'Junio',
            '07': 'Julio', '08': 'Agosto', '09': 'Septiembre',
            '10': 'Octubre', '11': 'Noviembre', '12': 'Diciembre'
        }
        for record in self:
            mes_nombre = meses_dict.get(record.mes, 'Mes Desconocido')
            record.nombre_periodo = f"{mes_nombre} {record.anio}" if record.mes and record.anio else "Sin Nombre"

    def generar_registros_ventas(self):

        anio = int(self.anio)
        mes = int(self.mes)
        ultimo_dia = calendar.monthrange(anio, mes)[1]
        fecha_inicio = f"{anio}-{mes:02d}-01"
        fecha_fin = f"{anio}-{mes:02d}-{ultimo_dia}"

        ventas_odoo = self.env['account.move'].search([
            ('move_type', 'in', ['out_invoice']),
            ('state', '=', 'posted'),
            '|',
                '&', ('invoice_date', '>=', fecha_inicio), ('invoice_date', '<=', fecha_fin),
                '&', ('invoice_date_due', '>=', fecha_inicio), ('invoice_date_due', '<=', fecha_fin),
        ])

        if not ventas_odoo:
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': 'No hay ventas registradas en este período.',
                    'type': 'rainbow_man',
                }
            }

        registros_creados = []
        for factura in ventas_odoo:
            cliente = factura.partner_id

            # Documento cliente
            tipo_doc = (
                cliente.l10n_latam_identification_type_id.l10n_pe_vat_code
                if cliente.l10n_latam_identification_type_id
                else '0'
            )
            nro_doc = cliente.vat or '-'
            nombre = cliente.name or 'Cliente Anónimo'

            # Serie y número
            if factura.name and '-' in factura.name:
                serie, numero = factura.name.split('-', 1)
            else:
                serie, numero = 'N/A', factura.name

            # Exonerado e inafecto por línea
            exonerado = 0.0
            inafecto = 0.0
            for line in factura.invoice_line_ids:
                for tax in line.tax_ids:
                    if hasattr(tax, 'l10n_pe_edi_affected_code'):
                        if tax.l10n_pe_edi_affected_code == '20':  # Exonerado
                            exonerado += line.price_subtotal
                        elif tax.l10n_pe_edi_affected_code == '30':  # Inafecto
                            inafecto += line.price_subtotal

            registros_creados.append({
                'periodo_id': self.id,
                'fecha_emision': factura.invoice_date or factura.invoice_date_due,
                'tipo_comprobante': factura.move_type,
                'serie': serie,
                'numero_comprobante': numero,
                'nombre_cliente': nombre,
                'tipo_documento_cliente': tipo_doc,
                'numero_documento_cliente': nro_doc,
                'base_imponible': factura.amount_untaxed,
                'igv': factura.amount_tax,
                'exonerado': exonerado,
                'inafecto': inafecto,
                'total': factura.amount_total,
                'moneda': factura.currency_id.name or 'PEN',
            })

        self.env['sire.ventas'].create(registros_creados)

        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Registros de ventas generados correctamente.',
                'type': 'rainbow_man',
            }
        }


    def generar_archivo_sire(self):
        """
        Genera y guarda el archivo TXT con los registros del período,
        y nombra el archivo siguiendo el estándar SUNAT.
        """
        if not self.ventas_ids:
            raise UserError("No hay registros de ventas generados para este período.")

        # Datos de la empresa emisora
        company = self.env.user.company_id
        ruc_emisor = company.vat or ''
        nombre_emisor = company.name or ''
        periodo = f"{self.anio}{self.mes}"
        fecha_generacion = fields.Date.today().strftime('%d/%m/%Y')

        contenido = ""
        for venta in self.ventas_ids:
            linea = [
                ruc_emisor,                                  # 1. RUC
                nombre_emisor,                               # 2. Razon Social
                periodo,                                     # 3. Periodo
                "", "",                                      # 4-5 vacíos
                fecha_generacion,                            # 6. Fecha de generación
                "",                                          # 7. vacío
                venta.tipo_comprobante or "",                # 8. Tipo Comprobante
                venta.serie or "",                           # 9. Serie
                venta.numero_comprobante or "",              # 10. Número
                "",                                          # 11. vacío
                venta.tipo_documento_cliente or "",          # 12. Tipo Doc Cliente
                venta.numero_documento_cliente or "",        # 13. Número Doc Cliente
                venta.nombre_cliente or "",                  # 14. Nombre
                f"{venta.base_imponible:.2f}",               # 15. Base Imponible
                "0.00", "0.00", "0.00", "0.00", "0.00",       # 16-20 vacíos
                f"{venta.total:.2f}",                        # 21. Total Venta
                "0.00", "0.00", "0.00", "0.00", "0.00", "0.00",  # 22-27 vacíos
                f"{venta.total:.2f}",                        # 28. Total Final
                venta.moneda or "PEN",                       # 29. Moneda
                "", "", "", "", "", "", "", "", ""           # 30-38 vacíos
            ]
            contenido += "|".join(linea) + "\n"

        # Generar nombre de archivo SUNAT oficial
        ruc = ruc_emisor
        anio = self.anio
        mes = self.mes
        dia = "00"
        codigo_libro = "140400"  # Ventas
        codigo_presentacion = "01"
        indicador_operacion = "1"  # Empresa operativa
        indicador_contenido = "1" if self.ventas_ids else "0"
        indicador_moneda = "1" if company.currency_id.name == "PEN" else "2"
        indicador_sistema = "2"
        correlativo_ajuste = "00"

        nombre_archivo = (
            f"LE{ruc}{anio}{mes}{dia}"
            f"{codigo_libro}{codigo_presentacion}"
            f"{indicador_operacion}{indicador_contenido}"
            f"{indicador_moneda}{indicador_sistema}"
            f"{correlativo_ajuste}.txt"
        )

        # Codificar contenido
        archivo = base64.b64encode(contenido.encode('utf-8'))

        # Guardar en campos binarios
        self.write({
            'archivo_sire': archivo,
            'archivo_nombre': nombre_archivo,
        })

        return {
            'effect': {
                'fadeout': 'slow',
                'message': f'Archivo TXT "{nombre_archivo}" generado correctamente.',
                'type': 'rainbow_man',
            }
        }



    def download_sire_txt(self):
        return {
            'type': 'ir.actions.act_url',
            'url': f"/web/content/?model=sire.periodo&id={self.id}&field=archivo_sire&download=true&filename={self.archivo_nombre}",
            'target': 'self',
        }

