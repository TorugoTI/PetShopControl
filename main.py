import sys
import os
import faulthandler
import pyrebase
from dotenv import load_dotenv

faulthandler.enable()
load_dotenv()

config_firebase = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID")
}

chave_gemini = os.getenv("GEMINI_API_KEY")
agenda_id = os.getenv("GOOGLE_CALENDAR_ID")
firebase = pyrebase.initialize_app(config_firebase)
auth_firebase = firebase.auth()

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
        """Valida as credenciais em tempo real nos servidores do Firebase Auth"""
        try:
            print(f"[FIREBASE] Tentando autenticar: {email}")
            
            usuario_firebase = auth_firebase.sign_in_with_email_and_password(email.strip(), senha.strip())
            
            token_sessao = usuario_firebase['idToken']
            print(f"[SISTEMA] Autenticação Firebase bem-sucedida para o usuário!")
            
            self.banco = BancoDeDados(modo_demonstracao=False)
            
            self.abrir_dashboard(email_logado=email.strip())
            
        except Exception as erro_firebase:
            print(f"[ERRO AUTENTICAÇÃO]: {str(erro_firebase)}")
            
            mensagem_erro = "E-mail ou senha incorretos."
            erro_str = str(erro_firebase)
            
            if "EMAIL_NOT_FOUND" in erro_str:
                mensagem_erro = "Este e-mail de usuário não está cadastrado no sistema."
            elif "INVALID_PASSWORD" in erro_str:
                mensagem_erro = "Senha incorreta. Verifique os dados e tente novamente."
            elif "USER_DISABLED" in erro_str:
                mensagem_erro = "Esta conta administrativa foi desativada pelo desenvolvedor."
            
            QMessageBox.warning(self.tela_login, "Acesso Negado", mensagem_erro)
            
            if self.banco:
                self.banco.fechar_conexao()
                self.banco = None

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