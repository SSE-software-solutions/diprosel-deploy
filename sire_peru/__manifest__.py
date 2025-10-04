{
    'name': 'SIRE Perú',
    'summary': 'Módulo de Registro de Ventas SIRE para SUNAT',
    'description': 'Este módulo permite gestionar los registros de ventas para el SIRE de SUNAT.',
    'author': 'SSE',
    'website': 'https://tuweb.com',
    'category': 'Accounting',
    'version': '1.0',
    'depends': ['base', 'account'],  # Asegúrate de incluir dependencias necesarias
    'data': [
        'security/ir.model.access.csv',
        'views/sire_periodo_view.xml',
        'views/sire_ventas_view.xml',
        'views/sire_periodo_compra_view.xml',
        'views/sire_compras_view.xml',
        'views/menu_views.xml',
        
    ],
    'application': True, 
    'installable': True,
    'auto_install': False,
}
