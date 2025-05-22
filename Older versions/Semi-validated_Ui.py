import streamlit as st
import requests
import base64
import json
import io

# Importar o validador (assumindo que está no mesmo diretório)
try:
    from first_validator import InvoiceValidator, ValidationStatus
    VALIDATOR_AVAILABLE = True
except ImportError:
    VALIDATOR_AVAILABLE = False
    st.warning("⚠️ invoice_validator.py não encontrado. Validação desabilitada.")

# Configure page
st.set_page_config(page_title="Invoice Processor", page_icon="📄", layout="wide")

# CSS personalizado para melhorar a aparência
st.markdown("""
<style>
.validation-good {
    color: #28a745;
    font-weight: bold;
}
.validation-warning {
    color: #ffc107;
    font-weight: bold;
}
.validation-bad {
    color: #dc3545;
    font-weight: bold;
}
.field-container {
    border: 1px solid #ddd;
    border-radius: 5px;
    padding: 10px;
    margin: 5px 0;
    background-color: #f9f9f9;
}
.field-label {
    font-weight: bold;
    margin-bottom: 5px;
}
.status-indicator {
    float: right;
    font-size: 16px;
}
.pdf-container {
    border: 2px solid #ddd;
    border-radius: 10px;
    padding: 10px;
    background-color: #f8f9fa;
}
.summary-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 10px;
    margin: 10px 0;
    text-align: center;
}
.metric-box {
    background: white;
    border-radius: 8px;
    padding: 15px;
    margin: 5px;
    text-align: center;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

st.title("📄 Invoice Processor com Validação")

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
if 'validation_results' not in st.session_state:
    st.session_state.validation_results = {}
if 'pdf_filename' not in st.session_state:
    st.session_state.pdf_filename = ""

# Função para criar uma sessão
def create_session():
    try:
        session_url = f"{SERVER_URL}/apps/{APP_NAME}/users/{USER_ID}/sessions/{SESSION_ID}"
        payload = json.dumps({"state": {}})
        headers = {'Content-Type': 'application/json'}

        response = requests.get(session_url, headers=headers)

        if response.status_code == 404:
            response = requests.post(session_url, headers=headers, data=payload)
            response.raise_for_status()

        st.session_state.session_created = True
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de rede ao tentar criar/verificar sessão: {e}")
        st.session_state.session_created = False
        return False
    except Exception as e:
        st.error(f"Erro inesperado ao criar sessão: {e}")
        st.session_state.session_created = False
        return False

# Função para validar dados
def validate_invoice_data():
    """Valida todos os campos dos dados da fatura"""
    if VALIDATOR_AVAILABLE and st.session_state.invoice_data:
        st.session_state.validation_results = InvoiceValidator.validate_all_fields(st.session_state.invoice_data)

# Função para mostrar resumo de validação
def show_validation_summary():
    """Mostra um resumo detalhado do status de validação"""
    if not VALIDATOR_AVAILABLE or not st.session_state.validation_results:
        st.info("ℹ️ Validação não disponível - carregue o arquivo invoice_validator.py")
        return
    
    good_count = sum(1 for result in st.session_state.validation_results.values() 
                    if result.status == ValidationStatus.GOOD)
    warning_count = sum(1 for result in st.session_state.validation_results.values() 
                       if result.status == ValidationStatus.WARNING)
    bad_count = sum(1 for result in st.session_state.validation_results.values() 
                   if result.status == ValidationStatus.BAD)
    
    total_fields = len(st.session_state.validation_results)
    
    # Resumo geral
    st.markdown(f"""
    <div class="summary-card">
        <h3>📊 Resumo de Validação</h3>
        <p>Status geral dos campos extraídos da fatura</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Métricas em colunas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-box">
            <h2 style="color: #333; margin: 0;">{total_fields}</h2>
            <p style="margin: 5px 0; color: #666;">Total Campos</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-box" style="border-left: 4px solid #28a745;">
            <h2 style="color: #28a745; margin: 0;">✅ {good_count}</h2>
            <p style="margin: 5px 0; color: #666;">Válidos</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-box" style="border-left: 4px solid #ffc107;">
            <h2 style="color: #ffc107; margin: 0;">⚠️ {warning_count}</h2>
            <p style="margin: 5px 0; color: #666;">Avisos</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-box" style="border-left: 4px solid #dc3545;">
            <h2 style="color: #dc3545; margin: 0;">❌ {bad_count}</h2>
            <p style="margin: 5px 0; color: #666;">Erros</p>
        </div>
        """, unsafe_allow_html=True)

# Função para criar campo com validação visual
def create_validated_field(label, field_key, current_value=""):
    """Cria um campo de input com status de validação claramente visível"""
    
    # Obter resultado da validação
    validation_result = None
    if VALIDATOR_AVAILABLE and field_key in st.session_state.validation_results:
        validation_result = st.session_state.validation_results[field_key]
    
    # Determinar classe CSS e ícone baseado no status
    if validation_result:
        if validation_result.status == ValidationStatus.GOOD:
            css_class = "validation-good"
            icon = "✅"
            border_color = "#28a745"
        elif validation_result.status == ValidationStatus.WARNING:
            css_class = "validation-warning"  
            icon = "⚠️"
            border_color = "#ffc107"
        else:  # BAD
            css_class = "validation-bad"
            icon = "❌"
            border_color = "#dc3545"
    else:
        css_class = ""
        icon = "ℹ️"
        border_color = "#ddd"
    
    # Container do campo com borda colorida
    st.markdown(f"""
    <div style="border: 2px solid {border_color}; border-radius: 8px; padding: 10px; margin: 8px 0; background-color: white;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
            <strong>{label}</strong>
            <span class="{css_class}">{icon}</span>
        </div>
    """, unsafe_allow_html=True)
    
    # Campo de input
    input_value = st.text_input(
        label="", 
        value=current_value, 
        key=field_key,
        label_visibility="collapsed"
    )
    
    # Mostrar mensagem de validação se houver
    if validation_result and validation_result.message:
        st.markdown(f'<small class="{css_class}">💬 {validation_result.message}</small>', 
                   unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    return input_value

# Tentar criar sessão automaticamente no início
if not st.session_state.session_created:
    with st.spinner("🔄 Estabelecendo ligação ao sistema..."):
        create_session()

# Conteúdo principal
if st.session_state.session_created:
    # Seção de upload
    st.header("📤 Upload da Fatura")
    
    if not st.session_state.uploaded_pdf:
        st.info("👆 Carregue um arquivo PDF da sua fatura para começar o processamento.")
    
    uploaded_file = st.file_uploader(
        "Selecione o arquivo PDF da fatura", 
        type=['pdf'], 
        help="Apenas arquivos PDF são aceitos"
    )

    # Processar PDF quando carregado
    if uploaded_file is not None:
        st.session_state.pdf_filename = uploaded_file.name
        
        with st.spinner("🔄 Processando fatura... Isso pode levar alguns segundos."):
            try:
                pdf_bytes = uploaded_file.getvalue()
                pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

                # Payload para o servidor
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

                # Enviar para servidor
                headers = {'Content-Type': 'application/json'}
                response = requests.post(
                    f"{SERVER_URL}/run",
                    headers=headers,
                    data=json.dumps(payload),
                    timeout=90
                )
                response.raise_for_status()

                # Processar resposta
                response_data = response.json()

                if isinstance(response_data, list) and len(response_data) > 0:
                    first_element = response_data[0]

                    if (isinstance(first_element, dict) and 'content' in first_element and
                        isinstance(first_element['content'], dict) and 'parts' in first_element['content'] and
                        isinstance(first_element['content']['parts'], list) and len(first_element['content']['parts']) > 0 and
                        isinstance(first_element['content']['parts'][0], dict) and 'text' in first_element['content']['parts'][0]):

                        json_string_with_fences = first_element['content']['parts'][0]['text']
                        start_index = json_string_with_fences.find('{')
                        end_index = json_string_with_fences.rfind('}')

                        if start_index != -1 and end_index != -1 and end_index > start_index:
                            cleaned_json_string = json_string_with_fences[start_index:end_index + 1]

                            try:
                                extracted_data = json.loads(cleaned_json_string)

                                if isinstance(extracted_data, dict):
                                    # Salvar dados extraídos
                                    st.session_state.uploaded_pdf = pdf_bytes
                                    st.session_state.invoice_data = {}

                                    # Mapear campos extraídos
                                    field_mapping = {
                                        "DocumentType": "DocumentType",
                                        "DocumentID": "DocumentID", 
                                        "DocumentDate": "DocumentDate",
                                        "Language": "Language",
                                        "CurrencyCode": "CurrencyCode",
                                        "TotalDocumentAmount": "TotalDocumentAmount",
                                        "NetDocumentAmount": "NetDocumentAmount", 
                                        "VATAmount": "VATAmount",
                                        "VendorName": "VendorName",
                                        "VendorTaxID": "VendorTaxID",
                                        "VendorCountryCode": "VendorCountryCode",
                                        "CustomerName": "CustomerName",
                                        "CustomerTaxID": "CustomerTaxID",
                                        "CustomerCountryCode": "CustomerCountryCode"
                                    }

                                    for json_key, form_key in field_mapping.items():
                                        value = extracted_data.get(json_key)
                                        st.session_state.invoice_data[form_key] = "" if value is None else str(value)

                                    # Validar dados extraídos
                                    validate_invoice_data()
                                    
                                    st.success("✅ Fatura processada com sucesso! Dados extraídos e validados.")

                                else:
                                    st.error("❌ Formato de dados inválido extraído da fatura.")

                            except json.JSONDecodeError as e:
                                st.error(f"❌ Erro ao processar dados da fatura: {e}")
                        else:
                            st.error("❌ Não foi possível extrair dados válidos da fatura.")
                    else:
                        st.error("❌ Resposta inesperada do servidor de processamento.")
                else:
                    st.error("❌ Erro na comunicação com o servidor de processamento.")

            except requests.exceptions.Timeout:
                st.error("⏱️ Timeout: O servidor demorou muito para responder. Tente novamente.")
            except requests.exceptions.RequestException as e:
                st.error(f"🌐 Erro de comunicação com o servidor: {e}")
            except Exception as e:
                st.error(f"❌ Erro inesperado ao processar a fatura: {str(e)}")

    # Mostrar formulário de edição se houver dados
    if st.session_state.invoice_data and st.session_state.uploaded_pdf:
        st.markdown("---")
        
        # Mostrar resumo de validação
        show_validation_summary()
        
        st.markdown("---")
        
        # Layout em duas colunas: Formulário + PDF
        col_form, col_pdf = st.columns([3, 2])
        
        with col_form:
            st.header("✏️ Dados da Fatura - Edição e Validação")
            st.info("📝 Revise e edite os campos abaixo. Os ícones indicam o status de validação de cada campo.")
            
            # Formulário editável
            with st.form("invoice_form"):
                # Seção: Informações do Documento
                st.subheader("📋 Informações do Documento")
                
                doc_type = create_validated_field(
                    "Tipo de Documento", 
                    "DocumentType", 
                    st.session_state.invoice_data.get("DocumentType", "")
                )
                
                doc_id = create_validated_field(
                    "ID/Número da Fatura",
                    "DocumentID",
                    st.session_state.invoice_data.get("DocumentID", "")
                )
                
                doc_date = create_validated_field(
                    "Data da Fatura",
                    "DocumentDate", 
                    st.session_state.invoice_data.get("DocumentDate", "")
                )
                
                language = create_validated_field(
                    "Idioma",
                    "Language",
                    st.session_state.invoice_data.get("Language", "")
                )
                
                # Seção: Valores Financeiros
                st.subheader("💰 Informações Financeiras")
                
                currency = create_validated_field(
                    "Código da Moeda",
                    "CurrencyCode",
                    st.session_state.invoice_data.get("CurrencyCode", "")
                )
                
                total_amount = create_validated_field(
                    "Valor Total",
                    "TotalDocumentAmount",
                    st.session_state.invoice_data.get("TotalDocumentAmount", "")
                )
                
                net_amount = create_validated_field(
                    "Valor Líquido (sem IVA)",
                    "NetDocumentAmount",
                    st.session_state.invoice_data.get("NetDocumentAmount", "")
                )
                
                vat_amount = create_validated_field(
                    "Valor do IVA",
                    "VATAmount", 
                    st.session_state.invoice_data.get("VATAmount", "")
                )
                
                # Seção: Fornecedor
                st.subheader("🏢 Dados do Fornecedor")
                
                vendor_name = create_validated_field(
                    "Nome do Fornecedor",
                    "VendorName",
                    st.session_state.invoice_data.get("VendorName", "")
                )
                
                vendor_tax = create_validated_field(
                    "NIF do Fornecedor", 
                    "VendorTaxID",
                    st.session_state.invoice_data.get("VendorTaxID", "")
                )
                
                vendor_country = create_validated_field(
                    "País do Fornecedor",
                    "VendorCountryCode",
                    st.session_state.invoice_data.get("VendorCountryCode", "")
                )
                
                # Seção: Cliente  
                st.subheader("👤 Dados do Cliente")
                
                customer_name = create_validated_field(
                    "Nome do Cliente",
                    "CustomerName",
                    st.session_state.invoice_data.get("CustomerName", "")
                )
                
                customer_tax = create_validated_field(
                    "NIF do Cliente",
                    "CustomerTaxID", 
                    st.session_state.invoice_data.get("CustomerTaxID", "")
                )
                
                customer_country = create_validated_field(
                    "País do Cliente", 
                    "CustomerCountryCode",
                    st.session_state.invoice_data.get("CustomerCountryCode", "")
                )
                
                # Botão de confirmação
                st.markdown("---")
                submitted = st.form_submit_button(
                    "💾 Confirmar e Salvar Alterações",
                    use_container_width=True,
                    type="primary"
                )
                
                # Processar confirmação
                if submitted:
                    # Atualizar dados com valores do formulário
                    st.session_state.invoice_data.update({
                        "DocumentType": st.session_state.get("DocumentType", ""),
                        "DocumentID": st.session_state.get("DocumentID", ""),
                        "DocumentDate": st.session_state.get("DocumentDate", ""),
                        "Language": st.session_state.get("Language", ""),
                        "CurrencyCode": st.session_state.get("CurrencyCode", ""),
                        "TotalDocumentAmount": st.session_state.get("TotalDocumentAmount", ""),
                        "NetDocumentAmount": st.session_state.get("NetDocumentAmount", ""),
                        "VATAmount": st.session_state.get("VATAmount", ""),
                        "VendorName": st.session_state.get("VendorName", ""),
                        "VendorTaxID": st.session_state.get("VendorTaxID", ""),
                        "VendorCountryCode": st.session_state.get("VendorCountryCode", ""),
                        "CustomerName": st.session_state.get("CustomerName", ""),
                        "CustomerTaxID": st.session_state.get("CustomerTaxID", ""),
                        "CustomerCountryCode": st.session_state.get("CustomerCountryCode", "")
                    })
                    
                    # Revalidar
                    validate_invoice_data()
                    
                    st.success("✅ Dados confirmados e salvos com sucesso!")
                    st.balloons()
        
        with col_pdf:
            st.header(f"📄 Fatura Carregada")
            st.info(f"📁 Arquivo: **{st.session_state.pdf_filename}**")
            
            # Mostrar PDF
            pdf_display_bytes = st.session_state.uploaded_pdf
            pdf_base64 = base64.b64encode(pdf_display_bytes).decode()
            
            st.markdown(f"""
            <div class="pdf-container">
                <iframe 
                    src="data:application/pdf;base64,{pdf_base64}" 
                    width="100%" 
                    height="600px" 
                    type="application/pdf"
                    style="border: none; border-radius: 5px;">
                </iframe>
            </div>
            """, unsafe_allow_html=True)
            
            # Botão de download
            st.download_button(
                label="📥 Baixar PDF Original",
                data=pdf_display_bytes,
                file_name=st.session_state.pdf_filename,
                mime="application/pdf",
                use_container_width=True
            )
            
            # Botão para revalidar
            if st.button("🔍 Revalidar Todos os Campos", use_container_width=True):
                validate_invoice_data()
                st.rerun()

elif not st.session_state.session_created:
    st.error("❌ Falha ao conectar ao sistema. Verifique se o servidor está rodando e tente recarregar a página.")
    
    if st.button("🔄 Tentar Reconectar"):
        st.rerun()