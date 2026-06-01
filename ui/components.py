from PyQt6.QtWidgets import QPushButton, QLineEdit, QDateEdit
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QFont

COR_BEGE_FUNDO = "#F4F1EA"
COR_BEGE_BOTAO = "#D1C7BD"
COR_VERDE_OLIVA = "#8CA485"
COR_TEXTO_ESCURO = "#3A3530"
COR_INPUT_BORDAS = "#9A9590"

class BotaoPrincipal(QPushButton):
    """Botão customizado para ações padrão (Autenticar, Salvar, etc.)"""
    def __init__(self, texto, parent=None):
        super().__init__(texto, parent)
        self.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {COR_BEGE_BOTAO};
                color: {COR_TEXTO_ESCURO};
                border: 1px solid {COR_INPUT_BORDAS};
                border-radius: 6px;
                padding: 10px 20px;
            }}
            QPushButton:hover {{
                background-color: #C2B7AC;
            }}
            QPushButton:pressed {{
                background-color: #B3A89D;
            }}
        """)

class BotaoDemonstracao(QPushButton):
    """Botão verde-oliva específico para o Modo Demonstração"""
    def __init__(self, texto, parent=None):
        super().__init__(texto, parent)
        self.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {COR_VERDE_OLIVA};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 20px;
            }}
            QPushButton:hover {{
                background-color: #7D9376;
            }}
            QPushButton:pressed {{
                background-color: #6E8268;
            }}
        """)

class CampoTexto(QLineEdit):
    """Campos de entrada de texto (E-mail, Senha, etc.) estilizados"""
    def __init__(self, placeholder, parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setFont(QFont("Arial", 10))
        self.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {COR_INPUT_BORDAS};
                border-radius: 4px;
                padding: 8px 12px;
                background-color: white;
                color: {COR_TEXTO_ESCURO};
            }}
            QLineEdit:focus {{
                border: 2px solid {COR_VERDE_OLIVA};
            }}
        """)

class SeletorData(QDateEdit):
    """Mini-calendário visual solicitado para evitar digitação manual"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCalendarPopup(True)
        self.setDate(QDate.currentDate())
        self.setFont(QFont("Arial", 10))
        self.setStyleSheet(f"""
            QDateEdit {{
                border: 1px solid {COR_INPUT_BORDAS};
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                color: {COR_TEXTO_ESCURO};
            }}
            QDateEdit::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid {COR_INPUT_BORDAS};
            }}
        """)

from PyQt6.QtWidgets import QLineEdit

class CampoMoedaBancario(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft) 
        self.setText("R$ 0,00")
        self.textChanged.connect(self.formatar_moeda)
        self._bloquear_sinal = False

    def formatar_moeda(self, texto):
        if self._bloquear_sinal:
            return

        numeros = "".join([c for c in texto if c.isdigit()])
        
        valor_int = int(numeros) if numeros else 0
        
        valor_final = valor_int / 100.0
        
        texto_formatado = f"R$ {valor_final:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        self._bloquear_sinal = True
        self.setText(texto_formatado)
        self._bloquear_sinal = False

    def pegar_valor_float(self):
        """Retorna o valor puro em float pronto para salvar no SQLite (Ex: 100.50)"""
        numeros = "".join([c for c in self.text() if c.isdigit()])
        return int(numeros) / 100.0 if numeros else 0.0

    def clear(self):
        self._bloquear_sinal = True
        self.setText("R$ 0,00")
        self._bloquear_sinal = False