import sys
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QTableWidget, QTableWidgetItem, QHeaderView, QStackedWidget, 
    QPushButton, QMessageBox, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ui.components import COR_BEGE_FUNDO, COR_TEXTO_ESCURO
from ui.cadastro_central import TelaCadastroCentral
from ui.financeiro import TelaFinanceiro
from ui.estoque import TelaEstoque
from ui.perfil import TelaPerfil

class TelaDashboard(QWidget):
    sinal_logout = pyqtSignal()

    def __init__(self, banco, email_usuario, cargo, versao):
        super().__init__() 
        self.banco = banco
        self.email_usuario = email_usuario
        self.email_logado = email_usuario
        self.cargo = cargo
        self.versao = versao
        self.botoes_menu = {}
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
        self.aba_perfil = TelaPerfil(self.email_usuario, self.banco, self.cargo)
        self.aba_configuracoes = self.aba_perfil 

        self.conteudo_central.addWidget(self.aba_dashboard)
        self.conteudo_central.addWidget(self.aba_cadastros)
        self.conteudo_central.addWidget(self.aba_financeiro)
        self.conteudo_central.addWidget(self.aba_estoque)
        self.conteudo_central.addWidget(self.aba_perfil)

        layout_principal.addWidget(menu_lateral)
        layout_principal.addWidget(self.conteudo_central)

    def montar_painel_inicial(self):
        layout = QVBoxLayout(self.aba_dashboard)
        
        self.card_faturamento = QFrame()
        self.card_faturamento.setStyleSheet("""
            QFrame {
                background-color: #f0f0f0;
                border: 1px solid #dcdcdc;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        layout_card = QVBoxLayout(self.card_faturamento)

        self.lbl_titulo = QLabel("Faturamento Previsto (Futuro)")
        self.lbl_titulo.setStyleSheet("font-weight: bold; color: #555;")
        layout_card.addWidget(self.lbl_titulo)

        self.lbl_valor_futuro = QLabel("R$ 0,00")
        self.lbl_valor_futuro.setStyleSheet("font-size: 20px; font-weight: bold; color: #2e7d32;")
        layout_card.addWidget(self.lbl_valor_futuro)

        layout.addWidget(self.card_faturamento)
        
        self.tabela_atendimentos = QTableWidget()
        self.tabela_atendimentos.setColumnCount(6)
        self.tabela_atendimentos.setHorizontalHeaderLabels(["ID", "Cliente", "Serviço", "Data", "Hora", "Valor"])
        self.tabela_atendimentos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabela_atendimentos)
        
        self.atualizar_dados_dashboard()

    def atualizar_dados_dashboard(self):
        try:
            if self.banco:
                atendimentos = self.banco.buscar_atendimentos_futuros()
                
                faturamento = sum(item[5] for item in atendimentos if item[5] is not None)
                
                self.lbl_valor_futuro.setText(f"R$ {faturamento:.2f}")
                
                self.tabela_atendimentos.setRowCount(0)
                for row_idx, row_data in enumerate(atendimentos):
                    self.tabela_atendimentos.insertRow(row_idx)
                    for col_idx, data in enumerate(row_data):
                        valor_exibicao = f"R$ {data:.2f}" if col_idx == 5 else str(data)
                        self.tabela_atendimentos.setItem(row_idx, col_idx, QTableWidgetItem(valor_exibicao))
                    
        except Exception as e:
            print(f"[ERRO NO DASHBOARD] {e}")

    def mudar_aba(self, index):
        self.conteudo_central.setCurrentIndex(index)
        for idx, btn in self.botoes_menu.items():
            btn.setStyleSheet("background-color: #D1C7BD;" if idx == index else "background: transparent; color: #3A3530;")
    
    def showEvent(self, event):
        """Sempre que a tela for exibida/focada, atualiza os dados."""
        super().showEvent(event)
        self.atualizar_dados_dashboard()

    def checar_nova_versao(self):
        dados_fb = self.firebase.verificar_atualizacao()
        if not dados_fb:
            QMessageBox.warning(self, "Erro", "Não foi possível conectar ao servidor.")
            return

        versao_remota = dados_fb.get('versao_recente')
        url_download = dados_fb.get('url_download')

        if versao_remota > self.versao_atual:
            reply = QMessageBox.question(self, "Atualização Disponível", 
                                         f"Nova versão {versao_remota} encontrada. Deseja baixar agora?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                self.baixar_atualizacao(url_download)
        else:
            QMessageBox.information(self, "Atualização", "Você já está usando a versão mais recente!")

    def baixar_atualizacao(self, url):
        import requests
        caminho_salvar = "atualizacao_setup.exe"
        
        try:
            response = requests.get(url)
            with open(caminho_salvar, 'wb') as f:
                f.write(response.content)
            
            QMessageBox.information(self, "Sucesso", "Download concluído. O instalador será aberto.")
            os.startfile(caminho_salvar)
            sys.exit()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha no download: {e}")