# Sistema de Gestão de Caixa e Estoque (PDV)

Este é um software desktop moderno e intuitivo desenvolvido em Python, projetado para automatizar o controle de vendas e estoque de qualquer tipo de comércio. Com uma interface em modo escuro (dark mode) elegante, o sistema oferece desde a gestão financeira diária até o controle detalhado de mercadorias.
## Funcionalidades Principais

    Frente de Caixa (PDV):

        Leitura de produtos via código de barras ou busca dinâmica por nome.

        Inteligência de auto-soma: Adiciona quantidades automaticamente se o item já estiver no carrinho.

        Múltiplas formas de pagamento integradas (Dinheiro, PIX, Débito, Crédito).

        Cálculo automático de troco exibido na confirmação da venda.

        Remoção inteligente de itens com opção de retirada total ou parcial.

    Controle de Estoque:

        Tabela organizada e alinhada com colunas de Custo, Venda e Preço de Fardo.

        Gestão por unidade ou volume (Fardos/Caixas) com cálculo automático de unidades restantes.

        Busca rápida de itens e sistema de exclusão com trava de segurança e confirmação.

    Relatórios e BI:

        Filtro de fechamento de caixa por período customizado (Data Inicial e Final).

        Cálculo automático de Lucro Líquido e Faturamento Geral.

        Resumo detalhado de vendas por método de pagamento e desempenho por vendedor.

    Segurança e Ajustes:

        Sistema de login com níveis de acesso diferenciados (Admin e Operador).

        Configuração dinâmica de horários de turno para o BI.

        Mensagens de confirmação para todas as ações críticas (excluir, sair, finalizar).

## Tecnologias Utilizadas

    Linguagem: Python 3.10+

    Interface Gráfica: CustomTkinter (UI moderna e responsiva)

    Banco de Dados: SQLite (Leve, rápido e embutido no sistema)

    Bibliotecas: tkinter, sqlite3, datetime

## Como Instalar e Rodar

    Clonar o repositório:
    Bash

    git clone https://github.com/DimasRabelo/SistemaDeCaixaeEstoque.git
    cd SistemaDeCaixaeEstoque

    Instalar dependências:
    Bash

    pip install customtkinter

    Executar o sistema:
    Bash

    python3 main.py

## Autor

Desenvolvido por Dimas Rabelo.
