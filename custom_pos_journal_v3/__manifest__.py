{
    'name': 'POS Dynamic Invoice',
    'version': '1.0',
    'category': 'Point of Sale',
    'summary': 'Automatically selects the correct journal for invoices based on customer document type in POS.',
    'author': 'SSE',
    'depends': ['point_of_sale', 'account', 'l10n_latam_base'],
    'data': ['security/ir.model.access.csv'],
    'installable': True,
    'application': False,
}


