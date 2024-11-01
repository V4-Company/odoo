from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError
import base64
import xml.etree.ElementTree as ET

def format_currency(value):
    return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

class NFEmissionController(http.Controller):

    @http.route('/nota-fiscal/create', type='http', auth="public", website=True, methods=['GET'])
    def render_nf_emission_create_form(self, **kwargs):
        """Renderiza o formulário de criação de Nota Fiscal"""
        users = request.env['res.users'].sudo().search([])  # Buscar todos os usuários
        return request.render('nfe_attachment_copy.nf_emission_create_form', {
            'users': users  # Passar os usuários para o template
        })

    # Rota para processar a criação do registro
    @http.route('/nota-fiscal/create', type='http', auth="public", website=True, methods=['POST'])
    def submit_nf_emission_create_form(self, **kwargs):
        """Processa a submissão do formulário de criação de Nota Fiscal"""
        user_id = int(kwargs.get('user_id'))
        valor_nf = kwargs.get('valor_nf')
        mes_ref = kwargs.get('mes_ref')
        description = kwargs.get('description')

        # Validações básicas
        if not user_id or not valor_nf or not mes_ref:
            raise ValidationError("Todos os campos obrigatórios devem ser preenchidos.")

        # Criar o registro com estado inicial 'draft'
        request.env['nf.emission'].sudo().create({
            'user_id': user_id,
            'valor_nf': valor_nf,
            'mes_ref': mes_ref,
            'description': description,
            'state': 'draft'  # Sempre criar em draft
        })

        # Redireciona para uma página de sucesso ou outra página, se preferir
        return request.redirect('/nota-fiscal/create/success')


    @http.route('/nota-fiscal/create/success', type='http', auth="public", website=True)
    def form_success(self):
        """Página de sucesso após submissão"""
        return request.render('nfe_attachment_copy.nf_emission_success')

    @http.route('/form/error', type='http', auth="public", website=True)
    def form_error(self):
        """Página de erro após submissão"""
        return request.render('website_custom_form.nf_emission_error')
    
    
    @http.route('/nota-fiscal/list', type='http', auth="public", website=True)
    def list_nf_emission(self, **kwargs):
        """Exibe a lista de Notas Fiscais emitidas"""
        # Busca todos os registros de nf.emission
        records = request.env['nf.emission'].sudo().search([])

        # Renderiza o template com os registros
        return request.render('nfe_attachment_copy.nf_emission_list', {
            'records': records
        })
        
        
        


    @http.route('/nota-fiscal/send-nf', type='http', auth="public", website=True)
    def list_nf_emission_with_button(self, **kwargs):
        """Lista de Notas Fiscais com botões de ação."""
        user_id = request.env.user.id
        records = request.env['nf.emission'].sudo().search([('user_id', '=', user_id)], order='mes_ref desc')

        # Criar uma lista com os registros e os valores formatados
        records_data = [
            {
                'mes_ref': record.mes_ref.strftime('%m/%Y') if record.mes_ref else '',
                'valor_nf': format_currency(record.valor_nf),
                'bonus': format_currency(record.bonus),
                'desconto': format_currency(record.desconto),
                'valor_total': format_currency(record.valor_total),
                'state': record.state,
                'id': record.id,
                'user_id': record.user_id.name,
                'description': record.description,
            }
            for record in records
        ]

        return request.render('nfe_attachment_copy.nf_emission_list_with_button', {'records': records_data})
        
    # Rota para exibir o formulário (GET)
    # @http.route('/nota-fiscal/attach/<int:id>', type='http', auth="public", website=True)
    # def attach_nf_emission_form(self, id, **kwargs):
    #     """Exibe o formulário para anexar o PDF a uma Nota Fiscal"""
    #     record = request.env['nf.emission'].sudo().browse(id)
    #     return request.render('nfe_attachment_copy.nf_emission_attach_form', {
    #         'record': record
    #     })

    # Rota para processar o upload do arquivo (POST)
    def get_namespace(self, element):
        """Extrai o namespace do elemento raiz, se presente"""
        match = ET.ElementTree(element).getroot().tag
        if '}' in match:
            return match.split('}')[0] + '}'  # Ex: {http://www.portalfiscal.inf.br/nfe}
        return ''  # Retorna string vazia se não houver namespace

    @http.route('/nota-fiscal/attach/<int:id>/submit', type='http', auth="public", website=True, methods=['POST'])
    def submit_attach_nf_emission(self, id, **kwargs):
        """Processa o upload do arquivo XML de Nota Fiscal para o registro"""
        print(f"Função acionada para o registro com ID {id}")

        # Obter o registro correspondente e os registros do usuário
        record = request.env['nf.emission'].sudo().browse(id)
        records = request.env['nf.emission'].sudo().search(
            [('user_id', '=', request.env.user.id)], order='mes_ref desc'
        )

        # Transformar registros em dicionários formatados para a view
        def format_record(record):
            return {
                'id': record.id,
                'mes_ref': record.mes_ref.strftime('%m/%Y') if record.mes_ref else '',
                'valor_nf': f"R$ {record.valor_nf:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                'bonus': f"R$ {record.bonus:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                'desconto': f"R$ {record.desconto:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                'valor_total': f"R$ {record.valor_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                'state': record.state,
                'description': record.description or '',
                'user_id': record.user_id.name,
            }

        records_data = [format_record(r) for r in records]

        # Variável para mensagens de erro
        error_message = None

        # Obter o arquivo enviado no formulário
        uploaded_file = kwargs.get('nf_file')
        if not uploaded_file:
            error_message = "Você deve anexar um arquivo antes de enviar."
            print(error_message)
            return request.render('nfe_attachment_copy.nf_emission_list_with_button', {
                'records': records_data,
                'error': error_message,
            })

        # Ler o conteúdo do arquivo
        file_data = uploaded_file.read()

        # Verificar se é um arquivo XML
        try:
            tree = ET.ElementTree(ET.fromstring(file_data))
            root = tree.getroot()
            namespace = self.get_namespace(root)

            # Validar os campos do XML
            emitente_cnpj_element = root.find(f'.//{namespace}IdentificacaoPrestador/{namespace}Cnpj')
            if emitente_cnpj_element is None:
                raise ValueError("CNPJ do emitente não encontrado no XML.")
            cnpj_usuario_xml = emitente_cnpj_element.text

            valor_nf_xml = root.find(f'.//{namespace}Servico/{namespace}Valores/{namespace}ValorServicos')
            if valor_nf_xml is None:
                raise ValueError("Valor da NF não encontrado no XML.")
            valor_nf_xml = valor_nf_xml.text

            cnpj_cliente_xml = root.find(f'.//{namespace}IdentificacaoTomador/{namespace}CpfCnpj/{namespace}Cnpj')
            if cnpj_cliente_xml is None:
                raise ValueError("CNPJ do cliente não encontrado no XML.")
            cnpj_cliente_xml = cnpj_cliente_xml.text

        except ET.ParseError:
            error_message = "O arquivo enviado não é um XML válido."
            print(error_message)
            return request.render('nfe_attachment_copy.nf_emission_list_with_button', {
                'records': records_data,
                'error': error_message,
            })

        except ValueError as e:
            error_message = str(e)
            print(error_message)
            return request.render('nfe_attachment_copy.nf_emission_list_with_button', {
                'records': records_data,
                'error': error_message,
            })

        # Validar CNPJ e valores
        cnpj_usuario_odoo = request.env.user.cnpj
        CNPJ_CLIENTE_FIXO = "12345678000199"

        if cnpj_usuario_xml != cnpj_usuario_odoo:
            error_message = f"CNPJ do usuário no XML ({cnpj_usuario_xml}) não corresponde ao registrado ({cnpj_usuario_odoo})."
            print(error_message)
            return request.render('nfe_attachment_copy.nf_emission_list_with_button', {
                'records': records_data,
                'error': error_message,
            })

        if cnpj_cliente_xml != CNPJ_CLIENTE_FIXO:
            error_message = f"CNPJ da V4 incorreto: esperado {CNPJ_CLIENTE_FIXO}, recebido {cnpj_cliente_xml}."
            print(error_message)
            return request.render('nfe_attachment_copy.nf_emission_list_with_button', {
                'records': records_data,
                'error': error_message,
            })

        if format(record.valor_total,".2f") != valor_nf_xml:
            error_message = f"Valor do serviço divergente: esperado {format(record.valor_total,".2f")}, recebido {valor_nf_xml}."
            print(error_message)
            return request.render('nfe_attachment_copy.nf_emission_list_with_button', {
                'records': records_data,
                'error': error_message,
            })

        # Codificar o arquivo e atualizar o registro
        encoded_file = base64.b64encode(file_data)
        record.sudo().write({
            'nf_file': encoded_file,
            'nf_filename': uploaded_file.filename,
            'state': 'done',
        })

        # Redirecionar para a lista após sucesso
        return request.redirect('/nota-fiscal/send-nf')
