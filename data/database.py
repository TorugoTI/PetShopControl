import sqlite3
import os
import sys
from dotenv import load_dotenv

class BancoDeDados:
    def __init__(self, modo_demonstracao=False):
        load_dotenv()
        
        self.modo_demonstracao = modo_demonstracao
        self.conexao = None
        
        try:
            self.conectar()
            self.criar_tabelas_padrao()
            self.inicializar_servicos_padrao()
        except Exception as e:
            print(f"[ERRO CRÍTICO] Falha ao inicializar banco de dados: {e}")
            raise

    def conectar(self):
        if self.modo_demonstracao:
            print("[BANCO] Conectando ao Banco Volátil em memória RAM...")
            self.conexao = sqlite3.connect(":memory:")
            self.conexao.execute("PRAGMA foreign_keys = ON;")
            self.criar_tabelas_padrao()
            self.inicializar_servicos_padrao()
            self.injetar_dados_demonstracao()
        else:
            caminho_banco = BancoDeDados.obter_caminho_banco()
            diretorio_db = os.path.dirname(caminho_banco)
            
            if diretorio_db and not os.path.exists(diretorio_db):
                os.makedirs(diretorio_db, exist_ok=True)
            
            print(f"[BANCO] Conectando ao Banco de Dados Físico: {caminho_banco}")
            novo_banco = not os.path.exists(caminho_banco)
            
            self.conexao = sqlite3.connect(caminho_banco)
            self.conexao.execute("PRAGMA foreign_keys = ON;")
            
            if novo_banco:
                print("[BANCO] Criando estrutura local pela primeira vez...")
                self.criar_tabelas_padrao()
                self.inicializar_servicos_padrao()
                self.injetar_usuario_administrador_padrao()
        
        return self.conexao

    def criar_tabelas_padrao(self):
        """Gera o esquema relacional completo do banco local"""
        cursor = self.conexao.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                perfil TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tutores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf TEXT,
                telefone TEXT,
                email TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tutor_id INTEGER,
                nome TEXT NOT NULL,
                especie TEXT,
                raca TEXT,
                FOREIGN KEY (tutor_id) REFERENCES tutores(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS atendimentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_id INTEGER,
                servico TEXT,
                data_atendimento TEXT,
                hora_atendimento TEXT,
                valor REAL,
                status TEXT,
                forma_pagamento TEXT,
                FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE SET NULL
            )
        """)

        try:
            cursor.execute("ALTER TABLE atendimentos ADD COLUMN forma_pagamento TEXT")
        except sqlite3.OperationalError:
            pass

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gastos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                descricao TEXT NOT NULL,
                valor REAL,
                data_gasto TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                quantidade INTEGER NOT NULL DEFAULT 0,
                preco_custo REAL NOT NULL DEFAULT 0.0,
                preco_venda REAL NOT NULL DEFAULT 0.0
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS codigos_convite (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE NOT NULL,
                status TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS servicos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL,
                preco REAL NOT NULL
            )
        """)
        
        self.conexao.commit()

    def inicializar_servicos_padrao(self):
        """Garante que os 4 serviços base existam apenas na primeira inicialização"""
        if not self.conexao: return
        cursor = self.conexao.cursor()
        
        cursor.execute("CREATE TABLE IF NOT EXISTS meta_control (chave TEXT PRIMARY KEY)")
        cursor.execute("SELECT 1 FROM meta_control WHERE chave = 'servicos_padrao_init'")
        if cursor.fetchone():
            return
            
        defaults = [
            ("Banho Simples", 50.0),
            ("Banho e Tosa", 80.0),
            ("Consulta Veterinária", 120.0),
            ("Tosa Higiênica", 40.0)
        ]
        cursor.executemany("INSERT OR IGNORE INTO servicos (nome, preco) VALUES (?, ?)", defaults)
        cursor.execute("INSERT OR IGNORE INTO meta_control (chave) VALUES ('servicos_padrao_init')")
        self.conexao.commit()

    def listar_servicos(self):
        cursor = self.conexao.cursor()
        cursor.execute("SELECT id, nome, preco FROM servicos ORDER BY nome")
        return cursor.fetchall()

    def salvar_ou_atualizar_servico(self, nome, preco, servico_id=None):
        cursor = self.conexao.cursor()
        if servico_id:
            cursor.execute("UPDATE servicos SET nome = ?, preco = ? WHERE id = ?", (nome, preco, servico_id))
        else:
            cursor.execute("INSERT OR REPLACE INTO servicos (nome, preco) VALUES (?, ?)", (nome, preco))
        self.conexao.commit()

    def excluir_servico(self, servico_id):
        cursor = self.conexao.cursor()
        cursor.execute("DELETE FROM servicos WHERE id = ?", (servico_id,))
        self.conexao.commit()

    def injetar_usuario_administrador_padrao(self):
        """Lê os dados ocultos do .env e popula a conta master de produção"""
        cursor = self.conexao.cursor()
        
        admin_email = os.getenv("ADMIN_EMAIL")
        admin_senha = os.getenv("ADMIN_PASSWORD")
        
        if not admin_email or not admin_senha:
            print("[ALERTA] Variáveis ADMIN_EMAIL ou ADMIN_PASSWORD não localizadas no .env!")
            return

        admin_email = admin_email.strip().replace("'", "").replace('"', "")
        admin_senha = admin_senha.strip().replace("'", "").replace('"', "")

        cursor.execute("""
            INSERT OR IGNORE INTO usuarios (email, senha, perfil) 
            VALUES (?, ?, 'administrador')
        """, (admin_email, admin_senha))
        
        cursor.execute("""
            INSERT OR IGNORE INTO codigos_convite (codigo, status)
            VALUES ('PETMASTER123', 'Ativo')
        """)
        
        self.conexao.commit()
        print(f"[BANCO] Administrador master ({admin_email}) e código inicial 'PETMASTER123' provisionados.")

    def injetar_dados_demonstracao(self):
        """Gera registros fictícios para o ambiente de simulação em RAM"""
        cursor = self.conexao.cursor()
        
        cursor.execute("INSERT INTO usuarios (email, senha, perfil) VALUES ('demo@petshop.com', 'demo', 'Desenvolvedor')")
        
        cursor.execute("INSERT INTO tutores (nome, telefone, email) VALUES ('Carlos Silva', '27999881122', 'carlos@gmail.com')")
        tutor_id = cursor.lastrowid
        
        cursor.execute("INSERT INTO pets (tutor_id, nome, especie, raca) VALUES (?, 'Rex', 'Cão', 'Pastor Alemão')", (tutor_id,))
        pet_id = cursor.lastrowid
        
        cursor.executemany("""
            INSERT INTO atendimentos (pet_id, servico, data_atendimento, hora_atendimento, valor, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [
            (pet_id, 'Banho e Tosa', '2026-05-28', '14:00', 90.00, 'Agendado'),
            (pet_id, 'Consulta Veterinária', '2026-05-28', '15:30', 150.00, 'Agendado'),
            (pet_id, 'Banho e Tosa', '2026-12-31', '14:00', 90.00, 'Agendado')
        ])
        
        cursor.execute("INSERT INTO gastos (descricao, valor, data_gasto) VALUES ('Conta de Energia Elétrica', 320.00, '2026-05-28')")
        self.conexao.commit()

    def contar_clientes(self):
        """Retorna o total de tutores cadastrados."""
        try:
            cursor = self.conexao.cursor()
            cursor.execute("SELECT COUNT(*) FROM tutores") 
            resultado = cursor.fetchone()[0]
            return resultado
        except Exception as e:
            print(f"Erro ao contar clientes: {e}")
            return 0
    
    def buscar_atendimentos_futuros(self):
        from datetime import datetime
        hoje = datetime.now().strftime("%Y-%m-%d")
        cursor = self.conexao.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM atendimentos")
        print(f"[DEBUG] Total na tabela atendimentos: {cursor.fetchone()[0]}")
        
        query = """
            SELECT a.id, COALESCE(t.nome, 'Não vinculado'), COALESCE(p.nome, 'Não vinculado'), 
                a.servico, a.data_atendimento, a.hora_atendimento, a.valor, COALESCE(a.forma_pagamento, '')
            FROM atendimentos a
            LEFT JOIN pets p ON a.pet_id = p.id
            LEFT JOIN tutores t ON p.tutor_id = t.id
            WHERE a.data_atendimento >= ? 
            AND (a.status != 'Concluído' OR a.status IS NULL OR a.status = '')
            ORDER BY a.data_atendimento, a.hora_atendimento
        """
        cursor.execute(query, (hoje,))
        dados = cursor.fetchall()
        print(f"[DEBUG] Atendimentos futuros retornados: {len(dados)}")
        return dados

    def adicionar_atendimento(self, pet_id, servico, data_atendimento, hora_atendimento, valor, forma_pagamento=""):
        """Insere um novo atendimento/serviço agendado."""
        try:
            cursor = self.conexao.cursor()
            cursor.execute("""
                INSERT INTO atendimentos (pet_id, servico, data_atendimento, hora_atendimento, valor, status, forma_pagamento)
                VALUES (?, ?, ?, ?, ?, 'Agendado', ?)
            """, (pet_id, servico, data_atendimento, hora_atendimento, valor, forma_pagamento))
            self.conexao.commit()
            return True, cursor.lastrowid
        except Exception as e:
            self.conexao.rollback()
            return False, str(e)

    @staticmethod
    def obter_caminho_banco():
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        
        return os.path.join(base_dir, "petshop.db")
    
    def fechar_conexao(self):
        if self.conexao:
            self.conexao.close()