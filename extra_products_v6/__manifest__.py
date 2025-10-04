{
    'name': 'Product Extension',
    'version': '1.0',
    'summary': 'Extension for Product Module with additional characteristics.',
    'author': 'SSE',
    'depends': ['product', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
        'views/negocio_template_views.xml',
        'views/familia_views.xml',
        'views/cateogria_views.xml',
        'views/condicion_almacenaje_views.xml'
       
        
    ],
    'installable': True,
    'application': False
}
