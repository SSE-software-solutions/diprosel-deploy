{
    'name': 'Product Profit Margin',
    'version': '1.0',
    'summary': 'Agrega un porcentaje de ganancia a los productos y actualiza precios automáticamente',
    'category': 'Sales',
    'author': 'SSE',
    'depends': ['product', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
