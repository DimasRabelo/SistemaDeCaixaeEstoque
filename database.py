import sqlite3
import os

def inicializar_banco():
    # Nome do arquivo do banco
    nome_banco = 'adega.db'
    
    # Conecta ao banco de dados
    conexao = sqlite3.connect(nome_banco)
    cursor = conexao.cursor()

    # Criando a tabela de produtos ATUALIZADA
    # Adicionamos: preco_fardo e unidades_por_fardo
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_custo REAL NOT NULL,
            preco_venda REAL NOT NULL,
            preco_fardo REAL,
            unidades_por_fardo INTEGER
        )
    ''')

    # Cria a tabela de vendas (Histórico)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_produto INTEGER,
            quantidade_vendida INTEGER,
            valor_pago REAL,
            tipo_venda TEXT, -- 'Unidade' ou 'Fardo'
            data_venda DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_produto) REFERENCES produtos (id)
        )
    ''')

    conexao.commit()
    conexao.close()
    print("Sucesso: Banco de dados atualizado para suportar Fardos!")

if __name__ == "__main__":
    # DICA: Se você quiser garantir que as colunas novas apareçam, 
    # apague o arquivo adega.db antigo da pasta antes de rodar este código.
    inicializar_banco()