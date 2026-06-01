from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class JanelaCadastro(QDialog):
    def __init__(self, banco):
        super().__init__()
        self.banco = banco
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Criar Nova Conta")
        self.setFixedSize(360, 420)
        self.setStyleSheet("background-color: #EFECE6;")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        titulo = QLabel("Cadastro de Funcionário")
        titulo.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        titulo.setStyleSheet("color: #4A4540;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)
        
        estilo_input = "padding: 10px; border: 1px solid #D1C7BD; border-radius: 6px; background: white;"
        
        self.txt_email = QLineEdit()
        self.txt_email.setPlaceholderText("E-mail corporativo")
        self.txt_email.setStyleSheet(estilo_input)
        
        self.txt_senha = QLineEdit()
        self.txt_senha.setPlaceholderText("Senha de acesso")
        self.txt_senha.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_senha.setStyleSheet(estilo_input)
        
        self.txt_confirmar_senha = QLineEdit()
        self.txt_confirmar_senha.setPlaceholderText("Repita a senha")
        self.txt_confirmar_senha.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_confirmar_senha.setStyleSheet(estilo_input)
        
        self.txt_codigo = QLineEdit()
        self.txt_codigo.setPlaceholderText("Código de validação (Gerado pelo ADM)")
        self.txt_codigo.setStyleSheet(estilo_input)
        
        btn_registrar = QPushButton("Finalizar Registro")
        btn_registrar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_registrar.setStyleSheet("""
            QPushButton { background-color: #8CA485; color: white; font-weight: bold; padding: 12px; border-radius: 6px; border: none; }
            QPushButton:hover { background-color: #7D9376; }
        """)
        btn_registrar.clicked.connect(self.processar_cadastro)
        
        layout.addWidget(self.txt_email)
        layout.addWidget(self.txt_senha)
        layout.addWidget(self.txt_confirmar_senha)
        layout.addWidget(self.txt_codigo)
        layout.addWidget(btn_registrar)

    def processar_cadastro(self):
        email = self.txt_email.text().strip()
        senha = self.txt_senha.text()
        conf_senha = self.txt_confirmar_senha.text()
        codigo = self.txt_codigo.text().strip()
        
        if not email or not senha or not codigo:
            QMessageBox.warning(self, "Campos Vazios", "Todos os campos precisam ser preenchidos.")
            return
            
        if senha != conf_senha:
            QMessageBox.warning(self, "Senhas Divergentes", "As senhas digitadas não são iguais.")
            return
            
        cursor = self.banco.conexao.cursor()
        cursor.execute("SELECT status FROM codigos_convite WHERE codigo = ? AND status = 'Ativo'", (codigo,))
        resultado = cursor.fetchone()
        
        if not resultado:
            QMessageBox.critical(self, "Acesso Negado", "Código de cadastro inválido, expirado ou já utilizado!")
            return
            
        try:
            cursor.execute("INSERT INTO usuarios (email, senha, perfil) VALUES (?, ?, 'funcionario')", (email, senha))
            cursor.execute("UPDATE codigos_convite SET status = 'Utilizado' WHERE codigo = ?", (codigo,))
            self.banco.conexao.commit()
            
            QMessageBox.information(self, "Sucesso!", "Conta criada com sucesso! Agora você já pode fazer login.")
            self.accept()
        except Exception:
            QMessageBox.critical(self, "Erro", "Este e-mail já está cadastrado no sistema.")