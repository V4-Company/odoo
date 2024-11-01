from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
import requests
from odoo.addons.auth_oauth.controllers.main import OAuthLogin
from odoo import api, models, fields, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo import api, models, _
from odoo.exceptions import AccessDenied, UserError
import requests
import json
from odoo import api, models, _
from odoo.exceptions import AccessDenied, UserError
import requests
import json
from werkzeug.http import parse_www_authenticate_header
import logging

_logger = logging.getLogger(__name__)
class UserAccessManager(models.Model):
    _inherit = 'res.users'
    last_name = fields.Char(string="Sobrenome")
    job_title = fields.Char(string="Cargo")
    start_date = fields.Date(string="Data de início")
    salary = fields.Float(string="Remuneração")
    email_corp = fields.Char(string="E-mail corporativo")
    responsable = fields.Char(string="Departamento")
    stream = fields.Char(string="Value Strem")
    art = fields.Char(string="ART")
    stream_align = fields.Char(string="Stream Align")
    direct_leader = fields.Char(string="Liderança direta")
    contract_model = fields.Char(string="Modelo de contratação")
    work_model = fields.Char(string="Modelo de Trabalho")
    email_pessoal = fields.Char(string="E-mail pessoal")
    telefone = fields.Char(string="Telefone")
    cpf = fields.Char(string="CPF")
    rg = fields.Char(string="RG")
    birth_date = fields.Date(string="Data de nascimento")
    logradouro = fields.Char(string="Logradouro")
    numero = fields.Char(string="Número")
    complemento = fields.Char(string="Complemento")
    bairro = fields.Char(string="Bairro")
    cidade = fields.Char(string="Cidade")
    estado = fields.Char(string="Estado")
    cep = fields.Char(string="CEP")
    grau_escola = fields.Char(string="Grau de escolaridade")
    cnpj = fields.Char(string="CNPJ")
    razao_social = fields.Char(string="Razão social")
    estado_civil = fields.Char(string="Estado civil")
    cor = fields.Char(string="Cor ou raça/etnia")
    deficiencia_bool = fields.Boolean(string="Possui alguma deficiência")
    deficiencia = fields.Char(string="Qual sua  deficiência")
    gender = fields.Selection([('M', 'Masculino'), ('F', 'Feminino')], string="Gênero")
    sexo = fields.Char(string="Sexo")
    orientacao = fields.Char(string="Orientação sexual")
    def create_user(self):
        """Cria um novo usuário com base no formulário"""
        for record in self:
            if not record.login:
                raise ValidationError("O login é obrigatório para criar um usuário.")
            
            if not record.password:
                raise ValidationError("A senha é obrigatória para criar um usuário.")

            # Criar o usuário com todos os campos necessários, incluindo a senha
            self.create({
                'name': record.name,
                'login': record.login,
                'password': record.password,  # Inclui a senha diretamente na criação
                'groups_id': [(6, 0, record.groups_id.ids)],
                'job_title': record.job_title,
                'active': record.active,
            })

    def set_password(self, new_password):
        """Atualiza a senha do usuário"""
        self.ensure_one()
        self.write({'password': new_password})

    def toggle_active(self):
        """Ativa ou desativa o usuário"""
        self.active = not self.active
        
        
    def action_next_step(self):
        """ Redireciona o usuário para a página 2 (Informações de Contato) """
        return {
            'type': 'ir.actions.act_window',
            'name': 'Informações de Contato',
            'res_model': 'res.users',
            'view_mode': 'form',
            'view_id': self.env.ref('res.users.view_step_2').id,
            'target': 'current',
            'res_id': self.id,
        }

    def action_previous_step(self):
        """ Redireciona o usuário para a página 1 (Informações Pessoais) """
        return {
            'type': 'ir.actions.act_window',
            'name': 'Informações Pessoais',
            'res_model': 'res.users',
            'view_mode': 'form',
            'view_id': self.env.ref('res.users.view_step_1').id,
            'target': 'current',
            'res_id': self.id,
        }

    def action_save(self):
        """ Lógica para salvar o registro """
        self.ensure_one()
        # Adicione sua lógica de validação ou salvamento aqui
        return True
    
    
    