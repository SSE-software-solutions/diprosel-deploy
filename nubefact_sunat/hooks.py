# -*- coding: utf-8 -*-

import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """
    Hook que se ejecuta después de instalar el módulo.
    Crea y configura los diarios de Factura y Boleta con las secuencias correctas.
    
    Args:
        env: Environment de Odoo
    """
    
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
                'code': 'F001',  # El código corto define el prefijo
                'type': 'sale',
                'company_id': company.id,
                'show_on_dashboard': True,
                'sequence': 10,
            })
        else:
            # Si ya existe, asegurar que tenga el código correcto
            if journal_factura.code != 'F001':
                journal_factura.write({'code': 'F001'})
        
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
                'code': 'B001',  # El código corto define el prefijo
                'type': 'sale',
                'company_id': company.id,
                'show_on_dashboard': True,
                'sequence': 20,
            })
        else:
            # Si ya existe, asegurar que tenga el código correcto
            if journal_boleta.code != 'B001':
                journal_boleta.write({'code': 'B001'})
        
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
        
        # Configurar diario de Factura
        if journal_factura:
            _logger.info(f"✅ Diario {journal_factura.name} creado con código: {journal_factura.code}")
            _logger.info("Las secuencias se ajustarán automáticamente al crear la primera factura")
        
        # Configurar diario de Boleta
        if journal_boleta:
            _logger.info(f"✅ Diario {journal_boleta.name} creado con código: {journal_boleta.code}")
            _logger.info("Las secuencias se ajustarán automáticamente al crear la primera boleta")
    
    _logger.info("✅ Configuración de diarios electrónicos completada")

