{
    'name': 'Dashboard',
    'version': '1.0',
    'summary': 'Custom Dashboard for Loan Management',
    'sequence': -1,
    'description': """Dashboard showing key statistics using OWL.""",
    'category': 'Finance',
    'depends': ['base', 'web', 'bus'],
    'data': [
        'views/sse_dashboard_v3.xml',
    ],
    'images': ['static/description/icon.png'],
    'assets': {
        'web.assets_backend': [
            'sse_dashboard_v3/static/src/components/**/*.js',
            'sse_dashboard_v3/static/src/components/**/*.xml',
            'sse_dashboard_v3/static/src/components/**/*.scss',
        ],
    },
    'installable': True,
    'application': True,
}
