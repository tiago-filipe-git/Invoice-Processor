from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
import re
from enum import Enum

class ValidationStatus(Enum):
    GOOD = "good"      # Verde
    WARNING = "warning" # Amarelo
    BAD = "bad"        # Vermelho

class ValidationResult:
    def __init__(self, status: ValidationStatus, message: str = ""):
        self.status = status
        self.message = message

class InvoiceData(BaseModel):
    DocumentType: Optional[str] = Field(default="", description="Tipo do documento")
    DocumentID: Optional[str] = Field(default="", description="ID do documento")
    DocumentDate: Optional[str] = Field(default="", description="Data do documento")
    Language: Optional[str] = Field(default="", description="Idioma do documento")
    
    CurrencyCode: Optional[str] = Field(default="", description="Código da moeda")
    TotalDocumentAmount: Optional[str] = Field(default="", description="Valor total")
    NetDocumentAmount: Optional[str] = Field(default="", description="Valor líquido")
    VATAmount: Optional[str] = Field(default="", description="Valor do IVA")
    
    VendorName: Optional[str] = Field(default="", description="Nome do fornecedor")
    VendorTaxID: Optional[str] = Field(default="", description="NIF do fornecedor")
    VendorCountryCode: Optional[str] = Field(default="", description="País do fornecedor")
    
    CustomerName: Optional[str] = Field(default="", description="Nome do cliente")
    CustomerTaxID: Optional[str] = Field(default="", description="NIF do cliente")
    CustomerCountryCode: Optional[str] = Field(default="", description="País do cliente")

    @validator('DocumentDate')
    def validate_date(cls, v):
        if not v or v.strip() == "":
            return v
        
        # Tentar diferentes formatos de data
        date_formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d']
        for fmt in date_formats:
            try:
                datetime.strptime(v.strip(), fmt)
                return v
            except ValueError:
                continue
        
        # Se chegou aqui, a data não está em formato válido
        raise ValueError(f"Data inválida: {v}")

    @validator('CurrencyCode')
    def validate_currency(cls, v):
        if not v or v.strip() == "":
            return v
        
        # Lista de códigos de moeda válidos (ISO 4217)
        valid_currencies = ['EUR', 'USD', 'GBP', 'BRL', 'JPY', 'CHF', 'CAD', 'AUD']
        if v.upper() not in valid_currencies:
            raise ValueError(f"Código de moeda inválido: {v}")
        
        return v.upper()

    @validator('TotalDocumentAmount', 'NetDocumentAmount', 'VATAmount')
    def validate_amounts(cls, v):
        if not v or v.strip() == "":
            return v
        
        # Remover símbolos de moeda e espaços
        cleaned = re.sub(r'[€$£¥\s]', '', v.strip())
        
        # Aceitar tanto vírgula quanto ponto como separador decimal
        cleaned = cleaned.replace(',', '.')
        
        try:
            float(cleaned)
            return cleaned
        except ValueError:
            raise ValueError(f"Valor monetário inválido: {v}")

    @validator('VendorTaxID', 'CustomerTaxID')
    def validate_tax_id(cls, v):
        if not v or v.strip() == "":
            return v
        
        # Validação básica para NIF português (9 dígitos)
        cleaned = re.sub(r'[^\d]', '', v)
        if len(cleaned) != 9:
            raise ValueError(f"NIF deve ter 9 dígitos: {v}")
        
        return cleaned

class InvoiceValidator:
    @staticmethod
    def validate_field(field_name: str, value: str, invoice_data: Dict[str, Any]) -> ValidationResult:
        """Valida um campo específico e retorna o status de validação"""
        
        if not value or value.strip() == "":
            if field_name in ['DocumentID', 'DocumentDate', 'VendorName', 'CustomerName']:
                return ValidationResult(ValidationStatus.BAD, "Campo obrigatório vazio")
            else:
                return ValidationResult(ValidationStatus.WARNING, "Campo vazio (opcional)")
        
        try:
            # Criar instância temporária para validar o campo específico
            temp_data = {field_name: value}
            temp_invoice = InvoiceData(**temp_data)
            
            # Validações específicas por campo
            if field_name == 'DocumentType':
                valid_types = ['Invoice', 'Factura', 'Receipt', 'Recibo', 'Credit Note', 'Nota de Crédito']
                if value not in valid_types:
                    return ValidationResult(ValidationStatus.WARNING, f"Tipo não reconhecido: {value}")
            
            elif field_name == 'DocumentDate':
                # Verificar se a data não é muito antiga ou futura
                try:
                    date_formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d']
                    parsed_date = None
                    for fmt in date_formats:
                        try:
                            parsed_date = datetime.strptime(value.strip(), fmt)
                            break
                        except ValueError:
                            continue
                    
                    if parsed_date:
                        now = datetime.now()
                        if parsed_date > now:
                            return ValidationResult(ValidationStatus.WARNING, "Data no futuro")
                        elif (now - parsed_date).days > 365 * 5:  # Mais de 5 anos
                            return ValidationResult(ValidationStatus.WARNING, "Data muito antiga")
                except:
                    pass
            
            elif field_name in ['TotalDocumentAmount', 'NetDocumentAmount', 'VATAmount']:
                try:
                    amount = float(value.replace(',', '.'))
                    if amount < 0:
                        return ValidationResult(ValidationStatus.BAD, "Valor não pode ser negativo")
                    elif amount == 0:
                        return ValidationResult(ValidationStatus.WARNING, "Valor zero")
                    
                    # Verificar consistência entre valores
                    if field_name == 'TotalDocumentAmount' and 'NetDocumentAmount' in invoice_data and 'VATAmount' in invoice_data:
                        try:
                            net = float(invoice_data['NetDocumentAmount'].replace(',', '.'))
                            vat = float(invoice_data['VATAmount'].replace(',', '.'))
                            expected_total = net + vat
                            if abs(amount - expected_total) > 0.01:  # Tolerância de 1 cêntimo
                                return ValidationResult(ValidationStatus.WARNING, f"Total não confere (esperado: {expected_total:.2f})")
                        except:
                            pass
                
                except ValueError:
                    return ValidationResult(ValidationStatus.BAD, "Formato de valor inválido")
            
            elif field_name in ['VendorTaxID', 'CustomerTaxID']:
                cleaned = re.sub(r'[^\d]', '', value)
                if len(cleaned) != 9:
                    return ValidationResult(ValidationStatus.BAD, "NIF deve ter 9 dígitos")
                
                # Validação do dígito de controle do NIF português
                if not InvoiceValidator._validate_portuguese_nif(cleaned):
                    return ValidationResult(ValidationStatus.BAD, "NIF inválido (dígito de controle)")
            
            elif field_name == 'CurrencyCode':
                valid_currencies = ['EUR', 'USD', 'GBP', 'BRL', 'JPY', 'CHF', 'CAD', 'AUD']
                if value.upper() not in valid_currencies:
                    return ValidationResult(ValidationStatus.WARNING, f"Moeda não reconhecida: {value}")
            
            return ValidationResult(ValidationStatus.GOOD, "Válido")
            
        except ValueError as e:
            return ValidationResult(ValidationStatus.BAD, str(e))
        except Exception as e:
            return ValidationResult(ValidationStatus.WARNING, f"Erro na validação: {str(e)}")
    
    @staticmethod
    def _validate_portuguese_nif(nif: str) -> bool:
        """Valida o dígito de controle do NIF português"""
        if len(nif) != 9:
            return False
        
        try:
            # Algoritmo de validação do NIF português
            check_digit = int(nif[8])
            sum_digits = sum(int(nif[i]) * (9 - i) for i in range(8))
            remainder = sum_digits % 11
            
            if remainder < 2:
                return check_digit == 0
            else:
                return check_digit == (11 - remainder)
        except:
            return False
    
    @staticmethod
    def validate_all_fields(invoice_data: Dict[str, Any]) -> Dict[str, ValidationResult]:
        """Valida todos os campos e retorna um dicionário com os resultados"""
        results = {}
        
        field_names = [
            'DocumentType', 'DocumentID', 'DocumentDate', 'Language',
            'CurrencyCode', 'TotalDocumentAmount', 'NetDocumentAmount', 'VATAmount',
            'VendorName', 'VendorTaxID', 'VendorCountryCode',
            'CustomerName', 'CustomerTaxID', 'CustomerCountryCode'
        ]
        
        for field_name in field_names:
            value = invoice_data.get(field_name, "")
            results[field_name] = InvoiceValidator.validate_field(field_name, value, invoice_data)
        
        return results

    @staticmethod
    def get_status_color(status: ValidationStatus) -> str:
        """Retorna a cor correspondente ao status"""
        color_map = {
            ValidationStatus.GOOD: "#28a745",    # Verde
            ValidationStatus.WARNING: "#ffc107", # Amarelo
            ValidationStatus.BAD: "#dc3545"      # Vermelho
        }
        return color_map.get(status, "#6c757d")  # Cinza por defeito

    @staticmethod
    def get_status_icon(status: ValidationStatus) -> str:
        """Retorna o ícone correspondente ao status"""
        icon_map = {
            ValidationStatus.GOOD: "✅",
            ValidationStatus.WARNING: "⚠️",
            ValidationStatus.BAD: "❌"
        }
        return icon_map.get(status, "ℹ️")