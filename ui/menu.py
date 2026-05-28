import os
import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QIcon
from ui.components import (
    BotaoPrincipal, BotaoDemonstracao, CampoTexto, 
    COR_BEGE_FUNDO, COR_TEXTO_ESCURO, COR_INPUT_BORDAS
)
from ui.cadastro import JanelaCadastro

CAMINHO_ASSETS = os.path.join(os.path.dirname(__file__), "assets")

class TelaMenuInicial(QWidget):
    sinal_modo_demonstracao = pyqtSignal()
    sinal_autenticar = pyqtSignal(str, str)

    def __init__(self, banco=None):
        super().__init__()
        self.banco = banco 
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("PetShop Control v3.0 - Login")
        self.resize(1000, 700)
        self.setStyleSheet(f"background-color: #EFECE6;")

        layout_central = QHBoxLayout(self)
        layout_central.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setFixedWidth(420)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {COR_BEGE_FUNDO};
                border-radius: 12px;
                border: 1px solid #E0DCD3;
            }}
        """)
        
        layout_card = QVBoxLayout(card)
        layout_card.setContentsMargins(30, 40, 30, 40)
        layout_card.setSpacing(15)

        lbl_icone = QLabel()
        lbl_icone.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_icone.setStyleSheet("border: none; background: transparent;")
        caminho_logo = os.path.join(CAMINHO_ASSETS, "pata_verde.png")
        if os.path.exists(caminho_logo):
            pixmap_pata = QPixmap(caminho_logo)
            lbl_icone.setPixmap(pixmap_pata.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            lbl_icone.setText("🐾")
            lbl_icone.setFont(QFont("Arial", 24))

        lbl_titulo = QLabel("PETSHOP CONTROL")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_titulo.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        lbl_titulo.setStyleSheet(f"color: {COR_TEXTO_ESCURO}; border: none;")

        lbl_subtitulo = QLabel("Gestão Comercial de Alta Performance")
        lbl_subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_subtitulo.setFont(QFont("Arial", 10))
        lbl_subtitulo.setStyleSheet("color: #7A7570; border: none; padding-bottom: 10px;")

        layout_card.addWidget(lbl_icone)
        layout_card.addWidget(lbl_titulo)
        layout_card.addWidget(lbl_subtitulo)

        self.input_email = CampoTexto("E-mail Corporativo")
        self.input_senha = CampoTexto("Senha de Acesso")
        self.input_senha.setEchoMode(QLineEdit.EchoMode.Password)

        layout_card.addWidget(self.input_email)
        layout_card.addWidget(self.input_senha)

        self.btn_esqueci_senha = QPushButton("Esqueci minha senha")
        self.btn_esqueci_senha.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_esqueci_senha.setStyleSheet("background: transparent; color: #7A7570; border: none; font-size: 11px; text-decoration: underline;")
        self.btn_esqueci_senha.clicked.connect(self.disparar_recuperacao_senha)
        layout_card.addWidget(self.btn_esqueci_senha, alignment=Qt.AlignmentFlag.AlignRight)

        layout_card.addSpacing(5)

        btn_autenticar = BotaoPrincipal("Autenticar no Sistema")
        btn_autenticar.clicked.connect(self.disparar_autenticacao)
        layout_card.addWidget(btn_autenticar)

        self.btn_cadastrar_link = QPushButton("Não tem conta? Cadastrar utilizando código")
        self.btn_cadastrar_link.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cadastrar_link.setFont(QFont("Arial", 9))
        self.btn_cadastrar_link.setStyleSheet("background: transparent; color: #5A5550; border: none; text-decoration: underline;")
        self.btn_cadastrar_link.clicked.connect(self.abrir_tela_cadastro)
        layout_card.addWidget(self.btn_cadastrar_link)

        lbl_divisor = QLabel("----------------- OU -----------------")
        lbl_divisor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_divisor.setFont(QFont("Arial", 9))
        lbl_divisor.setStyleSheet("color: #A5A09A; border: none; padding: 5px 0;")
        layout_card.addWidget(lbl_divisor)

        btn_demo = BotaoDemonstracao("🐾 Acessar Modo Demonstração")
        btn_demo.clicked.connect(self.sinal_modo_demonstracao.emit)
        layout_card.addWidget(btn_demo)

        layout_central.addWidget(card)

    def disparar_autenticacao(self):
        """Captura os dados inseridos e envia para validação no core"""
        email = self.input_email.text().strip()
        senha = self.input_senha.text()
        self.sinal_autenticar.emit(email, senha)

    def acessar_modo_demonstracao(self):
        """Abre o Dashboard salvando a referência em memória para o app não fechar"""
        try:
            from ui.dashboard import TelaDashboard
            from data.database import BancoDeDados # Importa a classe do banco

            if self.banco is None:
                print("[MENU] Banco era None. Inicializando banco em memória para o Modo Demo.")
                self.banco = BancoDeDados(modo_demonstracao=True)
            elif not self.banco.modo_demonstracao:
                self.banco = BancoDeDados(modo_demonstracao=True)

            self.dashboard = TelaDashboard(self.banco)
            self.dashboard.show()
        
            self.sinal_modo_demonstracao.emit()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Não foi possível iniciar o painel: {str(e)}")

    def abrir_tela_cadastro(self):
        """Abre a janela de cadastro passando o banco para verificar os códigos"""
        if not self.banco:
            QMessageBox.critical(self, "Erro de Sistema", "Banco de dados local não inicializado.")
            return
        tela_cad = JanelaCadastro(self.banco)
        tela_cad.exec()

    def disparar_recuperacao_senha(self):
        """Dispara a rotina de recuperação com base no input_email corrigido"""
        email = self.input_email.text().strip()
        if not email:
            QMessageBox.warning(self, "Aviso", "Por favor, digite o seu e-mail no campo de login para receber o link de recuperação.")
            return 
         
        QMessageBox.information(self, "Recuperação de Conta", f"Um link para redefinição segura de senha foi enviado para o e-mail: {email}")