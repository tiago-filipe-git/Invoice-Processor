import streamlit as st
import requests
import base64
import json
import io

# Importar o validador
try:
    from invoice_validator import InvoiceValidator, ValidationStatus, ValidationResult
    VALIDATOR_AVAILABLE = True
except ImportError:
    VALIDATOR_AVAILABLE = False
    st.warning("⚠️ invoice_validator.py não encontrado. Validação desabilitada.")

# Configure page
st.set_page_config(page_title="Invoice Processor", page_icon="📄", layout="wide")

# CSS (igual ao fornecido)
st.markdown("""
<style>
/* Estilos para os indicadores de validação */
.validation-good { color: #28a745; font-weight: bold; }
.validation-warning { color: #ffc107; font-weight: bold; }
.validation-bad { color: #dc3545; font-weight: bold; }
.field-container { margin-bottom: 15px; }
.field-label { font-weight: bold; margin-bottom: 5px; display: block; }
.summary-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin: 10px 0; text-align: center; }
.metric-box { background: white; border-radius: 8px; padding: 15px; margin: 5px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

st.title("📄 Processador automático de Faturas")

# Configurações do servidor
SERVER_URL = "http://localhost:8000"
APP_NAME = "invoices"
USER_ID = "user0"
SESSION_ID = "session0"

# --- NEW: Define all available fields and categories ---
ALL_AVAILABLE_FIELDS = {
    # form_key: {label, model_key}
    "doc_type": {"label": "Tipo de Documento", "model_key": "DocumentType"},
    "doc_id": {"label": "ID/Número da Fatura", "model_key": "DocumentID"},
    "doc_date": {"label": "Data da Fatura", "model_key": "DocumentDate"},
    "language": {"label": "Idioma", "model_key": "Language"},
    "currency": {"label": "Código da Moeda", "model_key": "CurrencyCode"},
    "total_amount": {"label": "Valor Total", "model_key": "TotalDocumentAmount"},
    "net_amount": {"label": "Valor Líquido (sem IVA)", "model_key": "NetDocumentAmount"},
    "vat_amount": {"label": "Valor do IVA", "model_key": "VATAmount"},
    "vendor_name": {"label": "Nome do Fornecedor", "model_key": "VendorName"},
    "vendor_tax_id": {"label": "NIF do Fornecedor", "model_key": "VendorTaxID"},
    "vendor_country": {"label": "País do Fornecedor", "model_key": "VendorCountryCode"},
    "customer_name": {"label": "Nome do Cliente", "model_key": "CustomerName"},
    "customer_tax_id": {"label": "NIF do Cliente", "model_key": "CustomerTaxID"},
    "customer_country": {"label": "País do Cliente", "model_key": "CustomerCountryCode"},
}

FIELD_CATEGORIES = {
    "📋 Informações do Documento": ["doc_type", "doc_id", "doc_date", "language"],
    "💰 Informações Financeiras": ["currency", "total_amount", "net_amount", "vat_amount"],
    "🏢 Dados do Fornecedor": ["vendor_name", "vendor_tax_id", "vendor_country"],
    "👤 Dados do Cliente": ["customer_name", "customer_tax_id", "customer_country"],
}

PRESETS = {
    "Default (Todos os Campos)": list(ALL_AVAILABLE_FIELDS.keys()),
    "Essenciais do Documento": ["doc_type", "doc_id", "doc_date", "vendor_name", "customer_name", "total_amount"],
    "Apenas Financeiro": ["currency", "total_amount", "net_amount", "vat_amount"],
    "Apenas Fornecedor": ["vendor_name", "vendor_tax_id", "vendor_country"],
    "Apenas Cliente": ["customer_name", "customer_tax_id", "customer_country"],
    "Personalizado": [] # Handled by multiselect
}

# Inicializa variáveis de estado
if 'session_created' not in st.session_state:
    st.session_state.session_created = False
if 'invoice_data' not in st.session_state: # Stores data with model_key
    st.session_state.invoice_data = {}
if 'uploaded_pdf' not in st.session_state:
    st.session_state.uploaded_pdf = None
if 'validation_results' not in st.session_state: # Stores validation with form_key
    st.session_state.validation_results = {}
if 'pdf_filename' not in st.session_state:
    st.session_state.pdf_filename = ""
if 'selected_preset_name' not in st.session_state:
    st.session_state.selected_preset_name = "Default (Todos os Campos)"
if 'fields_to_display' not in st.session_state:
    st.session_state.fields_to_display = PRESETS["Default (Todos os Campos)"]

# Função para criar uma sessão (igual ao fornecido)
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

# Função para validar dados (igual ao fornecido, mas agora relies on invoice_data being correctly populated)
def validate_invoice_data():
    if VALIDATOR_AVAILABLE and st.session_state.invoice_data:
        # invoice_validator.validate_all_fields expects invoice_data keyed by model_key
        # and returns results keyed by form_key
        st.session_state.validation_results = InvoiceValidator.validate_all_fields(st.session_state.invoice_data)

# Função para mostrar resumo de validação (igual ao fornecido)
def show_validation_summary():
    if not VALIDATOR_AVAILABLE or not st.session_state.validation_results:
        st.info("ℹ️ Validação não disponível ou sem resultados.")
        return
    
    good_count = sum(1 for result in st.session_state.validation_results.values() if result.status == ValidationStatus.GOOD)
    warning_count = sum(1 for result in st.session_state.validation_results.values() if result.status == ValidationStatus.WARNING)
    bad_count = sum(1 for result in st.session_state.validation_results.values() if result.status == ValidationStatus.BAD)
    total_fields_validated = len(st.session_state.validation_results) # Should reflect all fields attemptedly validated
    
    st.markdown("""<div class="summary-card"><h3>📊 Resumo de Validação</h3><p>Status geral dos campos extraídos da fatura</p></div>""", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.markdown(f"""<div class="metric-box"><h2 style="color: #333; margin: 0;">{total_fields_validated}</h2><p style="margin: 5px 0; color: #666;">Total Validado</p></div>""", unsafe_allow_html=True)
    with col2: st.markdown(f"""<div class="metric-box" style="border-left: 4px solid #28a745;"><h2 style="color: #28a745; margin: 0;">✅ {good_count}</h2><p style="margin: 5px 0; color: #666;">Válidos</p></div>""", unsafe_allow_html=True)
    with col3: st.markdown(f"""<div class="metric-box" style="border-left: 4px solid #ffc107;"><h2 style="color: #ffc107; margin: 0;">⚠️ {warning_count}</h2><p style="margin: 5px 0; color: #666;">Avisos</p></div>""", unsafe_allow_html=True)
    with col4: st.markdown(f"""<div class="metric-box" style="border-left: 4px solid #dc3545;"><h2 style="color: #dc3545; margin: 0;">❌ {bad_count}</h2><p style="margin: 5px 0; color: #666;">Erros</p></div>""", unsafe_allow_html=True)

# Função para criar campo com validação visual (adaptada para usar form_key)
def create_validated_field(label, form_key, current_value=""):
    validation_result = None
    if VALIDATOR_AVAILABLE and form_key in st.session_state.validation_results:
        validation_result = st.session_state.validation_results[form_key]
    
    css_class, icon = "", ""
    if validation_result:
        if validation_result.status == ValidationStatus.GOOD: css_class, icon = "validation-good", "✅"
        elif validation_result.status == ValidationStatus.WARNING: css_class, icon = "validation-warning", "⚠️"
        else: css_class, icon = "validation-bad", "❌"
    
    st.markdown(f"""<div class="field-container"><div class="field-label">{label}:</div></div>""", unsafe_allow_html=True)
    # The key for st.text_input IS the form_key
    input_value = st.text_input(label="", value=current_value, key=form_key, label_visibility="collapsed")
    
    if validation_result and validation_result.message:
        st.markdown(f'<small class="{css_class}">{icon} {validation_result.message}</small>', unsafe_allow_html=True)
    return input_value # Not strictly needed if accessing via st.session_state[form_key]

# --- MODIFIED: Função para processar o formulário de edição ---
def process_form_submission():
    form_updated = False
    # Iterate only through fields that were displayed and thus potentially edited
    for form_key in st.session_state.get("fields_to_display", []):
        if form_key in st.session_state and form_key in ALL_AVAILABLE_FIELDS: # Check if input widget exists and config is available
            new_value_from_input = st.session_state[form_key] # Get value from the input widget (keyed by form_key)
            model_key = ALL_AVAILABLE_FIELDS[form_key]["model_key"]

            current_invoice_data_value = st.session_state.invoice_data.get(model_key)
            if current_invoice_data_value != new_value_from_input and new_value_from_input is not None:
                st.session_state.invoice_data[model_key] = new_value_from_input
                form_updated = True
    
    if form_updated:
        validate_invoice_data()
        st.success("Dados atualizados com sucesso!")
    else:
        st.info("Nenhuma alteração detectada nos dados para os campos exibidos.")
    # Não há necessidade de st.rerun() aqui, pois o submit do form já causa um rerun.

# --- NEW: Função para exportar os dados como JSON ---
def export_invoice_data_to_json():
    export_data = {}
    for form_key in st.session_state.get("fields_to_display", []):
        if form_key in ALL_AVAILABLE_FIELDS:
            model_key = ALL_AVAILABLE_FIELDS[form_key]["model_key"]
            label = ALL_AVAILABLE_FIELDS[form_key]["label"]
            
            current_value = ""
            # Prioritize the value from the form input if it exists and is different from the original,
            # otherwise use the value from invoice_data (which reflects the last processed or updated data)
            # Make sure to get the value that is currently in the text input widget if the form was rendered
            if form_key in st.session_state:
                current_value = st.session_state[form_key]
            else: # Fallback if widget key is not directly in session_state (e.g., if it was not rendered yet)
                current_value = st.session_state.invoice_data.get(model_key, "")

            export_data[label] = current_value
    
    json_string = json.dumps(export_data, indent=4, ensure_ascii=False)
    return json_string.encode('utf-8')


# Tentar criar sessão automaticamente
if not st.session_state.session_created:
    with st.spinner("🔄 Estabelecendo ligação ao sistema..."):
        create_session()

# --- NEW: Sidebar for Form Configuration ---
with st.sidebar:
    st.header("⚙️ Configuração do Formulário")
    
    # Callback to update fields_to_display when preset changes
    def update_fields_from_preset():
        preset_name = st.session_state.selected_preset_name_widget
        st.session_state.selected_preset_name = preset_name # Update the main state
        if preset_name != "Personalizado":
            st.session_state.fields_to_display = PRESETS[preset_name]
        # If "Personalizado", fields_to_display is managed by the multiselect below

    selected_preset_name_widget = st.selectbox(
        "Escolha um preset de campos:",
        options=list(PRESETS.keys()),
        key="selected_preset_name_widget", # Use a different key for the widget to manage on_change
        index=list(PRESETS.keys()).index(st.session_state.selected_preset_name), # Set initial value
        on_change=update_fields_from_preset
    )

    if st.session_state.selected_preset_name == "Personalizado":
        # Get current display fields if available, otherwise default to all for custom start
        default_custom_fields = st.session_state.fields_to_display if st.session_state.fields_to_display else list(ALL_AVAILABLE_FIELDS.keys())
        
        selected_custom_fields = st.multiselect(
            "Selecione os campos para exibir/editar:",
            options=list(ALL_AVAILABLE_FIELDS.keys()),
            default=default_custom_fields,
            format_func=lambda form_key: ALL_AVAILABLE_FIELDS[form_key]["label"],
            key="custom_fields_selector"
        )
        # Update fields_to_display live for custom
        if selected_custom_fields != st.session_state.fields_to_display:
            st.session_state.fields_to_display = selected_custom_fields
            # st.rerun() # Rerun if multiselect changes for immediate form update

# Conteúdo principal
if st.session_state.session_created:
    st.header("📤 Upload da Fatura")
    if not st.session_state.uploaded_pdf:
        st.info("👆 Carregue um ficheiro PDF com a fatura para começar o processamento.")
    
    uploaded_file = st.file_uploader("Selecione o arquivo PDF da fatura", type=['pdf'], help="Apenas ficheiros PDF são aceites")

    if uploaded_file is not None:
        # Check if it's a new file or the same one to avoid reprocessing without need
        # This simple check relies on filename and size; more robust would be hashing content
        new_file_identifier = (uploaded_file.name, uploaded_file.size)
        if st.session_state.get("last_uploaded_file_identifier") != new_file_identifier:
            st.session_state.pdf_filename = uploaded_file.name
            st.session_state.last_uploaded_file_identifier = new_file_identifier # Store identifier of processed file
            
            with st.spinner("🔄 Processando a sua fatura... Pode levar alguns segundos."):
                try:
                    pdf_bytes = uploaded_file.getvalue()
                    pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
                    payload = { # Payload structure as per original
                        "app_name": APP_NAME, "user_id": USER_ID, "session_id": SESSION_ID,
                        "new_message": {
                            "role": "user",
                            "parts": [{"text": "Extract information from invoice"}, {"inline_data": {"mime_type": "application/pdf", "data": pdf_base64}}]
                        }
                    }
                    headers = {'Content-Type': 'application/json'}
                    response = requests.post(f"{SERVER_URL}/run", headers=headers, data=json.dumps(payload), timeout=90)
                    response.raise_for_status()
                    response_data = response.json()

                    # Simplified response parsing based on original structure
                    if isinstance(response_data, list) and response_data and 'content' in response_data[0] and 'parts' in response_data[0]['content'] and response_data[0]['content']['parts'] and 'text' in response_data[0]['content']['parts'][0]:
                        json_string_with_fences = response_data[0]['content']['parts'][0]['text']
                        start_index = json_string_with_fences.find('{')
                        end_index = json_string_with_fences.rfind('}')
                        if start_index != -1 and end_index != -1 and end_index > start_index:
                            cleaned_json_string = json_string_with_fences[start_index:end_index + 1]
                            extracted_data_from_llm = json.loads(cleaned_json_string) # Keys are expected to be model_keys

                            if isinstance(extracted_data_from_llm, dict):
                                st.session_state.uploaded_pdf = pdf_bytes
                                st.session_state.invoice_data = {} # Clear previous

                                # Populate st.session_state.invoice_data using model_keys
                                # Assumes LLM returns data with keys that match 'model_key' definitions
                                for form_key_iter, config in ALL_AVAILABLE_FIELDS.items():
                                    model_key_iter = config["model_key"]
                                    value_from_llm = extracted_data_from_llm.get(model_key_iter)
                                    st.session_state.invoice_data[model_key_iter] = "" if value_from_llm is None else str(value_from_llm)
                                
                                validate_invoice_data()
                                st.success("✅ Fatura processada com sucesso! Dados extraídos e validados.")
                                st.rerun() # Rerun to update form with new data
                            else: st.error("❌ Formato de dados inválido extraído da fatura.")
                        else: st.error("❌ Não foi possível extrair dados JSON válidos da fatura.")
                    else: st.error("❌ Resposta inesperada do servidor de processamento.")
                except requests.exceptions.Timeout: st.error("⏱️ Timeout: O servidor demorou muito para responder.")
                except requests.exceptions.RequestException as e: st.error(f"🌐 Erro de comunicação com o servidor: {e}")
                except json.JSONDecodeError as e: st.error(f"❌ Erro ao processar JSON da fatura: {e}")
                except Exception as e: st.error(f"❌ Erro inesperado ao processar a fatura: {str(e)}")
        # If it's the same file, do nothing to prevent reprocessing, data is already in session_state

    if st.session_state.invoice_data and st.session_state.uploaded_pdf:
        st.markdown("---")
        show_validation_summary()
        st.markdown("---")
        
        col_form, col_pdf = st.columns([3, 2])
        
        with col_form:
            st.header("✏️ Dados da Fatura - Edição e Validação")
            st.info("📝 Reveja e edite os campos abaixo. Os ícones indicam o estado de validação.")
            
            with st.form("invoice_form"):
                # Dynamically render form based on selected fields and categories
                for category_label, field_keys_in_category in FIELD_CATEGORIES.items():
                    # Check if any field from this category is selected for display
                    fields_to_render_in_category = [fk for fk in field_keys_in_category if fk in st.session_state.fields_to_display]
                    
                    if fields_to_render_in_category:
                        st.subheader(category_label)
                        for form_key_render in fields_to_render_in_category:
                            field_config = ALL_AVAILABLE_FIELDS[form_key_render]
                            model_key_render = field_config["model_key"]
                            
                            create_validated_field(
                                label=field_config["label"],
                                form_key=form_key_render, # This is the key for st.text_input
                                current_value=st.session_state.invoice_data.get(model_key_render, "")
                            )
                
                st.markdown("---")
                submitted = st.form_submit_button("💾 Confirmar e Salvar Alterações", use_container_width=True, type="primary")
                if submitted:
                    process_form_submission() # This will now rerun
            
            # MOVIDO PARA FORA DO st.form()
            st.markdown("---") # Adiciona uma linha divisória para separar o formulário do botão de exportar
            # Usar st.columns para alinhar o botão de exportar abaixo do formulário, se desejado
            st.download_button(
                label="📤 Exportar Dados (JSON)",
                data=export_invoice_data_to_json(),
                file_name=f"{st.session_state.pdf_filename.replace('.pdf', '')}_exported.json",
                mime="application/json",
                use_container_width=True
            )


        with col_pdf: # PDF display part is largely the same
            st.header(f"📄 Fatura Carregada")
            st.info(f"📁 Arquivo: **{st.session_state.pdf_filename}**")
            pdf_display_bytes = st.session_state.uploaded_pdf
            pdf_base64_display = base64.b64encode(pdf_display_bytes).decode()
            st.markdown(f"""<iframe src="data:application/pdf;base64,{pdf_base64_display}" width="100%" height="600px" type="application/pdf" style="border: none; border-radius: 5px;"></iframe>""", unsafe_allow_html=True)
            st.download_button(label="📥 Baixar PDF Original", data=pdf_display_bytes, file_name=st.session_state.pdf_filename, mime="application/pdf", use_container_width=True)
            if st.button("🔍 Revalidar Todos os Campos", use_container_width=True):
                validate_invoice_data()
                st.rerun()

elif not st.session_state.session_created:
    st.error("❌ Falha ao conectar ao sistema. Verifique se o servidor está ligado e tente recarregar a página.")
    if st.button("🔄 Tentar Reconectar"):
        st.rerun()