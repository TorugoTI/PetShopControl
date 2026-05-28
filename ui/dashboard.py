import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QStackedWidget, QPushButton, QLineEdit, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap
from ui.components import COR_BEGE_FUNDO, COR_TEXTO_ESCURO

CAMINHO_ASSETS = os.path.join(os.path.dirname(__file__), "assets")

class TelaDashboard(QWidget):
    def __init__(self, banco):
        super().__init__()
        self.banco = banco
        self.botoes_menu = {}
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("PetShop Control v1.0.0 - Painel Geral")
        self.resize(1200, 750)
        self.setStyleSheet(f"background-color: #EFECE6;")

        layout_principal = QHBoxLayout(self)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)

        menu_lateral = QFrame()
        menu_lateral.setFixedWidth(240)
        menu_lateral.setStyleSheet(f"background-color: {COR_BEGE_FUNDO}; border-right: 1px solid #D1C7BD;")
        
        layout_menu = QVBoxLayout(menu_lateral)
        layout_menu.setContentsMargins(15, 25, 15, 25)
        layout_menu.setSpacing(10)

        lbl_logo = QLabel("🐾 PetShop Control")
        lbl_logo.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        lbl_logo.setStyleSheet(f"color: {COR_TEXTO_ESCURO}; margin-bottom: 20px;")
        layout_menu.addWidget(lbl_logo)

        icones_abas = [
            "Dashboard Geral",
            "Painel de Cadastros",
            "Consulta & Prontuário",
            "Financeiro & Caixa",
            "Estoque Inteligente",
            "Perfil & Usuários"
        ]
        
        for idx, nome_aba in enumerate(icones_abas):
            btn_item = QPushButton()
            btn_item.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_item.setFixedHeight(40)
            
            layout_item = QHBoxLayout(btn_item)
            layout_item.setContentsMargins(15, 0, 15, 0)
            layout_item.setSpacing(12)
            
            lbl_icone_aba = QLabel("🐾")
            lbl_icone_aba.setStyleSheet("background: transparent; border: none;")
            lbl_icone_aba.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            
            lbl_texto_aba = QLabel(nome_aba)
            lbl_texto_aba.setFont(QFont("Arial", 10))
            lbl_texto_aba.setStyleSheet(f"color: {COR_TEXTO_ESCURO}; border: none; background: transparent;")
            lbl_texto_aba.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            
            layout_item.addWidget(lbl_icone_aba)
            layout_item.addWidget(lbl_texto_aba)
            layout_item.addStretch()
            
            btn_item.setStyleSheet("""
                QPushButton {
                    border-radius: 6px;
                    background-color: transparent;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #E6E1D6;
                }
            """)
            
            if idx == 0:
                btn_item.setStyleSheet("background-color: #D6E4D2; border-radius: 6px; border: none;")
                lbl_texto_aba.setStyleSheet(f"color: {COR_TEXTO_ESCURO}; font-weight: bold; background: transparent;")
            
            btn_item.clicked.connect(lambda checked, i=idx: self.mudar_pagina(i))
            
            self.botoes_menu[idx] = (btn_item, lbl_texto_aba)
            layout_menu.addWidget(btn_item)

        layout_menu.addStretch()
        layout_principal.addWidget(menu_lateral)

        self.stacked_widget = QStackedWidget()
        layout_principal.addWidget(self.stacked_widget)

        self.verificar_e_popular_estoque_inicial()

        self.stacked_widget.addWidget(self.criar_pagina_dashboard())
        self.stacked_widget.addWidget(self.criar_painel_cadastros_completo())
        self.stacked_widget.addWidget(self.criar_pagina_consultas_real())
        self.stacked_widget.addWidget(self.criar_pagina_financeiro_real())
        self.stacked_widget.addWidget(self.criar_pagina_estoque_real())
        self.stacked_widget.addWidget(self.criar_pagina_perfil_real())  

    def mudar_pagina(self, indice):
        """Altera a tela visível no painel central e gerencia o destaque visual do menu"""
        print(f"[NAVEGAÇÃO] Mudando para a página índice: {indice}")
        self.stacked_widget.setCurrentIndex(indice)
        
        for idx, (btn, texto) in self.botoes_menu.items():
            if idx == indice:
                btn.setStyleSheet("background-color: #D6E4D2; border-radius: 6px; border: none;")
                texto.setStyleSheet(f"color: {COR_TEXTO_ESCURO}; font-weight: bold; background: transparent;")
            else:
                btn.setStyleSheet("""
                    QPushButton { background-color: transparent; border-radius: 6px; border: none; } 
                    QPushButton:hover { background-color: #E6E1D6; }
                """)
                texto.setStyleSheet(f"color: {COR_TEXTO_ESCURO}; font-weight: normal; background: transparent;")

    def criar_pagina_dashboard(self):
        """Layout da página inicial do Dashboard Geral"""
        area_centro = QWidget()
        layout_centro = QVBoxLayout(area_centro)
        layout_centro.setContentsMargins(30, 25, 30, 25)
        layout_centro.setSpacing(20)

        lbl_boas_vindas = QLabel("Painel de Controle Comercial")
        lbl_boas_vindas.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        lbl_boas_vindas.setStyleSheet(f"color: {COR_TEXTO_ESCURO};")
        layout_centro.addWidget(lbl_boas_vindas)

        layout_cards = QHBoxLayout()
        layout_cards.setSpacing(15)

        receita, despesa, saldo = self.calcular_metricas_financeiras()

        card_lucro = self.criar_card_metrica("Faturamento Estimado", f"R$ {receita:.2f}", "#8CA485")
        card_gasto = self.criar_card_metrica("Gastos Registrados", f"R$ {despesa:.2f}", "#C27A7A")
        card_saldo = self.criar_card_metrica("Balanço Geral", f"R$ {saldo:.2f}", "#7AA2C2")

        layout_cards.addWidget(card_lucro)
        layout_cards.addWidget(card_gasto)
        layout_cards.addWidget(card_saldo)
        layout_centro.addLayout(layout_cards)

        lbl_secao_agenda = QLabel("🗓️ Próximos Atendimentos Programados (Hoje)")
        lbl_secao_agenda.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        lbl_secao_agenda.setStyleSheet(f"color: {COR_TEXTO_ESCURO}; margin-top: 10px;")
        layout_centro.addWidget(lbl_secao_agenda)

        self.tabela_agenda = QTableWidget()
        self.tabela_agenda.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #D1C7BD;
                border-radius: 6px;
                gridline-color: #EFECE6;
            }
            QHeaderView::section {
                background-color: #F4F1EA;
                padding: 6px;
                border: none;
                font-weight: bold;
            }
        """)
        self.carregar_dados_agenda()
        layout_centro.addWidget(self.tabela_agenda)
        
        return area_centro

    def criar_pagina_placeholder(self, nome_tela):
        """Gera telas limpas temporárias para visualização dos outros recursos no Modo Demo"""
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl = QLabel(f"Módulo: {nome_tela}\n\n[Ambiente de Simulação de Recursos - Fordan]")
        lbl.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {COR_TEXTO_ESCURO};")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(lbl)
        return pagina

    def criar_card_metrica(self, titulo, valor, cor_borda):
        card = QFrame()
        card.setStyleSheet(f"background-color: white; border-left: 5px solid {cor_borda}; border-radius: 6px;")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)

        lbl_t = QLabel(titulo)
        lbl_t.setFont(QFont("Arial", 9))
        lbl_t.setStyleSheet("color: #7A7570;")
        
        lbl_v = QLabel(valor)
        lbl_v.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        lbl_v.setStyleSheet(f"color: {COR_TEXTO_ESCURO};")

        layout.addWidget(lbl_t)
        layout.addWidget(lbl_v)
        return card

    def calcular_metricas_financeiras(self):
        cursor = self.banco.conexao.cursor()
        cursor.execute("SELECT SUM(valor) FROM atendimentos WHERE status != 'Cancelado'")
        receita = cursor.fetchone()[0] or 0.0
        cursor.execute("SELECT SUM(valor) FROM gastos")
        despesa = cursor.fetchone()[0] or 0.0
        return receita, despesa, (receita - despesa)

    def carregar_dados_agenda(self):
        cursor = self.banco.conexao.cursor()
        query = """
            SELECT p.nome, t.nome, a.servico, a.hora_atendimento, a.valor, a.status
            FROM atendimentos a
            JOIN pets p ON a.pet_id = p.id
            JOIN tutores t ON p.tutor_id = t.id
            ORDER BY a.hora_atendimento ASC
        """
        cursor.execute(query)
        resultados = cursor.fetchall()

        self.tabela_agenda.setColumnCount(6)
        self.tabela_agenda.setRowCount(len(resultados))
        self.tabela_agenda.setHorizontalHeaderLabels(["Pet", "Responsável", "Serviço", "Horário", "Preço", "Status"])
        
        header = self.tabela_agenda.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        for linha_idx, linha_dados in enumerate(resultados):
            for col_idx, dado in enumerate(linha_dados):
                item = QTableWidgetItem(str(dado))
                item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.tabela_agenda.setItem(linha_idx, col_idx, item)

    def criar_painel_cadastros_completo(self):
        """Cria o painel central de cadastros usando abas organizadas (QTabWidget)"""
        from PyQt6.QtWidgets import QTabWidget
        
        pagina_mestre = QWidget()
        layout_mestre = QVBoxLayout(pagina_mestre)
        layout_mestre.setContentsMargins(30, 25, 30, 25)
        layout_mestre.setSpacing(15)

        lbl_titulo = QLabel("🗂️ Central de Cadastros do Sistema")
        lbl_titulo.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        lbl_titulo.setStyleSheet(f"color: {COR_TEXTO_ESCURO};")
        layout_mestre.addWidget(lbl_titulo)

        self.abas_cadastro = QTabWidget()
        self.abas_cadastro.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid #D1C7BD;
                background: white;
                border-radius: 6px;
            }}
            QTabBar::tab {{
                background: #E6E1D6;
                color: {COR_TEXTO_ESCURO};
                padding: 10px 20px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected, QTabBar::tab:hover {{
                background: white;
                font-weight: bold;
                border: 1px solid #D1C7BD;
                border-bottom-color: white;
            }}
        """)

        self.abas_cadastro.addTab(self._form_tutor(), "👤 Cadastrar Tutor")
        self.abas_cadastro.addTab(self._form_pet(), "🐾 Cadastrar Pet")
        self.abas_cadastro.addTab(self._form_agendamento(), "🗓️ Novo Agendamento")
        self.abas_cadastro.addTab(self._form_gasto(), "💸 Registrar Gasto")
        self.abas_cadastro.currentChanged.connect(self.atualizar_comboboxes_cadastro)

        layout_mestre.addWidget(self.abas_cadastro)
        return pagina_mestre

    def _form_tutor(self):
        aba = QWidget()
        layout = QVBoxLayout(aba)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        layout.addWidget(QLabel("Nome Completo do Tutor:"))
        self.inp_tutor_nome = QLineEdit()
        self.inp_tutor_nome.setPlaceholderText("Ex: Carlos Eduardo de Souza")
        layout.addWidget(self.inp_tutor_nome)

        layout.addWidget(QLabel("Telefone de Contato / WhatsApp:"))
        self.inp_tutor_fone = QLineEdit()
        self.inp_tutor_fone.setPlaceholderText("Ex: 27999991122")
        layout.addWidget(self.inp_tutor_fone)

        layout.addWidget(QLabel("E-mail corporativo/pessoal:"))
        self.inp_tutor_email = QLineEdit()
        self.inp_tutor_email.setPlaceholderText("Ex: carlos@email.com")
        layout.addWidget(self.inp_tutor_email)

        btn = QPushButton("💾 Gravar Cadastro do Tutor")
        btn.clicked.connect(self.salvar_tutor)
        self._estilizar_botao_form(btn)
        layout.addWidget(btn)
        layout.addStretch()
        self._estilizar_inputs_aba(aba)
        return aba

    def _form_pet(self):
        aba = QWidget()
        layout = QVBoxLayout(aba)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        layout.addWidget(QLabel("Vincular ao Tutor (Responsável):"))
        self.cb_pet_tutor = QComboBox()
        layout.addWidget(self.cb_pet_tutor)

        layout.addWidget(QLabel("Nome do Pet:"))
        self.inp_pet_nome = QLineEdit()
        self.inp_pet_nome.setPlaceholderText("Ex: Max, Mel, Pandora")
        layout.addWidget(self.inp_pet_nome)

        layout.addWidget(QLabel("Espécie do Animal:"))
        self.cb_pet_especie = QComboBox()
        self.cb_pet_especie.addItems(["Cão", "Gato", "Pássaro", "Roedor", "Outros"])
        layout.addWidget(self.cb_pet_especie)

        layout.addWidget(QLabel("Raça (Se houver):"))
        self.inp_pet_raca = QLineEdit()
        self.inp_pet_raca.setPlaceholderText("Ex: Golden Retriever, SRD, Persa")
        layout.addWidget(self.inp_pet_raca)

        btn = QPushButton("💾 Gravar Cadastro do Pet")
        btn.clicked.connect(self.salvar_pet)
        self._estilizar_botao_form(btn)
        layout.addWidget(btn)
        layout.addStretch()
        self._estilizar_inputs_aba(aba)
        return aba

    def _form_agendamento(self):
        aba = QWidget()
        layout = QVBoxLayout(aba)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        layout.addWidget(QLabel("Selecione o Pet Agendado:"))
        self.cb_agenda_pet = QComboBox()
        layout.addWidget(self.cb_agenda_pet)

        layout.addWidget(QLabel("Tipo de Serviço / Procedimento:"))
        self.cb_agenda_servico = QComboBox()
        self.cb_agenda_servico.addItems(["Banho Simples", "Banho & Tosa Completa", "Tosa Higiênica", "Consulta Veterinária", "Aplicação de Vacina"])
        layout.addWidget(self.cb_agenda_servico)

        layout.addWidget(QLabel("Data do Atendimento (AAAA-MM-DD):"))
        self.inp_agenda_data = QLineEdit()
        self.inp_agenda_data.setPlaceholderText("Ex: 2026-05-28")
        layout.addWidget(self.inp_agenda_data)

        layout.addWidget(QLabel("Horário Programado (HH:MM):"))
        self.inp_agenda_hora = QLineEdit()
        self.inp_agenda_hora.setPlaceholderText("Ex: 14:30")
        layout.addWidget(self.inp_agenda_hora)

        layout.addWidget(QLabel("Preço Cobrado / Negociado (R$):"))
        self.inp_agenda_valor = QLineEdit()
        self.inp_agenda_valor.setPlaceholderText("Ex: 85.00")
        layout.addWidget(self.inp_agenda_valor)

        btn = QPushButton("🗓️ Confirmar Agendamento de Serviço")
        btn.clicked.connect(self.salvar_agendamento)
        self._estilizar_botao_form(btn)
        layout.addWidget(btn)
        layout.addStretch()
        self._estilizar_inputs_aba(aba)
        return aba

    def _form_gasto(self):
        aba = QWidget()
        layout = QVBoxLayout(aba)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        layout.addWidget(QLabel("Descrição do Gasto Operacional:"))
        self.inp_gasto_desc = QLineEdit()
        self.inp_gasto_desc.setPlaceholderText("Ex: Compra de 5x Shampoos Neutros, Conta de Luz, Aluguel")
        layout.addWidget(self.inp_gasto_desc)

        layout.addWidget(QLabel("Valor Total da Despesa (R$):"))
        self.inp_gasto_valor = QLineEdit()
        self.inp_gasto_valor.setPlaceholderText("Ex: 140.00")
        layout.addWidget(self.inp_gasto_valor)

        layout.addWidget(QLabel("Data da Saída (AAAA-MM-DD):"))
        self.inp_gasto_data = QLineEdit()
        self.inp_gasto_data.setPlaceholderText("Ex: 2026-05-28")
        layout.addWidget(self.inp_gasto_data)

        btn = QPushButton("💸 Lançar Despesa no Caixa")
        btn.clicked.connect(self.salvar_gasto)
        self._estilizar_botao_form(btn)
        layout.addWidget(btn)
        layout.addStretch()
        self._estilizar_inputs_aba(aba)
        return aba


    def salvar_tutor(self):
        nome = self.inp_tutor_nome.text().strip()
        fone = self.inp_tutor_fone.text().strip()
        email = self.inp_tutor_email.text().strip()

        if not nome:
            QMessageBox.warning(self, "Aviso", "O nome do tutor é obrigatório!")
            return

        cursor = self.banco.conexao.cursor()
        cursor.execute("INSERT INTO tutores (nome, telefone, email) VALUES (?, ?, ?)", (nome, fone, email))
        self.banco.conexao.commit()
        
        QMessageBox.information(self, "Sucesso", "Tutor registrado com sucesso no Simulador!")
        self.inp_tutor_nome.clear()
        self.inp_tutor_fone.clear()
        self.inp_tutor_email.clear()

    def salvar_pet(self):
        nome = self.inp_pet_nome.text().strip()
        especie = self.cb_pet_especie.currentText()
        raca = self.inp_pet_raca.text().strip()
        
        tutor_id = self.cb_pet_tutor.currentData()

        if not nome or tutor_id is None:
            QMessageBox.warning(self, "Aviso", "Preencha o nome do Pet e selecione um Tutor responsável!")
            return

        cursor = self.banco.conexao.cursor()
        cursor.execute("INSERT INTO pets (tutor_id, nome, especie, raca) VALUES (?, ?, ?, ?)", (tutor_id, nome, especie, raca))
        self.banco.conexao.commit()

        QMessageBox.information(self, "Sucesso", f"Pet '{nome}' cadastrado e vinculado com sucesso!")
        self.inp_pet_nome.clear()
        self.inp_pet_raca.clear()

    def salvar_agendamento(self):
        pet_id = self.cb_agenda_pet.currentData()
        servico = self.cb_agenda_servico.currentText()
        data_at = self.inp_agenda_data.text().strip()
        hora_at = self.inp_agenda_hora.text().strip()
        valor_str = self.inp_agenda_valor.text().strip()

        if not pet_id or not data_at or not hora_at or not valor_str:
            QMessageBox.warning(self, "Aviso", "Por favor, preencha todos os campos do agendamento!")
            return

        try:
            valor = float(valor_str)
            cursor = self.banco.conexao.cursor()
            cursor.execute(
                "INSERT INTO atendimentos (pet_id, servico, data_atendimento, hora_atendimento, valor, status) VALUES (?, ?, ?, ?, ?, 'Agendado')",
                (pet_id, servico, data_at, hora_at, valor)
            )
            self.banco.conexao.commit()

            QMessageBox.information(self, "Confirmado", "Serviço agendado com sucesso!")
            self.inp_agenda_data.clear()
            self.inp_agenda_hora.clear()
            self.inp_agenda_valor.clear()
            
            self.carregar_dados_agenda()
        except ValueError:
            QMessageBox.warning(self, "Erro", "O preço precisa ser um valor numérico válido (ex: 85.50).")

    def salvar_gasto(self):
        desc = self.inp_gasto_desc.text().strip()
        valor_str = self.inp_gasto_valor.text().strip()
        data_g = self.inp_gasto_data.text().strip()

        if not desc or not valor_str or not data_g:
            QMessageBox.warning(self, "Aviso", "Preencha todos os campos da despesa!")
            return

        try:
            valor = float(valor_str)
            cursor = self.banco.conexao.cursor()
            cursor.execute("INSERT INTO gastos (descricao, valor, data_gasto) VALUES (?, ?, ?)", (desc, valor, data_g))
            self.banco.conexao.commit()

            QMessageBox.information(self, "Sucesso", "Despesa lançada com sucesso no fluxo de caixa!")
            self.inp_gasto_desc.clear()
            self.inp_gasto_valor.clear()
            self.inp_gasto_data.clear()
        except ValueError:
            QMessageBox.warning(self, "Erro", "O valor precisa ser numérico.")

    def atualizar_comboboxes_cadastro(self, index_aba):
        """Atualiza os registros das caixas de seleção buscando dados novos inseridos em tempo real"""
        cursor = self.banco.conexao.cursor()
        
        if index_aba == 1:
            self.cb_pet_tutor.clear()
            cursor.execute("SELECT id, nome FROM tutores ORDER BY nome ASC")
            for id_t, nome_t in cursor.fetchall():
                self.cb_pet_tutor.addItem(nome_t, id_t)

        elif index_aba == 2:
            self.cb_agenda_pet.clear()
            cursor.execute("SELECT id, nome FROM pets ORDER BY nome ASC")
            for id_p, nome_p in cursor.fetchall():
                self.cb_agenda_pet.addItem(nome_p, id_p)

    def _estilizar_botao_form(self, botao):
        botao.setCursor(Qt.CursorShape.PointingHandCursor)
        botao.setFixedHeight(38)
        botao.setStyleSheet("""
            QPushButton { background-color: #8CA485; color: white; font-weight: bold; border-radius: 4px; border: none; margin-top: 10px; }
            QPushButton:hover { background-color: #7A9373; }
        """)

    def _estilizar_inputs_aba(self, container):
        container.setStyleSheet(f"""
            QLabel {{ color: {COR_TEXTO_ESCURO}; font-weight: bold; background: transparent; border: none; }}
            QLineEdit, QComboBox {{ 
                background-color: #FDFDFD; border: 1px solid #C0B5A9; border-radius: 4px; padding: 6px; color: #333; 
            }}
            QLineEdit:focus {{ border: 1px solid #8CA485; }}
        """)
    def criar_pagina_estoque_real(self):
        """Gera a interface do Estoque Inteligente com alertas de nível baixo"""
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(15)

        lbl_titulo = QLabel("📦 Estoque Inteligente e Consumo Automatizado")
        lbl_titulo.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        lbl_titulo.setStyleSheet(f"color: {COR_TEXTO_ESCURO};")
        layout.addWidget(lbl_titulo)

        self.tabela_estoque = QTableWidget()
        self.tabela_estoque.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #D1C7BD;
                border-radius: 6px;
                gridline-color: #EFECE6;
            }
            QHeaderView::section {
                background-color: #F4F1EA;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.tabela_estoque)

        btn_reabastecer = QPushButton("➕ Simular Compra / Reabastecer Produto")
        btn_reabastecer.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_reabastecer.setFixedHeight(35)
        btn_reabastecer.setStyleSheet("""
            QPushButton { background-color: #7AA2C2; color: white; font-weight: bold; border-radius: 4px; border: none; }
            QPushButton:hover { background-color: #6A92B2; }
        """)
        btn_reabastecer.clicked.connect(self.reabastecer_estoque_demo)
        layout.addWidget(btn_reabastecer)

        self.verificar_e_popular_estoque_inicial()
        self.carregar_dados_estoque()

        return pagina

    def verificar_e_popular_estoque_inicial(self):
        """Insere produtos padrão para teste se a tabela do Modo Demo estiver zerada"""
        cursor = self.banco.conexao.cursor()
        cursor.execute("SELECT COUNT(*) FROM produtos_estoque")
        if cursor.fetchone()[0] == 0:
            produtos = [
                ("Shampoo Neutro 5L", 3, 2, 5, 0), # Qtd atual: 3, Minima: 2, Rende 5 banhos
                ("Condicionador Brilho 5L", 2, 1, 5, 0),
                ("Ração Premium Filhotes 10kg", 5, 2, 10, 0),
                ("Coleira Antipulgas", 8, 3, 1, 0)
            ]
            cursor.executemany(
                "INSERT INTO produtos_estoque (nome_produto, quantidade_atual, quantidade_minima, rendimento_por_atendimento, atendimentos_realizados) VALUES (?, ?, ?, ?, ?)",
                produtos
            )
            self.banco.conexao.commit()

    def carregar_dados_estoque(self):
        """Busca os produtos e renderiza aplicando alertas visuais caso estejam abaixo do limite"""
        cursor = self.banco.conexao.cursor()
        cursor.execute("SELECT nome_produto, quantidade_atual, quantidade_minima, rendimento_por_atendimento FROM produtos_estoque")
        resultados = cursor.fetchall()

        self.tabela_estoque.setColumnCount(5)
        self.tabela_estoque.setRowCount(len(resultados))
        self.tabela_estoque.setHorizontalHeaderLabels(["Produto", "Qtd Atual", "Qtd Mínima", "Rendimento", "Status do Nível"])
        
        header = self.tabela_estoque.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        for linha_idx, linha_dados in enumerate(resultados):
            nome, qtd_atual, qtd_min, rendimento = linha_dados
            
            if qtd_atual <= qtd_min:
                status_texto = "⚠️ ESTOQUE BAIXO"
                cor_status = "#C27A7A"
            else:
                status_texto = "✅ Normal"
                cor_status = "#8CA485"

            dados_colunas = [nome, str(qtd_atual), str(qtd_min), f"{rendimento} usos", status_texto]

            for col_idx, dado in enumerate(dados_colunas):
                item = QTableWidgetItem(dado)
                item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                
                if status_texto == "⚠️ ESTOQUE BAIXO":
                    item.setForeground(Qt.GlobalColor.red)
                    
                self.tabela_estoque.setItem(linha_idx, col_idx, item)

    def reabastecer_estoque_demo(self):
        """Simula a entrada de mercadorias somando +5 unidades em todos os produtos"""
        cursor = self.banco.conexao.cursor()
        cursor.execute("UPDATE produtos_estoque SET quantidade_atual = quantidade_atual + 5")
        self.banco.conexao.commit()
        self.carregar_dados_estoque()
        QMessageBox.information(self, "Estoque", "Todos os produtos foram reabastecidos com +5 unidades!")  

    def computar_consumo_de_produto(self, nome_produto_alvo):
        """Soma um atendimento realizado ao produto. A cada X usos, reduz 1 unidade do estoque."""
        cursor = self.banco.conexao.cursor()
        
        cursor.execute(
            "SELECT id, quantidade_atual, rendimento_por_atendimento, atendimentos_realizados FROM produtos_estoque WHERE nome_produto LIKE ?", 
            (f"%{nome_produto_alvo}%",)
        )
        produto = cursor.fetchone()
        
        if produto:
            p_id, qtd_atual, rendimento, usos_atuais = produto
            novos_usos = usos_atuais + 1
            
            if novos_usos >= rendimento:
                nova_qtd = max(0, qtd_atual - 1)
                cursor.execute(
                    "UPDATE produtos_estoque SET quantidade_atual = ?, atendimentos_realizados = 0 WHERE id = ?",
                    (nova_qtd, p_id)
                )
                cursor.execute(
                    "INSERT INTO gastos (descricao, valor, data_gasto) VALUES (?, 25.00, '2026-05-28')",
                    (f"Consumo automático: 1x {nome_produto_alvo}",)
                )
            else:
                cursor.execute("UPDATE produtos_estoque SET atendimentos_realizados = ? WHERE id = ?", (novos_usos, p_id))
                
            self.banco.conexao.commit()
            
            self.carregar_dados_estoque() 
    
    def criar_pagina_consultas_real(self):
        """Gera a interface de busca e prontuário histórico"""
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(15)

        lbl_titulo = QLabel("🔍 Consulta de Histórico & Prontuários")
        lbl_titulo.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        lbl_titulo.setStyleSheet(f"color: {COR_TEXTO_ESCURO};")
        layout.addWidget(lbl_titulo)

        layout_busca = QHBoxLayout()
        self.inp_busca = QLineEdit()
        self.inp_busca.setPlaceholderText("Digite o nome do Pet ou do Tutor para buscar...")
        self.inp_busca.setStyleSheet("""
            QLineEdit { 
                background-color: white; border: 1px solid #D1C7BD; 
                border-radius: 4px; padding: 8px; color: #333; font-size: 11pt;
            }
        """)
        self.inp_busca.textChanged.connect(self.filtrar_prontuarios)
        layout_busca.addWidget(self.inp_busca)
        layout.addLayout(layout_busca)

        self.tabela_consultas = QTableWidget()
        self.tabela_consultas.setStyleSheet("""
            QTableWidget {
                background-color: white; border: 1px solid #D1C7BD;
                border-radius: 6px; gridline-color: #EFECE6;
            }
            QHeaderView::section {
                background-color: #F4F1EA; padding: 8px; border: none; font-weight: bold;
            }
        """)
        layout.addWidget(self.tabela_consultas)

        self.filtrar_prontuarios()

        return pagina

    def filtrar_prontuarios(self):
        """Filtra os atendimentos com base no texto digitado na barra de pesquisa"""
        texto_busca = self.inp_busca.text().strip()
        cursor = self.banco.conexao.cursor()

        query = """
            SELECT p.nome, t.nome, a.servico, a.data_atendimento || ' ás ' || a.hora_atendimento, a.valor, a.status
            FROM atendimentos a
            JOIN pets p ON a.pet_id = p.id
            JOIN tutores t ON p.tutor_id = t.id
            WHERE p.nome LIKE ? OR t.nome LIKE ?
            ORDER BY a.data_atendimento DESC, a.hora_atendimento DESC
        """
        
        parametro = f"%{texto_busca}%"
        cursor.execute(query, (parametro, parametro))
        resultados = cursor.fetchall()

        self.tabela_consultas.setColumnCount(6)
        self.tabela_consultas.setRowCount(len(resultados))
        self.tabela_consultas.setHorizontalHeaderLabels(["Pet", "Tutor (Responsável)", "Serviço Prestado", "Data & Horário", "Preço (R$)", "Status"])
        
        header = self.tabela_consultas.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        for linha_idx, linha_dados in enumerate(resultados):
            for col_idx, dado in enumerate(linha_dados):
                item = QTableWidgetItem(str(dado))
                item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                
                if col_idx == 5:
                    if dado == "Agendado":
                        item.setForeground(Qt.GlobalColor.blue)
                    else:
                        item.setForeground(Qt.GlobalColor.darkGreen)

                self.tabela_consultas.setItem(linha_idx, col_idx, item)

    def criar_pagina_financeiro_real(self):
        """Gera a interface do Financeiro & Caixa detalhado por Pet/Tutor e Gastos"""
        pagina = QWidget()
        layout_principal = QVBoxLayout(pagina)
        layout_principal.setContentsMargins(30, 25, 30, 25)
        layout_principal.setSpacing(15)

        lbl_titulo = QLabel("📊 Fluxo de Caixa Detalhado (Demonstrativo)")
        lbl_titulo.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        lbl_titulo.setStyleSheet(f"color: {COR_TEXTO_ESCURO};")
        layout_principal.addWidget(lbl_titulo)

        layout_tabelas = QHBoxLayout()
        layout_tabelas.setSpacing(20)

        container_entradas = QWidget()
        layout_ent = QVBoxLayout(container_entradas)
        layout_ent.setContentsMargins(0, 0, 0, 0)
        
        lbl_ent = QLabel("📈 Receitas (Preços Negociados por Pet)")
        lbl_ent.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        lbl_ent.setStyleSheet("color: #4A6B40;")
        layout_ent.addWidget(lbl_ent)

        self.tabela_financeiro_entradas = QTableWidget()
        self.tabela_financeiro_entradas.setStyleSheet(self._estilo_tabela_financeira())
        layout_ent.addWidget(self.tabela_financeiro_entradas)
        layout_tabelas.addWidget(container_entradas)

        container_saidas = QWidget()
        layout_sai = QVBoxLayout(container_saidas)
        layout_sai.setContentsMargins(0, 0, 0, 0)
        
        lbl_sai = QLabel("📉 Despesas & Custos Operacionais")
        lbl_sai.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        lbl_sai.setStyleSheet("color: #A34747;")
        layout_sai.addWidget(lbl_sai)

        self.tabela_financeiro_saidas = QTableWidget()
        self.tabela_financeiro_saidas.setStyleSheet(self._estilo_tabela_financeira())
        layout_sai.addWidget(self.tabela_financeiro_saidas)
        layout_tabelas.addWidget(container_saidas)

        layout_principal.addLayout(layout_tabelas)

        self.carregar_dados_financeiros_detalhados()

        return pagina

    def carregar_dados_financeiros_detalhados(self):
        """Busca os dados de faturamento mapeando Pet/Tutor e as despesas registradas"""
        cursor = self.banco.conexao.cursor()

        query_entradas = """
            SELECT p.nome, t.nome, a.servico, a.valor
            FROM atendimentos a
            JOIN pets p ON a.pet_id = p.id
            JOIN tutores t ON p.tutor_id = t.id
            WHERE a.status != 'Cancelado'
        """
        cursor.execute(query_entradas)
        entradas = cursor.fetchall()

        self.tabela_financeiro_entradas.setColumnCount(3)
        self.tabela_financeiro_entradas.setRowCount(len(entradas))
        self.tabela_financeiro_entradas.setHorizontalHeaderLabels(["Pet (Tutor)", "Serviço", "Arrecadado"])
        self.tabela_financeiro_entradas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        for linha_idx, dados in enumerate(entradas):
            pet_nome, tutor_nome, servico, valor = dados
            identificacao = f"{pet_nome} ({tutor_nome.split()[0]})"
            
            item_id = QTableWidgetItem(identificacao)
            item_srv = QTableWidgetItem(servico)
            item_val = QTableWidgetItem(f"R$ {valor:.2f}")
            item_val.setForeground(Qt.GlobalColor.darkGreen)

            for col_idx, item in enumerate([item_id, item_srv, item_val]):
                item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.tabela_financeiro_entradas.setItem(linha_idx, col_idx, item)

        query_saidas = """
            SELECT descricao, valor, data_gasto FROM gastos ORDER BY data_gasto DESC
        """
        cursor.execute(query_saidas)
        saidas = cursor.fetchall()

        self.tabela_financeiro_saidas.setColumnCount(2)
        self.tabela_financeiro_saidas.setRowCount(len(saidas))
        self.tabela_financeiro_saidas.setHorizontalHeaderLabels(["Descrição do Custo", "Pago"])
        self.tabela_financeiro_saidas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        for linha_idx, dados in enumerate(saidas):
            descricao, valor, _ = dados
            
            item_desc = QTableWidgetItem(descricao)
            item_val = QTableWidgetItem(f"R$ {valor:.2f}")
            item_val.setForeground(Qt.GlobalColor.red)

            for col_idx, item in enumerate([item_desc, item_val]):
                item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.tabela_financeiro_saidas.setItem(linha_idx, col_idx, item)

    def _estilo_tabela_financeira(self):
        return """
            QTableWidget {
                background-color: white;
                border: 1px solid #D1C7BD;
                border-radius: 6px;
                gridline-color: #EFECE6;
            }
            QHeaderView::section {
                background-color: #F4F1EA;
                padding: 6px;
                border: none;
                font-weight: bold;
            }
        """
    
    def criar_pagina_perfil_real(self):
        """Gera a interface de Perfil & Usuários com recursos operacionais e de segurança"""
        pagina = QWidget()
        layout_principal = QVBoxLayout(pagina)
        layout_principal.setContentsMargins(30, 25, 30, 25)
        layout_principal.setSpacing(20)

        lbl_titulo = QLabel("👤 Central do Usuário e Configurações")
        lbl_titulo.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        lbl_titulo.setStyleSheet(f"color: {COR_TEXTO_ESCURO};")
        layout_principal.addWidget(lbl_titulo)

        card_usuario = QFrame()
        card_usuario.setStyleSheet("background-color: white; border: 1px solid #D1C7BD; border-radius: 6px;")
        layout_card = QVBoxLayout(card_usuario)
        layout_card.setSpacing(8)

        lbl_user_tit = QLabel("📋 Dados da Sessão Ativa")
        lbl_user_tit.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        lbl_user_tit.setStyleSheet(f"color: {COR_TEXTO_ESCURO};")
        
        lbl_email = QLabel("<b>E-mail:</b> demo@petshop.com (Ambiente Isolado)")
        lbl_cargo = QLabel("<b>Nível de Acesso:</b> Administrador / Desenvolvedor")
        lbl_status = QLabel("<b>Sessão:</b> Temporária (Dados serão resetados ao fechar)")
        lbl_status.setStyleSheet("color: #7AA2C2; font-weight: bold;")

        layout_card.addWidget(lbl_user_tit)
        layout_card.addWidget(lbl_email)
        layout_card.addWidget(lbl_cargo)
        layout_card.addWidget(lbl_status)
        layout_principal.addWidget(card_usuario)

        lbl_secao_acoes = QLabel("⚙️ Ferramentas de Gerenciamento")
        lbl_secao_acoes.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        lbl_secao_acoes.setStyleSheet(f"color: {COR_TEXTO_ESCURO}; margin-top: 10px;")
        layout_principal.addWidget(lbl_secao_acoes)

        layout_botoes = QHBoxLayout()
        layout_botoes.setSpacing(15)

        btn_senha = QPushButton("🔑 Mudar Senha")
        btn_senha.clicked.connect(self.simular_mudanca_senha)
        self._estilizar_botao_perfil(btn_senha, "#8CA485")

        btn_codigo = QPushButton("🎫 Gerar Código de Convite")
        btn_codigo.clicked.connect(self.simular_geracao_codigo)
        self._estilizar_botao_perfil(btn_codigo, "#7AA2C2")

        btn_backup = QPushButton("💾 Fazer Backup da RAM")
        btn_backup.clicked.connect(self.simular_backup_banco)
        self._estilizar_botao_perfil(btn_backup, "#7AA2C2")

        layout_botoes.addWidget(btn_senha)
        layout_botoes.addWidget(btn_codigo)
        layout_botoes.addWidget(btn_backup)
        layout_principal.addLayout(layout_botoes)

        layout_rodape = QHBoxLayout()
        layout_rodape.setSpacing(15)

        btn_update = QPushButton("🔄 Verificar Atualizações do App")
        btn_update.clicked.connect(lambda: QMessageBox.information(self, "Atualização", "PetShop Control v1.0.0\n\nO aplicativo já está na versão mais recente disponível."))
        self._estilizar_botao_perfil(btn_update, "#E6E1D6", texto_escuro=True)

        btn_sair = QPushButton("🚪 Encerrar Sessão (Sair)")
        btn_sair.clicked.connect(self.close)
        self._estilizar_botao_perfil(btn_sair, "#C27A7A")

        layout_rodape.addWidget(btn_update)
        layout_rodape.addWidget(btn_sair)
        
        layout_principal.addStretch()
        layout_principal.addLayout(layout_rodape)

        card_usuario.setStyleSheet("""
            QFrame { background-color: white; border: 1px solid #D1C7BD; border-radius: 6px; }
            QLabel { color: #4A4540; border: none; }
        """)

        return pagina


    def simular_mudanca_senha(self):
        """Simula a rotina de update de credenciais"""
        from PyQt6.QtWidgets import QInputDialog
        nova_senha, ok = QInputDialog.getText(self, "Segurança", "Digite a sua nova senha de acesso:", QLineEdit.EchoMode.Password)
        if ok and nova_senha.strip():
            cursor = self.banco.conexao.cursor()
            cursor.execute("UPDATE usuarios SET senha = ? WHERE email = 'demo@petshop.com'", (nova_senha.strip(),))
            self.banco.conexao.commit()
            QMessageBox.information(self, "Sucesso", "Senha do usuário de testes atualizada com sucesso na RAM!")

    def simular_geracao_codigo(self):
        """Simula a geração de chaves de convite exclusivas para novos operadores"""
        import secrets
        codigo_gerado = f"PET-{secrets.token_hex(4).upper()}"
        cursor = self.banco.conexao.cursor()
        cursor.execute("INSERT INTO codigos_convite (codigo, status) VALUES (?, 'Ativo')", (codigo_gerado,))
        self.banco.conexao.commit()
        
        QMessageBox.information(self, "Token Gerado", f"Código de convite para novo funcionário criado:\n\n🔑 {codigo_gerado}\n\nEnvie este código para o novo operador se registrar.")

    def simular_backup_banco(self):
        """Simula a exportação de segurança do banco em memória"""
        import json
        cursor = self.banco.conexao.cursor()
        
        cursor.execute("SELECT nome_produto, quantidade_atual FROM produtos_estoque")
        dados_estoque = cursor.fetchall()
        
        QMessageBox.information(
            self, 
            "Backup Concluído", 
            f"Rotina de integridade executada!\n\n"
            f"• Estado da RAM espelhado com sucesso.\n"
            f"• {len(dados_estoque)} itens de estoque catalogados na imagem de segurança.\n"
            f"• Arquivo temporário criado localmente."
        )

    def _estilizar_botao_perfil(self, botao, cor_fundo, texto_escuro=False):
        botao.setCursor(Qt.CursorShape.PointingHandCursor)
        botao.setFixedHeight(40)
        cor_texto = COR_TEXTO_ESCURO if texto_escuro else "white"
        font_weight = "bold" if not texto_escuro else "normal"
        
        botao.setStyleSheet(f"""
            QPushButton {{
                background-color: {cor_fundo};
                color: {cor_texto};
                font-weight: {font_weight};
                border-radius: 4px;
                border: none;
                padding: 0px 15px;
            }}
            QPushButton:hover {{
                opacity: 0.9;
                background-color: {cor_fundo}; /* Fallback visual */
            }}
        """)