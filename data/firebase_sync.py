import os
import firebase_admin
import glob
import shutil
import base64
import pyrebase

from firebase_admin import credentials, db, firestore, auth
from datetime import datetime
from dotenv import load_dotenv
from google.cloud.firestore_v1.base_query import FieldFilter


load_dotenv()

class SincronizadorFirebase:
    def __init__(self):
        config = {
            "apiKey": os.getenv("FIREBASE_API_KEY"),
            "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
            "databaseURL": os.getenv("FIREBASE_DATABASE_URL"),
            "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET")
        }
        self.firebase = pyrebase.initialize_app(config)
        self.auth = self.firebase.auth()
        self.versao_atual_app = "1.0.0"
        self.db_url = os.getenv("FIREBASE_DATABASE_URL")
        self.cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        self.db = self.firebase.database()
        
        if not firebase_admin._apps:
            try:
                raiz_projeto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                caminho_completo_chave = os.path.join(raiz_projeto, os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
                
                cred = credentials.Certificate(caminho_completo_chave)
                firebase_admin.initialize_app(cred, {'databaseURL': os.getenv("FIREBASE_DATABASE_URL")})
                print("[FIREBASE] Admin inicializado com sucesso!")
            except Exception as e:
                print(f"[ERRO] Falha ao inicializar o Firebase Admin: {e}")

        self.db = firestore.client()
        
        self.pasta_backup = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backups")
        self._limpar_backups_antigos()

    def salvar_codigo_convite(self, codigo):
        try:
            dados = {
                'codigo': codigo,
                'status': 'Ativo',
                'criado_em': firestore.SERVER_TIMESTAMP
            }
            self.db.collection('codigos_convite').add(dados)
            print(f"[SUCESSO] Código {codigo} salvo no Firestore!")
            return True
        except Exception as e:
            print(f"[ERRO Firestore] Falha ao salvar: {e}")
            return False

    def listar_codigos_ativos(self):
        """Busca apenas códigos com status 'Ativo' para o Admin."""
        try:
            codigos_ref = self.db.collection('codigos_convite')
            query = codigos_ref.where('status', '==', 'Ativo').stream()
            
            lista = [doc.to_dict() for doc in query]
            return lista
        except Exception as e:
            print(f"[ERRO Firestore] Falha ao listar: {e}")
            return []
            
    def _limpar_backups_antigos(self):
        """Método privado para rodar na inicialização."""
        if not os.path.exists(self.pasta_backup): return
        
        arquivos = glob.glob(os.path.join(self.pasta_backup, "backup_*.db"))
        arquivos.sort(key=os.path.getctime)
        
        while len(arquivos) > 2:
            os.remove(arquivos[0])
            print(f"[LIMPEZA] Backup local antigo removido: {arquivos[0]}")
            arquivos.pop(0)

    def marcar_codigo_como_usado(self, codigo):
        """Atualiza o status para 'Usado' após a criação da conta."""
        try:
            docs = self.db.collection('codigos_convite').where('codigo', '==', codigo).stream()
            for doc in docs:
                doc.reference.update({'status': 'Usado'})
            return True
        except Exception as e:
            return False

    def salvar_backup_resumido_firestore(self, dados_essenciais):
        """Salva um documento no Firestore com o estado atual do banco."""
        doc_ref = self.db.collection('backups').document(datetime.now().strftime("%Y%m%d"))
        doc_ref.set({
            'data': datetime.now(),
            'conteudo': dados_essenciais,
            'versao': self.versao_atual_app
        })

        backups = self.db.collection('backups').order_by('data').limit_to_last(2).stream()

    def enviar_backup_semanal_com_retencao(self, conta_id):
        dados_backup = {"status": "backup_automatico", "data": datetime.now().isoformat()}
        return self.salvar_backup_firestore(conta_id, dados_backup)

    def salvar_backup_firestore(self, conta_id, caminho_banco):
        with open(caminho_banco, "rb") as f:
            conteudo_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        doc_ref = self.db.collection('backups').document(f"{conta_id}_{datetime.now().strftime('%Y%m%d')}")
        doc_ref.set({
            'arquivo_base64': conteudo_base64,
            'data': datetime.now()
        })

    def alterar_senha(self, token_usuario, nova_senha):
        try:
            self.auth.update_email_password(token_usuario, None, nova_senha)
            return True
        except Exception as e:
            print(f"[ERRO] Falha ao alterar senha: {e}")
            return False

    def alterar_senha_admin(self, email, nova_senha):
        """Usa o SDK Admin para alterar a senha diretamente."""
        try:
            user = auth.get_user_by_email(email)
            auth.update_user(user.uid, password=nova_senha)
            return True
        except Exception as e:
            print(f"[ERRO] Falha ao atualizar senha via Admin SDK: {e}")
            return False

    def restaurar_backup_firestore(self, conta_id, data_backup):
        """Baixa os dados do Firestore e reconstrói o banco (exemplo conceitual)."""
        try:
            doc_ref = self.db.collection('backups').document(f"{conta_id}_{data_backup}")
            doc = doc_ref.get()
            if doc.exists:
                dados = doc.to_dict()
                print("Backup encontrado! Iniciando restauração...")
                return True
        except Exception as e:
            print(f"[ERRO] Falha ao restaurar: {e}")
            return False
        
    def restaurar_backup_local(self, caminho_arquivo_origem):
        """Sobrescreve o banco de dados local com o arquivo escolhido."""
        try:
            caminho_banco_atual = os.path.join(os.path.dirname(os.path.dirname(__file__)), "petshop.db")
            
            shutil.copy(caminho_arquivo_origem, caminho_banco_atual)
            return True
        except Exception as e:
            print(f"[ERRO] Falha na restauração: {e}")
            return False
    
    def listar_codigos_ativos(self):
        try:
            codigos_ref = self.db.collection('codigos_convite') 
            query = codigos_ref.where(filter=FieldFilter('status', '==', 'Ativo')).stream()
        
            lista = [doc.to_dict() for doc in query]
            print(f"[DEBUG] Códigos encontrados no Firebase: {len(lista)}")
            return lista
        except Exception as e:
            print(f"[ERRO Firestore] Falha ao listar: {e}")
            return []

    def baixar_e_aplicar_backup(self, doc_id):
        """Baixa o backup do Firestore e sobrescreve o arquivo .db local."""
        try:
            doc_ref = self.db.collection('backups').document(doc_id)
            doc = doc_ref.get()
            
            if doc.exists:
                dados = doc.to_dict()
                conteudo_base64 = dados.get('arquivo_base64')
                
                if conteudo_base64:
                    caminho_banco = os.path.join(os.path.dirname(os.path.dirname(__file__)), "petshop.db")
                    
                    with open(caminho_banco, "wb") as f:
                        f.write(base64.b64decode(conteudo_base64))
                        
                    print(f"[SUCESSO] Backup {doc_id} restaurado com sucesso.")
                    return True
            return False
        except Exception as e:
            print(f"[ERRO] Falha ao baixar/aplicar backup da nuvem: {e}")
            return False

    def listar_backups_nuvem(self):
        """Lista os últimos 5 backups salvos no Firestore."""
        try:
            docs = self.db.collection('backups').order_by('data', direction='DESCENDING').limit(5).stream()
            return [doc.id for doc in docs]
        except Exception as e:
            print(f"[ERRO] Falha ao listar backups na nuvem: {e}")
            return []
        
    def verificar_atualizacao(self):
        try:
            data = self.db.child("configuracoes").get().val()
            return data
        except Exception as e:
            print(f"[ERRO] Falha ao verificar atualização: {e}")
            return None