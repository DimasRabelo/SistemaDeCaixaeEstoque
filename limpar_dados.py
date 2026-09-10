import sqlite3

def limpar_banco_de_dados():
    confirmacao = input("⚠️ TEM CERTEZA que deseja apagar todos os PRODUTOS e VENDAS? (digite 'sim' para confirmar): ")
    if confirmacao.strip().lower() != 'sim':
        print("Operação cancelada.")
        return

    try:
        conn = sqlite3.connect('adega.db')
        cursor = conn.cursor()

        # Limpa as tabelas de produtos e vendas
        cursor.execute("DELETE FROM produtos")
        cursor.execute("DELETE FROM vendas")
        cursor.execute("DELETE FROM pagamentos_venda")
        cursor.execute("DELETE FROM vendas_avulsas")

        # Reseta os contadores de ID automático
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('produtos', 'vendas', 'pagamentos_venda', 'vendas_avulsas')")

        conn.commit()
        conn.close()
        print("\n✅ Banco de dados limpo com sucesso!")
        print("Todos os produtos, vendas e históricos foram removidos.")
        print("Os usuários e configurações de turno foram preservados.\n")

    except Exception as e:
        print(f"\n❌ Erro ao limpar o banco de dados: {e}\n")

if __name__ == "__main__":
    limpar_banco_de_dados()