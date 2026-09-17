from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem, 
    QHBoxLayout, QPushButton, QMessageBox, QHeaderView, QInputDialog
)
from PyQt6.QtCore import Qt

class GerenciamentoCadastrosWidget(QWidget):
    def __init__(self, banco, callback_atualizar=None):
        super().__init__()
        self.banco = banco
        self.callback_atualizar = callback_atualizar
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        
        self.tab_servicos = QWidget()
        self.setup_tab_servicos()
        self.tabs.addTab(self.tab_servicos, "⚙️ Serviços & Preços Fixos")

        self.tab_tutores = QWidget()
        self.setup_tab_tutores()
        self.tabs.addTab(self.tab_tutores, "👤 Tutores")

        self.tab_pets = QWidget()
        self.setup_tab_pets()
        self.tabs.addTab(self.tab_pets, "🐾 Pets")

        layout.addWidget(self.tabs)
        self.recarregar_tudo()

    def recarregar_tudo(self):
        """Atualiza todas as abas de gerenciamento."""
        self.carregar_servicos()
        self.carregar_tutores()
        self.carregar_pets()

    def setup_tab_servicos(self):
        layout = QVBoxLayout(self.tab_servicos)
        topo = QHBoxLayout()
        btn_novo_servico = QPushButton("➕ Novo Serviço Específico")
        btn_novo_servico.clicked.connect(self.adicionar_servico_custom)
        btn_atualizar = QPushButton("🔄 Atualizar Lista")
        btn_atualizar.clicked.connect(self.carregar_servicos)
        topo.addWidget(btn_novo_servico)
        topo.addWidget(btn_atualizar)
        layout.addLayout(topo)

        self.tabela_servicos = QTableWidget()
        self.tabela_servicos.setColumnCount(3)
        self.tabela_servicos.setHorizontalHeaderLabels(["ID", "Serviço", "Preço Fixo (R$)"])
        self.tabela_servicos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabela_servicos)

        acoes = QHBoxLayout()
        btn_editar = QPushButton("✏️ Alterar Preço/Nome")
        btn_editar.clicked.connect(self.editar_servico_selecionado)
        btn_excluir = QPushButton("🗑️ Excluir Serviço")
        btn_excluir.clicked.connect(self.excluir_servico_selecionado)
        acoes.addWidget(btn_editar)
        acoes.addWidget(btn_excluir)
        layout.addLayout(acoes)

    def carregar_servicos(self):
        self.tabela_servicos.setRowCount(0)
        if not self.banco or not self.banco.conexao: return
        cursor = self.banco.conexao.cursor()
        cursor.execute("SELECT id, nome, preco FROM servicos ORDER BY nome")
        for row_idx, (sid, nome, preco) in enumerate(cursor.fetchall()):
            self.tabela_servicos.insertRow(row_idx)
            self.tabela_servicos.setItem(row_idx, 0, QTableWidgetItem(str(sid)))
            self.tabela_servicos.setItem(row_idx, 1, QTableWidgetItem(nome))
            self.tabela_servicos.setItem(row_idx, 2, QTableWidgetItem(f"R$ {preco:.2f}"))

    def adicionar_servico_custom(self):
        nome, ok1 = QInputDialog.getText(self, "Novo Serviço", "Nome do serviço:")
        if not ok1 or not nome.strip(): return
        preco_txt, ok2 = QInputDialog.getText(self, "Preço Fixo", "Preço (ex: 80.00):")
        if not ok2: return
        try:
            preco = float(preco_txt.replace(",", "."))
            cursor = self.banco.conexao.cursor()
            cursor.execute("INSERT OR REPLACE INTO servicos (nome, preco) VALUES (?, ?)", (nome.strip(), preco))
            self.banco.conexao.commit()
            self.carregar_servicos()
            if self.callback_atualizar: self.callback_atualizar()
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))

    def editar_servico_selecionado(self):
        row = self.tabela_servicos.currentRow()
        if row < 0: return
        sid = self.tabela_servicos.item(row, 0).text()
        nome_atual = self.tabela_servicos.item(row, 1).text()
        preco_atual = self.tabela_servicos.item(row, 2).text().replace("R$", "").strip()
        
        novo_nome, ok1 = QInputDialog.getText(self, "Editar Serviço", "Nome:", text=nome_atual)
        if not ok1: return
        novo_preco_txt, ok2 = QInputDialog.getText(self, "Editar Preço", "Preço:", text=preco_atual)
        if not ok2: return
        try:
            preco = float(novo_preco_txt.replace(",", "."))
            cursor = self.banco.conexao.cursor()
            cursor.execute("UPDATE servicos SET nome = ?, preco = ? WHERE id = ?", (novo_nome.strip(), preco, sid))
            self.banco.conexao.commit()
            self.carregar_servicos()
            if self.callback_atualizar: self.callback_atualizar()
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))

    def excluir_servico_selecionado(self):
        row = self.tabela_servicos.currentRow()
        if row < 0: return
        sid = self.tabela_servicos.item(row, 0).text()
        if QMessageBox.question(self, "Confirmação", "Excluir serviço?") == QMessageBox.StandardButton.Yes:
            cursor = self.banco.conexao.cursor()
            cursor.execute("DELETE FROM servicos WHERE id = ?", (sid,))
            self.banco.conexao.commit()
            self.carregar_servicos()
            if self.callback_atualizar: self.callback_atualizar()

    def setup_tab_tutores(self):
        layout = QVBoxLayout(self.tab_tutores)
        topo = QHBoxLayout()
        btn_atualizar = QPushButton("🔄 Atualizar Lista de Tutores")
        btn_atualizar.clicked.connect(self.carregar_tutores)
        topo.addWidget(btn_atualizar)
        layout.addLayout(topo)

        self.tabela_tutores = QTableWidget()
        self.tabela_tutores.setColumnCount(5)
        self.tabela_tutores.setHorizontalHeaderLabels(["ID", "Nome", "CPF", "Telefone", "E-mail"])
        self.tabela_tutores.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabela_tutores)

        acoes = QHBoxLayout()
        btn_editar = QPushButton("✏️ Editar Tutor")
        btn_editar.clicked.connect(self.editar_tutor_selecionado)
        btn_excluir = QPushButton("🗑️ Excluir Tutor")
        btn_excluir.clicked.connect(self.excluir_tutor_selecionado)
        acoes.addWidget(btn_editar)
        acoes.addWidget(btn_excluir)
        layout.addLayout(acoes)

    def carregar_tutores(self):
        self.tabela_tutores.setRowCount(0)
        if not self.banco or not self.banco.conexao: return
        cursor = self.banco.conexao.cursor()
        cursor.execute("SELECT id, nome, cpf, telefone, email FROM tutores ORDER BY nome")
        for row_idx, (tid, nome, cpf, tel, email) in enumerate(cursor.fetchall()):
            self.tabela_tutores.insertRow(row_idx)
            self.tabela_tutores.setItem(row_idx, 0, QTableWidgetItem(str(tid)))
            self.tabela_tutores.setItem(row_idx, 1, QTableWidgetItem(nome or ""))
            self.tabela_tutores.setItem(row_idx, 2, QTableWidgetItem(cpf or ""))
            self.tabela_tutores.setItem(row_idx, 3, QTableWidgetItem(tel or ""))
            self.tabela_tutores.setItem(row_idx, 4, QTableWidgetItem(email or ""))

    def editar_tutor_selecionado(self):
        row = self.tabela_tutores.currentRow()
        if row < 0: return
        tid = self.tabela_tutores.item(row, 0).text()
        nome_a = self.tabela_tutores.item(row, 1).text()
        cpf_a = self.tabela_tutores.item(row, 2).text()
        tel_a = self.tabela_tutores.item(row, 3).text()
        email_a = self.tabela_tutores.item(row, 4).text()

        novo_nome, ok1 = QInputDialog.getText(self, "Editar Tutor", "Nome:", text=nome_a)
        if not ok1: return
        novo_cpf, ok2 = QInputDialog.getText(self, "Editar Tutor", "CPF:", text=cpf_a)
        if not ok2: return
        novo_tel, ok3 = QInputDialog.getText(self, "Editar Tutor", "Telefone:", text=tel_a)
        if not ok3: return
        novo_email, ok4 = QInputDialog.getText(self, "Editar Tutor", "E-mail:", text=email_a)
        if not ok4: return

        try:
            cursor = self.banco.conexao.cursor()
            cursor.execute("UPDATE tutores SET nome = ?, cpf = ?, telefone = ?, email = ? WHERE id = ?",
                           (novo_nome.strip(), novo_cpf.strip(), novo_tel.strip(), novo_email.strip(), tid))
            self.banco.conexao.commit()
            self.carregar_tutores()
            if self.callback_atualizar: self.callback_atualizar()
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))

    def excluir_tutor_selecionado(self):
        row = self.tabela_tutores.currentRow()
        if row < 0: return
        tid = self.tabela_tutores.item(row, 0).text()
        nome_tutor = self.tabela_tutores.item(row, 1).text()

        if not self.banco or not self.banco.conexao: return
        try:
            cursor = self.banco.conexao.cursor()
            cursor.execute("SELECT id, nome FROM pets WHERE tutor_id = ?", (tid,))
            pets_vinculados = cursor.fetchall()

            msg = f"Tem certeza que deseja excluir o tutor '{nome_tutor}'?"
            if pets_vinculados:
                lista_pets = ", ".join([p[1] for p in pets_vinculados])
                msg += f"\n\n⚠️ Atenção: Este tutor possui {len(pets_vinculados)} pet(s) ligado(s) a ele ({lista_pets}), que também serão excluídos, pois não é permitido pet sem tutor."

            resp = QMessageBox.question(
                self, "Confirmação de Exclusão", msg,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if resp == QMessageBox.StandardButton.Yes:
                cursor.execute("DELETE FROM pets WHERE tutor_id = ?", (tid,))
                cursor.execute("DELETE FROM tutores WHERE id = ?", (tid,))
                self.banco.conexao.commit()
                
                self.carregar_tutores()
                self.carregar_pets()
                if self.callback_atualizar: 
                    self.callback_atualizar()
        except Exception as e:
            QMessageBox.critical(self, "Erro ao excluir tutor", str(e))

    def setup_tab_pets(self):
        layout = QVBoxLayout(self.tab_pets)
        topo = QHBoxLayout()
        btn_atualizar = QPushButton("🔄 Atualizar Lista de Pets")
        btn_atualizar.clicked.connect(self.carregar_pets)
        topo.addWidget(btn_atualizar)
        layout.addLayout(topo)

        self.tabela_pets = QTableWidget()
        self.tabela_pets.setColumnCount(5)
        self.tabela_pets.setHorizontalHeaderLabels(["ID", "Tutor", "Nome do Pet", "Espécie", "Raça"])
        self.tabela_pets.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabela_pets)

        acoes = QHBoxLayout()
        btn_editar = QPushButton("✏️ Editar Pet")
        btn_editar.clicked.connect(self.editar_pet_selecionado)
        btn_excluir = QPushButton("🗑️ Excluir Pet")
        btn_excluir.clicked.connect(self.excluir_pet_selecionado)
        acoes.addWidget(btn_editar)
        acoes.addWidget(btn_excluir)
        layout.addLayout(acoes)

    def carregar_pets(self):
        self.tabela_pets.setRowCount(0)
        if not self.banco or not self.banco.conexao: return
        cursor = self.banco.conexao.cursor()
        query = """
            SELECT p.id, COALESCE(t.nome, 'Sem tutor'), p.nome, p.especie, p.raca 
            FROM pets p 
            LEFT JOIN tutores t ON p.tutor_id = t.id 
            ORDER BY p.nome
        """
        cursor.execute(query)
        for row_idx, (pid, tutor_nome, nome, especie, raca) in enumerate(cursor.fetchall()):
            self.tabela_pets.insertRow(row_idx)
            self.tabela_pets.setItem(row_idx, 0, QTableWidgetItem(str(pid)))
            self.tabela_pets.setItem(row_idx, 1, QTableWidgetItem(tutor_nome))
            self.tabela_pets.setItem(row_idx, 2, QTableWidgetItem(nome or ""))
            self.tabela_pets.setItem(row_idx, 3, QTableWidgetItem(especie or ""))
            self.tabela_pets.setItem(row_idx, 4, QTableWidgetItem(raca or ""))

    def editar_pet_selecionado(self):
        row = self.tabela_pets.currentRow()
        if row < 0: return
        pid = self.tabela_pets.item(row, 0).text()
        nome_a = self.tabela_pets.item(row, 2).text()
        esp_a = self.tabela_pets.item(row, 3).text()
        raca_a = self.tabela_pets.item(row, 4).text()

        novo_nome, ok1 = QInputDialog.getText(self, "Editar Pet", "Nome:", text=nome_a)
        if not ok1: return
        novo_esp, ok2 = QInputDialog.getText(self, "Editar Pet", "Espécie:", text=esp_a)
        if not ok2: return
        novo_raca, ok3 = QInputDialog.getText(self, "Editar Pet", "Raça:", text=raca_a)
        if not ok3: return

        try:
            cursor = self.banco.conexao.cursor()
            cursor.execute("UPDATE pets SET nome = ?, especie = ?, raca = ? WHERE id = ?",
                           (novo_nome.strip(), novo_esp.strip(), novo_raca.strip(), pid))
            self.banco.conexao.commit()
            self.carregar_pets()
            if self.callback_atualizar: self.callback_atualizar()
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))

    def excluir_pet_selecionado(self):
        row = self.tabela_pets.currentRow()
        if row < 0: return
        pid = self.tabela_pets.item(row, 0).text()
        if QMessageBox.question(self, "Confirmação", "Excluir pet?") == QMessageBox.StandardButton.Yes:
            try:
                cursor = self.banco.conexao.cursor()
                cursor.execute("DELETE FROM pets WHERE id = ?", (pid,))
                self.banco.conexao.commit()
                self.carregar_pets()
                if self.callback_atualizar: self.callback_atualizar()
            except Exception as e:
                QMessageBox.critical(self, "Erro", str(e))