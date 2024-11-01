{
    'name': 'Acesso de usuário',
    'version': '1.0',
    'summary': 'Módulo para gerenciar usuários e seus acessos',
    'description': """
        Este módulo permite que os administradores gerenciem a criação de novos usuários e seus direitos de acesso.
    """,
    'author': 'Seu Nome',
    'depends': ['base'],  # Base é necessário para criar usuários
    'category': 'Administration',
    'data': [
        'views/user_access_views.xml',  # Arquivo de views
        'security/ir.model.access.csv',  # Permissões de acesso
    ],
    'assets': {
        'web.assets_backend': [
            'user_access_manager/static/src/css/custom_styles.css',
  
        ],
    },
    'installable': True,
    'application': True,
}