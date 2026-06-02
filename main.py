import sys
import os
import pyrebase
import schedule
import time
import threading
from dotenv import load_dotenv
from PyQt6.QtCore import QSettings

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
db = firebase.database()

from PyQt6.QtWidgets import QApplication, QMessageBox
from data.database import BancoDeDados
from ui.menu import TelaMenuInicial
from ui.dashboard import TelaDashboard
from ui.registro import JanelaCadastro

class ControladorSistema:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.versao_atual = "v1.0.0"
        self.banco = None
        self.tela_login = None
        self.tela_dashboard = None
        

    def rotina_de_backup():
        print("Executando backup automático...")

    schedule.every(7).days.do(rotina_de_backup)

    def rodar_agendador():
        while True:
            schedule.run_pending()
            time.sleep(1)

    threading.Thread(target=rodar_agendador, daemon=True).start()

    def iniciar(self):
        """Abre a tela de login inicializando-a com as dependências necessárias"""
        self.tela_login = TelaMenuInicial(self.banco, self)
        
        self.tela_login.sinal_abrir_cadastro.connect(self.abrir_cadastro)
        
        self.tela_login.sinal_modo_demonstracao.connect(self.ativar_modo_demonstracao)
        self.tela_login.sinal_autenticar.connect(self.processar_autenticacao)
        
        self.tela_login.show()
        
        codigo_saida = self.app.exec()
        if self.banco:
            self.banco.fechar_conexao()
        sys.exit(codigo_saida)

        def inicializar_banco_se_vazio(banco):
            cursor = banco.conexao.cursor()
            tabelas = ["atendimentos", "tutores", "pets", "produtos", "usuarios"]
            for tabela in tabelas:
                cursor.execute(f"CREATE TABLE IF NOT EXISTS {tabela} (id INTEGER PRIMARY KEY)")
            banco.conexao.commit()

        if self.banco:
            inicializar_banco_se_vazio(self.banco)

    def ativar_modo_demonstracao(self):
        print("[SISTEMA] Inicializando Modo Demonstração...")
        if self.banco:
            self.banco.fechar_conexao()
            
        self.banco = BancoDeDados(modo_demonstracao=True)
        self.abrir_dashboard("demo@petshop.com", "Visitante (Modo Demo)")
        

    def abrir_dashboard(self, email_logado, cargo):
        print(f"Abrindo dashboard para {email_logado} com cargo {cargo}")
        
        self.tela_dashboard = TelaDashboard(self.banco, email_logado, cargo, self.versao_atual)
        
        self.tela_dashboard.sinal_logout.connect(self.realizar_logout)
        
        self.tela_dashboard.show()
        
        if self.tela_login:
            self.tela_login.close()

    def processar_autenticacao(self, email, senha):
        """Valida as credenciais e define o nível de acesso do usuário"""

        try:
            print(f"[FIREBASE] Tentando autenticar: {email}")
            usuario_firebase = auth_firebase.sign_in_with_email_and_password(email.strip(), senha.strip())
            
            email_limpo = email.strip()
            admin_email = os.getenv("ADMIN_EMAIL", "").strip()
            cargo_usuario = "Administrador Master" if email_limpo == admin_email else "Funcionário / Operador"
            
            print(f"[SISTEMA] Usuário {email_limpo} autenticado como: {cargo_usuario}")

            settings = QSettings("PetShopControl", "Login")
            settings.setValue("ultimo_email", email_limpo)
            
            self.banco = BancoDeDados(modo_demonstracao=False)

            self.abrir_dashboard(email_logado=email_limpo, cargo=cargo_usuario)
            
        except Exception as erro_firebase:
            print(f"[ERRO AUTENTICAÇÃO]: {str(erro_firebase)}")
            QMessageBox.warning(self.tela_login, "Acesso Negado", "E-mail ou senha incorretos.")

        def garantir_tabelas(self):
            cursor = self.banco.conexao.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS atendimentos (id INTEGER PRIMARY KEY, cliente TEXT, pet TEXT, valor REAL)")
            cursor.execute("CREATE TABLE IF NOT EXISTS tutores (id INTEGER PRIMARY KEY, nome TEXT)")
            cursor.execute("CREATE TABLE IF NOT EXISTS pets (id INTEGER PRIMARY KEY, nome TEXT, tutor_id INTEGER)")
            cursor.execute("CREATE TABLE IF NOT EXISTS produtos (id INTEGER PRIMARY KEY, nome TEXT, estoque INTEGER)")
            cursor.execute("CREATE TABLE IF NOT EXISTS usuarios (email TEXT PRIMARY KEY, senha TEXT, perfil TEXT)")
            self.banco.conexao.commit()

    def realizar_logout(self):
        try:
            print("[SISTEMA] Processando encerramento de sessão...")
            
            if self.banco:
                self.banco.fechar_conexao()
                self.banco = None
            
            if self.tela_dashboard:
                self.tela_dashboard.close()
                self.tela_dashboard = None
                
            self.tela_login = TelaMenuInicial(self.banco, self)
            
            self.tela_login.sinal_abrir_cadastro.connect(self.abrir_cadastro)
            self.tela_login.sinal_modo_demonstracao.connect(self.ativar_modo_demonstracao)
            self.tela_login.sinal_autenticar.connect(self.processar_autenticacao)
            
            self.tela_login.show()
            print("[SISTEMA] Sessão finalizada.")
        except Exception as e:
            QMessageBox.critical(None, "Erro ao Sair", f"Falha ao retornar para o menu: {str(e)}")
    
    def abrir_cadastro(self):
        if self.banco is None:
            self.banco = BancoDeDados(modo_demonstracao=False)
            self.banco.conectar()
            
        from ui.registro import JanelaCadastro
        janela = JanelaCadastro(self.banco, auth_firebase, db) 
        janela.exec()

if __name__ == "__main__":
    sistema = ControladorSistema()
    sistema.iniciar()