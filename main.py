import sys
import faulthandler

faulthandler.enable()

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
        """Abre a tela de login isolada de conexões com o banco"""
        self.tela_login = TelaMenuInicial()
        
        self.tela_login.sinal_modo_demonstracao.connect(self.ativar_modo_demonstracao)
        self.tela_login.sinal_autenticar.connect(self.processar_autenticacao)
        
        self.tela_login.show()
        
        codigo_saida = self.app.exec()
        if self.banco:
            self.banco.fechar_conexao()
        sys.exit(codigo_saida)

    def ativar_modo_demonstracao(self):
        """Inicializa o sistema operando em memória RAM (Banco Volátil)"""
        try:
            print("[SISTEMA] Inicializando Modo Demonstração...")
            if self.banco:
                self.banco.fechar_conexao()
                
            self.banco = BancoDeDados(modo_demonstracao=True)
            self.abrir_dashboard(email_logado="demo@petshop.com")
        except Exception as e:
            QMessageBox.critical(None, "Erro Crítico", f"Erro ao iniciar demonstração: {str(e)}")

    def processar_autenticacao(self, email, senha):
        """Inicializa o banco de dados físico apenas após o clique de autenticação"""
        try:
            print(f"[SISTEMA] Tentando autenticar o usuário: {email}")
            if self.banco:
                self.banco.fechar_conexao()

            self.banco = BancoDeDados(modo_demonstracao=False)
            cursor = self.banco.conexao.cursor()
            
            cursor.execute(
                "SELECT cargo FROM usuarios WHERE email = ? AND senha = ?", 
                (email.strip(), senha.strip())
            )
            usuario = cursor.fetchone()
            
            if usuario:
                print(f"[SISTEMA] Autenticado com sucesso!")
                self.abrir_dashboard(email_logado=email.strip())
            else:
                QMessageBox.warning(self.tela_login, "Acesso Negado", "E-mail ou senha incorretos.")
                self.banco.fechar_conexao()
                self.banco = None
                
        except Exception as e:
            QMessageBox.critical(self.tela_login, "Erro de Conexão", f"Falha ao autenticar: {str(e)}")

    def abrir_dashboard(self, email_logado):
        """Realiza a transição de janelas injetando o e-mail de forma dinâmica"""
        try:
            self.tela_dashboard = TelaDashboard(self.banco, email_logado)
            
            self.tela_dashboard.sinal_logout.connect(self.realizar_logout)
            
            self.tela_dashboard.show()
            self.tela_login.close()
        except Exception as e:
            QMessageBox.critical(None, "Erro de Inicialização", f"Falha ao abrir o painel: {str(e)}")

    def realizar_logout(self):
        """Fecha o painel logado, limpa a sessão do banco e ressuscita a tela de login"""
        try:
            print("[SISTEMA] Processando encerramento de sessão...")
            
            if self.banco:
                self.banco.fechar_conexao()
                self.banco = None
            
            if self.tela_dashboard:
                self.tela_dashboard.close()
                self.tela_dashboard = None
                
            self.tela_login = TelaMenuInicial()
            self.tela_login.sinal_modo_demonstracao.connect(self.ativar_modo_demonstracao)
            self.tela_login.sinal_autenticar.connect(self.processar_autenticacao)
            self.tela_login.show()
            
            print("[SISTEMA] Sessão finalizada. Retornado ao Menu Inicial.")
        except Exception as e:
            QMessageBox.critical(None, "Erro ao Sair", f"Falha ao retornar para o menu: {str(e)}")

if __name__ == "__main__":
    sistema = ControladorSistema()
    sistema.iniciar()