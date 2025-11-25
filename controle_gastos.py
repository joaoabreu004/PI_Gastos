# -*- coding: utf-8 -*-
import sys
import csv
import json
import os
from datetime import datetime
from rich.console import Console
from rich.table import Table

sys.stdout.reconfigure(encoding='utf-8')

console = Console()
ARQUIVO_CSV = "gastos.csv"

class Transacao:
    def __init__(self, data, tipo, categoria, descricao, valor):
        self.data = data
        self.tipo = tipo.upper()
        self.categoria = categoria.title()
        self.descricao = descricao
        self.valor = float(valor)

class ControleFinanceiro:
    def __init__(self):
        self.transacoes = []
        self.carregar_dados()

    def carregar_dados(self):
        if not os.path.exists(ARQUIVO_CSV):
            return
        with open(ARQUIVO_CSV, newline="", encoding="utf-8") as arquivo:
            leitor = csv.DictReader(arquivo)
            for linha in leitor:
                self.transacoes.append(Transacao(
                    linha["data"],
                    linha["tipo"],
                    linha["categoria"],
                    linha["descricao"],
                    float(linha["valor"])
                ))

    def salvar_dados(self):
        with open(ARQUIVO_CSV, "w", newline="", encoding="utf-8") as arquivo:
            campos = ["data", "tipo", "categoria", "descricao", "valor"]
            escritor = csv.DictWriter(arquivo, fieldnames=campos)
            escritor.writeheader()
            for t in self.transacoes:
                escritor.writerow({
                    "data": t.data,
                    "tipo": t.tipo,
                    "categoria": t.categoria,
                    "descricao": t.descricao,
                    "valor": f"{t.valor:.2f}"
                })

    def registrar_transacao(self):
        try:
            data = input("Data (dd/mm/aaaa) [ENTER = hoje]: ").strip()
            if not data:
                data = datetime.now().strftime("%d/%m/%Y")
            tipo = input("Tipo (R = Receita / D = Despesa): ").strip().upper()
            if tipo not in ("R", "D"):
                console.print("[red]Tipo inválido! Digite R para receita ou D para despesa.[/red]")
                return

            categoria = input("Categoria (ex: alimentação, transporte, lazer): ").strip()
            descricao = input("Descrição: ").strip()
            valor = float(input("Valor (R$): ").replace(",", "."))

            nova = Transacao(data, tipo, categoria, descricao, valor)
            self.transacoes.append(nova)
            self.salvar_dados()

            console.print("[green]Transação registrada com sucesso![/green]\n")

        except ValueError:
            console.print("[red]Erro: valor inválido. Digite um número válido.[/red]\n")

    def listar_transacoes(self):
        if not self.transacoes:
            console.print("[yellow]Nenhuma transação registrada.[/yellow]\n")
            return

        tabela = Table(title="Histórico de Transações")
        tabela.add_column("Data", justify="center")
        tabela.add_column("Tipo")
        tabela.add_column("Categoria")
        tabela.add_column("Descrição")
        tabela.add_column("Valor (R$)", justify="right")

        for t in self.transacoes:
            cor = "green" if t.tipo == "R" else "red"
            tipo_str = "Receita" if t.tipo == "R" else "Despesa"
            tabela.add_row(
                t.data, tipo_str, t.categoria, t.descricao,
                f"[{cor}]{t.valor:.2f}[/{cor}]"
            )

        console.print(tabela)

    def calcular_saldo(self):
        saldo = sum(t.valor if t.tipo == "R" else -t.valor for t in self.transacoes)
        cor = "green" if saldo >= 0 else "red"
        console.print(f"\n[bold {cor}]Saldo atual: R$ {saldo:.2f}[/bold {cor}]\n")

    def resumo_por_categoria(self):
        if not self.transacoes:
            console.print("[yellow]Nenhum dado disponível para resumo.[/yellow]")
            return

        resumo = {}
        for t in self.transacoes:
            resumo.setdefault(t.categoria, 0)
            resumo[t.categoria] += t.valor if t.tipo == "R" else -t.valor

        tabela = Table(title="Resumo por Categoria")
        tabela.add_column("Categoria")
        tabela.add_column("Saldo (R$)", justify="right")

        for cat, valor in resumo.items():
            cor = "green" if valor >= 0 else "red"
            tabela.add_row(cat, f"[{cor}]{valor:.2f}[/{cor}]")

        console.print(tabela)

    def exportar_json(self):
        dados = [vars(t) for t in self.transacoes]
        nome = "gastos_exportados.json"

        with open(nome, "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=4)

        console.print(f"[green]Dados exportados com sucesso para '{nome}'.[/green]\n")

def menu():
    sistema = ControleFinanceiro()

    while True:
        console.print("\n[bold cyan]=== SISTEMA DE CONTROLE DE GASTOS PESSOAIS ===[/bold cyan]")
        console.print("1. Registrar transação")
        console.print("2. Listar transações")
        console.print("3. Consultar saldo atual")
        console.print("4. Resumo por categoria")
        console.print("5. Exportar dados para JSON")
        console.print("0. Sair")

        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == "1":
            sistema.registrar_transacao()
        elif opcao == "2":
            sistema.listar_transacoes()
        elif opcao == "3":
            sistema.calcular_saldo()
        elif opcao == "4":
            sistema.resumo_por_categoria()
        elif opcao == "5":
            sistema.exportar_json()
        elif opcao == "0":
            console.print("[blue]Encerrando o sistema... Até logo![/blue]")
            break
        else:
            console.print("[red]Opção inválida. Tente novamente.[/red]")

if __name__ == "__main__":
    menu()
