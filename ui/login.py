import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QLineEdit
from PyQt6.QtCore import Qt, pyqtSignal, QSettings
from PyQt6.QtGui import QFont, QPixmap
from ui.components import BotaoPrincipal, BotaoDemonstracao, CampoTexto, COR_BEGE_FUNDO, COR_TEXTO_ESCURO

CAMINHO_ASSETS = os.path.join(os.path.dirname(__file__), "assets")

class ComponenteLogin(QWidget):
    sinal_autenticar = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        
    def configurar_layout_login(self, layout_card, parent_widget):
        parent_widget.input_email = CampoTexto("E-mail Corporativo")
        parent_widget.input_senha = CampoTexto("Senha de Acesso")
        parent_widget.input_senha.setEchoMode(QLineEdit.EchoMode.Password)

        settings = QSettings("PetShopControl", "Login")
        ultimo_email = settings.value("ultimo_email", "")

        if ultimo_email:
            parent_widget.input_email.setText(ultimo_email)
            parent_widget.input_senha.setFocus()

        layout_card.addWidget(parent_widget.input_email)
        layout_card.addWidget(parent_widget.input_senha)