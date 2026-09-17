from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, 
    QTableWidgetItem, QHeaderView, QFormLayout, QMessageBox, QSpinBox, QPushButton, QMenu
)
from PyQt6.QtGui import QFont, QColor, QAction
from PyQt6.QtCore import Qt
from ui.components import BotaoPrincipal, CampoTexto, CampoMoedaBancario, COR_TEXTO_ESCURO

class TelaEstoque(QWidget):
    def __init__(self, banco):
        super().__init__()
        self.banco = banco
        self.init_ui()

    def init_ui(self):
        layout_principal = QHBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(20)

        container_esquerda = QWidget()
        layout_esquerda = QVBoxLayout(container_esquerda)
        layout_esquerda.setContentsMargins(0, 0, 0, 0)

        lbl_titulo = QLabel("📦 Controle de Inventário / Estoque")
        lbl_titulo.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        lbl_titulo.setStyleSheet(f"color: {COR_TEXTO_ESCURO if 'COR_TEXTO_ESCURO' in globals() else '#3A3530'};")
        layout_esquerda.addWidget(lbl_titulo)

        self.tabela_estoque = QTableWidget()
        colunas = ["ID", "Nome do Produto", "Qtd", "Preço Custo", "Preço Venda", "Status"]
        self.tabela_estoque.setColumnCount(len(colunas))
        self.tabela_estoque.setHorizontalHeaderLabels(colunas)
        self.tabela_estoque.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabela_estoque.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabela_estoque.verticalHeader().setVisible(False)
        self.tabela_estoque.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabela_estoque.customContextMenuRequested.connect(self.abrir_menu_contexto)
        
        header = self.tabela_estoque.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

        self.tabela_estoque.setStyleSheet("""
            QTableWidget { background-color: white; border: 1px solid #D1C7BD; border-radius: 6px; }
            QHeaderView::section { background-color: #D1C7BD; color: #3A3530; padding: 8px; font-weight: bold; border: none; }
        """)
        layout_esquerda.addWidget(self.tabela_estoque)

        # Botão físico de exclusão abaixo da tabela
        btn_excluir_tabela = QPushButton("🗑️ Excluir ItemSelecionado do Estoque")
        btn_excluir_tabela.setStyleSheet("background-color: #BA3C2A; color: white; font-weight: bold; padding: 8px; border-radius: 4px;")
        btn_excluir_tabela.clicked.connect(self.excluir_item_selecionado)
        layout_esquerda.addWidget(btn_excluir_tabela)

        layout_principal.addWidget(container_esquerda, stretch=3)

        container_direita = QWidget()
        container_direita.setFixedWidth(320)
        container_direita.setStyleSheet("background: white; border: 1px solid #D1C7BD; border-radius: 8px; padding: 15px;")
        layout_direita = QVBoxLayout(container_direita)
        
        lbl_form = QLabel("🆕 Adicionar / Atualizar Item")
        lbl_form.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        lbl_form.setStyleSheet("color: #3A3530; margin-bottom: 10px; border: none;")
        layout_direita.addWidget(lbl_form)

        form = QFormLayout()
        form.setSpacing(12)

        self.txt_nome = CampoTexto("Ex: Shampoo Clareador 5L")
        self.txt_qtd = QSpinBox()
        self.txt_qtd.setRange(0, 9999)
        self.txt_qtd.setValue(1)
        self.txt_qtd.setStyleSheet("font-size: 14px; padding: 6px; background: white; border: 1px solid #D1C7BD; border-radius: 4px;")
        
        self.txt_custo = CampoMoedaBancario()
        self.txt_custo.setStyleSheet("font-size: 14px; padding: 6px; background: white; border: 1px solid #D1C7BD; border-radius: 4px;")
        
        self.txt_venda = CampoMoedaBancario()
        self.txt_venda.setStyleSheet("font-size: 14px; padding: 6px; background: white; border: 1px solid #D1C7BD; border-radius: 4px;")

        form.addRow(QLabel("Nome do Item:"), self.txt_nome)
        form.addRow(QLabel("Quantidade Inicial:"), self.txt_qtd)
        form.addRow(QLabel("Preço de Custo:"), self.txt_custo)
        form.addRow(QLabel("Preço de Venda:"), self.txt_venda)
        layout_direita.addLayout(form)

        btn_salvar = BotaoPrincipal("Registrar no Estoque")
        btn_salvar.clicked.connect(self.salvar_produto)
        layout_direita.addWidget(btn_salvar)
        layout_direita.addStretch()

        layout_principal.addWidget(container_direita, stretch=1)
        self.atualizar_tabela_estoque()

    def abrir_menu_contexto(self, pos):
        item = self.tabela_estoque.itemAt(pos)
        if not item: return
        menu = QMenu(self)
        acao = QAction("🗑️ Excluir Produto", self)
        acao.triggered.connect(self.excluir_item_selecionado)
        menu.addAction(acao)
        menu.exec(self.tabela_estoque.viewport().mapToGlobal(pos))

    def excluir_item_selecionado(self):
        row = self.tabela_estoque.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Selecione um item na tabela para excluir.")
            return
        id_item = self.tabela_estoque.item(row, 0).text()
        nome_item = self.tabela_estoque.item(row, 1).text()
        
        if QMessageBox.question(self, "Confirmar", f"Excluir '{nome_item}' do estoque?") == QMessageBox.StandardButton.Yes:
            try:
                cursor = self.banco.conexao.cursor()
                cursor.execute("DELETE FROM produtos WHERE id = ?", (id_item,))
                self.banco.conexao.commit()
                self.atualizar_tabela_estoque()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao excluir: {e}")

    def atualizar_tabela_estoque(self):
        if not self.banco or not self.banco.conexao: return
        try:
            cursor = self.banco.conexao.cursor()
            cursor.execute("SELECT id, nome, quantidade, preco_custo, preco_venda FROM produtos ORDER BY nome ASC")
            produtos = cursor.fetchall()
            self.tabela_estoque.setRowCount(0)
            for row_idx, (id_prod, nome, qtd, custo, venda) in enumerate(produtos):
                self.tabela_estoque.insertRow(row_idx)
                self.tabela_estoque.setItem(row_idx, 0, QTableWidgetItem(str(id_prod)))
                self.tabela_estoque.setItem(row_idx, 1, QTableWidgetItem(nome))
                self.tabela_estoque.setItem(row_idx, 2, QTableWidgetItem(str(qtd)))
                self.tabela_estoque.setItem(row_idx, 3, QTableWidgetItem(f"R$ {custo:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")))
                self.tabela_estoque.setItem(row_idx, 4, QTableWidgetItem(f"R$ {venda:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")))
                
                status_item = QTableWidgetItem("🚫 Esgotado" if qtd <= 0 else ("⚠️ Baixo" if qtd <= 5 else "✅ OK"))
                status_item.setForeground(QColor("#BA3C2A" if qtd <= 0 else ("#E6C15C" if qtd <= 5 else "#8CA485")))
                status_item.setFont(QFont("Arial", 9, QFont.Weight.Bold))
                self.tabela_estoque.setItem(row_idx, 5, status_item)
        except Exception as e:
            print(f"Erro estoque: {e}")

    def salvar_produto(self):
        nome = self.txt_nome.text().strip()
        qtd = self.txt_qtd.value()
        custo = self.txt_custo.pegar_valor_float()
        venda = self.txt_venda.pegar_valor_float()
        if not nome: return
        try:
            cursor = self.banco.conexao.cursor()
            cursor.execute("SELECT id, quantidade FROM produtos WHERE LOWER(nome) = LOWER(?)", (nome,))
            existe = cursor.fetchone()
            if existe:
                cursor.execute("UPDATE produtos SET quantidade = quantidade + ?, preco_custo = ?, preco_venda = ? WHERE id = ?", (qtd, custo, venda, existe[0]))
            else:
                cursor.execute("INSERT INTO produtos (nome, quantidade, preco_custo, preco_venda) VALUES (?, ?, ?, ?)", (nome, qtd, custo, venda))
            self.banco.conexao.commit()
            self.txt_nome.clear()
            self.atualizar_tabela_estoque()
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))

    def showEvent(self, event):
        super().showEvent(event)
        self.atualizar_tabela_estoque()