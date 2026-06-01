from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QFormLayout
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class TelaPerfil(QWidget):
    def __init__(self, email_logado):
        super().__init__()
        self.email = email_logado
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)

        lbl_titulo = QLabel("👤 Perfil do Usuário")
        lbl_titulo.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(lbl_titulo)

        card = QFrame()
        card.setStyleSheet("background: white; border: 1px solid #D1C7BD; border-radius: 10px; padding: 20px;")
        form = QFormLayout(card)

        is_demo = self.email == "demo@petshop.com"
        nome_exibicao = "Operador Padrão (Demonstração)" if is_demo else "Administrador"
        nivel_acesso = "Operador (Restrito)" if is_demo else "Administrador Geral"

        form.addRow(QLabel("<b>E-mail:</b>"), QLabel(self.email))
        form.addRow(QLabel("<b>Nome:</b>"), QLabel(nome_exibicao))
        form.addRow(QLabel("<b>Nível de Acesso:</b>"), QLabel(nivel_acesso))
        
        layout.addWidget(card)
        
        if is_demo:
            lbl_aviso = QLabel("⚠️ Você está no modo demonstração. Algumas configurações administrativas estão bloqueadas.")
            lbl_aviso.setStyleSheet("color: #BA3C2A; font-style: italic;")
            layout.addWidget(lbl_aviso)
            
        layout.addStretch()