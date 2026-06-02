import sqlite3
import os
from dotenv import load_dotenv

class BancoDeDados:
    def __init__(self, modo_demonstracao=False):
        load_dotenv()
        
        self.modo_demonstracao = modo_demonstracao
        self.conexao = None
        
        self.conectar()

    def conectar(self):
        self.conexao = sqlite3.connect("petshop.db")
        """Estabelece a conexão com o banco de dados (RAM ou Físico)"""
        if self.modo_demonstracao:
            print("[BANCO] Conectando ao Banco Volátil em memória RAM...")
            self.conexao = sqlite3.connect(":memory:")
            self.criar_tabelas_padrao()
            self.injetar_dados_demonstracao()
        else:
            diretorio_raiz = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
            caminho_banco = os.path.join(diretorio_raiz, "petshop.db")
            
            print(f"[BANCO] Conectando ao Banco de Dados Físico: {caminho_banco}")
            
            novo_banco = not os.path.exists(caminho_banco)
            
            self.conexao = sqlite3.connect(caminho_banco)
            self.conexao.execute("PRAGMA foreign_keys = ON;")
            
            if novo_banco:
                print("[BANCO] Criando estrutura local pela primeira vez...")
                self.criar_tabelas_padrao()
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
                FOREIGN KEY (tutor_id) REFERENCES tutores(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS atendimentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_id INTEGER,
                servico TEXT NOT NULL,
                data_atendimento TEXT,
                hora_atendimento TEXT,
                valor REAL,
                status TEXT,
                FOREIGN KEY (pet_id) REFERENCES pets(id)
            )
        """)

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
            (pet_id, 'Banho & Tosa Completa', '2026-05-28', '14:00', 90.00, 'Agendado'),
            (pet_id, 'Consulta Veterinária', '2026-05-28', '15:30', 150.00, 'Agendado'),
            (pet_id, 'Banho & Tosa Completa', '2026-12-31', '14:00', 90.00, 'Agendado')
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
        """Busca atendimentos que ainda não ocorreram."""
        from datetime import datetime
        hoje = datetime.now().strftime("%Y-%m-%d")
    
        cursor = self.conexao.cursor()
        query = """
            SELECT a.id, t.nome, a.servico, a.data_atendimento, a.hora_atendimento, a.valor
            FROM atendimentos a
            JOIN pets p ON a.pet_id = p.id
            JOIN tutores t ON p.tutor_id = t.id
            WHERE a.data_atendimento >= ? AND (a.status != 'Concluído' OR a.status IS NULL)
            ORDER BY a.data_atendimento ASC, a.hora_atendimento ASC
        """
        cursor.execute(query, (hoje,))
        return cursor.fetchall()

    def fechar_conexao(self):
        if self.conexao:
            self.conexao.close()