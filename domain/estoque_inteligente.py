class GerenciadorEstoqueInteligente:
    def __init__(self, banco):
        self.banco = banco

    def processar_consumo_por_atendimento(self, servico):
        """
        Verifica se o serviço prestado consome insumos de forma automática.
        Regra: Serviços que contêm 'Banho' afetam o estoque de Shampoo/Condicionador.
        """
        if "Banho" not in servico:
            return None

        cursor = self.banco.conexao.cursor()
        
        cursor.execute("SELECT id, nome_produto, quantidade_atual, quantidade_minima, rendimento_por_atendimento FROM produtos_estoque")
        produtos = cursor.fetchall()

        alertas_estoque_baixo = []

        for prod_id, nome, qtd_atual, qtd_min, rendimento in produtos:
            cursor.execute("SELECT COUNT(*) FROM atendimentos WHERE servico LIKE '%Banho%' AND status = 'Agendado'")
            total_banhos = cursor.fetchone()[0]

            if total_banhos > 0 and (total_banhos % rendimento == 0):
                nova_qtd = max(0, qtd_atual - 1)
                
                cursor.execute("""
                    UPDATE produtos_estoque 
                    SET quantidade_atual = ? 
                    WHERE id = ?
                """, (nova_qtd, prod_id))
                
                print(f"[ESTOQUE] Inteligência: 1 unidade de '{nome}' foi consumida automaticamente após {rendimento} banhos.")
                
                if nova_qtd <= qtd_min:
                    alertas_estoque_baixo.append(f"⚠️ {nome} atingiu o nível crítico! Restam apenas {nova_qtd} unidades.")

        self.banco.conexao.commit()
        return alertas_estoque_baixo