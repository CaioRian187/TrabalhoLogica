from pysat.solvers import Glucose3
from itertools import combinations

#variais globais
proposicoes = {}
valor_proposicao_inicial = 1
estado_final = [[1, 2 ,3],[4 ,5 ,6],[7, 8, 0]]

def get_proposicao(passo, linha, coluna, valor):
    global valor_proposicao_inicial
    aux = str(passo) + "_P_" + str(linha) + "_" + str(coluna) + "_" + str(valor)
    if aux not in proposicoes:
        proposicoes[aux] = valor_proposicao_inicial
        valor_proposicao_inicial += 1
    return proposicoes[aux]

def get_acao(passo, acao):
    global valor_proposicao_inicial
    aux = str(passo) + "_A_" + str(acao)
    if aux not in proposicoes:
        proposicoes[aux] = valor_proposicao_inicial
        valor_proposicao_inicial += 1
    return proposicoes[aux]

def mostrar_puzzle(puzzle):
    print("-"*13)
    for linha in range(3):
        print("|", end=" ")
        for coluna in range(3):
            valor_celula = puzzle[linha][coluna]
            if valor_celula == 0:
                valor_exibicao = 0
            else:
                valor_exibicao = valor_celula
            print(f"{valor_exibicao}", end=" | ")
        print("\n"+"-"*13)

def regras_de_estado(solver, passo):
    for linha in range(3):
        for coluna in range(3):
            clausula = [get_proposicao(passo, linha, coluna, valor) for valor in range(9)]
            solver.add_clause(clausula)
            for valor1 in range(9):
                for valor2 in range(valor1+1,9):
                    proposicao1 = get_proposicao(passo, linha, coluna, valor1)
                    proposicao2 = get_proposicao(passo, linha, coluna, valor2)
                    solver.add_clause([-proposicao1, -proposicao2])

    for valor in range(9):
        clausula = []
        for linha in range(3):
            for coluna in range(3):
                proposicao = get_proposicao(passo, linha, coluna, valor)
                clausula.append(proposicao)
        solver.add_clause(clausula)

def regras_de_acao(solver, passo):
    acoes = ['U','D','L','R']
    proposicao_acao = [get_acao(passo, acao) for acao in acoes]
    solver.add_clause(proposicao_acao)
    for acao1, acao2 in combinations(proposicao_acao, 2):
        solver.add_clause([-acao1, -acao2])

def regras_de_transicao(solver, passo):
    mapa_de_movimento = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}

    for linha in range(3):
        for coluna in range(3):
            for acao, (dlinha, dcoluna) in mapa_de_movimento.items():
                nlinha, ncoluna = linha + dlinha, coluna + dcoluna
                if 0<= nlinha < 3 and 0<= ncoluna < 3:
                    proposicao_acao = get_acao(passo, acao)
                    proposicao_vazio_atual = get_proposicao(passo, nlinha, ncoluna,0)
                    for valor in range(1,9):
                        proposicao_peca_atual = get_proposicao(passo, linha, coluna, valor)
                        proposicao_vazio_destino = get_proposicao(passo +1, linha, coluna, 0)
                        proposicao_peca_destino = get_proposicao(passo +1, nlinha, ncoluna, valor)
                        solver.add_clause([-proposicao_acao, -proposicao_vazio_atual, -proposicao_peca_atual, -proposicao_vazio_destino])
                        solver.add_clause([-proposicao_acao, -proposicao_vazio_atual, -proposicao_peca_atual, -proposicao_peca_destino])

            acoes_de_mover = []
            for acao, (dlinha, dcoluna) in mapa_de_movimento.items():
                nlinha, ncoluna = linha + dlinha, coluna + dcoluna
                if 0 <= nlinha < 3 and 0 <= ncoluna < 3:
                    acoes_de_mover.append((get_acao(passo, acao), get_proposicao(passo, nlinha, ncoluna, 0)))

            for valor in range(1,9):
                proposicao_peca_atual = get_proposicao(passo, linha, coluna, valor)
                proposicao_peca_avanca = get_proposicao(passo + 1, linha, coluna, valor)
                clausula = [-proposicao_peca_atual, proposicao_peca_avanca]
                for proposicao_acao, proposicao_vazio in acoes_de_mover:
                    clausula.append(proposicao_vazio)
                solver.add_clause(clausula)

def exibir_solucao(modelo, passos_solucao):
    if not modelo:
        print("o modelo de puzzle é invalido")
        return

    mapa_invertido = {}
    for chave, variavel in proposicoes.items():
        mapa_invertido[variavel] = chave

    solucao = []

    for proposicao in modelo:
        if proposicao > 0:
            aux = mapa_invertido[proposicao]
            solucao.append(aux)

    for passo in range(passos_solucao + 1):
        print(f"\npasso: {passo}")
        if passo < passos_solucao:
            for s in solucao:
                if s.startswith(f"{passo}_A_"):
                    acao = s.split("_")[-1]
                    nome_acao = {'U': 'Cima', 'D': 'Baixo', 'L': 'Esquerda', 'R': 'Direita'}
                    print(f"Açao: mover o '0' para {nome_acao.get(acao, acao)}")
                    break
        puzzle = []
        for linha in range(3):
            nlinha = []
            for coluna in range(3):
                nlinha.append(-1)
            puzzle.append(nlinha)

        for i in solucao:
            if i.startswith(f"{passo}_P_"):
                parte = i.split("_")
                linha, coluna, valor = int(parte[2]), int(parte[3]), int(parte[4])
                puzzle[linha][coluna] = valor
        mostrar_puzzle(puzzle)

if __name__ == "__main__":
    passos_maximos = 20

    puzzle_inicial = [
        [1,4,7],
        [2,5,0],
        [3,6,8]
    ]
    print("estado inicial do puzzle")
    mostrar_puzzle(puzzle_inicial)

    solucao_encontrada = False
    for i in range(1, passos_maximos + 1):
        print("\n"+"="*13)
        print(f"tentando encontrar a solução com {i} passos")
        print("="*13)

        solver = Glucose3()
        proposicoes.clear()
        valor_proposicao_inicial = 1

        for passo in range(i):
            regras_de_estado(solver, passo)
            regras_de_acao(solver, passo)
            regras_de_transicao(solver, passo)
        regras_de_estado(solver, i)

        for linha in range(3):
            for coluna in range(3):
                valor = puzzle_inicial[linha][coluna]
                solver.add_clause([get_proposicao(0, linha, coluna, valor)])

                valor_final = estado_final[linha][coluna]
                solver.add_clause([get_proposicao(i, linha, coluna, valor_final)])

        if solver.solve():
            print(f"solução encontrada com {i} passos")
            modelo = solver.get_model()
            exibir_solucao(modelo, i)
            solucao_encontrada = True
            break
        else:
            print(f"não encontrada com {i} passos")

    if not solucao_encontrada:
        print("não foi possivel encontrar uma solução com esse numero de passos fornecidos. (mude o numero de passos_maximos)")
