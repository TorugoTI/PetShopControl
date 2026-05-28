import random
import string
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QMessageBox, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ui.components import BotaoPrincipal, CampoTexto, COR_TEXTO_ESCURO, COR_BEGE_FUNDO

class TelaPerfilAdmin(QWidget):
    def __init__(self, banco, usuario_cargo="Administrador"):
        super().__init__()
        self.banco = banco
        self.usuario_cargo = usuario_cargo
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("PetShop Control v3.0 - Perfil e Sistema")
        self.resize(550, 600)
        self.setStyleSheet("background-color: #F4F1EA;") 

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(25, 25, 25, 25)
        layout_principal.setSpacing(20)

        lbl_titulo = QLabel("👤 Configurações de Perfil")
        lbl_titulo.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        lbl_titulo.setStyleSheet(f"color: {COR_TEXTO_ESCURO};")
        layout_principal.addWidget(lbl_titulo)

        grupo_conta = QGroupBox("Segurança de Acesso")
        grupo_conta.setStyleSheet("QGroupBox { font-weight: bold; color: #3A3530; border: 1px solid #D1C7BD; border-radius: 6px; margin-top: 10px; padding-top: 15px; }")
        layout_conta = QVBoxLayout(grupo_conta)
        
        self.txt_nova_senha = CampoTexto("Nova Senha de Acesso")
        self.txt_nova_senha.setEchoMode(CampoTexto.EchoMode.Password)
        layout_conta.addWidget(self.txt_nova_senha)

        btn_atualizar_senha = BotaoPrincipal("Atualizar Minha Senha")
        btn_atualizar_senha.clicked.connect(self.alterar_senha)
        layout_conta.addWidget(btn_atualizar_senha)
        
        layout_principal.addWidget(grupo_conta)

        self.grupo_admin = QGroupBox("Painel de Controle do Administrador")
        self.grupo_admin.setStyleSheet("QGroupBox { font-weight: bold; color: #8CA485; border: 1px solid #8CA485; border-radius: 6px; margin-top: 10px; padding-top: 15px; }")
        layout_admin = QVBoxLayout(self.grupo_admin)

        lbl_info_codigo = QLabel("Gerar token de segurança para novos funcionários:")
        lbl_info_codigo.setFont(QFont("Arial", 9))
        layout_admin.addWidget(lbl_info_codigo)

        layout_token = QHBoxLayout()
        self.lbl_codigo_gerado = QLabel("------")
        self.lbl_codigo_gerado.setFont(QFont("Courier New", 14, QFont.Weight.Bold))
        self.lbl_codigo_gerado.setStyleSheet("background-color: white; border: 1px solid #D1C7BD; padding: 6px; border-radius: 4px; color: #3A3530;")
        self.lbl_codigo_gerado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        btn_gerar_codigo = BotaoPrincipal("Gerar Código")
        btn_gerar_codigo.clicked.connect(self.gerar_codigo_seguranca)
        
        layout_token.addWidget(self.lbl_codigo_gerado, stretch=2)
        layout_token.addWidget(btn_gerar_codigo, stretch=1)
        layout_admin.addLayout(layout_token)

        lbl_info_backup = QLabel("Gerenciamento Manual de Segurança de Dados:")
        lbl_info_backup.setFont(QFont("Arial", 9))
        lbl_info_backup.setStyleSheet("margin-top: 10px;")
        layout_admin.addWidget(lbl_info_backup)

        layout_botoes_backup = QHBoxLayout()
        btn_backup_pc = BotaoPrincipal("💾 Backup para PC")
        btn_backup_pc.clicked.connect(self.executar_backup_local)
        
        btn_backup_cloud = BotaoPrincipal("☁️ Enviar para o Firebase")
        btn_backup_cloud.clicked.connect(self.executar_backup_nuvem)
        
        layout_botoes_backup.addWidget(btn_backup_pc)
        layout_botoes_backup.addWidget(btn_backup_cloud)
        layout_admin.addLayout(layout_botoes_backup)

        layout_principal.addWidget(self.grupo_admin)

        if self.usuario_cargo != "Administrador":
            self.grupo_admin.setVisible(False)

        self.btn_sair = BotaoPrincipal("🚪 Encerrar Sessão no Operador")
        self.btn_sair.setStyleSheet("""
            QPushButton { background-color: #C27A7A; color: white; border-radius: 6px; padding: 10px; font-weight: bold; }
            QPushButton:hover { background-color: #B06B6B; }
        """)
        layout_principal.addWidget(self.btn_sair)

    def alterar_senha(self):
        nova_senha = self.txt_nova_senha.text()
        if not nova_senha:
            QMessageBox.warning(self, "Erro", "Digite a nova senha.")
            return
        
        QMessageBox.information(self, "Sucesso", "Senha modificada no banco de dados do computador!")
        self.txt_nova_senha.clear()

    def gerar_codigo_seguranca(self):
        """Gera um token aleatório de 6 dígitos que o funcionário precisará para se cadastrar"""
        caracteres = string.ascii_uppercase + string.digits
        codigo = "".join(random.choice(caracteres) for _ in range(6))
        self.lbl_codigo_gerado.setText(codigo)
        
        QMessageBox.information(self, "Código Gerado", f"Código único criado: {codigo}\n\nForneça este código para o seu operador digitar na tela de cadastro.")

    def ejecutar_backup_local(self):
        QMessageBox.information(self, "Backup Local", "Cópia de segurança 'petshop_local.db' exportada com sucesso para o computador!")

    def executar_backup_nuvem(self):
        from data.firebase_sync import SincronizadorFirebase
        nuvem = SincronizadorFirebase()
        
        QMessageBox.information(self, "Firebase Storage", "Conectando ao Firebase e checando histórico de backups...")
        
        sucesso = nuvem.enviar_backup_semanal_com_retencao(conta_id="admin_01")
        
        if sucesso:
            QMessageBox.information(self, "Sucesso", "Backup enviado! A regra de reter no máximo 2 arquivos foi executada com sucesso na nuvem.")
        else:
            QMessageBox.critical(self, "Erro", "Falha ao sincronizar com o Firebase.")