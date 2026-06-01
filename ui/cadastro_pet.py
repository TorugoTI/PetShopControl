from PyQt6.QtWidgets import QWidget, QFormLayout, QLabel, QMessageBox, QComboBox
from ui.components import CampoTexto, BotaoPrincipal

class CadastroPetWidget(QWidget):
    def __init__(self, banco):
        super().__init__()
        self.banco = banco
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        self.txt_pet_nome = CampoTexto("Nome do Pet")
        self.txt_pet_especie = CampoTexto("Ex: Cão, Gato")
        self.txt_pet_raca = CampoTexto("Raça")
        
        self.cb_tutores = QComboBox()
        self.atualizar_combobox_tutores()

        layout.addRow(QLabel("Nome do Paciente:"), self.txt_pet_nome)
        layout.addRow(QLabel("Espécie:"), self.txt_pet_especie)
        layout.addRow(QLabel("Raça:"), self.txt_pet_raca)
        layout.addRow(QLabel("Selecionar Tutor:"), self.cb_tutores)

        btn_salvar = BotaoPrincipal("Concluir Cadastro do Pet")
        btn_salvar.clicked.connect(self.salvar_pet)
        layout.addRow("", btn_salvar)

    def atualizar_combobox_tutores(self):
        self.cb_tutores.clear()
        if not self.banco or not self.banco.conexao: return
        try:
            cursor = self.banco.conexao.cursor()
            cursor.execute("SELECT id, nome FROM tutores ORDER BY nome ASC")
            for id_tutor, nome in cursor.fetchall():
                self.cb_tutores.addItem(nome, id_tutor)
        except Exception as e:
            print(f"Erro ao carregar combo de tutores: {e}")

    def salvar_pet(self):
        nome = self.txt_pet_nome.text().strip()
        especie = self.txt_pet_especie.text().strip()
        raca = self.txt_pet_raca.text().strip()

        if self.cb_tutores.currentIndex() == -1:
            QMessageBox.warning(self, "Aviso", "Cadastre um tutor antes de registrar um pet.")
            return

        tutor_id = self.cb_tutores.currentData()

        if not nome:
            QMessageBox.warning(self, "Campos Obrigatórios", "Por favor, preencha o Nome do Pet.")
            return

        try:
            cursor = self.banco.conexao.cursor()
            cursor.execute("""
                INSERT INTO pets (nome, especie, raca, tutor_id)
                VALUES (?, ?, ?, ?)
            """, (nome, especie, raca, tutor_id))
            self.banco.conexao.commit()
            
            QMessageBox.information(self, "Sucesso", f"O pet '{nome}' foi cadastrado com sucesso!")
            self.txt_pet_nome.clear()
            self.txt_pet_especie.clear()
            self.txt_pet_raca.clear()
        except Exception as e:
            QMessageBox.critical(self, "Erro SQL", f"Falha ao salvar pet: {str(e)}")