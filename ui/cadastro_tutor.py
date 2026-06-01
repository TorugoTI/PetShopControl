from PyQt6.QtWidgets import QWidget, QFormLayout, QLabel, QMessageBox
from ui.components import CampoTexto, BotaoPrincipal

class CadastroTutorWidget(QWidget):
    def __init__(self, banco):
        super().__init__()
        self.banco = banco
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        self.txt_tutor_nome = CampoTexto("Nome Completo do Tutor")
        
        self.txt_cpf = CampoTexto("")
        self.txt_cpf.setInputMask("999.999.999-99;_") 
        
        self.txt_telefone = CampoTexto("")
        self.txt_telefone.setInputMask("(99) 99999-9999;_")
        
        self.txt_email = CampoTexto("exemplo@email.com")

        layout.addRow(QLabel("Nome do Tutor:"), self.txt_tutor_nome)
        layout.addRow(QLabel("CPF:"), self.txt_cpf)
        layout.addRow(QLabel("Telefone:"), self.txt_telefone)
        layout.addRow(QLabel("E-mail:"), self.txt_email)

        btn_salvar = BotaoPrincipal("Concluir Cadastro do Tutor")
        btn_salvar.clicked.connect(self.salvar_tutor)
        layout.addRow("", btn_salvar)

    def salvar_tutor(self):
        nome = self.txt_tutor_nome.text().strip()
        cpf_limpo = self.txt_cpf.text().replace(".", "").replace("-", "").strip()
        cpf_formatado = self.txt_cpf.text()
        
        tel_limpo = self.txt_telefone.text().replace("(", "").replace(")", "").replace("-", "").replace(" ", "").strip()
        tel_formatado = self.txt_telefone.text()
        
        email = self.txt_email.text().strip()

        if not nome or len(tel_limpo) < 11:
            QMessageBox.warning(self, "Campos Obrigatórios", "Por favor, insira o Nome e o Telefone com DDD completo.")
            return

        if len(cpf_limpo) > 0 and len(cpf_limpo) < 11:
            QMessageBox.warning(self, "CPF Incompleto", "Por favor, digite todos os 11 números do CPF.")
            return

        try:
            cursor = self.banco.conexao.cursor()
            cursor.execute("""
                INSERT INTO tutores (nome, cpf, telefone, email)
                VALUES (?, ?, ?, ?)
            """, (nome, cpf_formatado if len(cpf_limpo) == 11 else "", tel_formatado, email))
            self.banco.conexao.commit()
            
            QMessageBox.information(self, "Sucesso", f"O tutor '{nome}' foi cadastrado com sucesso!")
            
            self.txt_tutor_nome.clear()
            self.txt_cpf.clear()  
            self.txt_telefone.clear()
            self.txt_email.clear()
        except Exception as e:
            QMessageBox.critical(self, "Erro SQL", f"Falha ao salvar tutor: {str(e)}")