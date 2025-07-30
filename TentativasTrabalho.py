from pysat.solvers import Glucose3
from itertools import combinations
import random

# Variáveis globais
proposicoes = {}
valor_proposicao_inicial = 1
estado_final = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]


def get_proposicao(passo, linha, coluna, valor):
    """Mapeia proposições para variáveis inteiras únicas"""
    global valor_proposicao_inicial
    aux = f"{passo}_P_{linha}_{coluna}_{valor}"
    if aux not in proposicoes:
        proposicoes[aux] = valor_proposicao_inicial
        valor_proposicao_inicial += 1
    return proposicoes[aux]


def get_acao(passo, acao):
    """Mapeia ações para variáveis inteiras únicas"""
    global valor_proposicao_inicial
    aux = f"{passo}_A_{acao}"
    if aux not in proposicoes:
        proposicoes[aux] = valor_proposicao_inicial
        valor_proposicao_inicial += 1
    return proposicoes[aux]


def mostrar_puzzle(puzzle, titulo=""):
    """Exibe o puzzle de forma visual"""
    if titulo:
        print(f"\n{titulo}")
    print("+" + "---+" * 3)
    for linha in puzzle:
        print("|", end="")
        for valor in linha:
            print(f" {valor if valor != 0 else ' '} |", end="")
        print("\n+" + "---+" * 3)


def gerar_estado_inicial(passos=20):
    """Gera um estado inicial válido a partir do estado final"""
    estado = [linha[:] for linha in estado_final]
    vazio_linha, vazio_coluna = 0, 0

    movimentos = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}

    for _ in range(passos):
        mov_validos = []
        for acao, (dl, dc) in movimentos.items():
            nl, nc = vazio_linha + dl, vazio_coluna + dc
            if 0 <= nl < 3 and 0 <= nc < 3:
                mov_validos.append(acao)

        if not mov_validos:
            break

        acao = random.choice(mov_validos)
        dl, dc = movimentos[acao]
        nl, nc = vazio_linha + dl, vazio_coluna + dc

        estado[vazio_linha][vazio_coluna], estado[nl][nc] = estado[nl][nc], estado[vazio_linha][vazio_coluna]
        vazio_linha, vazio_coluna = nl, nc

    return estado


def eh_soluvel(puzzle):
    """Verifica se o puzzle tem solução"""
    lista = [puzzle[i][j] for i in range(3) for j in range(3) if puzzle[i][j] != 0]
    inversoes = 0

    for i in range(len(lista)):
        for j in range(i + 1, len(lista)):
            if lista[i] > lista[j]:
                inversoes += 1

    return inversoes % 2 == 0


def regras_de_estado(solver, passo):
    """Adiciona regras sobre a configuração do tabuleiro"""
    for linha in range(3):
        for coluna in range(3):
            # Cada célula deve conter exatamente um valor
            clausula = [get_proposicao(passo, linha, coluna, valor) for valor in range(9)]
            solver.add_clause(clausula)

            # Nenhuma célula pode ter mais de um valor
            for v1, v2 in combinations(range(9), 2):
                solver.add_clause([
                    -get_proposicao(passo, linha, coluna, v1),
                    -get_proposicao(passo, linha, coluna, v2)
                ])

    for valor in range(9):
        # Cada valor deve aparecer em exatamente uma célula
        clausula = []
        for linha in range(3):
            for coluna in range(3):
                clausula.append(get_proposicao(passo, linha, coluna, valor))
        solver.add_clause(clausula)


def regras_de_acao(solver, passo):
    """Define regras sobre as ações possíveis"""
    acoes = ['U', 'D', 'L', 'R']
    vars_acao = [get_acao(passo, acao) for acao in acoes]

    # Pelo menos uma ação deve ser selecionada
    solver.add_clause(vars_acao)

    # No máximo uma ação por passo
    for a1, a2 in combinations(vars_acao, 2):
        solver.add_clause([-a1, -a2])


def regras_de_transicao(solver, passo):
    """Define como o tabuleiro muda entre passos"""
    movimentos = {
        'U': (-1, 0),  # Cima
        'D': (1, 0),  # Baixo
        'L': (0, -1),  # Esquerda
        'R': (0, 1)  # Direita
    }

    # Para cada possível movimento
    for acao, (dl, dc) in movimentos.items():
        acao_var = get_acao(passo, acao)

        # Para cada posição do 0
        for l in range(3):
            for c in range(3):
                zero_atual = get_proposicao(passo, l, c, 0)
                nl, nc = l + dl, c + dc  # Nova posição do 0

                if 0 <= nl < 3 and 0 <= nc < 3:
                    # Para cada possível peça que pode ser movida
                    for valor in range(1, 9):
                        peca = get_proposicao(passo, nl, nc, valor)

                        # Se ação ocorre e 0 está em (l,c), então:
                        # 1. A peça vai para (l,c)
                        solver.add_clause([
                            -acao_var, -zero_atual, -peca,
                            get_proposicao(passo + 1, l, c, valor)
                        ])

                        # 2. O 0 vai para (nl,nc)
                        solver.add_clause([
                            -acao_var, -zero_atual, -peca,
                            get_proposicao(passo + 1, nl, nc, 0)
                        ])

                        # 3. Todas outras peças permanecem
                        for ol in range(3):
                            for oc in range(3):
                                if (ol, oc) not in [(l, c), (nl, nc)]:
                                    for v in range(9):
                                        solver.add_clause([
                                            -acao_var, -zero_atual, -peca,
                                            -get_proposicao(passo, ol, oc, v),
                                            get_proposicao(passo + 1, ol, oc, v)
                                        ])
                else:
                    # Movimento impossível - invalidar ação
                    solver.add_clause([-get_proposicao(passo, l, c, 0), -acao_var])


def exibir_solucao(modelo, passos_solucao):
    """Mostra a solução passo a passo"""
    if not modelo:
        print("Nenhuma solução encontrada")
        return

    mapa_invertido = {v: k for k, v in proposicoes.items()}
    solucao = []

    for prop in modelo:
        if prop > 0:
            solucao.append(mapa_invertido[prop])

    for passo in range(passos_solucao + 1):
        print(f"\nPasso {passo}:")
        if passo < passos_solucao:
            for s in solucao:
                if s.startswith(f"{passo}_A_"):
                    acao = s.split("_")[-1]
                    nome_acao = {'U': '↑', 'D': '↓', 'L': '←', 'R': '→'}
                    print(f"Movimento: {nome_acao[acao]}")
                    break

        puzzle = [[0 for _ in range(3)] for _ in range(3)]
        for s in solucao:
            if s.startswith(f"{passo}_P_"):
                partes = s.split("_")
                l, c, v = int(partes[2]), int(partes[3]), int(partes[4])
                puzzle[l][c] = v
        mostrar_puzzle(puzzle)


def resolver_puzzle(puzzle_inicial, max_passos=2000):
    """Encontra a solução com o menor número de passos"""
    for passos in range(1, max_passos + 1):
        solver = Glucose3()
        proposicoes.clear()
        global valor_proposicao_inicial
        valor_proposicao_inicial = 1

        # Adicionar regras para todos os passos
        for passo in range(passos):
            regras_de_estado(solver, passo)
            regras_de_acao(solver, passo)
            regras_de_transicao(solver, passo)

        # Estado final também precisa de regras
        regras_de_estado(solver, passos)

        # Adicionar estado inicial
        for l in range(3):
            for c in range(3):
                solver.add_clause([get_proposicao(0, l, c, puzzle_inicial[l][c])])

        # Adicionar estado final desejado
        for l in range(3):
            for c in range(3):
                solver.add_clause([get_proposicao(passos, l, c, estado_final[l][c])])

        if solver.solve():
            modelo = solver.get_model()
            print(f"\nSolução encontrada em {passos} movimentos:")
            exibir_solucao(modelo, passos)
            return True

    print(f"\nNão foi encontrada solução em {max_passos} passos")
    return False


def main():
    """Função principal"""
    # Gera um estado inicial válido ou usa o fornecido
    usar_exemplo = input("Usar puzzle de exemplo? (s/n): ").lower() == 's'

    if usar_exemplo:
        puzzle = [
            [1, 2, 3],
            [8, 0, 4],
            [7, 6, 5]
        ]
    else:
        while True:
            puzzle = gerar_estado_inicial(random.randint(15, 25))
            if eh_soluvel(puzzle):
                break

    print("\nEstado Inicial:")
    mostrar_puzzle(puzzle)
    print("\nEstado Final:")
    mostrar_puzzle(estado_final)

    resolver_puzzle(puzzle)


if __name__ == "__main__":
    main()