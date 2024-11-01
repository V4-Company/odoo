{
    'name': 'Website Custom NF Emission',
    'version': '1.0',
    'category': 'Website',
    'summary': 'Formulário de emissão de nota fiscal integrado com o website',
    'description': 'Permite que os usuários enviem notas fiscais diretamente do website.',
    'author': 'Your Name',
    'depends': ['website' , 'base'],
    'data': [
        'views/nf_emission_views.xml',
        'views/nf_emission_form.xml',
        'security/ir.model.access.csv'
    ],
      'assets': {
        'web.assets_frontend': [
            'nfe_attachment_copy/static/src/css/custom_styles.css',  # Adicione o caminho do CSS aqui
        ],
    },
    'installable': True,
    'application': True,
}
