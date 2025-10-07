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
        """Prueba la conexión real con NubeFact"""
        import requests
        import json
        from datetime import datetime
        
        self.ensure_one()
        
        # Validar campos requeridos
        if not self.ruc or not self.token or not self.api_url:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'message': 'Por favor complete todos los campos: RUC, Token y URL API',
                    'type': 'warning',
                    'sticky': True,
                }
            }
        
        # Validar formato de URL
        url = self.get_api_url()
        if not url.startswith('https://api.nubefact.com'):
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'message': 'La URL debe comenzar con: https://api.nubefact.com',
                    'type': 'warning',
                    'sticky': True,
                }
            }
        
        try:
            # Intentar consultar un comprobante ficticio para probar la autenticación
            # Según la documentación de NubeFact, operación "consultar_comprobante"
            test_data = {
                "operacion": "consultar_comprobante",
                "tipo_de_comprobante": 1,
                "serie": "TEST",
                "numero": 1
            }
            
            headers = {
                'Authorization': self.token,
                'Content-Type': 'application/json'
            }
            
            _logger.info(f"Probando conexión con NubeFact - URL: {url}")
            
            response = requests.post(
                url,
                headers=headers,
                json=test_data,
                timeout=10
            )
            
            self.last_connection_test = datetime.now()
            
            _logger.info(f"Respuesta de prueba: Status {response.status_code}, Body: {response.text}")
            
            # Analizar respuesta
            if response.status_code == 200:
                # Conexión exitosa (aunque el comprobante no exista)
                self.connection_status = 'success'
                self.connection_message = f'Conexión exitosa con NubeFact. Token y URL correctos.'
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': '✅ Conexión Exitosa',
                        'message': 'Token y URL de NubeFact verificados correctamente. Ya puede enviar facturas a SUNAT.',
                        'type': 'success',
                        'sticky': False,
                    }
                }
            elif response.status_code == 401:
                # Token incorrecto
                self.connection_status = 'failed'
                self.connection_message = 'Token de autenticación incorrecto'
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': '❌ Error de Autenticación',
                        'message': 'El Token es incorrecto. Verifique en su panel de NubeFact.',
                        'type': 'danger',
                        'sticky': True,
                    }
                }
            elif response.status_code == 404:
                # URL incorrecta
                self.connection_status = 'failed'
                self.connection_message = 'URL de API incorrecta o no encontrada'
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': '❌ URL Incorrecta',
                        'message': 'La URL de API no es válida. Verifique que sea la URL correcta de su cuenta en NubeFact.',
                        'type': 'danger',
                        'sticky': True,
                    }
                }
            else:
                # Otro error
                try:
                    error_data = response.json()
                    error_msg = error_data.get('errors', response.text)
                except:
                    error_msg = response.text
                
                self.connection_status = 'failed'
                self.connection_message = f'Error {response.status_code}: {error_msg}'
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': '⚠️ Error de Conexión',
                        'message': f'Error al conectar con NubeFact: {error_msg[:200]}',
                        'type': 'warning',
                        'sticky': True,
                    }
                }
                
        except requests.exceptions.Timeout:
            self.connection_status = 'failed'
            self.connection_message = 'Tiempo de espera agotado al conectar con NubeFact'
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': '⏱️ Tiempo Agotado',
                    'message': 'No se pudo conectar con NubeFact. Verifique su conexión a internet.',
                    'type': 'warning',
                    'sticky': True,
                }
            }
            
        except requests.exceptions.ConnectionError:
            self.connection_status = 'failed'
            self.connection_message = 'No se pudo conectar con el servidor de NubeFact'
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': '🌐 Sin Conexión',
                    'message': 'No se pudo conectar con NubeFact. Verifique su conexión a internet o que el servidor de NubeFact esté disponible.',
                    'type': 'warning',
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
                    'title': '❌ Error',
                    'message': f'Error inesperado: {str(e)}',
                    'type': 'danger',
                    'sticky': True,
                }
            }
