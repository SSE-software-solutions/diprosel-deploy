# -*- coding: utf-8 -*-

from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class NubefactConfig(models.Model):
    _name = 'nubefact.config'
    _description = 'Configuración de NubeFact'
    _rec_name = 'company_id'

    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.company,
        ondelete='cascade'
    )
    
    # Credenciales NubeFact
    token = fields.Char(
        string='Token NubeFact',
        required=True,
        help='Token de autorización proporcionado por NubeFact'
    )
    
    ruc = fields.Char(
        string='RUC',
        required=True,
        help='RUC de la empresa emisora'
    )
    
    # URL de API personalizada de NubeFact
    api_url = fields.Char(
        string='URL API de NubeFact',
        required=True,
        help='URL completa proporcionada por NubeFact. El entorno (pruebas/producción) se configura desde el panel de NubeFact.'
    )
    
    active = fields.Boolean(
        string='Activo',
        default=True
    )
    
    _sql_constraints = [
        ('company_unique', 'UNIQUE(company_id)', 'Ya existe una configuración para esta compañía.')
    ]
    
    def get_api_url(self):
        """Retorna la URL de la API configurada"""
        self.ensure_one()
        # Remover espacios y @ si los hay
        url = self.api_url.strip().lstrip('@')
        return url
