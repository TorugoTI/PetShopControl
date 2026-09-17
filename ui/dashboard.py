import sys
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QTableWidget, QTableWidgetItem, QHeaderView, QStackedWidget, 
    QPushButton, QMessageBox, QInputDialog, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QAction
from packaging import version
from ui.components import COR_BEGE_FUNDO, COR_TEXTO_ESCURO
from ui.cadastro_central import TelaCadastroCentral
from ui.financeiro import TelaFinanceiro
from ui.estoque import TelaEstoque
from ui.perfil import TelaPerfil
from data.firebase_sync import SincronizadorFirebase

class TelaDashboard(QWidget):
    sinal_logout = pyqtSignal()

    def __init__(self, banco, email, cargo, versao_atual):
        super().__init__()
        self.email = email
        self.email_usuario = email
        self.email_logado = email
        self.cargo = cargo
        self.banco = banco 
        self.versao_atual = versao_atual
        self.versao = versao_atual
        self.botoes_menu = {}
        self.sync = SincronizadorFirebase()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"PetShop Control {self.versao} - Painel Geral")
        self.resize(1200, 750)
        self.setStyleSheet("background-color: #EFECE6;")

        layout_principal = QHBoxLayout(self)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)

        menu_lateral = QFrame()
        menu_lateral.setFixedWidth(240)
        menu_lateral.setStyleSheet(f"""
            QFrame {{ background-color: {COR_BEGE_FUNDO}; border-right: 1px solid #D1C7BD; }}
            QPushButton {{ background: transparent; color: {COR_TEXTO_ESCURO}; border: none; text-align: left; padding: 12px 20px; font-size: 13px; font-weight: bold; }}
            QPushButton:hover {{ background-color: #D1C7BD; }}
        """)
        
        layout_menu = QVBoxLayout(menu_lateral)
        layout_menu.setContentsMargins(10, 30, 10, 30)
        
        lbl_usuario = QLabel(f"👤 {self.email_usuario}\nNível: {self.cargo}")
        lbl_usuario.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        lbl_usuario.setStyleSheet(f"color: {COR_TEXTO_ESCURO}; padding-bottom: 20px;")
        layout_menu.addWidget(lbl_usuario)

        modulos = [("📊 Dashboard", 0), ("📝 Cadastros", 1), ("💰 Financeiro", 2), ("📦 Estoque", 3), ("⚙️ Perfil", 4)]
        for texto, index in modulos:
            btn = QPushButton(texto)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, idx=index: self.mudar_aba(idx))
            layout_menu.addWidget(btn)
            self.botoes_menu[index] = btn

        layout_menu.addStretch()
        btn_logout = QPushButton("🚪 Sair do Sistema")
        btn_logout.setStyleSheet("color: #BA3C2A; font-weight: bold;")
        btn_logout.clicked.connect(self.sinal_logout.emit)
        layout_menu.addWidget(btn_logout)

        btn_atualizar = QPushButton("🔄 Verificar Atualizações")
        btn_atualizar.setStyleSheet("color: #2980B9; border: none; font-weight: bold;")
        btn_atualizar.clicked.connect(self.checar_nova_versao)
        layout_menu.addWidget(btn_atualizar)

        self.conteudo_central = QStackedWidget()
        
        self.aba_dashboard = QWidget()
        self.montar_painel_inicial()
        
        self.aba_cadastros = TelaCadastroCentral(self.banco, atualizar_dashboard_callback=self.atualizar_dados_dashboard)
        self.aba_financeiro = TelaFinanceiro(self.banco)
        self.aba_estoque = TelaEstoque(self.banco)
        self.tela_perfil = TelaPerfil(self.sync, self.email, self.banco, self.cargo)
        self.aba_configuracoes = self.tela_perfil 

        self.conteudo_central.addWidget(self.aba_dashboard)
        self.conteudo_central.addWidget(self.aba_cadastros)
        self.conteudo_central.addWidget(self.aba_financeiro)
        self.conteudo_central.addWidget(self.aba_estoque)
        self.conteudo_central.addWidget(self.tela_perfil)

        layout_principal.addWidget(menu_lateral)
        layout_principal.addWidget(self.conteudo_central)

    def montar_painel_inicial(self):
        layout = QVBoxLayout(self.aba_dashboard)
        
        layout_topo = QHBoxLayout()
        
        self.card_faturamento = QFrame()
        self.card_faturamento.setStyleSheet("""
            QFrame {
                background-color: #8CA485;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        layout_card = QVBoxLayout(self.card_faturamento)

        self.lbl_titulo = QLabel("🟢 Faturamento Previsto (Futuro)")
        self.lbl_titulo.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.lbl_titulo.setStyleSheet("color: #3A3530; background: transparent;")
        layout_card.addWidget(self.lbl_titulo)

        self.lbl_valor_futuro = QLabel("R$ 0,00")
        self.lbl_valor_futuro.setStyleSheet("font-size: 20px; font-weight: bold; color: #3A3530; background: transparent;")
        layout_card.addWidget(self.lbl_valor_futuro)

        layout_topo.addWidget(self.card_faturamento, stretch=4)

        btn_reload = QPushButton("🔄 Atualizar Dados")
        btn_reload.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_reload.setStyleSheet("""
            QPushButton {
                background-color: #D1C7BD;
                color: #3A3530;
                font-weight: bold;
                border-radius: 10px;
                padding: 15px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #BDB3A7;
            }
        """)
        btn_reload.clicked.connect(self.atualizar_dados_dashboard)
        layout_topo.addWidget(btn_reload, stretch=1)

        layout.addLayout(layout_topo)
        
        self.tabela_atendimentos = QTableWidget()
        colunas = ["ID", "Cliente", "Pet", "Serviço", "Data", "Hora", "Valor", "Pgto"]
        self.tabela_atendimentos.setColumnCount(len(colunas))
        self.tabela_atendimentos.setHorizontalHeaderLabels(colunas)
        self.tabela_atendimentos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela_atendimentos.setFont(QFont("Arial", 11))
        self.tabela_atendimentos.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabela_atendimentos.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabela_atendimentos.customContextMenuRequested.connect(self.abrir_menu_contexto_dashboard)
        
        self.tabela_atendimentos.setStyleSheet("""
            QTableWidget { background-color: white; border: 1px solid #D1C7BD; border-radius: 6px; }
            QHeaderView::section { background-color: #D1C7BD; color: #3A3530; padding: 8px; font-weight: bold; border: none; }
        """)
        layout.addWidget(self.tabela_atendimentos)

        layout_acoes = QHBoxLayout()
        
        btn_concluir = QPushButton("✅ Concluir Atendimento")
        btn_concluir.setStyleSheet("background-color: #2E7D32; color: white; font-weight: bold; padding: 10px; border-radius: 6px;")
        btn_concluir.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_concluir.clicked.connect(self.concluir_atendimento_selecionado)

        btn_pagamento = QPushButton("💳 Incluir/Alterar Pagamento")
        btn_pagamento.setStyleSheet("background-color: #8CA485; color: #3A3530; font-weight: bold; padding: 10px; border-radius: 6px;")
        btn_pagamento.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_pagamento.clicked.connect(self.incluir_pagamento_atendimento)

        btn_excluir = QPushButton("🗑️ Excluir Atendimento")
        btn_excluir.setStyleSheet("background-color: #BA3C2A; color: white; font-weight: bold; padding: 10px; border-radius: 6px;")
        btn_excluir.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_excluir.clicked.connect(self.excluir_atendimento_selecionado)

        layout_acoes.addWidget(btn_concluir)
        layout_acoes.addWidget(btn_pagamento)
        layout_acoes.addWidget(btn_excluir)
        layout.addLayout(layout_acoes)
        
        self.atualizar_dados_dashboard()

    def abrir_menu_contexto_dashboard(self, pos):
        item = self.tabela_atendimentos.itemAt(pos)
        if not item: return
        menu = QMenu(self)
        acao_concluir = QAction("✅ Concluir Atendimento", self)
        acao_concluir.triggered.connect(self.concluir_atendimento_selecionado)
        acao_pagamento = QAction("💳 Incluir/Alterar Forma de Pagamento", self)
        acao_pagamento.triggered.connect(self.incluir_pagamento_atendimento)
        acao_excluir = QAction("🗑️ Excluir Atendimento", self)
        acao_excluir.triggered.connect(self.excluir_atendimento_selecionado)
        menu.addAction(acao_concluir)
        menu.addAction(acao_pagamento)
        menu.addAction(acao_excluir)
        menu.exec(self.tabela_atendimentos.viewport().mapToGlobal(pos))

    def atualizar_dados_dashboard(self):
        try:
            if self.banco and self.banco.conexao:
                atendimentos = self.banco.buscar_atendimentos_futuros()
                
                faturamento = sum(item[6] for item in atendimentos if item[6] is not None)
                self.lbl_valor_futuro.setText(f"R$ {faturamento:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                
                self.tabela_atendimentos.setRowCount(0)
                for row_idx, row_data in enumerate(atendimentos):
                    self.tabela_atendimentos.insertRow(row_idx)
                    id_a, cliente, pet, servico, data, hora, valor, pgto = row_data
                    
                    self.tabela_atendimentos.setItem(row_idx, 0, QTableWidgetItem(str(id_a)))
                    self.tabela_atendimentos.setItem(row_idx, 1, QTableWidgetItem(str(cliente)))
                    self.tabela_atendimentos.setItem(row_idx, 2, QTableWidgetItem(str(pet)))
                    self.tabela_atendimentos.setItem(row_idx, 3, QTableWidgetItem(str(servico)))
                    self.tabela_atendimentos.setItem(row_idx, 4, QTableWidgetItem(str(data)))
                    self.tabela_atendimentos.setItem(row_idx, 5, QTableWidgetItem(str(hora)))
                    
                    val_str = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if valor else "R$ 0,00"
                    self.tabela_atendimentos.setItem(row_idx, 6, QTableWidgetItem(val_str))
                    self.tabela_atendimentos.setItem(row_idx, 7, QTableWidgetItem(str(pgto)))
                    
        except Exception as e:
            print(f"[ERRO NO DASHBOARD] {e}")

    def incluir_pagamento_atendimento(self):
        row = self.tabela_atendimentos.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Selecione um atendimento na tabela.")
            return
        id_atend = self.tabela_atendimentos.item(row, 0).text()
        
        opcoes = ["Dinheiro", "Cartão", "Pix"]
        forma, ok = QInputDialog.getItem(self, "Forma de Pagamento", "Escolha a forma de pagamento:", opcoes, 0, False)
        
        if ok and forma:
            try:
                cursor = self.banco.conexao.cursor()
                cursor.execute("UPDATE atendimentos SET forma_pagamento = ? WHERE id = ?", (forma, id_atend))
                self.banco.conexao.commit()
                QMessageBox.information(self, "Sucesso", f"Forma de pagamento '{forma}' registrada!")
                self.atualizar_dados_dashboard()
            except Exception as e:
                self.banco.conexao.rollback()
                QMessageBox.critical(self, "Erro SQL", f"Falha ao registrar pagamento: {str(e)}")

    def excluir_atendimento_selecionado(self):
        row = self.tabela_atendimentos.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Selecione um atendimento para excluir.")
            return
        id_atend = self.tabela_atendimentos.item(row, 0).text()
        if QMessageBox.question(self, "Confirmação", f"Deseja excluir o atendimento ID {id_atend}?") == QMessageBox.StandardButton.Yes:
            try:
                cursor = self.banco.conexao.cursor()
                cursor.execute("DELETE FROM atendimentos WHERE id = ?", (id_atend,))
                self.banco.conexao.commit()
                self.atualizar_dados_dashboard()
            except Exception as e:
                QMessageBox.critical(self, "Erro", str(e))

    def mudar_aba(self, index):
        self.conteudo_central.setCurrentIndex(index)
        for idx, btn in self.botoes_menu.items():
            btn.setStyleSheet("background-color: #D1C7BD;" if idx == index else "background: transparent; color: #3A3530;")
    
    def showEvent(self, event):
        super().showEvent(event)
        self.atualizar_dados_dashboard()

    def checar_nova_versao(self):
        try:
            dados = self.banco.child("Configuracoes").get().val()
            versao_remota = dados.get("Versao Recente")
            url_download = dados.get("url_download")
            if version.parse(versao_remota) > version.parse(self.versao):
                if QMessageBox.question(self, "Atualização", f"Nova versão {versao_remota} disponível! Baixar?") == QMessageBox.StandardButton.Yes:
                    self.baixar_atualizacao(url_download)
            else:
                QMessageBox.information(self, "Sistema", "Versão mais recente.")
        except Exception as e:
            print(f"Erro ao checar atualização: {e}")

    def baixar_atualizacao(self, url):
        import requests
        caminho_salvar = "atualizacao_setup.exe"
        try:
            response = requests.get(url)
            with open(caminho_salvar, 'wb') as f:
                f.write(response.content)
            QMessageBox.information(self, "Sucesso", "Download concluído.")
            os.startfile(caminho_salvar)
            sys.exit()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha no download: {e}")

    def concluir_atendimento_selecionado(self):
        row = self.tabela_atendimentos.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Selecione um atendimento para concluir.")
            return
        id_atend = self.tabela_atendimentos.item(row, 0).text()
        if QMessageBox.question(self, "Confirmação", f"Marcar o atendimento ID {id_atend} como Concluído?") == QMessageBox.StandardButton.Yes:
            try:
                cursor = self.banco.conexao.cursor()
                cursor.execute("UPDATE atendimentos SET status = 'Concluído' WHERE id = ?", (id_atend,))
                self.banco.conexao.commit()
                QMessageBox.information(self, "Sucesso", f"Atendimento ID {id_atend} concluído e removido da previsão!")
                self.atualizar_dados_dashboard()
            except Exception as e:
                self.banco.conexao.rollback()
                QMessageBox.critical(self, "Erro SQL", f"Falha ao concluir: {str(e)}")