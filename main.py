import customtkinter as ctk
from tkinter import messagebox
from funcoes import *
from datetime import date, datetime
import sys, os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class Aplicativo(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Adega do Dimas - Gestão Completa")
        self.geometry("1200x900")
        self.after(10, self.withdraw)
        self.usuario_atual, self.nivel_acesso = None, None
        self.carrinho, self.pagamentos_venda = [], []
        self.after(100, self.abrir_login)

    # --- TRATAMENTO E MÁSCARAS ---
    def formatar_data_brasil(self, event):
        widget = event.widget
        if event.keysym == "BackSpace": return
        texto = "".join(filter(str.isdigit, widget.get()))
        novo = ""
        for i, char in enumerate(texto[:8]):
            if i == 2 or i == 4: novo += "/"
            novo += char
        widget.delete(0, 'end'); widget.insert(0, novo)

    def data_br_para_sql(self, data_br):
        try:
            d, m, a = data_br.split("/")
            return f"{a}-{m}-{d}"
        except: return date.today().strftime('%Y-%m-%d')

    def formatar_moeda_dinamico(self, event):
        widget = event.widget
        digitos = "".join(filter(str.isdigit, widget.get()))
        if not digitos: return
        v_float = float(digitos) / 100
        widget.delete(0, 'end'); widget.insert(0, f"{v_float:.2f}")

    # --- SEGURANÇA (MENSAGEM AO SAIR) ---
    def logout(self):
        if messagebox.askyesno("Sair", "Deseja realmente encerrar a sessão atual?"):
            os.execl(sys.executable, sys.executable, *sys.argv)

    # --- LOGIN ---
    def abrir_login(self):
        self.login_win = ctk.CTkToplevel(self); self.login_win.title("Acesso Dimtech"); self.login_win.geometry("400x380")
        self.login_win.attributes("-topmost", True); self.login_win.protocol("WM_DELETE_WINDOW", self.quit)
        ctk.CTkLabel(self.login_win, text="ADEGA DO OH RAÇA", font=("Arial", 20, "bold")).pack(pady=20)
        ctk.CTkLabel(self.login_win, text="Por favor, identifique-se:").pack()
        
        # --- AJUSTE: LOGIN COM COMBOBOX ---
        users = [u[2] for u in listar_usuarios()]
        self.en_user = ctk.CTkComboBox(self.login_win, values=users, width=250)
        self.en_user.pack(pady=10)
        if "admin" in users: self.en_user.set("admin")
        
        self.en_pass = ctk.CTkEntry(self.login_win, placeholder_text="Senha", placeholder_text_color="#a9a9a9", show="*", width=250); self.en_pass.pack(pady=10)
        self.en_pass.bind("<Return>", lambda e: self.tentar_login())
        self.lbl_erro = ctk.CTkLabel(self.login_win, text="", text_color="red"); self.lbl_erro.pack(pady=5)
        ctk.CTkButton(self.login_win, text="ENTRAR", command=self.tentar_login, width=250, height=40).pack(pady=10)
        self.after(200, lambda: self.en_pass.focus_set())

    def tentar_login(self):
        u, s = self.en_user.get(), self.en_pass.get(); d = verificar_login(u, s)
        if d: self.usuario_atual, self.nivel_acesso = d['nome'], d['nivel']; self.login_win.destroy(); self.montar_sistema(); self.aplicar_restricoes()
        else: self.lbl_erro.configure(text="Usuário ou senha incorretos!"); self.en_pass.delete(0, 'end')

    def montar_sistema(self):
        f = ctk.CTkFrame(self, fg_color="transparent"); f.pack(fill="x", padx=15, pady=(10, 0))
        ctk.CTkLabel(f, text=f"👤 Logado como: {self.usuario_atual}", font=("Arial", 14, "bold"), text_color="#32CD32").pack(side="left")
        ctk.CTkButton(f, text="SAIR / TROCAR USUÁRIO", width=180, height=32, fg_color="#A52A2A", command=self.logout).pack(side="right")
        self.tabview = ctk.CTkTabview(self, width=1150, height=820, command=self.ao_trocar_aba); self.tabview.pack(padx=10, pady=10, expand=True, fill="both")
        for aba in ["Vender", "Cadastrar", "Estoque", "Relatório", "Ajustes", "Usuários"]: self.tabview.add(aba)
        self.configurar_aba_vender(); self.configurar_aba_cadastrar(); self.configurar_aba_estoque(); self.configurar_aba_relatorio(); self.configurar_aba_ajustes(); self.configurar_aba_usuarios() 
        self.carregar_dados(); self.deiconify() 

    def carregar_dados(self):
        try: self.atualizar_lista_estoque(); self.atualizar_relatorio(); self.atualizar_lista_usuarios()
        except: pass

    def ao_trocar_aba(self):
        aba = self.tabview.get()
        if aba == "Estoque": self.atualizar_lista_estoque()
        elif aba == "Relatório": self.atualizar_relatorio()
        elif aba == "Usuários": self.atualizar_lista_usuarios()

    def aplicar_restricoes(self):
        if self.nivel_acesso == "Admin": return
        try: [self.tabview.delete(a) for a in ["Relatório", "Ajustes", "Usuários"]]
        except: pass

    # --- ABA VENDER ---
    def configurar_aba_vender(self):
        tab = self.tabview.tab("Vender"); f_main = ctk.CTkFrame(tab, fg_color="transparent"); f_main.pack(expand=True, fill="both", padx=50)
        f_esq = ctk.CTkFrame(f_main, fg_color="transparent", width=450); f_esq.pack(side="left", padx=20, pady=10, fill="both", expand=True)
        ctk.CTkLabel(f_esq, text="CARRINHO DE COMPRAS", font=("Arial", 14, "bold"), text_color="orange").pack(pady=(5,0))
        self.txt_carro_visual = ctk.CTkTextbox(f_esq, width=430, font=("Courier New", 12), border_width=1, border_color="#555555"); self.txt_carro_visual.pack(pady=(0, 10), fill="both", expand=True)
        f_rem = ctk.CTkFrame(f_esq, fg_color="#333333", corner_radius=10, height=50); f_rem.pack(pady=5, padx=10, fill="x"); f_rem.pack_propagate(False)
        ctk.CTkLabel(f_rem, text="Nº:").pack(side="left", padx=(10, 2))
        self.en_rem_idx = ctk.CTkEntry(f_rem, width=40, justify="center"); self.en_rem_idx.pack(side="left", padx=2)
        ctk.CTkButton(f_rem, text="REMOVER", fg_color="#A52A2A", width=80, font=("Arial", 12, "bold"), command=self.remover_item_carrinho).pack(side="left", padx=5)
        ctk.CTkLabel(f_rem, text="|", text_color="gray").pack(side="left", padx=5)
        self.tp_venda = ctk.CTkSegmentedButton(f_rem, values=["Unidade", "Fardo", "Caixa"], width=250, height=32, font=("Arial", 12, "bold")); self.tp_venda.set("Unidade"); self.tp_venda.pack(side="left", padx=10)
        ctk.CTkLabel(f_esq, text="ADICIONAR PRODUTO", font=("Arial", 16, "bold")).pack(pady=(10, 2))
        self.en_busca = ctk.CTkEntry(f_esq, placeholder_text="Nome ou Bipar ou Digitar Código...", width=350); self.en_busca.pack(pady=2); self.en_busca.bind("<KeyRelease>", self.filtrar_venda); self.en_busca.bind("<Return>", self.ao_pressionar_enter_venda)
        self.res_venda = ctk.CTkScrollableFrame(f_esq, width=320, height=50, label_text="Resultados", fg_color="#2b2b2b", border_width=2, border_color="orange"); self.res_venda.pack(pady=2, padx=10)
        f_q = ctk.CTkFrame(f_esq, fg_color="transparent"); f_q.pack(pady=2)
        self.en_qtd = ctk.CTkEntry(f_q, width=60, justify="center"); self.en_qtd.insert(0, "1"); self.en_qtd.pack(side="left", padx=5)
        ctk.CTkButton(f_q, text="ADICIONAR +", command=self.add_carro, fg_color="#1f538d", height=35, width=150, font=("Arial", 12, "bold")).pack(side="left", padx=5)
        f_dir = ctk.CTkFrame(f_main, fg_color="#2b2b2b", corner_radius=10, width=350); f_dir.pack(side="right", padx=20, pady=10, fill="y"); f_dir.pack_propagate(False) 
        self.lbl_tot = ctk.CTkLabel(f_dir, text="TOTAL: R$ 0,00", font=("Arial", 28, "bold"), text_color="yellow"); self.lbl_tot.pack(pady=10)
        self.lbl_troco = ctk.CTkLabel(f_dir, text="TROCO: R$ 0,00", font=("Arial", 18, "bold"), text_color="#32CD32"); self.lbl_troco.pack(pady=5)
        f_p = ctk.CTkFrame(f_dir, fg_color="transparent"); f_p.pack(pady=15)
        ctk.CTkButton(f_p, text="DINHEIRO", width=120, height=45, fg_color="#228B22", command=lambda: self.add_pag("Dinheiro")).grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkButton(f_p, text="PIX", width=120, height=45, fg_color="#008B8B", command=lambda: self.add_pag("PIX")).grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkButton(f_p, text="DÉBITO", width=120, height=45, fg_color="#4682B4", command=lambda: self.add_pag("Débito")).grid(row=1, column=0, padx=5, pady=5)
        ctk.CTkButton(f_p, text="CRÉDITO", width=120, height=45, fg_color="#6A5ACD", command=lambda: self.add_pag("Crédito")).grid(row=1, column=1, padx=5, pady=5)
        self.txt_pagos = ctk.CTkTextbox(f_dir, width=280, height=120); self.txt_pagos.pack(pady=10)
        self.btn_fim = ctk.CTkButton(f_dir, text="CONCLUIR VENDA", state="disabled", command=self.finalizar, fg_color="green", width=280, height=60, font=("Arial", 16, "bold")); self.btn_fim.pack(pady=10)
        ctk.CTkButton(f_dir, text="LIMPAR TUDO", command=self.limpar, fg_color="#A52A2A", width=280).pack()

    def add_carro(self):
        try:
            n, q, t = self.en_busca.get().strip(), int(self.en_qtd.get()), self.tp_venda.get()
            idp = buscar_id_por_nome_exato(n)
            
            if idp:
                p = buscar_produto_por_id(idp)
                # p[4] = Preço Venda Unitário | p[5] = Preço Fardo | p[6] = Unidades por fardo
                
                # --- LÓGICA DE PREÇO INFALÍVEL ---
                if t in ['Fardo', 'Caixa', 'Pacote']:
                    # 1. Se existir um preço de fardo cadastrado (maior que zero), usa ele
                    if p[5] and p[5] > 0:
                        preco_aplicado = p[5]
                    else:
                        # 2. Se não houver preço de fardo, calcula: Unitário * Qtd no Fardo
                        unidades = p[6] if p[6] and p[6] > 0 else 1
                        preco_aplicado = p[4] * unidades
                else:
                    # 3. Venda por unidade simples
                    preco_aplicado = p[4]

                # Verifica se o item já existe no carrinho para somar
                ex = next((i for i in self.carrinho if i['id'] == idp and i['tipo'] == t), None)
                if ex:
                    ex['qtd'] += q
                    ex['sub'] = ex['qtd'] * ex['unit']
                else:
                    self.carrinho.append({
                        'id': idp, 
                        'nome': n, 
                        'qtd': q, 
                        'tipo': t, 
                        'unit': preco_aplicado, 
                        'sub': preco_aplicado * q
                    })
                
                self.up_carro_visual()
                self.calc_venda()
                
                # Limpeza e foco
                self.en_busca.delete(0, 'end')
                self.en_qtd.delete(0, 'end')
                self.en_qtd.insert(0, "1")
                self.en_busca.focus_set()
        except Exception as e:
            print(f"Erro no cálculo do fardo: {e}")
    def remover_item_carrinho(self):
        try:
            idx = int(self.en_rem_idx.get()) - 1
            if 0 <= idx < len(self.carrinho):
                item = self.carrinho[idx]
                per = f"Produto: {item['nome']}\nQtd atual: {item['qtd']}\n\n• OK p/ apagar TUDO\n• Ou digite a qtd a retirar:"
                res = ctk.CTkInputDialog(text=per, title="Remover").get_input()
                if res is None: return
                if res.strip() == "": self.carrinho.pop(idx)
                elif res.isdigit():
                    q = int(res)
                    if q >= item['qtd']: self.carrinho.pop(idx)
                    else: item['qtd'] -= q; item['sub'] = item['qtd'] * item['unit']
                self.up_carro_visual(); self.calc_venda(); self.en_rem_idx.delete(0, 'end')
        except: pass

    def add_pag(self, forma):
        self.win_pag = ctk.CTkToplevel(self)
        self.win_pag.title(f"Pagamento: {forma}"); self.win_pag.geometry("350x250"); self.win_pag.attributes("-topmost", True)
        self.after(200, lambda: self.win_pag.grab_set())
        ctk.CTkLabel(self.win_pag, text=f"VALOR NO {forma.upper()}", font=("Arial", 16, "bold")).pack(pady=15)
        self.en_v_pag = ctk.CTkEntry(self.win_pag, width=200, placeholder_text="0.00", justify="center", font=("Arial", 20))
        self.en_v_pag.pack(pady=10)
        self.en_v_pag.bind("<KeyRelease>", self.formatar_moeda_dinamico)
        ctk.CTkButton(self.win_pag, text="CONFIRMAR", fg_color="green", height=40, command=lambda: self.confirmar_pag_final(forma)).pack(pady=20)
        self.win_pag.bind("<Return>", lambda e: self.confirmar_pag_final(forma)); self.after(300, lambda: self.en_v_pag.focus_set())

    def confirmar_pag_final(self, forma):
        try:
            val = float(self.en_v_pag.get())
            self.pagamentos_venda.append({'forma': forma, 'valor': val})
            self.txt_pagos.insert("end", f"{forma}: R$ {val:.2f}\n")
            self.calc_venda(); self.win_pag.destroy()
        except: pass

    def finalizar(self):
        try:
            total_venda = sum(item['sub'] for item in self.carrinho)
            total_pago = sum(p['valor'] for p in self.pagamentos_venda)
            troco = round(total_pago - total_venda, 2)
            forma = self.pagamentos_venda[0]['forma'] if self.pagamentos_venda else "Dinheiro"
            for i in self.carrinho: registrar_venda(i['id'], i['qtd'], i['tipo'], forma, self.usuario_atual)
            msg = "Venda concluída com sucesso!"; 
            if troco > 0: msg += f"\n\nTroco a devolver: R$ {troco:.2f}"
            messagebox.showinfo("Venda OK", msg); self.limpar(); self.carregar_dados() 
        except Exception as e: messagebox.showerror("Erro", str(e))

    # --- ABA ESTOQUE ---
    def configurar_aba_estoque(self):
        tab = self.tabview.tab("Estoque"); ctk.CTkLabel(tab, text="ESTOQUE DE PRODUTOS", font=("Arial", 22, "bold")).pack(pady=10)
        f_c = ctk.CTkFrame(tab, fg_color="transparent"); f_c.pack(fill="both", expand=True)
        f_l = ctk.CTkFrame(f_c, width=220, fg_color="transparent"); f_l.pack(side="left", padx=10, pady=10, fill="y"); f_l.pack_propagate(False) 
        ctk.CTkLabel(f_l, text="BUSCAR:", font=("Arial", 14, "bold")).pack()
        self.en_busca_est = ctk.CTkEntry(f_l, width=200, placeholder_text="Pesquisar..."); self.en_busca_est.pack(pady=5); self.en_busca_est.bind("<KeyRelease>", self.filtrar_estoque)
        ctk.CTkButton(f_l, text="LIMPAR", command=self.limpar_busca_estoque, width=180).pack(pady=2)
        self.res_estoque = ctk.CTkScrollableFrame(f_l, width=190, height=200); self.res_estoque.pack(pady=10)
        ctk.CTkLabel(f_l, text="ID Excluir:").pack()
        self.en_del = ctk.CTkEntry(f_l, width=80, justify="center", state="readonly"); self.en_del.pack(pady=5)
        ctk.CTkButton(f_l, text="EXCLUIR", fg_color="#A52A2A", command=self.acao_excluir, width=180).pack(pady=20)
        self.txt_est = ctk.CTkTextbox(f_c, font=("Courier New", 13), border_width=1); self.txt_est.pack(side="right", padx=10, pady=10, expand=True, fill="both")

    def acao_excluir(self):
        id_d = self.en_del.get()
        if id_d and messagebox.askyesno("Confirmar Exclusão", f"Deseja realmente REMOVER este produto?"):
            excluir_produto_db(id_d); self.atualizar_lista_estoque()
            self.en_del.configure(state='normal'); self.en_del.delete(0, 'end'); self.en_del.configure(state='readonly')

    def atualizar_lista_estoque(self):
        self.txt_est.delete("0.0", "end")
        
        # --- CABEÇALHO COM LARGURAS FIXAS ---
        # Definimos larguras fixas (ex: 4 para ID, 20 para PRODUTO)
        header = (
            f"{'ID':<4} | "
            f"{'PRODUTO':<20} | "
            f"{'CATEGORIA':<12} | "
            f"{'TOTAL':<6} | "
            f"{'UN/F':<5} | "
            f"{'VOL (F/UN)':<12} | "
            f"{'CUSTO':<9} | "
            f"{'VENDA':<9} | "
            f"{'V. FARDO':<9} | "
            f"{'COD. BARRAS'}\n"
        )
        
        # 135 traços para manter seu padrão
        separator = "-" * 135 + "\n"
        
        self.txt_est.insert("end", header)
        self.txt_est.insert("end", separator)
        
        # --- LOOP DE DADOS COM AS MESMAS LARGURAS ---
        for p in listar_produtos():
            # Mapeamento: p[0]=ID, p[1]=Nome, p[2]=Qtd, p[3]=Custo, p[4]=Venda, p[5]=PreçoFardo, p[6]=UnPorFardo, p[7]=Barras, p[8]=Categoria
            id_p      = p[0]
            nome      = (p[1][:20]) # Corta o nome se for maior que 20 para não quebrar a linha
            categoria = (p[8] or "Geral")[:12]
            qtd_total = p[2]
            un_vol    = p[6] if p[6] and p[6] > 0 else 1
            custo     = p[3]
            venda     = p[4]
            preco_f   = p[5] if p[5] else 0.00
            barras    = p[7] or "---"
            
            # Cálculo do Volume
            fardos = qtd_total // un_vol
            sobra  = qtd_total % un_vol
            txt_vol = f"{fardos}v/{sobra}u"
            
            # Montagem da linha respeitando exatamente o espaçamento do header
            linha = (
                f"{id_p:<4} | "
                f"{nome:<20} | "
                f"{categoria:<12} | "
                f"{qtd_total:<6} | "
                f"{un_vol:<5} | "
                f"{txt_vol:<12} | "
                f"{custo:>6.2f}    | " # Espaço extra para alinhar com o título CUSTO
                f"{venda:>6.2f}    | " # Espaço extra para alinhar com o título VENDA
                f"{preco_f:>7.2f}   | " # Espaço extra para alinhar com o título V. FARDO
                f"{barras}\n"
            )
            self.txt_est.insert("end", linha)
    # --- ABA RELATÓRIO ---
    def configurar_aba_relatorio(self):
        tab = self.tabview.tab("Relatório"); ctk.CTkLabel(tab, text="FECHAMENTO DE CAIXA", font=("Arial", 24, "bold")).pack(pady=10)
        f_filtros = ctk.CTkFrame(tab, fg_color="transparent"); f_filtros.pack(pady=5)
        # --- AJUSTE: FILTRO DE DATA COM MÁSCARA ---
        ctk.CTkLabel(f_filtros, text="De:").pack(side="left", padx=5)
        self.data_de = ctk.CTkEntry(f_filtros, width=110, placeholder_text="DD/MM/AAAA")
        self.data_de.insert(0, date.today().strftime('%d/%m/%Y'))
        self.data_de.pack(side="left", padx=5)
        self.data_de.bind("<KeyRelease>", self.formatar_data_brasil)
        
        ctk.CTkLabel(f_filtros, text="Até:").pack(side="left", padx=5)
        self.data_ate = ctk.CTkEntry(f_filtros, width=110, placeholder_text="DD/MM/AAAA")
        self.data_ate.insert(0, date.today().strftime('%d/%m/%Y'))
        self.data_ate.pack(side="left", padx=5)
        self.data_ate.bind("<KeyRelease>", self.formatar_data_brasil)
        
        self.lbl_horarios_info = ctk.CTkLabel(tab, text="Turno: --:--", font=("Arial", 16), text_color="gray"); self.lbl_horarios_info.pack()
        f_res = ctk.CTkFrame(tab, fg_color="#2b2b2b", corner_radius=15, border_width=1, border_color="#555555"); f_res.pack(pady=10, padx=20, fill="x")
        f_met = ctk.CTkFrame(f_res, fg_color="transparent"); f_met.pack(side="left", expand=True, pady=15, padx=30)
        self.lbl_rel_din = ctk.CTkLabel(f_met, text="Dinheiro: R$ 0,00", font=("Arial", 15)); self.lbl_rel_din.pack(anchor="w")
        self.lbl_rel_pix = ctk.CTkLabel(f_met, text="PIX: R$ 0,00", font=("Arial", 15)); self.lbl_rel_pix.pack(anchor="w")
        self.lbl_rel_deb = ctk.CTkLabel(f_met, text="Débito: R$ 0,00", font=("Arial", 15)); self.lbl_rel_deb.pack(anchor="w")
        self.lbl_rel_cre = ctk.CTkLabel(f_met, text="Crédito: R$ 0,00", font=("Arial", 15)); self.lbl_rel_cre.pack(anchor="w")
        f_t = ctk.CTkFrame(f_res, fg_color="transparent"); f_t.pack(side="right", expand=True, pady=15, padx=30)
        self.lbl_rel_geral = ctk.CTkLabel(f_t, text="FATURAMENTO: R$ 0,00", font=("Arial", 22, "bold"), text_color="yellow"); self.lbl_rel_geral.pack()
        self.lbl_rel_lucro = ctk.CTkLabel(f_t, text="LUCRO LÍQUIDO: R$ 0,00", font=("Arial", 22, "bold"), text_color="#00FF7F"); self.lbl_rel_lucro.pack()
        ctk.CTkButton(tab, text="🔄 FILTRAR E ATUALIZAR", command=lambda: self.atualizar_relatorio(True), height=45, width=300, font=("Arial", 14, "bold"), fg_color="#1f538d").pack(pady=10)
        self.txt_rel_itens = ctk.CTkTextbox(tab, width=1000, height=350, font=("Courier New", 12)); self.txt_rel_itens.pack(pady=10)

    def atualizar_relatorio(self, manual=False):
        try:
            ab, fe = obter_horarios(); self.lbl_horarios_info.configure(text=f"Turno: {ab} às {fe}")
            # --- AJUSTE: BUSCA POR PERÍODO ---
            d1, d2 = self.data_br_para_sql(self.data_de.get()) + " 00:00:00", self.data_br_para_sql(self.data_ate.get()) + " 23:59:59"
            din = resumo_vendas_por_metodo("Dinheiro", d1, d2); pix = resumo_vendas_por_metodo("PIX", d1, d2)
            deb = resumo_vendas_por_metodo("Débito", d1, d2); cre = resumo_vendas_por_metodo("Crédito", d1, d2)
            total = din + pix + deb + cre; luc = calcular_lucro_hoje(d1, d2)
            self.lbl_rel_din.configure(text=f"Dinheiro: R$ {din:.2f}"); self.lbl_rel_pix.configure(text=f"PIX: R$ {pix:.2f}")
            self.lbl_rel_deb.configure(text=f"Débito: R$ {deb:.2f}"); self.lbl_rel_cre.configure(text=f"Crédito: R$ {cre:.2f}")
            self.lbl_rel_geral.configure(text=f"FATURAMENTO: R$ {total:.2f}"); self.lbl_rel_lucro.configure(text=f"LUCRO: R$ {luc:.2f}")
            self.txt_rel_itens.delete("0.0", "end")
            self.txt_rel_itens.insert("end", f"VENDEDORES:\n" + "-"*45 + "\n")
            for v in resumo_vendas_por_vendedor(d1, d2): self.txt_rel_itens.insert("end", f"{v[0]:<25} | R$ {v[1]:>10.2f}\n")
            self.txt_rel_itens.insert("end", f"\nPRODUTOS:\n" + "-"*45 + "\n")
            for p in produtos_mais_vendidos_hoje(d1, d2): self.txt_rel_itens.insert("end", f"{p[0][:25]:<25} | {p[1]:<5} | {p[2]}\n")
            if manual: messagebox.showinfo("BI", "Dados filtrados com sucesso!")
        except Exception as e:
            if manual: messagebox.showerror("Erro", str(e))

    # --- ABA CADASTRAR ---
    def configurar_aba_cadastrar(self):
        tab = self.tabview.tab("Cadastrar"); tab.grid_columnconfigure(0, weight=2); tab.grid_columnconfigure(1, weight=1) 
        f_main = ctk.CTkFrame(tab, fg_color="transparent"); f_main.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)
        ctk.CTkLabel(f_main, text="GERENCIAR PRODUTOS", font=("Arial", 22, "bold")).pack(pady=5)
        ctk.CTkLabel(f_main, text="Código de Barras:").pack()
        self.en_cod = ctk.CTkEntry(f_main, width=400, placeholder_text="Bipe o código...", placeholder_text_color="#a9a9a9"); self.en_cod.pack(pady=2); self.en_cod.bind("<Return>", self.ao_bipar_no_cadastro)
        ctk.CTkLabel(f_main, text="ID p/ Editar (Vazio = Novo Produto):").pack()
        self.en_id = ctk.CTkEntry(f_main, width=400, placeholder_text="Digite ID ou Nome...", placeholder_text_color="#a9a9a9"); self.en_id.pack(pady=2); self.en_id.bind("<KeyRelease>", self.ao_digitar_no_id_cad)
        self.res_cad = ctk.CTkScrollableFrame(f_main, width=380, height=150, fg_color="#2b2b2b", border_width=2, border_color="orange")
        f_row1 = ctk.CTkFrame(f_main, fg_color="transparent"); f_row1.pack(fill="x", pady=2)
        sub_n = ctk.CTkFrame(f_row1, fg_color="transparent"); sub_c = ctk.CTkFrame(f_row1, fg_color="transparent"); sub_n.pack(side="left", expand=True); sub_c.pack(side="right", expand=True)
        ctk.CTkLabel(sub_n, text="Nome do Produto:").pack(); self.en_nome = ctk.CTkEntry(sub_n, width=195, placeholder_text="Ex: Skol 350ml", placeholder_text_color="#a9a9a9"); self.en_nome.pack()
        ctk.CTkLabel(sub_c, text="Categoria:").pack(); self.en_cat = ctk.CTkComboBox(sub_c, width=195, values=listar_categorias_unicas()); self.en_cat.set(""); self.en_cat.pack()
        ctk.CTkLabel(f_main, text="Estoque Total (Unid):").pack(); self.en_est = ctk.CTkEntry(f_main, width=400, placeholder_text="0", placeholder_text_color="#a9a9a9"); self.en_est.pack(pady=2)
        f_row2 = ctk.CTkFrame(f_main, fg_color="transparent"); f_row2.pack(fill="x", pady=5)
        s1 = ctk.CTkFrame(f_row2, fg_color="transparent"); s2 = ctk.CTkFrame(f_row2, fg_color="transparent"); s1.pack(side="left", expand=True); s2.pack(side="right", expand=True)
        ctk.CTkLabel(s1, text="Custo Unit.:").pack(); self.en_cus = ctk.CTkEntry(s1, width=195, placeholder_text="0.00", placeholder_text_color="#a9a9a9"); self.en_cus.pack(); self.en_cus.bind("<KeyRelease>", self.formatar_moeda_dinamico)
        ctk.CTkLabel(s2, text="Venda Unit.:").pack(); self.en_ven = ctk.CTkEntry(s2, width=195, placeholder_text="0.00", placeholder_text_color="#a9a9a9"); self.en_ven.pack(); self.en_ven.bind("<KeyRelease>", self.formatar_moeda_dinamico)
        ctk.CTkLabel(f_main, text="--- ATACADO / VOLUME ---", text_color="gray").pack(pady=2)
        f_row3 = ctk.CTkFrame(f_main, fg_color="transparent"); f_row3.pack(fill="x")
        s3 = ctk.CTkFrame(f_row3, fg_color="transparent"); s4 = ctk.CTkFrame(f_row3, fg_color="transparent"); s3.pack(side="left", expand=True); s4.pack(side="right", expand=True)
        ctk.CTkLabel(s3, text="Preço Fardo:").pack(); self.en_v_f = ctk.CTkEntry(s3, width=195, placeholder_text="0.00", placeholder_text_color="#a9a9a9"); self.en_v_f.pack(); self.en_v_f.bind("<KeyRelease>", self.formatar_moeda_dinamico)
        ctk.CTkLabel(s4, text="Unid. no Fardo:").pack(); self.en_q_f = ctk.CTkEntry(s4, width=195, placeholder_text="12", placeholder_text_color="#a9a9a9"); self.en_q_f.pack()
        f_btns = ctk.CTkFrame(f_main, fg_color="transparent"); f_btns.pack(pady=15)
        ctk.CTkButton(f_btns, text="SALVAR DADOS", command=self.salvar, width=220, fg_color="blue").pack(side="left", padx=10)
        ctk.CTkButton(f_btns, text="LIMPAR CAMPOS", command=self.limpar_cad, width=150, fg_color="#444444").pack(side="left", padx=10)
        f_calc = ctk.CTkFrame(tab, fg_color="#2b2b2b", corner_radius=15); f_calc.grid(row=0, column=1, sticky="nsew", padx=20, pady=100)
        ctk.CTkLabel(f_calc, text="🧮 CALCULADORA DE CUSTO", font=("Arial", 14, "bold"), text_color="orange").pack(pady=15)
        self.en_calc_val = ctk.CTkEntry(f_calc, placeholder_text="0.00"); self.en_calc_val.pack(pady=5); self.en_calc_val.bind("<KeyRelease>", self.formatar_moeda_dinamico)
        self.en_calc_fardos = ctk.CTkEntry(f_calc, placeholder_text="1"); self.en_calc_fardos.pack(pady=5)
        self.en_calc_un_por_f = ctk.CTkEntry(f_calc, placeholder_text="12"); self.en_calc_un_por_f.pack(pady=5)
        ctk.CTkButton(f_calc, text="CALCULAR E APLICAR", command=self.calcular_custo_fardo, fg_color="#0052cc").pack(pady=20)

    # --- ABA USUÁRIOS ---
    def configurar_aba_usuarios(self):
        tab = self.tabview.tab("Usuários"); f_main = ctk.CTkFrame(tab, fg_color="transparent"); f_main.pack(expand=True, fill="both", padx=20, pady=10)
        f_esq = ctk.CTkFrame(f_main, fg_color="transparent"); f_esq.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(f_esq, text="CADASTRAR NOVO FUNCIONÁRIO", font=("Arial", 18, "bold")).pack(pady=(10, 20))
        ctk.CTkLabel(f_esq, text="Nome Completo:").pack(); self.en_nome_user = ctk.CTkEntry(f_esq, width=300, placeholder_text="Nome...", placeholder_text_color="#a9a9a9"); self.en_nome_user.pack(pady=5)
        ctk.CTkLabel(f_esq, text="Usuário de Login:").pack(); self.en_login_user = ctk.CTkEntry(f_esq, width=300, placeholder_text="Login...", placeholder_text_color="#a9a9a9"); self.en_login_user.pack(pady=5)
        ctk.CTkLabel(f_esq, text="Senha de Acesso:").pack(); self.en_senha_user = ctk.CTkEntry(f_esq, show="*", width=300, placeholder_text="Senha...", placeholder_text_color="#a9a9a9"); self.en_senha_user.pack(pady=5)
        ctk.CTkLabel(f_esq, text="Nível de Permissão:").pack(); self.cb_nivel = ctk.CTkComboBox(f_esq, values=["Operador", "Admin"], width=300); self.cb_nivel.set("Operador"); self.cb_nivel.pack(pady=10)
        ctk.CTkButton(f_esq, text="SALVAR FUNCIONÁRIO", fg_color="green", height=40, command=self.acao_salvar_usuario).pack(pady=10)
        f_dir = ctk.CTkFrame(f_main, fg_color="#2b2b2b", corner_radius=10); f_dir.pack(side="right", fill="both", expand=True, padx=10)
        ctk.CTkLabel(f_dir, text="FUNCIONÁRIOS ATIVOS", font=("Arial", 14, "bold")).pack(pady=10)
        self.txt_lista_users = ctk.CTkTextbox(f_dir, width=400, height=300); self.txt_lista_users.pack(pady=10, padx=10)
        ctk.CTkLabel(f_dir, text="Digite o ID para remover:").pack()
        self.en_id_user_del = ctk.CTkEntry(f_dir, placeholder_text="ID", placeholder_text_color="#a9a9a9", width=120, justify="center"); self.en_id_user_del.pack(pady=5)
        ctk.CTkButton(f_dir, text="EXCLUIR USUÁRIO", fg_color="red", command=self.acao_excluir_usuario).pack(pady=(5, 15))

    def acao_excluir_usuario(self):
        id_u = self.en_id_user_del.get()
        if id_u and messagebox.askyesno("Confirmar", f"Deseja remover este funcionário do sistema?"):
            excluir_usuario_db(id_u); self.atualizar_lista_usuarios()

    # --- ABA AJUSTES ---
    def configurar_aba_ajustes(self):
        tab = self.tabview.tab("Ajustes"); f = ctk.CTkFrame(tab, fg_color="transparent"); f.pack(pady=50, expand=True)
        ctk.CTkLabel(f, text="CONFIGURAÇÕES DE TURNO", font=("Arial", 24, "bold")).pack(pady=20)
        ab, fe = obter_horarios()
        ctk.CTkLabel(f, text="Horário de Abertura (Ex: 05:00):").pack(); self.h_ab = ctk.CTkEntry(f, width=250, justify="center"); self.h_ab.insert(0, ab); self.h_ab.pack(pady=5)
        ctk.CTkLabel(f, text="Horário de Fechamento (Ex: 17:00):").pack(); self.h_fe = ctk.CTkEntry(f, width=250, justify="center"); self.h_fe.insert(0, fe); self.h_fe.pack(pady=5)
        ctk.CTkButton(f, text="SALVAR", command=self.acao_salvar_ajustes, fg_color="orange", width=250, height=45).pack(pady=40)

    # --- MÉTODOS DE APOIO ---
    def filtrar_venda(self, e):
        [w.destroy() for w in self.res_venda.winfo_children()]; n = self.en_busca.get().strip()
        if n and not n.isdigit():
            for p in buscar_produto_por_nome(n): ctk.CTkButton(self.res_venda, text=p[1], command=lambda np=p[1]: [self.en_busca.delete(0,'end'), self.en_busca.insert(0, np), self.add_carro()]).pack(fill="x")

    def ao_pressionar_enter_venda(self, e):
        t = self.en_busca.get().strip(); p = buscar_produto_por_codigo(t) if t.isdigit() else None
        if p: self.en_busca.delete(0, 'end'); self.en_busca.insert(0, p[1])
        self.add_carro()

    def up_carro_visual(self):
        self.txt_carro_visual.delete("1.0", "end"); pg = sum(p['valor'] for p in self.pagamentos_venda); ac = 0.0
        for i, item in enumerate(self.carrinho):
            ac += item['sub']; st = " [✓]" if pg >= (ac - 0.01) else ""
            self.txt_carro_visual.insert("end", f"{i+1} | {item['qtd']}x {item['nome']} | R$ {item['sub']:.2f}{st}\n")
            if st: self.txt_carro_visual.tag_add(f"p_{i}", f"{i+1}.0", f"{i+1}.end"); self.txt_carro_visual.tag_config(f"p_{i}", foreground="#32CD32")

    def calc_venda(self):
        tot, pg = sum(i['sub'] for i in self.carrinho), sum(p['valor'] for p in self.pagamentos_venda); dif = round(pg - tot, 2)
        self.lbl_tot.configure(text=f"TOTAL: R$ {tot:.2f}"); self.lbl_troco.configure(text=f"TROCO: R$ {max(0, dif):.2f}")
        self.btn_fim.configure(state="normal" if pg >= tot > 0 else "disabled")

    def finalizar(self):
        try:
            total_venda, total_pago = sum(item['sub'] for item in self.carrinho), sum(p['valor'] for p in self.pagamentos_venda)
            troco = round(total_pago - total_venda, 2)
            forma = self.pagamentos_venda[0]['forma'] if self.pagamentos_venda else "Dinheiro"
            for i in self.carrinho: registrar_venda(i['id'], i['qtd'], i['tipo'], forma, self.usuario_atual)
            msg = "Venda concluída com sucesso!"; 
            if troco > 0: msg += f"\n\nTroco a devolver: R$ {troco:.2f}"
            messagebox.showinfo("Venda OK", msg); self.limpar(); self.carregar_dados() 
        except Exception as e: messagebox.showerror("Erro", str(e))

    def limpar(self):
        self.carrinho, self.pagamentos_venda = [], []; self.txt_carro_visual.delete("1.0", "end"); self.txt_pagos.delete("1.0", "end"); self.calc_venda(); self.en_busca.focus_set()

    def filtrar_estoque(self, e):
        [w.destroy() for w in self.res_estoque.winfo_children()]; t = self.en_busca_est.get().strip()
        if t: [ctk.CTkButton(self.res_estoque, text=f"{p[1]}", command=lambda i=p[0]: [self.en_del.configure(state='normal'), self.en_del.delete(0,'end'), self.en_del.insert(0,i), self.en_del.configure(state='readonly')]).pack(fill="x") for p in (buscar_produto_por_nome(t) if not t.isdigit() else [buscar_produto_por_id(t)]) if p]

    def limpar_busca_estoque(self): self.en_busca_est.delete(0, 'end'); self.atualizar_lista_estoque()

    def ao_digitar_no_id_cad(self, event):
        termo = self.en_id.get().strip(); [w.destroy() for w in self.res_cad.winfo_children()]
        if len(termo) == 0: self.res_cad.place_forget(); return
        if termo.isdigit(): p = buscar_produto_por_id(termo); prods = [p] if p else []
        else: prods = buscar_produto_por_nome(termo)
        if prods:
            self.res_cad.place(x=20, y=170); self.res_cad.lift() 
            for p in prods: ctk.CTkButton(self.res_cad, text=f"{p[1]} (ID: {p[0]})", fg_color="transparent", anchor="w", height=25, hover_color="#1f538d", command=lambda idp=p[0]: self.selecionar_produto_cad(idp)).pack(fill="x", padx=5)
        else: self.res_cad.place_forget()

    def selecionar_produto_cad(self, i):
        p = buscar_produto_por_id(i); self.preencher_campos_cad(p); self.en_id.delete(0,'end'); self.en_id.insert(0, str(p[0])); self.res_cad.place_forget()

    def preencher_campos_cad(self, p):
        self.en_cod.delete(0,'end'); self.en_cod.insert(0, str(p[7] or "")); self.en_nome.delete(0,'end'); self.en_nome.insert(0, p[1]); self.en_est.delete(0,'end'); self.en_est.insert(0, str(p[2]))
        self.en_cus.delete(0,'end'); self.en_cus.insert(0, f"{p[3]:.2f}"); self.en_ven.delete(0,'end'); self.en_ven.insert(0, f"{p[4]:.2f}"); self.en_v_f.delete(0,'end'); self.en_v_f.insert(0, f"{p[5]:.2f}"); self.en_q_f.delete(0,'end'); self.en_q_f.insert(0, str(p[6])); self.en_cat.set(str(p[8] or ""))

    def calcular_custo_fardo(self):
        try:
            v, f, u = float(self.en_calc_val.get()), int(self.en_calc_fardos.get()), int(self.en_calc_un_por_f.get())
            c = v / (f * u); self.en_cus.delete(0,'end'); self.en_cus.insert(0, f"{c:.2f}"); self.en_est.delete(0,'end'); self.en_est.insert(0, str(f*u))
        except: pass

    def ao_bipar_no_cadastro(self, e):
        p = buscar_produto_por_codigo(self.en_cod.get())
        if p: self.en_id.delete(0,'end'); self.en_id.insert(0, str(p[0])); self.preencher_campos_cad(p)

    def salvar(self):
        try: adicionar_produto(self.en_nome.get(), int(self.en_est.get()), float(self.en_cus.get()), float(self.en_ven.get()), float(self.en_v_f.get() or 0), int(self.en_q_f.get() or 0), self.en_id.get() if self.en_id.get().isdigit() else None, self.en_cod.get(), self.en_cat.get()); messagebox.showinfo("OK", "Salvo!"); self.carregar_dados(); self.limpar_cad()
        except Exception as e: messagebox.showerror("Erro", str(e))

    def limpar_cad(self): [e.delete(0,'end') for e in [self.en_id, self.en_nome, self.en_est, self.en_cus, self.en_ven, self.en_cod, self.en_v_f, self.en_q_f]]

    def acao_salvar_usuario(self):
        adicionar_usuario(self.en_nome_user.get(), self.en_login_user.get(), self.en_senha_user.get(), self.cb_nivel.get()); self.atualizar_lista_usuarios()

    def atualizar_lista_usuarios(self):
        self.txt_lista_users.delete("0.0","end"); [self.txt_lista_users.insert("end", f"ID: {u[0]} | {u[1]} | {u[3]}\n") for u in listar_usuarios()]

    def acao_salvar_ajustes(self):
        configurar_horarios(self.h_ab.get(), self.h_fe.get()); self.atualizar_relatorio(); messagebox.showinfo("OK", "Horários atualizados!")

if __name__ == "__main__":
    app = Aplicativo(); app.mainloop()