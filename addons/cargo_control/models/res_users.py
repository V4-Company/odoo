from odoo import models, fields, api
from odoo.exceptions import AccessDenied, UserError
class ResUsers(models.Model):
    _inherit = 'res.users'

    password_set = fields.Boolean(string='Password Set', default=False)

    @api.model
    def create(self, vals):
        if 'password' in vals and vals['password']:
            vals['password_set'] = True
        return super(ResUsers, self).create(vals)

    def write(self, vals):
        if 'password' in vals:
            vals['password_set'] = bool(vals['password'])
        return super(ResUsers, self).write(vals)
    @api.model
    def _auth_oauth_signin(self, provider, validation, params):
        print("trigou 4 -------------")
        """ Retrieve and sign in the user corresponding to provider and validated access token.
            :param provider: oauth provider id (int)
            :param validation: result of validation of access token (dict)
            :param params: oauth parameters (dict)
            :return: user login (str)
            :raise: AccessDenied if signin failed.
        """
        oauth_uid = validation['user_id']
        email = validation.get('email')  # Pega o e-mail do usuário autenticado

        # 1. Buscar o usuário pelo e-mail
        oauth_user = self.search([('login', '=', email)], limit=1)


        if oauth_user:
            print("Usuário encontrado. Preenchendo dados OAuth.")
            # 2. Atualizar os campos OAuth do usuário
            oauth_user.write({
                'oauth_provider_id': provider,
                'oauth_uid': oauth_uid,
                'oauth_access_token': params['access_token']
            })
            return oauth_user.login

        # Se o usuário não for encontrado, nega o login
        print("Usuário OAuth não encontrado. Login negado.")
        raise AccessDenied("Usuário não cadastrado no sistema.")