from odoo import http
from odoo.http import request
import json
import logging
import base64
import functools
import json
import logging
import os

import werkzeug.urls
import werkzeug.utils
from werkzeug.exceptions import BadRequest

from odoo import api, http, SUPERUSER_ID, _
from odoo.exceptions import AccessDenied
from odoo.http import request, Response
from odoo import registry as registry_get
from odoo.tools.misc import clean_context
from odoo.addons.auth_oauth.controllers.main import OAuthController
from odoo.addons.auth_signup.controllers.main import AuthSignupHome as Home
from odoo.addons.web.controllers.utils import ensure_db, _get_login_redirect_url

_logger = logging.getLogger(__name__)
def fragment_to_query_string(func):
    @functools.wraps(func)
    def wrapper(self, *a, **kw):
        kw.pop('debug', False)
        if not kw:
            return Response("""<html><head><script>
                var l = window.location;
                var q = l.hash.substring(1);
                var r = l.pathname + l.search;
                if(q.length !== 0) {
                    var s = l.search ? (l.search === '?' ? '' : '&') : '?';
                    r = l.pathname + l.search + s + q;
                }
                if (r == l.pathname) {
                    r = '/';
                }
                window.location = r;
            </script></head><body></body></html>""")
        return func(self, *a, **kw)
    return wrapper

class OAuthControllerCustom(OAuthController):

    @http.route('/auth_oauth/signin', type='http', auth='none')
    @fragment_to_query_string
    def signin(self, **kw):
        state = json.loads(kw['state'])
        print("entrou na função sigin")
        # make sure request.session.db and state['d'] are the same,
        # update the session and retry the request otherwise
        dbname = state['d']
        if not http.db_filter([dbname]):
            return BadRequest()
        ensure_db(db=dbname)

        provider = state['p']
        request.update_context(**clean_context(state.get('c', {})))
        try:
            # auth_oauth may create a new user, the commit makes it
            # visible to authenticate()'s own transaction below
            _, login, key = request.env['res.users'].with_user(SUPERUSER_ID).auth_oauth(provider, kw)
            request.env.cr.commit()
            pre_uid = request.session.authenticate(dbname, login, key)
            action = state.get('a')
            menu = state.get('m')
            redirect = werkzeug.urls.url_unquote_plus(state['r']) if state.get('r') else False
            url = '/web'
            if redirect:
                url = redirect
            elif action:
                url = '/web#action=%s' % action
            elif menu:
                url = '/web#menu_id=%s' % menu
                                
            user = request.env['res.users'].sudo().browse(pre_uid)
            print("user", user.login)
            print("senha do cara", user.password_set)
            print(user.password_set == False)
            if user.password_set == False:
                print("trigou senha set")
                url = '/my_custom_url_for_setting_password'
            print("passou")
            pre_uid = request.session.authenticate(dbname, login, key)
            resp = request.redirect(_get_login_redirect_url(pre_uid, url), 303)
            resp.autocorrect_location_header = False

            # Since /web is hardcoded, verify user has right to land on it
            if werkzeug.urls.url_parse(resp.location).path == '/web' and not request.env.user._is_internal():
                resp.location = '/'
            return resp
        except AttributeError:  # TODO juc master: useless since ensure_db()
            # auth_signup is not installed
            _logger.error("auth_signup not installed on database %s: oauth sign up cancelled.", dbname)
            url = "/web/login?oauth_error=1"
        except AccessDenied:
            # oauth credentials not valid, user could be on a temporary session
            _logger.info('OAuth2: access denied, redirect to main page in case a valid session exists, without setting cookies')
            url = "/web/login?oauth_error=3"
        except Exception:
            # signup error
            _logger.exception("Exception during request handling")
            url = "/web/login?oauth_error=2"

        redirect = request.redirect(url, 303)
        redirect.autocorrect_location_header = False
        return redirect
    
    #criação de senha
    @http.route('/my_custom_url_for_setting_password', type='http', auth='public', website=True)
    def setting_password(self, **kw):
        # Obtém os parâmetros da requisição
        password = kw.get('password')
        confirm_password = kw.get('confirm_password')

        # Verifica se ambos os campos de senha estão presentes
        if not password or not confirm_password:
            error_message = 'Both password and confirmation password are required.'
            return request.render('cargo_control.setting_password_template', {'error_message': error_message})

        # Verifica se as senhas correspondem
        if password != confirm_password:
            error_message = "Passwords don't match."
            return request.render('cargo_control.setting_password_template', {'error_message': error_message})

        # Adiciona uma validação mínima para a senha
        if len(password) < 8:
            error_message = "Password must be at least 8 characters long."
            return request.render('cargo_control.setting_password_template', {'error_message': error_message})

        try:
            # Garante que o usuário atual está autenticado
            if not request.session.uid:
                error_message = "User is not logged in."
                return request.render('cargo_control.setting_password_template', {'error_message': error_message})

            # Obtém o usuário atual usando sudo()
            user = request.env['res.users'].sudo().browse(request.session.uid)

            # Altera a senha do usuário
            user.write({'password': password})

            # Reautentica o usuário para garantir que a sessão seja válida
            # request.session.authenticate(request.db, user.login, password)

            # Redireciona para a interface web do Odoo
            return request.redirect('/web/login',303)

        except Exception as e:
            # Captura erros e retorna uma mensagem de erro
            error_message = f"An error occurred: {str(e)}"
            return request.render('cargo_control.setting_password_template', {'error_message': error_message})