import streamlit as st

def inject_custom_css():
    """Injeta CSS personalizado para melhorar a aparência da validação"""
    st.markdown("""
    <style>
    /* Estilos para os indicadores de validação */
    .validation-indicator {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 40px;
        border-radius: 5px;
        margin-top: 8px;
        font-weight: bold;
        font-size: 16px;
    }
    
    .validation-good {
        background-color: rgba(40, 167, 69, 0.1);
        border: 2px solid #28a745;
        color: #28a745;
    }
    
    .validation-warning {
        background-color: rgba(255, 193, 7, 0.1);
        border: 2px solid #ffc107;
        color: #ffc107;
    }
    
    .validation-bad {
        background-color: rgba(220, 53, 69, 0.1);
        border: 2px solid #dc3545;
        color: #dc3545;
    }
    
    /* Melhorar aparência dos formulários */
    .stTextInput > div > div > input {
        border-radius: 5px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #007bff;
        box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
    }
    
    /* Estilo para seções do formulário */
    .form-section {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
        border-left: 4px solid #007bff;
    }
    
    /* Estilo para o resumo de validação */
    .validation-summary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    
    .validation-summary h3 {
        margin-top: 0;
        color: white;
    }
    
    /* Estilo para tooltips personalizados */
    .validation-tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
    }
    
    .validation-tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: #555;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 12px;
    }
    
    .validation-tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    
    /* Animação para mudanças de status */
    .status-change {
        animation: pulse 1s;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    
    /* Estilo para botões */
    .stButton > button {
        border-radius: 8px;
        border: none;
        background: linear-gradient(90deg, #007bff, #0056b3);
        color: white;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 123, 255, 0.3);
    }
    
    /* Estilo para métricas do resumo */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        margin: 10px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .metric-good {
        border-left: 5px solid #28a745;
    }
    
    .metric-warning {
        border-left: 5px solid #ffc107;
    }
    
    .metric-bad {
        border-left: 5px solid #dc3545;
    }
    
    /* Responsividade para dispositivos móveis */
    @media (max-width: 768px) {
        .validation-summary {
            padding: 10px;
        }
        
        .metric-card {
            margin: 5px;
            padding: 15px;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def create_validation_badge(status, message="", size="normal"):
    """Cria um badge de validação com estilo personalizado"""
    from  pydantic_val import ValidationStatus, InvoiceValidator
    
    color = InvoiceValidator.get_status_color(status)
    icon = InvoiceValidator.get_status_icon(status)
    
    size_class = "validation-badge-large" if size == "large" else "validation-badge"
    
    badge_html = f"""
    <div class="{size_class}" style="
        background-color: {color}20;
        border: 2px solid {color};
        color: {color};
        padding: 5px 10px;
        border-radius: 15px;
        display: inline-flex;
        align-items: center;
        font-size: 12px;
        font-weight: bold;
        margin: 2px;
    ">
        <span style="margin-right: 5px;">{icon}</span>
        <span>{status.value.upper()}</span>
        {f'<span style="margin-left: 10px; font-size: 10px; opacity: 0.8;">({message})</span>' if message else ''}
    </div>
    """
    
    return badge_html

def create_progress_ring(good_count, warning_count, bad_count, total_count):
    """Cria um anel de progresso para mostrar o status geral de validação"""
    if total_count == 0:
        return ""
    
    good_percentage = (good_count / total_count) * 100
    warning_percentage = (warning_count / total_count) * 100
    bad_percentage = (bad_count / total_count) * 100
    
    return f"""
    <div style="text-align: center; margin: 20px 0;">
        <div style="position: relative; display: inline-block;">
            <svg width="120" height="120" viewBox="0 0 120 120">
                <!-- Fundo do anel -->
                <circle cx="60" cy="60" r="50" fill="none" stroke="#e9ecef" stroke-width="10"/>
                
                <!-- Segmento vermelho (erros) -->
                <circle cx="60" cy="60" r="50" fill="none" stroke="#dc3545" stroke-width="10"
                        stroke-dasharray="{bad_percentage * 3.14} 314"
                        stroke-dashoffset="0" transform="rotate(-90 60 60)"/>
                
                <!-- Segmento amarelo (avisos) -->
                <circle cx="60" cy="60" r="50" fill="none" stroke="#ffc107" stroke-width="10"
                        stroke-dasharray="{warning_percentage * 3.14} 314"
                        stroke-dashoffset="-{bad_percentage * 3.14}" transform="rotate(-90 60 60)"/>
                
                <!-- Segmento verde (válidos) -->
                <circle cx="60" cy="60" r="50" fill="none" stroke="#28a745" stroke-width="10"
                        stroke-dasharray="{good_percentage * 3.14} 314"
                        stroke-dashoffset="-{(bad_percentage + warning_percentage) * 3.14}" transform="rotate(-90 60 60)"/>
            </svg>
            
            <!-- Texto no centro -->
            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);">
                <div style="font-size: 18px; font-weight: bold; color: #333;">
                    {good_count}/{total_count}
                </div>
                <div style="font-size: 12px; color: #666;">
                    Válidos
                </div>
            </div>
        </div>
    </div>
    """