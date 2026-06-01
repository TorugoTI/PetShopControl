from PyQt6.QtWidgets import QWidget, QFormLayout, QLabel, QMessageBox
from ui.components import BotaoPrincipal, SeletorData, CampoTexto, CampoMoedaBancario

class CadastroGastoWidget(QWidget):
    def __init__(self, banco, callback_atualizar):
        super().__init__()
        self.banco = banco
        self.callback_atualizar = callback_atualizar
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        self.txt_desc = CampoTexto("Ex: Máquina de Tosa, Aluguel, Shampoos")
        
        self.txt_valor = CampoMoedaBancario()
        self.txt_valor.setStyleSheet("font-size: 14px; padding: 6px; background: white; border: 1px solid #D1C7BD; border-radius: 4px;")
        
        self.cal_gasto = SeletorData()

        layout.addRow(QLabel("Descrição do Gasto/Equipamento:"), self.txt_desc)
        layout.addRow(QLabel("Valor Pago:"), self.txt_valor)
        layout.addRow(QLabel("Data do Pagamento:"), self.cal_gasto)

        btn_salvar = BotaoPrincipal("Registrar Despesa")
        btn_salvar.clicked.connect(self.salvar_gasto)
        layout.addRow("", btn_salvar)

    def salvar_gasto(self):
        desc = self.txt_desc.text().strip()
        
        valor = self.txt_valor.pegar_valor_float()
        data_texto = self.cal_gasto.date().toString("yyyy-MM-dd")

        if not desc:
            QMessageBox.warning(self, "Aviso", "Insira uma descrição para a despesa.")
            return

        try:
            cursor = self.banco.conexao.cursor()
            cursor.execute("""
                INSERT INTO gastos (descricao, valor, data_gasto)
                VALUES (?, ?, ?)
            """, (desc, valor, data_texto))
            self.banco.conexao.commit()

            QMessageBox.information(self, "Sucesso", "Despesa registrada com sucesso!")
            self.txt_desc.clear()
            self.txt_valor.clear()

            if self.callback_atualizar:
                self.callback_atualizar()
        except Exception as e:
            QMessageBox.critical(self, "Erro SQL", f"Falha ao registrar despesa: {str(e)}")