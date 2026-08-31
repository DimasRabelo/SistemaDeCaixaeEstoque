import sqlite3

DB_NAME = 'adega.db'

def limpar_relatorio():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Apaga o histórico das vendas e pagamentos
        cursor.execute("DELETE FROM vendas;")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='vendas';")
        
        # Se a tabela de pagamentos existir, apaga também
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pagamentos_venda';")
        if cursor.fetchone():
            cursor.execute("DELETE FROM pagamentos_venda;")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='pagamentos_venda';")

        conn.commit()
        conn.close()
        print("✅ Histórico do relatório e vendas zerado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao limpar relatório: {e}")

if __name__ == "__main__":
    limpar_relatorio()