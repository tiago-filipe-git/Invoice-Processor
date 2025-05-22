import streamlit as st
import requests
import base64
import json # Certifica-te que json está importado
import io

# Configure page
st.set_page_config(page_title="Invoice Processor", page_icon="📄", layout="wide")
st.title("Invoice Processor")

# Configurações do servidor
SERVER_URL = "http://localhost:8000"
APP_NAME = "invoices"
USER_ID = "user0"
SESSION_ID = "session0"

# Inicializa variáveis de estado
if 'session_created' not in st.session_state:
    st.session_state.session_created = False
if 'invoice_data' not in st.session_state:
    st.session_state.invoice_data = {}
if 'uploaded_pdf' not in st.session_state:
    st.session_state.uploaded_pdf = None

# Função para criar uma sessão
def create_session():
    try:
        session_url = f"{SERVER_URL}/apps/{APP_NAME}/users/{USER_ID}/sessions/{SESSION_ID}"
        payload = json.dumps({"state": {}})
        headers = {'Content-Type': 'application/json'}

        response = requests.get(session_url, headers=headers)

        if response.status_code == 404:
            response = requests.post(session_url, headers=headers, data=payload)
            response.raise_for_status() # Lança exceção se POST falhar

        st.session_state.session_created = True # Marcar sessão como criada
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de rede ao tentar criar/verificar sessão: {e}")
        st.session_state.session_created = False
        return False
    except Exception as e:
        st.error(f"Erro inesperado ao criar sessão: {e}")
        st.session_state.session_created = False
        return False

# Função para processar o formulário de edição
def process_form_submission():
    # Atualiza o dicionário com os valores *atuais* do formulário
    # Usa as chaves dos widgets (key="...") para obter os valores
    st.session_state.invoice_data = {
        "DocumentType": st.session_state.get("doc_type", ""),
        "DocumentID": st.session_state.get("doc_id", ""),
        "DocumentDate": st.session_state.get("doc_date", ""),
        "Language": st.session_state.get("language", ""),

        "CurrencyCode": st.session_state.get("currency", ""),
        # Nota: Se os valores numéricos devem ser guardados como números,
        # seria preciso converter aqui (e validar), mas text_input devolve string.
        # Para simplificar, vamos manter strings por agora.
        "TotalDocumentAmount": st.session_state.get("total_amount", ""),
        "NetDocumentAmount": st.session_state.get("net_amount", ""),
        "VATAmount": st.session_state.get("vat_amount", ""),

        "VendorName": st.session_state.get("vendor_name", ""),
        "VendorTaxID": st.session_state.get("vendor_tax_id", ""),
        "VendorCountryCode": st.session_state.get("vendor_country", ""),

        "CustomerName": st.session_state.get("customer_name", ""),
        "CustomerTaxID": st.session_state.get("customer_tax_id", ""),
        "CustomerCountryCode": st.session_state.get("customer_country", ""),

        # Adicionar campos do JSON que não estavam no formulário original,
        # se também quiseres guardá-los após edição (requer adicioná-los ao form)
        # Exemplo: "PONumber": st.session_state.get("po_number", ""),
    }
    st.success("Dados atualizados com sucesso!")

# Tentar criar sessão automaticamente no início
if not st.session_state.session_created:
    with st.spinner("A estabelecer ligação ao sistema..."):
        create_session() # A função agora atualiza session_created

# Conteúdo principal
if st.session_state.session_created:
    # Mensagem de boas-vindas se não houver PDF processado
    if not st.session_state.uploaded_pdf:
        st.write("Bem-vindo! Carregue o seu PDF de fatura.")

    # File uploader
    uploaded_file = st.file_uploader("Upload Invoice PDF", type=['pdf'], label_visibility="collapsed")

    # Processa o PDF automaticamente quando carregado
    if uploaded_file is not None:
        # Limpa dados antigos se um novo ficheiro for carregado
        # st.session_state.invoice_data = {} # Movido para dentro do sucesso da API
        # st.session_state.uploaded_pdf = None # Movido para dentro do sucesso da API

        with st.spinner("Processando invoice..."):
            try:
                pdf_bytes = uploaded_file.getvalue()
                pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

                # Payload para solicitação
                payload = {
                    "app_name": APP_NAME,
                    "user_id": USER_ID,
                    "session_id": SESSION_ID,
                    "new_message": {
                        "role": "user",
                        "parts": [
                            {"text": "Extract information from invoice"},
                            {
                                "inline_data": {
                                    "mime_type": "application/pdf",
                                    "data": pdf_base64
                                }
                            }
                        ]
                    }
                }

                # Enviar solicitação para o servidor
                headers = {'Content-Type': 'application/json'}
                response = requests.post(
                    f"{SERVER_URL}/run",
                    headers=headers,
                    data=json.dumps(payload),
                    timeout=90 # Aumentar timeout pode ser útil
                )
                response.raise_for_status() # Lança exceção para erros HTTP (4xx, 5xx)


                # --- LÓGICA DE PROCESSAMENTO DA RESPOSTA (VERSÃO 3) ---
                response_data = response.json()

                # 1. Verificar se a resposta é uma lista e tem elementos
                if isinstance(response_data, list) and len(response_data) > 0:
                    first_element = response_data[0] # Aceder ao primeiro objeto da lista

                    # 2. Navegar pela estrutura aninhada, verificando cada passo
                    if isinstance(first_element, dict) and 'content' in first_element \
                       and isinstance(first_element['content'], dict) and 'parts' in first_element['content'] \
                       and isinstance(first_element['content']['parts'], list) and len(first_element['content']['parts']) > 0 \
                       and isinstance(first_element['content']['parts'][0], dict) and 'text' in first_element['content']['parts'][0] \
                       and isinstance(first_element['content']['parts'][0]['text'], str):

                        json_string_with_fences = first_element['content']['parts'][0]['text']

                        # 3. Remover as marcas de formatação ```json ... ```
                        # Encontra o início '{' e o fim '}' do JSON real
                        start_index = json_string_with_fences.find('{')
                        end_index = json_string_with_fences.rfind('}')

                        if start_index != -1 and end_index != -1 and end_index > start_index:
                            cleaned_json_string = json_string_with_fences[start_index : end_index + 1]

                            # 4. Tentar fazer parse da string JSON limpa
                            try:
                                extracted_data = json.loads(cleaned_json_string)

                                if isinstance(extracted_data, dict):
                                    # Sucesso! Limpar estado antigo e preencher com novos dados
                                    st.session_state.invoice_data = {}
                                    st.session_state.uploaded_pdf = pdf_bytes # Guardar PDF atual

                                    # Mapeamento (o mesmo de antes)
                                    form_keys_mapping = {
                                        "doc_type": "DocumentType", "doc_id": "DocumentID", "doc_date": "DocumentDate", "language": "Language",
                                        "currency": "CurrencyCode", "total_amount": "TotalDocumentAmount", "net_amount": "NetDocumentAmount", "vat_amount": "VATAmount",
                                        "vendor_name": "VendorName", "vendor_tax_id": "VendorTaxID", "vendor_country": "VendorCountryCode",
                                        "customer_name": "CustomerName", "customer_tax_id": "CustomerTaxID", "customer_country": "CustomerCountryCode"
                                        # Adicionar mais se necessário
                                    }

                                    # Preencher st.session_state.invoice_data, tratando None
                                    for form_key, json_key in form_keys_mapping.items():
                                        value = extracted_data.get(json_key)
                                        st.session_state.invoice_data[json_key] = "" if value is None else value

                                    st.success("Invoice processada e dados extraídos!")

                                else:
                                    st.error("O conteúdo JSON extraído não é um objeto (dicionário) esperado.")
                                    st.write("Dados extraídos:", extracted_data)
                                    st.session_state.invoice_data = {}
                                    st.session_state.uploaded_pdf = None

                            except json.JSONDecodeError as e:
                                st.error(f"Erro ao interpretar a string JSON interna (após remover formatação): {e}")
                                st.write("String que falhou no parse:", cleaned_json_string)
                                st.session_state.invoice_data = {}
                                st.session_state.uploaded_pdf = None
                        else:
                            st.error("Não foi possível encontrar o objeto JSON {...} dentro das marcas de formatação no campo 'text'.")
                            st.write("Conteúdo original de 'text':", json_string_with_fences)
                            st.session_state.invoice_data = {}
                            st.session_state.uploaded_pdf = None
                    else:
                        # Mensagem de erro mais específica sobre onde a estrutura falhou
                        st.error("Estrutura de resposta inesperada. Não foi possível encontrar 'content.parts[0].text'.")
                        st.write("Primeiro elemento da resposta:", first_element)
                        st.session_state.invoice_data = {}
                        st.session_state.uploaded_pdf = None
                else:
                    st.error("Estrutura de resposta inesperada: a resposta principal não é uma lista JSON com pelo menos um elemento.")
                    st.write("Resposta completa recebida:", response_data)
                    st.session_state.invoice_data = {}
                    st.session_state.uploaded_pdf = None

            except requests.exceptions.Timeout:
                st.error("Timeout: O servidor demorou muito para responder.")
            except requests.exceptions.RequestException as e:
                st.error(f"Erro de comunicação com o servidor: {e}")
            except Exception as e:
                st.error(f"Erro inesperado ao processar invoice: {str(e)}")
                # Limpar estado em caso de erro genérico durante o processamento
                st.session_state.invoice_data = {}
                st.session_state.uploaded_pdf = None


    # Formulário para edição de dados (só mostra se houver dados e um PDF carregado)
    # A condição 'if st.session_state.invoice_data' garante que só mostra se a extração foi bem sucedida
    if st.session_state.invoice_data and st.session_state.uploaded_pdf:
        col1, col2 = st.columns(2)

        with col1:
            # Usar st.session_state.invoice_data.get(JSON_KEY, "") para preencher
            # Usar key="widget_key" para identificar cada campo na submissão
            with st.form("invoice_details"):
                st.header("Detalhes da Invoice (Editável)")

                # Informações do Documento
                st.subheader("Informações do Documento")
                col_doc1, col_doc2 = st.columns(2)
                with col_doc1:
                    st.text_input("Tipo de Documento",
                                  value=st.session_state.invoice_data.get("DocumentType", ""),
                                  key="doc_type")
                    st.text_input("ID do Documento",
                                  value=st.session_state.invoice_data.get("DocumentID", ""),
                                  key="doc_id")
                with col_doc2:
                    st.text_input("Data do Documento",
                                  value=st.session_state.invoice_data.get("DocumentDate", ""),
                                  key="doc_date")
                    st.text_input("Idioma",
                                  value=st.session_state.invoice_data.get("Language", ""),
                                  key="language")

                st.subheader("Informações Financeiras")
                col_fin1, col_fin2 = st.columns(2)
                with col_fin1:
                    st.text_input("Moeda",
                                  value=st.session_state.invoice_data.get("CurrencyCode", ""),
                                  key="currency")
                    st.text_input("Valor Total", # TotalDocumentAmount
                                  # Nota: st.number_input seria melhor para números, mas exige mais validação
                                  value=st.session_state.invoice_data.get("TotalDocumentAmount", ""),
                                  key="total_amount")
                with col_fin2:
                    st.text_input("Valor Líquido", # NetDocumentAmount
                                  value=st.session_state.invoice_data.get("NetDocumentAmount", ""),
                                  key="net_amount")
                    st.text_input("Valor IVA", # VATAmount
                                  value=st.session_state.invoice_data.get("VATAmount", ""),
                                  key="vat_amount")

                st.subheader("Informações do Fornecedor")
                col_vendor1, col_vendor2 = st.columns(2)
                with col_vendor1:
                    st.text_input("Nome do Fornecedor",
                                  value=st.session_state.invoice_data.get("VendorName", ""),
                                  key="vendor_name")
                    st.text_input("ID Fiscal do Fornecedor",
                                  value=st.session_state.invoice_data.get("VendorTaxID", ""),
                                  key="vendor_tax_id")
                with col_vendor2:
                    st.text_input("País do Fornecedor",
                                  value=st.session_state.invoice_data.get("VendorCountryCode", ""),
                                  key="vendor_country")

                st.subheader("Informações do Cliente")
                col_customer1, col_customer2 = st.columns(2)
                with col_customer1:
                    st.text_input("Nome do Cliente",
                                  value=st.session_state.invoice_data.get("CustomerName", ""),
                                  key="customer_name")
                    st.text_input("ID Fiscal do Cliente",
                                  value=st.session_state.invoice_data.get("CustomerTaxID", ""),
                                  key="customer_tax_id")
                with col_customer2:
                    st.text_input("País do Cliente",
                                  value=st.session_state.invoice_data.get("CustomerCountryCode", ""),
                                  key="customer_country")

                # Adicionar aqui mais campos se necessário, ex: PO Number
                # st.text_input("PO Number",
                #               value=st.session_state.invoice_data.get("PONumber", ""),
                #               key="po_number")


                # Botão de submissão do formulário
                submitted = st.form_submit_button("Confirmar Alterações", on_click=process_form_submission)

        with col2:
            st.header("PDF Carregado")
            # Exibe o PDF usando um iframe
            # É importante usar os bytes guardados em session_state para garantir que é o ficheiro correto
            pdf_display_bytes = st.session_state.uploaded_pdf
            pdf_display_base64 = base64.b64encode(pdf_display_bytes).decode()
            pdf_display_html = f'<iframe src="data:application/pdf;base64,{pdf_display_base64}" width="100%" height="800px" type="application/pdf"></iframe>'
            st.markdown(pdf_display_html, unsafe_allow_html=True)
            st.download_button(
                label="Baixar PDF Original",
                data=pdf_display_bytes,
                file_name=f"invoice_{st.session_state.invoice_data.get('DocumentID', 'unknown')}.pdf", # Nomeia com ID se disponível
                mime="application/pdf"
            )


elif not st.session_state.session_created:
    # Mensagem se a criação da sessão falhou inicialmente
    st.error("Falha ao conectar ao sistema. Verifique se o servidor está a correr e tente recarregar a página.")