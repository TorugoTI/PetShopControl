from PyQt6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QLabel, QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ui.components import BotaoPrincipal, COR_BEGE_FUNDO, COR_TEXTO_ESCURO
from data.firebase_sync import SincronizadorFirebase

class JanelaRecuperacao(QDialog):
    def __init__(self, email_inicial="", parent=None):
        super().__init__(parent)
        self.sincronizador = SincronizadorFirebase()
        self.init_ui(email_inicial)

    def init_ui(self, email_inicial):
        self.setWindowTitle("Redefinição de Senha - PetShop Control")
        self.setFixedWidth(400)
        self.setStyleSheet(f"background-color: {COR_BEGE_FUNDO};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        lbl_titulo = QLabel("Recuperar Acesso")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_titulo.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        lbl_titulo.setStyleSheet(f"color: {COR_TEXTO_ESCURO}; border: none;")
        layout.addWidget(lbl_titulo)

        lbl_sub = QLabel("Informe seu e-mail, o código de segurança do sistema e a nova senha.")
        lbl_sub.setWordWrap(True)
        lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_sub.setStyleSheet("color: #7A7570; border: none; font-size: 11px;")
        layout.addWidget(lbl_sub)

        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("E-mail cadastrado")
        self.input_email.setText(email_inicial)
        self.input_email.setStyleSheet("padding: 8px; border-radius: 6px; border: 1px solid #CCC; background: #FFF;")
        layout.addWidget(self.input_email)

        self.input_codigo = QLineEdit()
        self.input_codigo.setPlaceholderText("Código de Segurança (mesmo código para criar sua conta.)")
        self.input_codigo.setStyleSheet("padding: 8px; border-radius: 6px; border: 1px solid #CCC; background: #FFF;")
        layout.addWidget(self.input_codigo)

        self.input_nova_senha = QLineEdit()
        self.input_nova_senha.setPlaceholderText("Nova Senha")
        self.input_nova_senha.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_nova_senha.setStyleSheet("padding: 8px; border-radius: 6px; border: 1px solid #CCC; background: #FFF;")
        layout.addWidget(self.input_nova_senha)

        btn_confirmar = BotaoPrincipal("Redefinir Senha")
        btn_confirmar.clicked.connect(self.executar_redefinicao)
        layout.addWidget(btn_confirmar)

    def executar_redefinicao(self):
        email = self.input_email.text().strip()
        codigo = self.input_codigo.text().strip()
        nova_senha = self.input_nova_senha.text().strip()

        if not email or not codigo or not nova_senha:
            QMessageBox.warning(self, "Campos Vazios", "Por favor, preencha todos os campos.")
            return

        sucesso, mensagem = self.sincronizador.redefinir_senha_com_codigo(email, codigo, nova_senha)

        if sucesso:
            QMessageBox.information(self, "Sucesso", mensagem)
            self.accept()
        else:
            QMessageBox.critical(self, "Erro de Validação", mensagem)