from PyQt6.QtWidgets import QWidget, QFormLayout, QLabel, QComboBox, QTimeEdit, QMessageBox
from PyQt6.QtCore import QTime
from ui.components import BotaoPrincipal, SeletorData, CampoMoedaBancario

class CadastroAtendimentoWidget(QWidget):
    def __init__(self, banco, callback_atualizar):
        super().__init__()
        self.banco = banco
        self.callback_atualizar = callback_atualizar
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        self.cb_pets = QComboBox()
        self.atualizar_combobox_pets()

        self.cb_servico = QComboBox()
        self.cb_servico.addItems(["Banho Simples", "Banho e Tosa", "Consulta Veterinária", "Tosa Higiênica"])

        self.cal_atendimento = SeletorData()
        self.time_atendimento = QTimeEdit()
        self.time_atendimento.setTime(QTime.currentTime())
        
        self.txt_valor = CampoMoedaBancario()
        self.txt_valor.setStyleSheet("font-size: 14px; padding: 6px; background: white; border: 1px solid #D1C7BD; border-radius: 4px;")

        layout.addRow(QLabel("Selecionar Paciente:"), self.cb_pets)
        layout.addRow(QLabel("Serviço solicitado:"), self.cb_servico)
        layout.addRow(QLabel("Data da Agenda:"), self.cal_atendimento)
        layout.addRow(QLabel("Horário:"), self.time_atendimento)
        layout.addRow(QLabel("Preço Cobrado:"), self.txt_valor)

        btn_atendimento = BotaoPrincipal("Confirmar Agendamento")
        btn_atendimento.clicked.connect(self.salvar_atendimento)
        layout.addRow("", btn_atendimento)

    def atualizar_combobox_pets(self):
        self.cb_pets.clear()
        if not self.banco or not self.banco.conexao: return
        try:
            cursor = self.banco.conexao.cursor()
            cursor.execute("SELECT id, nome FROM pets ORDER BY nome ASC")
            for id_pet, nome in cursor.fetchall():
                self.cb_pets.addItem(nome, id_pet)
        except Exception as e:
            print(f"Erro ao carregar combo de pets: {e}")

    def salvar_atendimento(self):
        if self.cb_pets.currentIndex() == -1:
            QMessageBox.warning(self, "Aviso", "Cadastre um pet antes de realizar um agendamento.")
            return

        pet_id = self.cb_pets.currentData()
        servico = self.cb_servico.currentText()
        data_texto = self.cal_atendimento.date().toString("yyyy-MM-dd")
        hora_texto = self.time_atendimento.time().toString("hh:mm")
        
        valor = self.txt_valor.pegar_valor_float()

        try:
            cursor = self.banco.conexao.cursor()
            cursor.execute("""
                INSERT INTO atendimentos (pet_id, servico, data_atendimento, hora_atendimento, valor, status)
                VALUES (?, ?, ?, ?, ?, 'Agendado')
            """, (pet_id, servico, data_texto, hora_texto, valor))
            self.banco.conexao.commit()

            QMessageBox.information(self, "Agendado!", "Serviço agendado com sucesso!")
            self.txt_valor.clear()

            if self.callback_atualizar:
                self.callback_atualizar()
                
        except Exception as e:
            QMessageBox.critical(self, "Erro SQL", f"Falha ao agendar: {str(e)}")