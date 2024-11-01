{
    'name': 'Custom Sidebar',
    'version': '1.0',
    'category': 'Customizations',
    'summary': 'Substitui a navbar por uma sidebar.',
    'description': 'Este módulo substitui a navbar padrão do Odoo por uma sidebar personalizada.',
    'depends': ['web'],
    'data': [
        'views/custom_sidebar_template.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'custom_sidebar/static/src/css/sidebar.css',
            'custom_sidebar/static/src/js/sidebar.js',
        ],
    },
    
    'installable': True,
}
