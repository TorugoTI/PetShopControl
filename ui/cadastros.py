from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTabWidget, QFormLayout, QMessageBox, QComboBox, QTimeEdit
)
from PyQt6.QtCore import Qt, QTime
from PyQt6.QtGui import QFont
from ui.components import BotaoPrincipal, CampoTexto, SeletorData, COR_TEXTO_ESCURO

class TelaCadastros(QWidget):
    def __init__(self, banco, atualizar_dashboard_callback=None):
        super().__init__()
        self.banco = banco
        self.atualizar_dashboard_callback = atualizar_dashboard_callback
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("PetShop Control v3.0 - Central de Inserção")
        self.resize(600, 500)
        self.setStyleSheet("background-color: #F4F1EA;")

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)

        self.abas = QTabWidget()
        self.abas.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #D1C7BD; background: white; border-radius: 6px; }
            QTabBar::tab { background: #EFECE6; padding: 10px 20px; border-top-left-radius: 4px; border-top-right-radius: 4px; color: #3A3530; }
            QTabBar::tab:selected { background: white; border: 1px solid #D1C7BD; border-bottom: none; font-weight: bold; }
        """)

        self.aba_pet = QWidget()
        self.aba_atendimento = QWidget()
        self.aba_gasto = QWidget()

        self.montar_aba_pet()
        self.montar_aba_atendimento()
        self.montar_aba_gasto()

        self.abas.addTab(self.aba_pet, "🐾 Cadastrar Pet")
        self.abas.addTab(self.aba_atendimento, "🗓️ Agendar Consulta/Banho")
        self.abas.addTab(self.aba_gasto, "💰 Lançar Gastos")

        layout_principal.addWidget(self.abas)

    def montar_aba_pet(self):
        layout = QFormLayout(self.aba_pet)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        self.txt_nome_pet = CampoTexto("Ex: Rex")
        self.txt_especie = CampoTexto("Ex: Cão, Gato")
        self.txt_raca = CampoTexto("Ex: Golden Retriever")
        self.txt_dono = CampoTexto("Nome completo do tutor")
        self.txt_telefone = CampoTexto("Ex: (27) 99999-1111")

        layout.addRow(QLabel("Nome do Animal:"), self.txt_nome_pet)
        layout.addRow(QLabel("Espécie:"), self.txt_especie)
        layout.addRow(QLabel("Raça:"), self.txt_raca)
        layout.addRow(QLabel("Nome do Dono:"), self.txt_dono)
        layout.addRow(QLabel("Telefone:"), self.txt_telefone)

        btn_salvar = BotaoPrincipal("Gravar Cadastro do Pet")
        btn_salvar.clicked.connect(self.salvar_pet)
        layout.addRow("", btn_salvar)

    def salvar_pet(self):
        cursor = self.banco.conexao.cursor()
        cursor.execute("""
            INSERT INTO pets (nome, especie, raca, nome_dono, telefone_dono)
            VALUES (?, ?, ?, ?, ?)
        """, (self.txt_nome_pet.text(), self.txt_especie.text(), self.txt_raca.text(), self.txt_dono.text(), self.txt_telefone.text()))
        self.banco.conexao.commit()
        
        QMessageBox.information(self, "Sucesso", f"O pet {self.txt_nome_pet.text()} foi cadastrado no PC!")
        self.limpar_campos_pet()
        self.atualizar_combobox_pets()

    def limpar_campos_pet(self):
        self.txt_nome_pet.clear()
        self.txt_especie.clear()
        self.txt_raca.clear()
        self.txt_dono.clear()
        self.txt_telefone.clear()

    def montar_aba_atendimento(self):
        layout = QFormLayout(self.aba_atendimento)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        self.combo_pets = QComboBox()
        self.combo_pets.setStyleSheet("padding: 6px; border: 1px solid #9A9590; border-radius: 4px;")
        self.atualizar_combobox_pets()

        self.combo_servico = QComboBox()
        self.combo_servico.addItems(["Banho Completo", "Tosa Higiênica", "Banho e Tosa", "Consulta Veterinária"])
        self.combo_servico.setStyleSheet("padding: 6px; border: 1px solid #9A9590; border-radius: 4px;")

        self.calendario_data = SeletorData()
        
        self.relogio_hora = QTimeEdit()
        self.relogio_hora.setTime(QTime.currentTime())
        self.relogio_hora.setStyleSheet("padding: 6px; border: 1px solid #9A9590; border-radius: 4px;")

        self.txt_valor = CampoTexto("Ex: 80.00")

        layout.addRow(QLabel("Selecionar Pet:"), self.combo_pets)
        layout.addRow(QLabel("Serviço desejado:"), self.combo_servico)
        layout.addRow(QLabel("Data Agendada:"), self.calendario_data)
        layout.addRow(QLabel("Horário:"), self.relogio_hora)
        layout.addRow(QLabel("Valor Cobrado (R$):"), self.txt_valor)

        btn_agendar = BotaoPrincipal("Confirmar Agendamento")
        btn_agendar.clicked.connect(self.salvar_atendimento)
        layout.addRow("", btn_agendar)

    def atualizar_combobox_pets(self):
        """Busca os IDs e Nomes dos pets direto no SQLite para exibir no seletor"""
        self.combo_pets.clear()
        cursor = self.banco.conexao.cursor()
        cursor.execute("SELECT id, nome FROM pets")
        for pet_id, nome in cursor.fetchall():
            self.combo_pets.addItem(nome, pet_id)

    def salvar_atendimento(self):
        pet_id = self.combo_pets.currentData()
        if not pet_id:
            QMessageBox.warning(self, "Aviso", "Cadastre um pet primeiro antes de agendar.")
            return

        data_texto = self.calendario_data.date().toString("yyyy-MM-dd")
        hora_texto = self.relogio_hora.time().toString("HH:mm")
        servico_selecionado = self.combo_servico.currentText()

        cursor = self.banco.conexao.cursor()
        cursor.execute("""
            INSERT INTO atendimentos (pet_id, servico, data_atendimento, hora_atendimento, valor)
            VALUES (?, ?, ?, ?, ?)
        """, (pet_id, servico_selecionado, data_texto, hora_texto, float(self.txt_valor.text() or 0)))
        self.banco.conexao.commit()

        from domain.estoque_inteligente import GerenciadorEstoqueInteligente
        ia_estoque = GerenciadorEstoqueInteligente(self.banco)
        alertas = ia_estoque.processar_consumo_por_atendimento(servico_selecionado)
        
        if alertas:
            mensagem_alerta = "\n".join(alertas)
            QMessageBox.warning(self, "Alerta de Estoque Inteligente", 
                                f"Agendamento salvo!\n\n{mensagem_alerta}\n\nRecomendamos programar a compra desses insumos.")
        else:
            QMessageBox.information(self, "Sucesso", "Agendamento registrado localmente!")

        self.txt_valor.clear()
        
        if self.atualizar_dashboard_callback:
            self.atualizar_dashboard_callback()

    def montar_aba_gasto(self):
        layout = QFormLayout(self.aba_gasto)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        self.txt_gasto_desc = CampoTexto("Ex: Aluguel da Loja, Compra de Shampoo")
        self.txt_gasto_valor = CampoTexto("Ex: 150.00")
        self.calendario_gasto = SeletorData()

        layout.addRow(QLabel("Descrição da Despesa:"), self.txt_gasto_desc)
        layout.addRow(QLabel("Valor Pago (R$):"), self.txt_gasto_valor)
        layout.addRow(QLabel("Data do Gasto:"), self.calendario_gasto)

        btn_gasto = BotaoPrincipal("Registrar Despesa")
        btn_gasto.clicked.connect(self.salvar_gasto)
        layout.addRow("", btn_gasto)

    def salvar_gasto(self):
        data_texto = self.calendario_gasto.date().toString("yyyy-MM-dd")
        
        cursor = self.banco.conexao.cursor()
        cursor.execute("""
            INSERT INTO gastos (descricao, valor, data_gasto)
            VALUES (?, ?, ?)
        """, (self.txt_gasto_desc.text(), float(self.txt_gasto_valor.text() or 0), data_texto))
        self.banco.conexao.commit()

        QMessageBox.information(self, "Sucesso", "Despesa arquivada!")
        self.txt_gasto_desc.clear()
        self.txt_gasto_valor.clear()

        if self.atualizar_dashboard_callback:
            self.atualizar_dashboard_callback()