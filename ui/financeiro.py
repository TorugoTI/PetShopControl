from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from ui.components import COR_TEXTO_ESCURO

class TelaFinanceiro(QWidget):
    def __init__(self, banco):
        super().__init__()
        self.banco = banco
        self.init_ui()

    def init_ui(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(20)

        lbl_titulo = QLabel("💰 Fluxo de Caixa e Indicadores Financeiros")
        lbl_titulo.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        lbl_titulo.setStyleSheet(f"color: {COR_TEXTO_ESCURO if 'COR_TEXTO_ESCURO' in globals() else '#3A3530'};")
        layout_principal.addWidget(lbl_titulo)

        layout_cards = QHBoxLayout()
        layout_cards.setSpacing(15)

        self.card_receita = self.criar_card("🟢 FATURAMENTO BRUTO", "R$ 0,00", "#8CA485")
        self.card_despesa = self.criar_card("🔴 DESPESAS TOTAIS", "R$ 0,00", "#D1C7BD")
        self.card_lucro = self.criar_card("⚫ LUCRO LÍQUIDO", "R$ 0,00", "#E6C15C")

        layout_cards.addWidget(self.card_receita)
        layout_cards.addWidget(self.card_despesa)
        layout_cards.addWidget(self.card_lucro)
        layout_principal.addLayout(layout_cards)

        self.abas = QTabWidget()
        self.abas.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #D1C7BD; background: white; border-radius: 6px; }
            QTabBar::tab { background: #EFECE6; padding: 10px 20px; border-top-left-radius: 4px; border-top-right-radius: 4px; color: #3A3530; font-weight: bold;}
            QTabBar::tab:selected { background: white; border-bottom: 2px solid #8CA485; }
        """)

        self.tab_entradas = QWidget()
        layout_entradas = QVBoxLayout(self.tab_entradas)
        self.tabela_entradas = QTableWidget()
        self.configurar_tabela(self.tabela_entradas, ["ID", "Cliente/Pet", "Serviço Prestado", "Data", "Valor (R$)"])
        layout_entradas.addWidget(self.tabela_entradas)

        self.tab_saidas = QWidget()
        layout_saidas = QVBoxLayout(self.tab_saidas)
        self.tabela_saidas = QTableWidget()
        self.configurar_tabela(self.tabela_saidas, ["ID", "Descrição do Gasto", "Data de Pagamento", "Valor Pago (R$)"])
        layout_saidas.addWidget(self.tabela_saidas)

        self.abas.addTab(self.tab_entradas, "📈 Entradas (Serviços)")
        self.abas.addTab(self.tab_saidas, "📉 Saídas (Despesas / Estoque)")
        layout_principal.addWidget(self.abas)

        self.atualizar_dados_financeiros()

    def criar_card(self, titulo, valor_inicial, cor_fundo):
        """Helper para criar os cards coloridos de indicadores com texto escuro para melhor leitura"""
        card = QWidget()
        card.setObjectName("Card")
        card.setStyleSheet(f"""
            QWidget#Card {{
                background-color: {cor_fundo};
                border-radius: 8px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)

        cor_texto_legivel = "#3A3530"

        lbl_tit = QLabel(titulo)
        lbl_tit.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        lbl_tit.setStyleSheet(f"color: {cor_texto_legivel}; background: transparent;")

        lbl_val = QLabel(valor_inicial)
        lbl_val.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        lbl_val.setStyleSheet(f"color: {cor_texto_legivel}; background: transparent;")

        layout.addWidget(lbl_tit)
        layout.addWidget(lbl_val)
        
        card.lbl_valor = lbl_val
        return card

    def configurar_tabela(self, tabela, colunas):
        """Ajusta o design padrão das tabelas"""
        tabela.setColumnCount(len(colunas))
        tabela.setHorizontalHeaderLabels(colunas)
        tabela.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        tabela.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tabela.verticalHeader().setVisible(False)
        
        header = tabela.horizontalHeader()
        for i in range(len(colunas)):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

    def atualizar_dados_financeiros(self):
        """Busca as informações em tempo real no banco e atualiza os cards e tabelas"""
        if not self.banco or not self.banco.conexao:
            return

        try:
            cursor = self.banco.conexao.cursor()

            cursor.execute("""
                SELECT a.id, p.nome, a.servico, a.data_atendimento, a.valor 
                FROM atendimentos a
                JOIN pets p ON a.pet_id = p.id
                ORDER BY a.id DESC
            """)
            entradas = cursor.fetchall()
            
            self.tabela_entradas.setRowCount(0)
            total_receitas = 0.0
            for row_idx, (id_atend, pet, servico, data, valor) in enumerate(entradas):
                self.tabela_entradas.insertRow(row_idx)
                self.tabela_entradas.setItem(row_idx, 0, QTableWidgetItem(str(id_atend)))
                self.tabela_entradas.setItem(row_idx, 1, QTableWidgetItem(pet))
                self.tabela_entradas.setItem(row_idx, 2, QTableWidgetItem(servico))
                self.tabela_entradas.setItem(row_idx, 3, QTableWidgetItem(data))
                
                val_formatado = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                self.tabela_entradas.setItem(row_idx, 4, QTableWidgetItem(val_formatado))
                total_receitas += valor if valor else 0.0

            cursor.execute("SELECT id, descricao, data_gasto, valor FROM gastos ORDER BY data_gasto DESC")
            saidas = cursor.fetchall()
            
            self.tabela_saidas.setRowCount(0)
            total_despesas = 0.0
            for row_idx, (id_gasto, desc, data, valor) in enumerate(saidas):
                self.tabela_saidas.insertRow(row_idx)
                self.tabela_saidas.setItem(row_idx, 0, QTableWidgetItem(str(id_gasto)))
                self.tabela_saidas.setItem(row_idx, 1, QTableWidgetItem(desc))
                self.tabela_saidas.setItem(row_idx, 2, QTableWidgetItem(data))
                
                val_formatado = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                self.tabela_saidas.setItem(row_idx, 3, QTableWidgetItem(val_formatado))
                total_despesas += valor if valor else 0.0

            lucro_liquido = total_receitas - total_despesas

            txt_rec = f"R$ {total_receitas:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            txt_des = f"R$ {total_despesas:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            txt_luc = f"R$ {lucro_liquido:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            self.card_receita.lbl_valor.setText(txt_rec)
            self.card_despesa.lbl_valor.setText(txt_des)
            self.card_lucro.lbl_valor.setText(txt_luc)

            if lucro_liquido >= 0:
                self.card_lucro.lbl_valor.setStyleSheet("color: #3A3530; font-weight: bold;")
            else:
                self.card_lucro.lbl_valor.setStyleSheet("color: #BA3C2A; font-weight: bold;")

        except Exception as e:
            print(f"Erro ao carregar dados financeiros: {e}")

    def showEvent(self, event):
        """Atualiza a tela automaticamente sempre que o usuário clicar na aba Financeiro"""
        super().showEvent(event)
        self.atualizar_dados_financeiros()