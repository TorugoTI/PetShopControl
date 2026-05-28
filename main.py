import sys
import os
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
        """Monta a tela de login isolada de conexões pesadas"""
        self.tela_login = TelaMenuInicial()
        
        self.tela_login.sinal_modo_demonstracao.connect(self.ativar_modo_demonstracao)
        self.tela_login.sinal_autenticar.connect(self.processar_autenticacao)
        
        self.tela_login.show()
        
        codigo_saida = self.app.exec()
        if self.banco:
            self.banco.fechar_conexao()
        sys.exit(codigo_saida)

    def ativar_modo_demonstracao(self):
        """Inicia o modo demonstração criando o banco APENAS em memória RAM"""
        try:
            print("[SISTEMA] Inicializando Modo Demonstração...")
            if self.banco:
                self.banco.fechar_conexao()
                
            self.banco = BancoDeDados(modo_demonstracao=True)
            self.abrir_dashboard(email_logado="demo@petshop.com")
        except Exception as e:
            QMessageBox.critical(None, "Erro Crítico", f"Erro ao iniciar demonstração: {str(e)}")

    def processar_autenticacao(self, email, senha):
        """Cria o banco físico na hora e valida as credenciais ocultas do .env"""
        try:
            print(f"[SISTEMA] Tentando autenticar o usuário: {email}")
            
            self.banco = BancoDeDados(modo_demonstracao=False)
            
            if not self.banco.conexao:
                self.banco.conectar()
                
            cursor = self.banco.conexao.cursor()
            
            cursor.execute(
                "SELECT cargo FROM usuarios WHERE email = ? AND senha = ?", 
                (email.strip(), senha.strip())
            )
            usuario = cursor.fetchone()
            
            if usuario:
                print(f"[SISTEMA] Login aceito com sucesso para {email}!")
                self.abrir_dashboard(email_logado=email.strip())
            else:
                print(f"[SISTEMA] Credenciais inválidas para o e-mail: {email}")
                QMessageBox.warning(self.tela_login, "Acesso Negado", "E-mail ou senha incorretos.")
                self.banco.fechar_conexao()
                self.banco = None
                
        except Exception as e:
            print(f"[ERRO CRÍTICO NO LOGIN]: {str(e)}")
            QMessageBox.critical(self.tela_login, "Erro de Conexão", f"Falha ao autenticar: {str(e)}")

    def abrir_dashboard(self, email_logado):
        """Efetua a transição segura e limpa das janelas"""
        try:
            self.tela_dashboard = TelaDashboard(self.banco, email_logado)
            self.tela_dashboard.show()
            self.tela_login.close()
        except Exception as e:
            print(f"[ERRO CRÍTICO CRASH]: {str(e)}")
            QMessageBox.critical(None, "Erro de Inicialização", f"Falha ao abrir o painel: {str(e)}")

if __name__ == "__main__":
    sistema = ControladorSistema()
    sistema.iniciar()