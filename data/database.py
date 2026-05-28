import sqlite3
from datetime import datetime, timedelta

class BancoDeDados:
    def __init__(self, modo_demonstracao=False):
        self.modo_demonstracao = modo_demonstracao
        self.conexao = None
        self.conectar()
        self.criar_tabelas()
        
        if self.modo_demonstracao:
            self.injetar_dados_demonstracao()

    def conectar(self):
        """Conecta ao arquivo físico ou cria um banco temporário em memória RAM"""
        if self.modo_demonstracao:
            self.conexao = sqlite3.connect(":memory:")
            print("[BANCO] Modo Demonstração ativo. Banco criado em memória RAM.")
        else:
            self.conexao = sqlite3.connect("petshop_local.db")
            self.conexao.execute("PRAGMA foreign_keys = ON;")
            print("[BANCO] Modo Produção ativo. Conectado ao arquivo local.")

    def criar_tabelas(self):
        """Cria a estrutura de tabelas interligadas para o simulador funcionar"""
        cursor = self.conexao.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                cargo TEXT NOT NULL DEFAULT 'Operador'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS codigos_convite (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE NOT NULL,
                status TEXT NOT NULL DEFAULT 'Ativo'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tutores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                telefone TEXT,
                email TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tutor_id INTEGER,
                nome TEXT NOT NULL,
                especie TEXT NOT NULL,
                raca TEXT,
                FOREIGN KEY (tutor_id) REFERENCES tutores (id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS atendimentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_id INTEGER,
                servico TEXT NOT NULL,
                data_atendimento TEXT NOT NULL, -- YYYY-MM-DD
                hora_atendimento TEXT NOT NULL, -- HH:MM
                valor REAL NOT NULL,            -- Preço negociado (Arrecadação)
                status TEXT NOT NULL DEFAULT 'Agendado', -- 'Agendado' ou 'Concluído'
                FOREIGN KEY (pet_id) REFERENCES pets (id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gastos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                descricao TEXT NOT NULL, -- Ex: 'Compra de 5x Shampoos', 'Luz'
                valor REAL NOT NULL,     -- Custo/Despesa
                data_gasto TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos_estoque (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_produto TEXT NOT NULL,
                quantidade_atual INTEGER NOT NULL,
                quantidade_minima INTEGER NOT NULL DEFAULT 2,
                rendimento_por_atendimento INTEGER NOT NULL DEFAULT 5,
                atendimentos_realizados INTEGER NOT NULL DEFAULT 0 -- Contador para o gatilho de redução
            )
        """)

        cursor.execute("SELECT * FROM usuarios WHERE cargo = 'Administrador'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO usuarios (email, senha, cargo) VALUES (?, ?, ?)",
                           ("admin@petshop.com", "adm123", "Administrador"))

        self.conexao.commit()

    def injetar_dados_demonstracao(self):
        """Injeta dados fictícios para visualização dinâmica do portfólio"""
        cursor = self.conexao.cursor()
        data_hoje = datetime.now().strftime("%Y-%m-%d")
        data_amanha = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        cursor.execute("INSERT INTO usuarios (email, senha, cargo) VALUES (?, ?, ?)", 
                       ("demo@petshop.com", "123456", "Administrador"))

        pets_falsos = [
            ("Rex", "Cão", "Golden Retriever", "Carlos Silva", "27999991111"),
            ("Mel", "Cão", "Poodle", "Ana Oliveira", "27999992222"),
            ("Mia", "Gato", "Persa", "Maria Santos", "27999993333")
        ]
        cursor.executemany("INSERT INTO pets (nome, especie, raca, nome_dono, telefone_dono) VALUES (?,?,?,?,?)", pets_falsos)

        atendimentos_falsos = [
            (1, "Banho e Tosa", data_hoje, "14:00", 80.00, "Agendado"),
            (2, "Consulta Veterinária", data_hoje, "16:30", 150.00, "Agendado"),
            (3, "Banho Completo", data_amanha, "09:00", 60.00, "Agendado")
        ]
        cursor.executemany("INSERT INTO atendimentos (pet_id, servico, data_atendimento, hora_atendimento, valor, status) VALUES (?,?,?,?,?,?)", atendimentos_falsos)

        gastos_falsos = [
            ("Energia Elétrica", 320.00, data_hoje),
            ("Produtos de Limpeza", 85.50, data_hoje)
        ]
        cursor.executemany("INSERT INTO gastos (descricao, valor, data_gasto) VALUES (?,?,?)", gastos_falsos)

        produtos_falsos = [
            ("Shampoo Canino Neutro", 10, 2, 5),
            ("Condicionador Pelos Macios", 4, 1, 8),
            ("Perfume Pet Filhotes", 1, 2, 15) 
        ]
        cursor.executemany("INSERT INTO produtos_estoque (nome_produto, quantidade_atual, quantidade_minima, rendimento_por_atendimento) VALUES (?,?,?,?)", produtos_falsos)

        self.conexao.commit()
        print("[BANCO] Dados de demonstração injetados com sucesso.")

    def fechar_conexao(self):
        if self.conexao:
            self.conexao.close()