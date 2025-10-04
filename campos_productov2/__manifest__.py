{
    'name': 'Product Business Sector in Inventory',
    'version': '18.0.1.0.0',
    'category': 'Warehouse',
    'depends': ['base', 'stock'],
  'data': [
    'security/ir.model.access.csv',
    'views/business_sector_views.xml',
    'views/product_line_views.xml',
    'views/product_model_views.xml',
    'views/product_brand_views.xml',
    'views/product_subfamily_views.xml',
    'views/product_template_views.xml',
    'views/stock_quant_views.xml',
],



    'installable': True,
    'auto_install': False,
    'application': False,
}
