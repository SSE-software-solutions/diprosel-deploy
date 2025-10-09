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
        
        # Configurar diario de Factura con secuencia personalizada
        if journal_factura:
            _logger.info(f"Configurando secuencias para diario {journal_factura.name} (código: {journal_factura.code})")
            
            # Verificar si ya tiene secuencias asignadas
            existing_seq = env['ir.sequence'].search([
                ('code', '=', f'{journal_factura.code}.invoice'),
                ('company_id', '=', company.id)
            ], limit=1)
            
            if not existing_seq:
                # Crear secuencias específicas basadas en el código del diario
                # El prefijo será el código del diario + guion
                sequence_invoice = env['ir.sequence'].sudo().create({
                    'name': f'Secuencia {journal_factura.code}',
                    'implementation': 'standard',
                    'code': f'{journal_factura.code}.invoice',
                    'prefix': f'{journal_factura.code}-',  # Prefijo basado en código del diario
                    'padding': 6,  # 6 dígitos de padding
                    'number_increment': 1,
                    'number_next': 1,
                    'use_date_range': False,
                    'company_id': company.id,
                })
                
                sequence_refund = env['ir.sequence'].sudo().create({
                    'name': f'Secuencia NC {journal_factura.code}',
                    'implementation': 'standard',
                    'code': f'{journal_factura.code}.refund',
                    'prefix': f'FC{journal_factura.code[1:]}-',  # FC + los números del código
                    'padding': 6,
                    'number_increment': 1,
                    'number_next': 1,
                    'use_date_range': False,
                    'company_id': company.id,
                })
                
                # Asignar las secuencias al diario
                journal_factura.write({
                    'sequence_id': sequence_invoice.id,
                    'refund_sequence_id': sequence_refund.id,
                    'refund_sequence': True,
                })
                
                _logger.info(f"✅ Diario {journal_factura.name} configurado con secuencia {sequence_invoice.prefix}######")
            else:
                _logger.info(f"Diario {journal_factura.name} ya tiene secuencias configuradas")
        
        # Configurar diario de Boleta con secuencia personalizada
        if journal_boleta:
            _logger.info(f"Configurando secuencias para diario {journal_boleta.name} (código: {journal_boleta.code})")
            
            # Verificar si ya tiene secuencias asignadas
            existing_seq = env['ir.sequence'].search([
                ('code', '=', f'{journal_boleta.code}.invoice'),
                ('company_id', '=', company.id)
            ], limit=1)
            
            if not existing_seq:
                # Crear secuencias específicas basadas en el código del diario
                sequence_invoice = env['ir.sequence'].sudo().create({
                    'name': f'Secuencia {journal_boleta.code}',
                    'implementation': 'standard',
                    'code': f'{journal_boleta.code}.invoice',
                    'prefix': f'{journal_boleta.code}-',  # Prefijo basado en código del diario
                    'padding': 6,  # 6 dígitos de padding
                    'number_increment': 1,
                    'number_next': 1,
                    'use_date_range': False,
                    'company_id': company.id,
                })
                
                sequence_refund = env['ir.sequence'].sudo().create({
                    'name': f'Secuencia NC {journal_boleta.code}',
                    'implementation': 'standard',
                    'code': f'{journal_boleta.code}.refund',
                    'prefix': f'BC{journal_boleta.code[1:]}-',  # BC + los números del código
                    'padding': 6,
                    'number_increment': 1,
                    'number_next': 1,
                    'use_date_range': False,
                    'company_id': company.id,
                })
                
                # Asignar las secuencias al diario
                journal_boleta.write({
                    'sequence_id': sequence_invoice.id,
                    'refund_sequence_id': sequence_refund.id,
                    'refund_sequence': True,
                })
                
                _logger.info(f"✅ Diario {journal_boleta.name} configurado con secuencia {sequence_invoice.prefix}######")
            else:
                _logger.info(f"Diario {journal_boleta.name} ya tiene secuencias configuradas")
    
    _logger.info("✅ Configuración de diarios electrónicos completada")

