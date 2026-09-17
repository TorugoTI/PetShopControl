from PyQt6.QtWidgets import QWidget, QFormLayout, QLabel, QMessageBox
from ui.components import CampoTexto, BotaoPrincipal

class CadastroTutorWidget(QWidget):
    def __init__(self, banco, callback_atualizar=None):
        super().__init__()
        self.banco = banco
        self.callback_atualizar = callback_atualizar
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
        cpf_limpo = self.txt_cpf.text().replace(".", "").replace("-", "").replace("_", "").strip()
        tel_limpo = self.txt_telefone.text().replace("(", "").replace(")", "").replace("-", "").replace(" ", "").replace("_", "").strip()
        email = self.txt_email.text().strip()

        if not nome or len(tel_limpo) < 10:
            QMessageBox.warning(self, "Campos Obrigatórios", "Nome e Telefone são obrigatórios.")
            return

        if cpf_limpo and len(cpf_limpo) != 11:
            QMessageBox.warning(self, "CPF Incompleto", "O CPF deve ter 11 dígitos.")
            return

        try:
            cursor = self.banco.conexao.cursor()
            valor_cpf = self.txt_cpf.text() if len(cpf_limpo) == 11 else None
            
            cursor.execute("""
                INSERT INTO tutores (nome, cpf, telefone, email)
                VALUES (?, ?, ?, ?)
            """, (nome, valor_cpf, self.txt_telefone.text(), email))
            
            self.banco.conexao.commit()
            
            QMessageBox.information(self, "Sucesso", f"Tutor '{nome}' cadastrado!")
            
            self.txt_tutor_nome.clear()
            self.txt_cpf.clear()  
            self.txt_telefone.clear()
            self.txt_email.clear()
            
            if self.callback_atualizar:
                self.callback_atualizar()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro SQL", f"Falha ao salvar: {str(e)}")