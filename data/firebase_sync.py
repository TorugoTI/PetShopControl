import os
import glob
import shutil
import base64
import pyrebase
import sys
import firebase_admin
from firebase_admin import credentials, firestore, auth
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
        self.rt_db = self.firebase.database()
        self.versao_atual_app = "1.0.0"
        
        if not firebase_admin._apps:
            cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        
        self.db = firestore.client() 
        self.fs_db = self.db 
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.pasta_backup = os.path.join(base_dir, "backups")
        self.caminho_db_local = os.path.join(base_dir, "data", "petshop.db")
        
        os.makedirs(self.pasta_backup, exist_ok=True)
        self._limpar_backups_antigos()

    def restaurar_backup_local(self, caminho_arquivo_origem):
        """Sobrescreve o banco de dados local com o arquivo escolhido."""
        try:
            os.makedirs(os.path.dirname(self.caminho_db_local), exist_ok=True)
            shutil.copy(caminho_arquivo_origem, self.caminho_db_local)
            print(f"[SUCESSO] Backup local restaurado de {caminho_arquivo_origem}.")
            return True
        except Exception as e:
            print(f"[ERRO] Falha na restauração local: {e}")
            return False

    def fazer_backup_local_gerenciado(self):
        """Salva uma cópia datada na pasta local /backups/."""
        try:
            os.makedirs(self.pasta_backup, exist_ok=True)
            nome_arq = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            destino = os.path.join(self.pasta_backup, nome_arq)
            if os.path.exists(self.caminho_db_local):
                shutil.copy(self.caminho_db_local, destino)
                self._limpar_backups_antigos()
                return destino
            return None
        except Exception as e:
            print(f"[ERRO] Falha ao gerar backup local gerenciado: {e}")
            return None

    def carregar_dados_backup_nuvem(self, doc_id):
        """Baixa o backup do Firestore e retorna os bytes decodificados."""
        try:
            doc_ref = self.db.collection('backups').document(doc_id)
            doc = doc_ref.get()
            if doc.exists:
                dados = doc.to_dict()
                conteudo_base64 = dados.get('arquivo_base64')
                if conteudo_base64:
                    return base64.b64decode(conteudo_base64)
            return None
        except Exception as e:
            print(f"[ERRO] Falha ao carregar bytes do backup da nuvem: {e}")
            return None

    def baixar_e_aplicar_backup(self, doc_id):
        """Baixa o backup do Firestore e sobrescreve o arquivo .db local."""
        try:
            bytes_db = self.carregar_dados_backup_nuvem(doc_id)
            if bytes_db:
                os.makedirs(os.path.dirname(self.caminho_db_local), exist_ok=True)
                with open(self.caminho_db_local, "wb") as f:
                    f.write(bytes_db)
                print(f"[SUCESSO] Backup {doc_id} restaurado e aplicado localmente.")
                return True
            return False
        except Exception as e:
            print(f"[ERRO] Falha ao baixar/aplicar backup da nuvem: {e}")
            return False

    def listar_codigos_ativos(self):
        try:
            codigos_ref = self.db.collection('codigos_convite') 
            query = codigos_ref.where(filter=FieldFilter('status', '==', 'Ativo')).stream()
            return [doc.to_dict() for doc in query]
        except Exception as e:
            print(f"[ERRO Firestore] Falha ao listar códigos: {e}")
            return []

    def salvar_codigo_convite(self, codigo):
        try:
            dados = {
                'codigo': codigo,
                'status': 'Ativo',
                'criado_em': firestore.SERVER_TIMESTAMP
            }
            self.fs_db.collection('codigos_convite').add(dados)
            return True
        except Exception as e:
            print(f"[ERRO Firestore] Falha ao salvar código: {e}")
            return False
            
    def _limpar_backups_antigos(self):
        if not os.path.exists(self.pasta_backup): return
        arquivos = glob.glob(os.path.join(self.pasta_backup, "backup_*.db"))
        arquivos.sort(key=os.path.getctime)
        while len(arquivos) > 5:
            os.remove(arquivos[0])
            arquivos.pop(0)

    def marcar_codigo_como_usado(self, codigo):
        try:
            docs = self.db.collection('codigos_convite').where(filter=FieldFilter('codigo', '==', codigo)).stream()
            for doc in docs:
                doc.reference.update({'status': 'Usado'})
            return True
        except Exception as e:
            return False

    def enviar_backup_oficial_nuvem(self, conta_id):
        """Força o envio do arquivo .db real codificado em base64 para o Firestore."""
        try:
            if not os.path.exists(self.caminho_db_local):
                print(f"[ERRO] Banco local não encontrado em: {self.caminho_db_local}")
                return False
                
            with open(self.caminho_db_local, "rb") as f:
                conteudo_base64 = base64.b64encode(f.read()).decode('utf-8')
                
            doc_id = f"db_{conta_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.fs_db.collection('backups').document(doc_id).set({
                'tipo': 'banco_sqlite',
                'conta': conta_id,
                'arquivo_base64': conteudo_base64,
                'data': datetime.now(),
                'versao': self.versao_atual_app
            })
            print(f"[SUCESSO] Backup oficial {doc_id} enviado para o Firestore.")
            return True
        except Exception as e:
            print(f"[ERRO Firestore] Falha ao enviar backup oficial: {e}")
            return False

    def listar_backups_nuvem(self):
        """Lista os IDs de backups da nuvem que contêm arquivo binário do banco."""
        try:
            docs = self.db.collection('backups').order_by('data', direction='DESCENDING').limit(20).stream()
            lista_ids = []
            for doc in docs:
                data_dict = doc.to_dict()
                if 'arquivo_base64' in data_dict:
                    lista_ids.append(doc.id)
                if len(lista_ids) >= 5:
                    break
            return lista_ids
        except Exception as e:
            print(f"[ERRO] Falha ao listar backups na nuvem: {e}")
            return []
        
    def verificar_atualizacao(self):
        try:
            return self.rt_db.child("configuracoes").get().val()
        except Exception as e:
            return None
        
    @staticmethod
    def get_path_to_key():
        base_dir = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        return os.path.join(base_dir, 'config', 'firebase-key.json')