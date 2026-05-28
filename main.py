import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from data.database import BancoDeDados
from ui.menu import TelaMenuInicial
from ui.dashboard import TelaDashboard

class ControladorSistema:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.banco = None
        self.tela_login = None
        self.tela_dashboard = None

    def iniciar(self):
        self.tela_login = TelaMenuInicial()
        
        self.tela_login.sinal_modo_demonstracao.connect(self.ativar_modo_demonstracao)
        self.tela_login.sinal_autenticar.connect(self.processar_autenticacao)
        
        self.tela_login.show()
        sys.exit(self.app.exec())

    def ativar_modo_demonstracao(self):
        """Ativa o sistema na prática usando o banco volátil em memória RAM"""
        try:
            print("[SISTEMA] Inicializando Modo Demonstração...")
            self.banco = BancoDeDados(modo_demonstracao=True)
            
            self.abrir_dashboard()
        except Exception as e:
            QMessageBox.critical(None, "Erro Crítico", f"Erro ao iniciar demonstração: {str(e)}")

    def processar_autenticacao(self, email, senha):
        """Valida o login na prática usando o banco de dados físico real do cliente"""
        try:
            self.banco = BancoDeDados(modo_demonstracao=False)
            cursor = self.banco.conexao.cursor()
            
            cursor.execute(
                "SELECT cargo FROM usuarios WHERE email = ? AND senha = ?", 
                (email, senha)
            )
            usuario = cursor.fetchone()
            
            if usuario:
                cargo = usuario[0]
                print(f"[SISTEMA] Autenticado com sucesso! Usuário: {email} | Cargo: {cargo}")
                
                self.abrir_dashboard()
            else:
                QMessageBox.warning(self.tela_login, "Acesso Negado", "E-mail ou senha incorretos.")
                self.banco.fechar_conexao()
                
        except Exception as e:
            QMessageBox.critical(self.tela_login, "Erro de Conexão", f"Falha ao autenticar: {str(e)}")

    def abrir_dashboard(self):
        """Faz a transição de telas limpa mantendo a aplicação viva na memória"""
        self.tela_dashboard = TelaDashboard(self.banco)
        self.tela_dashboard.show()
        
        self.tela_login.close()

if __name__ == "__main__":
    sistema = ControladorSistema()
    sistema.iniciar()