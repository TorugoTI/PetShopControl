import shutil
import os
import uuid

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QFormLayout, QLabel, QPushButton, QMessageBox, QLineEdit, QInputDialog, QFileDialog, QListWidget
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from ui.components import BotaoPrincipal, COR_TEXTO_ESCURO
from data.firebase_sync import SincronizadorFirebase

class TelaPerfil(QWidget):
    def __init__(self, email_logado, banco):
        super().__init__()
        self.banco = banco
        self.email = email_logado
        self.firebase = SincronizadorFirebase()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)

        lbl_titulo = QLabel("👤 Perfil do Usuário")
        lbl_titulo.setFont(QFont("Arial", 16, QFont.Weight.Bold))
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

        btn_codigo = BotaoPrincipal("🔑 Gerar Código de Acesso")
        btn_codigo.clicked.connect(self.gerar_codigo)
        
        btn_senha = BotaoPrincipal("🔒 Alterar Senha")
        btn_senha.clicked.connect(self.abrir_troca_senha)
        
        btn_backup_local = BotaoPrincipal("💾 Backup Local (PC)")
        btn_backup_local.clicked.connect(self.fazer_backup_local)
        
        btn_backup_nuvem = BotaoPrincipal("☁️ Backup Nuvem (Firebase)")
        btn_backup_nuvem.clicked.connect(self.fazer_backup_nuvem)

        btn_restaurar_nuvem = BotaoPrincipal("☁️ Restaurar Backup da Nuvem")
        btn_restaurar_nuvem.setStyleSheet("background-color: #2980B9; color: white;")
        btn_restaurar_nuvem.clicked.connect(self.restaurar_backup_nuvem)

        btn_restaurar = BotaoPrincipal("🔄 Restaurar Backup (.db)")
        btn_restaurar.setStyleSheet("background-color: #BA3C2A; color: white;")
        btn_restaurar.clicked.connect(self.restaurar_backup_banco)
        
        
        layout_acoes = QVBoxLayout()
        layout_acoes.addWidget(btn_codigo)
        layout_acoes.addWidget(btn_senha)
        layout_acoes.addWidget(btn_backup_local)
        layout_acoes.addWidget(btn_backup_nuvem)
        layout_acoes.addWidget(btn_restaurar_nuvem)
        layout_acoes.addWidget(btn_restaurar)
        
        layout.addLayout(layout_acoes)

        self.lista_codigos = QListWidget()
        layout.addWidget(QLabel("<b>Códigos Ativos na Nuvem:</b>"))
        layout.addWidget(self.lista_codigos)
    
        self.carregar_codigos_admin()
            
        if is_demo:
            lbl_aviso = QLabel("⚠️ Modo demonstração: Ações administrativas bloqueadas.")
            lbl_aviso.setStyleSheet("color: #BA3C2A; font-style: italic;")
            layout.addWidget(lbl_aviso)
            btn_codigo.setEnabled(False)
            btn_backup_nuvem.setEnabled(False)
            
        layout.addStretch()

    def gerar_codigo(self):
        novo_codigo = str(uuid.uuid4())[:8].upper()
        try:
            cursor = self.banco.conexao.cursor()
            cursor.execute("INSERT INTO codigos_convite (codigo, status) VALUES (?, 'Ativo')", (novo_codigo,))
            self.banco.conexao.commit()
            
            self.firebase.salvar_codigo_convite(novo_codigo)
            
            self.carregar_codigos_admin()
            QMessageBox.information(self, "Sucesso", f"Código gerado: {novo_codigo}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao gerar código: {e}")

    def abrir_troca_senha(self):
        nova_senha, ok = QInputDialog.getText(self, "Alterar Senha", "Digite a nova senha:", QLineEdit.EchoMode.Password)
        if ok and nova_senha:
            cursor = self.banco.conexao.cursor()
            cursor.execute("UPDATE usuarios SET senha = ? WHERE email = ?", (nova_senha, self.email))
            self.banco.conexao.commit()
            QMessageBox.information(self, "Sucesso", "Senha alterada com êxito.")

    def restaurar_backup_local(self):
        caminho_backup, _ = QFileDialog.getOpenFileName(self, "Selecione o arquivo de Backup", "", "Arquivos DB (*.db)")
        if caminho_backup:
            caminho_banco_atual = os.path.join(os.path.dirname(os.path.dirname(__file__)), "petshop.db")
            
            confirm = QMessageBox.question(self, "Restaurar", "Isso sobrescreverá seu banco atual. Continuar?")
            if confirm == QMessageBox.StandardButton.Yes:
                shutil.copy(caminho_backup, caminho_banco_atual)
                QMessageBox.information(self, "Sucesso", "Backup restaurado! O sistema será reiniciado.")
    
    def fazer_backup_local(self):
        caminho_destino = QFileDialog.getExistingDirectory(self, "Escolher pasta para Backup")
        if caminho_destino:
            try:
                caminho_banco = os.path.join(os.path.dirname(os.path.dirname(__file__)), "petshop.db")
                shutil.copy(caminho_banco, os.path.join(caminho_destino, "backup_petshop.db"))
                QMessageBox.information(self, "Backup", "Backup local realizado com sucesso!")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao realizar backup: {e}")

    def restaurar_backup_nuvem(self):
        backups_disponiveis = self.firebase.listar_backups_nuvem()
        
        if not backups_disponiveis:
            QMessageBox.warning(self, "Aviso", "Nenhum backup encontrado na nuvem.")
            return

        item, ok = QInputDialog.getItem(self, "Restaurar Nuvem", 
                                        "Selecione o backup:", backups_disponiveis, 0, False)
        
        if ok and item:
            confirm = QMessageBox.question(self, "Confirmação", 
                                           f"Restaurar o backup {item}? Isso sobrescreverá seus dados atuais.")
            
            if confirm == QMessageBox.StandardButton.Yes:
                QMessageBox.information(self, "Progresso", "Iniciando download do backup...")
                self.firebase.baixar_e_aplicar_backup(item)

    def restaurar_backup_banco(self):
        caminho_backup, _ = QFileDialog.getOpenFileName(self, "Selecionar Backup", "", "Arquivos de Banco (*.db)")
        
        if caminho_backup:
            confirm = QMessageBox.question(self, "Confirmação", 
                                           "ATENÇÃO: Isso irá substituir seus dados atuais pelos dados do backup. Continuar?",
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if confirm == QMessageBox.StandardButton.Yes:
                sucesso = self.firebase.restaurar_backup_local(caminho_backup)
                if sucesso:
                    QMessageBox.information(self, "Sucesso", "Backup restaurado com êxito! Por favor, reinicie o sistema.")
                else:
                    QMessageBox.critical(self, "Erro", "Falha ao restaurar o arquivo.")
    
    def fazer_backup_nuvem(self):
        sucesso = self.firebase.enviar_backup_semanal_com_retencao(self.email)
        if sucesso:
            QMessageBox.information(self, "Nuvem", "Backup enviado ao Firebase com sucesso!")
        else:
            QMessageBox.critical(self, "Nuvem", "Falha ao enviar backup.")
    
    def carregar_codigos_admin(self):
        self.lista_codigos.clear()
        codigos = self.firebase.listar_codigos_ativos()
        for item in codigos:
            self.lista_codigos.addItem(item['codigo'])