from odoo import models, fields

class SIREReport(models.AbstractModel):
    _name = 'report.sire_peru.sire_report'
    _description = 'Reporte de Registros SIRE'

    def _get_report_values(self, docids, data=None):
        registros = self.env['sire.registro'].browse(docids)
        return {
            'docs': registros,
        }
