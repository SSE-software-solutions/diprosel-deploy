# -*- coding: utf-8 -*-

import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    """
    Hook que se ejecuta después de instalar el módulo.
    Crea y configura los diarios de Factura y Boleta con las secuencias correctas.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Obtener todas las compañías peruanas
    companies = env['res.company'].search([])
    
    for company in companies:
        # Solo configurar para compañías peruanas
        if company.country_code != 'PE':
            continue
            
        _logger.info(f"Configurando diarios electrónicos para la compañía: {company.name}")
        
        # Buscar o crear diario de Factura
        journal_factura = env['account.journal'].search([
            ('name', '=', 'Factura'),
            ('type', '=', 'sale'),
            ('company_id', '=', company.id)
        ], limit=1)
        
        if not journal_factura:
            _logger.info("Creando diario de Facturas Electrónicas")
            journal_factura = env['account.journal'].create({
                'name': 'Factura',
                'code': 'FE',
                'type': 'sale',
                'company_id': company.id,
                'show_on_dashboard': True,
                'sequence': 10,
            })
        
        # Buscar o crear diario de Boleta
        journal_boleta = env['account.journal'].search([
            ('name', '=', 'Boleta'),
            ('type', '=', 'sale'),
            ('company_id', '=', company.id)
        ], limit=1)
        
        if not journal_boleta:
            _logger.info("Creando diario de Boletas Electrónicas")
            journal_boleta = env['account.journal'].create({
                'name': 'Boleta',
                'code': 'BE',
                'type': 'sale',
                'company_id': company.id,
                'show_on_dashboard': True,
                'sequence': 20,
            })
        
        # Obtener las secuencias creadas
        seq_factura = env['ir.sequence'].search([
            ('code', '=', 'account.move.invoice.pe'),
            '|', ('company_id', '=', company.id), ('company_id', '=', False)
        ], limit=1)
        
        seq_boleta = env['ir.sequence'].search([
            ('code', '=', 'account.move.boleta.pe'),
            '|', ('company_id', '=', company.id), ('company_id', '=', False)
        ], limit=1)
        
        seq_credit_note = env['ir.sequence'].search([
            ('code', '=', 'account.move.credit_note.pe'),
            '|', ('company_id', '=', company.id), ('company_id', '=', False)
        ], limit=1)
        
        # Configurar secuencias dedicadas para diario de Factura
        if seq_factura and journal_factura:
            _logger.info(f"Configurando secuencia {seq_factura.name} para diario {journal_factura.name}")
            
            # Activar secuencias dedicadas
            journal_factura.write({
                'refund_sequence': True,
            })
            
            # Buscar o crear la secuencia de factura del diario
            journal_seq = env['ir.sequence'].search([
                ('code', '=', f'account.journal.{journal_factura.id}')
            ], limit=1)
            
            if not journal_seq:
                # Crear secuencia específica del diario usando la misma configuración
                journal_seq = env['ir.sequence'].create({
                    'name': f'{journal_factura.name} - Secuencia',
                    'code': f'account.journal.{journal_factura.id}',
                    'implementation': 'standard',
                    'prefix': seq_factura.prefix,
                    'padding': seq_factura.padding,
                    'number_increment': 1,
                    'number_next': seq_factura.number_next,
                    'company_id': company.id,
                })
            
            _logger.info(f"Diario Factura configurado con secuencia: {journal_seq.name}")
        
        # Configurar secuencias dedicadas para diario de Boleta
        if seq_boleta and journal_boleta:
            _logger.info(f"Configurando secuencia {seq_boleta.name} para diario {journal_boleta.name}")
            
            # Activar secuencias dedicadas
            journal_boleta.write({
                'refund_sequence': True,
            })
            
            # Buscar o crear la secuencia de boleta del diario
            journal_seq = env['ir.sequence'].search([
                ('code', '=', f'account.journal.{journal_boleta.id}')
            ], limit=1)
            
            if not journal_seq:
                # Crear secuencia específica del diario
                journal_seq = env['ir.sequence'].create({
                    'name': f'{journal_boleta.name} - Secuencia',
                    'code': f'account.journal.{journal_boleta.id}',
                    'implementation': 'standard',
                    'prefix': seq_boleta.prefix,
                    'padding': seq_boleta.padding,
                    'number_increment': 1,
                    'number_next': seq_boleta.number_next,
                    'company_id': company.id,
                })
            
            _logger.info(f"Diario Boleta configurado con secuencia: {journal_seq.name}")
    
    _logger.info("✅ Configuración de diarios electrónicos completada")

