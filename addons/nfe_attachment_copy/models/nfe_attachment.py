from odoo import models, fields, api
from odoo.exceptions import ValidationError
import mimetypes


class NFEmission(models.Model):
    _name = 'nf.emission'
    _description = 'Nota Fiscal Emission'

    user_id = fields.Many2one('res.users', string="Usuário", required=True, default=lambda self: self.env.user)
    nf_file = fields.Binary(string="Nota Fiscal (PDF)", readonly=False, attachment=True)
    nf_filename = fields.Char(string="Nome do Arquivo")
    description = fields.Text(string="Descrição")
    state = fields.Selection([
        ('draft', 'Não emitido'),
        ('done', 'Emitido')
    ], default='draft', string="Estado")
    
    # Alterado para float com precisão de 2 casas decimais
    valor_nf = fields.Float(string='Valor da Nota Fiscal', digits=(12, 2))
    bonus = fields.Float(string='Valor do bônus', digits=(12, 2))
    desconto = fields.Float(string='Valor do desconto', digits=(12, 2))
    mes_ref = fields.Date(string="Mês de referência")

    # Novo campo computado com precisão
    valor_total = fields.Float(string='Valor Total', compute='_compute_valor_total', store=True, digits=(12, 2))


    @api.depends('valor_nf', 'bonus', 'desconto')
    def _compute_valor_total(self):
        for record in self:
            record.valor_total = (record.valor_nf + record.bonus) - record.desconto
            

    def action_trigger_popup(self):
        """Mostra o pop-up baseado no estado do registro"""
        for record in self:
            if record.state != "done":
                # Abrir o formulário para anexar a nota fiscal
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Enviar Nota Fiscal',
                    'res_model': 'nf.emission',
                    'view_mode': 'form',
                    'view_id': self.env.ref('nfe_attachment_copy.view_nf_emission_form_attach_pdf').id,
                    'target': 'new',
                    'res_id': record.id,
                    'context': self.env.context,
                }
            else:
                # Abrir o pop-up de aviso
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'AVISO!',
                    'res_model': 'nf.emission',
                    'view_mode': 'form',
                    'view_id': self.env.ref('nfe_attachment_copy.view_nf_emission_warning_form').id,
                    'target': 'new',
                    'res_id': record.id,
                    'context': self.env.context,
                }
# Função para ser acionada pelo botão "Salvar"
    def action_save_pdf(self):
        """Função acionada pelo botão de salvar. Verifica se o arquivo foi anexado."""
        print(self)
        for record in self:
            print(record.nf_filename)
            if not record.nf_file:
                raise ValidationError("Você deve anexar um arquivo antes de salvar.")
            
            record.state = 'done'
            break

    # Função onchange para verificar se o arquivo anexado é um PDF
    @api.onchange('nf_file')
    def _onchange_nf_file(self):
        """Verifica automaticamente se o arquivo anexado é um PDF"""
        if self.nf_file:
            # Tentar determinar o tipo MIME com base no nome do arquivo
            mime_type, _ = mimetypes.guess_type(self.nf_filename or '')
            print(f"MIME Type: {mime_type}")

            # Verificar se o arquivo anexado é um PDF
            if mime_type != 'application/pdf':
                raise ValidationError("O arquivo anexado deve ser um PDF.")