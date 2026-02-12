from funcoes import adicionar_produto, listar_produtos

# Testando adicionar uma cerveja
adicionar_produto("Cerveja Skol Lata", 50, 2.50, 4.50)

# Verificando se ela aparece na lista
print("Produtos no estoque:")
for p in listar_produtos():
    print(p)