from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, 
    QTableWidgetItem, QHeaderView, QTabWidget, QMessageBox, QMenu, QPushButton
)
from PyQt6.QtGui import QFont, QAction
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
        self.tabela_entradas.customContextMenuRequested.connect(
            lambda pos: self.abrir_menu_contexto(pos, self.tabela_entradas, "atendimentos", "Atendimento/Receita")
        )
        layout_entradas.addWidget(self.tabela_entradas)
        btn_exc_ent = QPushButton("🗑️ Excluir Entrada Selecionada")
        btn_exc_ent.setStyleSheet("background-color: #BA3C2A; color: white; font-weight: bold; padding: 6px; border-radius: 4px;")
        btn_exc_ent.clicked.connect(lambda: self.excluir_selecionado_tabela(self.tabela_entradas, "atendimentos"))
        layout_entradas.addWidget(btn_exc_ent)

        self.tab_saidas = QWidget()
        layout_saidas = QVBoxLayout(self.tab_saidas)
        self.tabela_saidas = QTableWidget()
        self.configurar_tabela(self.tabela_saidas, ["ID", "Descrição do Gasto", "Data de Pagamento", "Valor Pago (R$)"])
        self.tabela_saidas.customContextMenuRequested.connect(
            lambda pos: self.abrir_menu_contexto(pos, self.tabela_saidas, "gastos", "Despesa/Gasto")
        )
        layout_saidas.addWidget(self.tabela_saidas)
        btn_exc_sai = QPushButton("🗑️ Excluir Saída Selecionada")
        btn_exc_sai.setStyleSheet("background-color: #BA3C2A; color: white; font-weight: bold; padding: 6px; border-radius: 4px;")
        btn_exc_sai.clicked.connect(lambda: self.excluir_selecionado_tabela(self.tabela_saidas, "gastos"))
        layout_saidas.addWidget(btn_exc_sai)

        self.abas.addTab(self.tab_entradas, "📈 Entradas (Serviços)")
        self.abas.addTab(self.tab_saidas, "📉 Saídas (Despesas / Estoque)")
        layout_principal.addWidget(self.abas)

        self.atualizar_dados_financeiros()

    def excluir_selecionado_tabela(self, tabela, tabela_sql):
        row = tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Selecione uma linha na tabela.")
            return
        id_item = tabela.item(row, 0).text()
        self.excluir_registro(id_item, tabela_sql)

    def criar_card(self, titulo, valor_inicial, cor_fundo):
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
        tabela.setColumnCount(len(colunas))
        tabela.setHorizontalHeaderLabels(colunas)
        tabela.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        tabela.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tabela.verticalHeader().setVisible(False)
        tabela.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        
        header = tabela.horizontalHeader()
        for i in range(len(colunas)):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

    def abrir_menu_contexto(self, pos, tabela, nome_tabela_sql, rotulo):
        item = tabela.itemAt(pos)
        if not item:
            return

        row = item.row()
        id_item = tabela.item(row, 0).text()

        menu = QMenu(self)
        acao_excluir = QAction(f"🗑️ Excluir {rotulo} (ID {id_item})", self)
        acao_excluir.triggered.connect(lambda: self.excluir_registro(id_item, nome_tabela_sql))
        menu.addAction(acao_excluir)
        
        menu.exec(tabela.viewport().mapToGlobal(pos))

    def excluir_registro(self, registro_id, nome_tabela_sql):
        if not self.banco or not self.banco.conexao:
            return

        confirmar = QMessageBox.question(
            self, 
            "Confirmar Exclusão", 
            f"Tem certeza que deseja excluir o registro ID {registro_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if confirmar == QMessageBox.StandardButton.Yes:
            try:
                cursor = self.banco.conexao.cursor()
                cursor.execute(f"DELETE FROM {nome_tabela_sql} WHERE id = ?", (registro_id,))
                self.banco.conexao.commit()
                QMessageBox.information(self, "Sucesso", "Registro excluído com sucesso!")
                self.atualizar_dados_financeiros()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao excluir registro: {e}")

    def atualizar_dados_financeiros(self):
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
        super().showEvent(event)
        self.atualizar_dados_financeiros()