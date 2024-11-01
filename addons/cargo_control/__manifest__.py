{
    'name': 'Custom User Access Management',
    'version': '1.0',
    'summary': 'Manage user roles with custom access control',
    'author': 'Your Name',
    'category': 'Website',
    'depends': ['base', 'website', 'auth_oauth'],
    'data': [
        # 'security/user_groups.xml',
        'security/ir.model.access.csv',
        # 'views/hide_backend_menu.xml',
        'views/setting_password_view.xml',
    ],
    'installable': True,
    'application': True,
}