from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTabWidget, QPushButton, QHBoxLayout
from PyQt6.QtGui import QFont
from ui.components import COR_TEXTO_ESCURO
from ui.cadastro_tutor import CadastroTutorWidget
from ui.cadastro_pet import CadastroPetWidget
from ui.cadastro_atendimento import CadastroAtendimentoWidget
from ui.cadastro_gasto import CadastroGastoWidget
from ui.gerenciamento_cadastros import GerenciamentoCadastrosWidget

class TelaCadastroCentral(QWidget):
    def __init__(self, banco, atualizar_dashboard_callback=None):
        super().__init__()
        self.banco = banco
        self.atualizar_dashboard_callback = atualizar_dashboard_callback
        self.init_ui()

    def init_ui(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(15)

        topo_layout = QHBoxLayout()
        lbl_titulo = QLabel("📝 Central de Cadastros e Registros")
        lbl_titulo.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        lbl_titulo.setStyleSheet(f"color: {COR_TEXTO_ESCURO};")
        topo_layout.addWidget(lbl_titulo)

        btn_atualizar_geral = QPushButton("🔄 Atualizar Dados da Tela")
        btn_atualizar_geral.setStyleSheet("background-color: #D1C7BD; color: #3A3530; font-weight: bold; padding: 8px 15px; border-radius: 6px;")
        btn_atualizar_geral.clicked.connect(self.atualizar_dados_abas)
        topo_layout.addWidget(btn_atualizar_geral)
        layout_principal.addLayout(topo_layout)

        self.abas = QTabWidget()
        self.abas.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #D1C7BD; background: white; border-radius: 6px; }
            QTabBar::tab { background: #EFECE6; padding: 10px 20px; border-top-left-radius: 4px; border-top-right-radius: 4px; color: #3A3530; font-weight: bold;}
            QTabBar::tab:selected { background: white; border-bottom: 2px solid #8CA485; }
        """)

        self.aba_tutor = CadastroTutorWidget(self.banco, self.atualizar_dashboard_callback)
        self.aba_pet = CadastroPetWidget(self.banco)
        self.aba_atendimento = CadastroAtendimentoWidget(self.banco, self.atualizar_dashboard_callback)
        self.aba_gasto = CadastroGastoWidget(self.banco, self.atualizar_dashboard_callback)
        self.aba_gerenciamento = GerenciamentoCadastrosWidget(self.banco, self.atualizar_dashboard_callback)

        self.abas.addTab(self.aba_tutor, "👤 Cadastrar Tutor")
        self.abas.addTab(self.aba_pet, "🐾 Cadastrar Pet")
        self.abas.addTab(self.aba_atendimento, "📅 Agendar Serviço")
        self.abas.addTab(self.aba_gasto, "📉 Registrar Despesa / Estoque")
        self.abas.addTab(self.aba_gerenciamento, "🗂️ Gerenciar Cadastros")

        layout_principal.addWidget(self.abas)

    def atualizar_dados_abas(self):
        self.aba_pet.atualizar_combobox_tutores()
        self.aba_atendimento.atualizar_combobox_pets()
        if hasattr(self.aba_atendimento, 'carregar_servicos_combobox'):
            self.aba_atendimento.carregar_servicos_combobox()
        self.aba_gerenciamento.recarregar_tudo()

    def showEvent(self, event):
        super().showEvent(event)
        self.atualizar_dados_abas()