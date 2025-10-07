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
    
    # Campos de auditoría
    last_connection_test = fields.Datetime(
        string='Última Prueba de Conexión',
        readonly=True
    )
    
    connection_status = fields.Selection([
        ('success', 'Exitosa'),
        ('failed', 'Fallida'),
        ('not_tested', 'No Probada')
    ], string='Estado de Conexión', default='not_tested', readonly=True)
    
    connection_message = fields.Text(
        string='Mensaje de Conexión',
        readonly=True
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
    
    def action_test_connection(self):
        """Prueba la conexión con NubeFact"""
        import requests
        import json
        from datetime import datetime
        
        self.ensure_one()
        
        try:
            # NubeFact no tiene endpoint de prueba, solo verificamos que responda
            url = self.get_api_url()
            headers = {
                'Authorization': f'Token token={self.token}',
                'Content-Type': 'application/json'
            }
            
            # Hacer un request simple para verificar autenticación
            response = requests.get(url, headers=headers, timeout=10)
            
            self.last_connection_test = datetime.now()
            
            if response.status_code == 200:
                self.connection_status = 'success'
                self.connection_message = 'Conexión exitosa con NubeFact'
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Éxito',
                        'message': 'Conexión exitosa con NubeFact',
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                self.connection_status = 'failed'
                self.connection_message = f'Error {response.status_code}: {response.text}'
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Error',
                        'message': f'Error al conectar: {response.text}',
                        'type': 'danger',
                        'sticky': True,
                    }
                }
                
        except Exception as e:
            _logger.error(f"Error al probar conexión con NubeFact: {str(e)}")
            self.connection_status = 'failed'
            self.connection_message = str(e)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'message': f'Error de conexión: {str(e)}',
                    'type': 'danger',
                    'sticky': True,
                }
            }
