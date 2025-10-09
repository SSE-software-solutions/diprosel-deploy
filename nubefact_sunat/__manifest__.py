# -*- coding: utf-8 -*-
{
    'name': 'Facturación Electrónica SUNAT - NubeFact',
    'version': '18.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Integración con NubeFact para envío de comprobantes electrónicos a SUNAT',
    'description': """
        Módulo de Facturación Electrónica para SUNAT
        =============================================
        
        Este módulo permite enviar comprobantes electrónicos a SUNAT mediante 
        la plataforma NubeFact (https://www.nubefact.com/).
        
        Características principales:
        * Envío de Facturas, Boletas, Notas de Crédito y Débito
        * Consulta de estado de comprobantes
        * Descarga de PDF y XML
        * Configuración de credenciales NubeFact
        * Registro de respuestas de SUNAT
    """,
    'author': 'SSE',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/ir_sequence_views.xml',
        'views/nubefact_config_views.xml',
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
    'post_init_hook': 'post_init_hook',
}
