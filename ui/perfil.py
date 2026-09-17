from PyQt6.QtWidgets import QDialog, QWidget, QVBoxLayout, QLabel, QFrame, QFormLayout, QPushButton, QMessageBox, QLineEdit, QInputDialog, QFileDialog, QListWidget
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from ui.components import BotaoPrincipal, COR_TEXTO_ESCURO
from data.firebase_sync import SincronizadorFirebase
from datetime import datetime
import shutil
import os
import uuid

class TelaPerfil(QWidget):
    def __init__(self, sync_instance, email, banco, cargo):
        super().__init__()
        self.sync = sync_instance
        self.auth = self.sync.auth
        self.cargo = cargo
        self.banco = banco
        self.email = email
        self.firebase = SincronizadorFirebase()
        self.is_admin = (self.email == "victor.ti.pereira@gmail.com")
        
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
        nome_exibicao = "Operador Padrão (Demonstração)" if is_demo else ("Administrador Master" if self.is_admin else "Operador")
        nivel_acesso = "Operador (Restrito)" if is_demo else ("Administrador Geral" if self.is_admin else "Operador")

        form.addRow(QLabel("<b>E-mail:</b>"), QLabel(self.email))
        form.addRow(QLabel("<b>Nome:</b>"), QLabel(nome_exibicao))
        form.addRow(QLabel("<b>Nível de Acesso:</b>"), QLabel(nivel_acesso))
        layout.addWidget(card)

        self.btn_codigo = BotaoPrincipal("🔑 Gerar Código de Acesso")
        self.btn_codigo.clicked.connect(self.gerar_codigo)
        
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
        
        if self.is_admin:
            layout_acoes.addWidget(self.btn_codigo)
            
        layout_acoes.addWidget(btn_senha)
        layout_acoes.addWidget(btn_backup_local)
        layout_acoes.addWidget(btn_backup_nuvem)
        layout_acoes.addWidget(btn_restaurar_nuvem)
        layout_acoes.addWidget(btn_restaurar)
        
        layout.addLayout(layout_acoes)

        self.lbl_titulo_codigos = QLabel("<b>Códigos Ativos/Utilizados na Nuvem:</b>")
        self.lista_codigos = QListWidget()
        
        layout.addWidget(self.lbl_titulo_codigos)
        layout.addWidget(self.lista_codigos)
        
        if self.is_admin:
            self.carregar_codigos()
        else:
            self.lbl_titulo_codigos.setVisible(False)
            self.lista_codigos.setVisible(False)
            
        if is_demo:
            lbl_aviso = QLabel("⚠️ Modo demonstração: Ações administrativas bloqueadas.")
            lbl_aviso.setStyleSheet("color: #BA3C2A; font-style: italic;")
            layout.addWidget(lbl_aviso)
            btn_backup_nuvem.setEnabled(False)
            if self.is_admin:
                self.btn_codigo.setEnabled(False)
            
        layout.addStretch()

        self.txt_senha_antiga = QLineEdit()
        self.txt_senha_antiga.setPlaceholderText("Senha atual")
        self.txt_senha_antiga.setEchoMode(QLineEdit.EchoMode.Password)

        self.txt_nova_senha = QLineEdit()
        self.txt_nova_senha.setPlaceholderText("Nova senha")
        self.txt_nova_senha.setEchoMode(QLineEdit.EchoMode.Password)

        self.txt_confirmar_nova = QLineEdit()
        self.txt_confirmar_nova.setPlaceholderText("Confirme a nova senha")
        self.txt_confirmar_nova.setEchoMode(QLineEdit.EchoMode.Password)

    def abrir_troca_senha(self):
        dialog = DialogTrocaSenha(self)
        if dialog.exec():
            antiga = dialog.txt_antiga.text()
            nova = dialog.txt_nova.text()
            confirma = dialog.txt_confirma.text()

            if nova != confirma:
                QMessageBox.warning(self, "Erro", "As novas senhas não coincidem.")
                return

            if self.firebase.alterar_senha_admin(self.email, nova):
                QMessageBox.information(self, "Sucesso", "Senha alterada com sucesso!")
            else:
                QMessageBox.critical(self, "Erro", "Falha ao comunicar com o Firebase.")

    def processar_troca_senha(self):
        antiga = self.txt_senha_antiga.text()
        nova = self.txt_nova_senha.text()
        confirmacao = self.txt_confirmar_nova.text()
        
        if not antiga or not nova or not confirmacao:
            QMessageBox.warning(self, "Erro", "Preencha todos os campos.")
            return

        if nova != confirmacao:
            QMessageBox.warning(self, "Erro", "A nova senha e a confirmação não conferem.")
            return
            
        try:
            user = self.auth.sign_in_with_email_and_password(self.email, antiga)
            self.auth.update_password(user['idToken'], nova)
            QMessageBox.information(self, "Sucesso", "Senha alterada com sucesso no Firebase!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erro", "Falha ao alterar senha. Verifique se a senha atual está correta.")
            print(f"[DEBUG] Erro Firebase: {e}")

    def restaurar_backup_local(self):
        caminho_backup, _ = QFileDialog.getOpenFileName(self, "Selecione o arquivo de Backup", "", "Arquivos DB (*.db)")
        if caminho_backup:
            caminho_banco_atual = os.path.join(os.path.dirname(os.path.dirname(__file__)), "petshop.db")
            confirm = QMessageBox.question(self, "Restaurar", "Isso sobrescreverá seu banco atual. Continuar?")
            if confirm == QMessageBox.StandardButton.Yes:
                shutil.copy(caminho_backup, caminho_banco_atual)
                QMessageBox.information(self, "Sucesso", "Backup restaurado! O sistema será reiniciado.")

    def restaurar_backup_nuvem(self):
        backups_disponiveis = self.firebase.listar_backups_nuvem()
        if not backups_disponiveis:
            QMessageBox.warning(self, "Aviso", "Nenhum backup com dados encontrado na nuvem.")
            return

        item, ok = QInputDialog.getItem(self, "Restaurar Nuvem", "Selecione o backup:", backups_disponiveis, 0, False)
        if ok and item:
            bytes_db = self.firebase.carregar_dados_backup_nuvem(item)
            if not bytes_db:
                QMessageBox.critical(self, "Erro", "Não foi possível carregar os dados do backup da nuvem.")
                return
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
                tmp.write(bytes_db)
                tmp_path = tmp.name

            confirm = QMessageBox.question(
                self, 
                "Confirmar Gravação Local", 
                f"Dados do backup '{item}' carregados no preview do dashboard.\n\nDeseja salvar definitivo no banco local (.db)?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if confirm == QMessageBox.StandardButton.Yes:
                sucesso = self.firebase.restaurar_backup_local(tmp_path)
                if sucesso:
                    QMessageBox.information(self, "Sucesso", "Backup gravado no banco local! Reinicie o sistema.")
                else:
                    QMessageBox.critical(self, "Erro", "Falha ao gravar o backup no banco local.")
            
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def restaurar_backup_banco(self):
        caminho_backup, _ = QFileDialog.getOpenFileName(self, "Selecionar Backup", "", "Arquivos de Banco (*.db)")
        if caminho_backup:
            confirm = QMessageBox.question(self, "Confirmação", "ATENÇÃO: Isso irá substituir seus dados atuais pelos dados do backup. Continuar?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirm == QMessageBox.StandardButton.Yes:
                sucesso = self.firebase.restaurar_backup_local(caminho_backup)
                if sucesso:
                    QMessageBox.information(self, "Sucesso", "Backup restaurado com êxito! Por favor, reinicie o sistema.")
                else:
                    QMessageBox.critical(self, "Erro", "Falha ao restaurar o arquivo.")
    
    def fazer_backup_nuvem(self):
        sucesso = self.firebase.enviar_backup_oficial_nuvem(self.email)
        if sucesso:
            QMessageBox.information(self, "Nuvem", "Backup completo do banco (.db) enviado para o Firebase com sucesso!")
        else:
            QMessageBox.critical(self, "Nuvem", "Falha ao enviar backup para o Firebase. Verifique o console.")

    def fazer_backup_local(self):
        destino = self.firebase.fazer_backup_local_gerenciado()
        if destino:
            QMessageBox.information(self, "Backup Local", f"Backup salvo em:\n{destino}")
        else:
            caminho_destino = QFileDialog.getExistingDirectory(self, "Escolher pasta para Backup")
            if caminho_destino:
                try:
                    shutil.copy(self.firebase.caminho_db_local, os.path.join(caminho_destino, f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"))
                    QMessageBox.information(self, "Backup", "Backup local realizado com sucesso!")
                except Exception as e:
                    QMessageBox.critical(self, "Erro", f"Falha ao realizar backup: {e}")
    
    def carregar_codigos(self):
        if not self.is_admin:
            return
        """Carrega e exibe todos os códigos (ativos e utilizados) com o respectivo e-mail associado na interface"""
        self.lista_codigos.clear() 
        
        try:
            docs = self.firebase.db.collection('codigos_convite').stream()
            tem_itens = False
            for doc in docs:
                tem_itens = True
                dados = doc.to_dict()
                codigo = dados.get('codigo', 'Desconhecido')
                status = dados.get('status', 'Ativo')
                email_associado = dados.get('email_associado')
                
                if status == 'Utilizado' and email_associado:
                    texto_exibicao = f"🔑 {codigo} - Status: {status} (Conta: {email_associado})"
                else:
                    texto_exibicao = f"🔑 {codigo} - Status: {status}"
                    
                self.lista_codigos.addItem(texto_exibicao)
                
            if not tem_itens:
                self.lista_codigos.addItem("Nenhum código encontrado.")
        except Exception as e:
            print(f"[DEBUG] Erro ao carregar códigos: {e}")
            self.lista_codigos.addItem("Erro ao carregar códigos da nuvem.")

    def gerar_codigo(self):
        if not self.is_admin:
            QMessageBox.critical(self, "Acesso Negado", "Apenas administradores podem gerar códigos.")
            return
        novo_codigo = str(uuid.uuid4())[:8].upper()
        try:
            cursor = self.banco.conexao.cursor()
            cursor.execute("INSERT INTO codigos_convite (codigo, status) VALUES (?, 'Ativo')", (novo_codigo,))
            self.banco.conexao.commit()
            
            self.firebase.salvar_codigo_convite(novo_codigo)
            self.carregar_codigos()
            QMessageBox.information(self, "Sucesso", f"Código gerado: {novo_codigo}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao gerar código: {e}")

class DialogTrocaSenha(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Alterar Senha")
        layout = QFormLayout(self)
        
        self.txt_antiga = QLineEdit()
        self.txt_antiga.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_nova = QLineEdit()
        self.txt_nova.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_confirma = QLineEdit()
        self.txt_confirma.setEchoMode(QLineEdit.EchoMode.Password)
        
        layout.addRow("Senha Atual:", self.txt_antiga)
        layout.addRow("Nova Senha:", self.txt_nova)
        layout.addRow("Confirmar Nova:", self.txt_confirma)
        
        btn = QPushButton("Confirmar")
        btn.clicked.connect(self.accept)
        layout.addRow(btn)