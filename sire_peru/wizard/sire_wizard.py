from odoo import models, fields, api

class SIREWizard(models.TransientModel):  # ✅ Debe ser TransientModel, NO Model
    _name = 'sire.wizard'
    _description = 'Wizard para Generar Reporte SIRE'

    periodo_id = fields.Many2one('sire.periodo', string="Período", required=True)

    def generar_reporte(self):
        """ Lógica para generar el reporte de SIRE """
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Reporte generado exitosamente.',
                'type': 'rainbow_man',
            }
        }
