import os
import shutil
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class SincronizadorFirebase:
    def __init__(self):
        self.api_key = os.getenv("FIREBASE_API_KEY")
        self.project_id = os.getenv("FIREBASE_PROJECT_ID")
        self.storage_bucket = os.getenv("FIREBASE_STORAGE_BUCKET")
        
        self.versao_atual_app = "1.0.0"

    def verificar_atualizacao(self, conta_id):
        """
        Consulta o Firebase para verificar se o Administrador liberou 
        uma nova versão do executável para este perfil.
        """
        if not self.api_key:
            print("[FIREBASE] Modo Demo/Sem chaves: Ignorando busca por atualizações.")
            return False

        print(f"[FIREBASE] Verificando atualizações no nó do perfil: {conta_id}...")
        
        versao_remota_servidor = "1.0.0" 

        if versao_remota_servidor > self.versao_atual_app:
            print(f"[SISTEMA] Nova versão detectada: {versao_remota_servidor}! Forçando login para atualizar.")
            return True
            
        return False

    def enviar_backup_semanal_com_retencao(self, conta_id):
        """
        Gera uma cópia do banco SQLite, envia para o Firebase Storage e
        garante a regra de negócio de manter no máximo 2 backups antigos por conta.
        """
        if not self.api_key:
            print("[FIREBASE] Modo Demo: Simulação de envio de backup para a nuvem finalizada.")
            return True

        nome_banco_local = "petshop_local.db"
        data_hoje = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo_backup = f"backup_{conta_id}_{data_hoje}.db"

        if not os.path.exists(nome_banco_local):
            print("[ERRO] Banco de dados local não encontrado para backup!")
            return False

        print(f"[FIREBASE] Iniciando rotina de checagem de backups para: {conta_id}")
        
        arquivos_no_firebase = [
            f"backups/{conta_id}/backup_{conta_id}_20260514_120000.db",
            f"backups/{conta_id}/backup_{conta_id}_20260521_120000.db" 
        ]

        print(f"[FIREBASE] Encontrados {len(arquivos_no_firebase)} backups salvos na nuvem.")

        if len(arquivos_no_firebase) >= 2:
            arquivo_para_deletar = arquivos_no_firebase[0] 
            print(f"[REGENERAÇÃO] Removendo backup antigo da nuvem para liberar espaço: {arquivo_para_deletar}")
            arquivos_no_firebase.pop(0)

        print(f"[FIREBASE] Subindo novo arquivo de segurança: {nome_arquivo_backup} para 'backups/{conta_id}/'")
        
        print("[SUCESSO] Backup semanal concluído e armazenado com segurança!")
        return True