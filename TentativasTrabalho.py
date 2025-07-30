from pysat.solvers import Glucose3
from itertools import combinations

'''
Teste do solver da video aula do thiago
g = Glucose3()
g.add_clause([-1, 2])
g.add_clause([-2, 3])
print(g.solve())
print(g.get_model())'''

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
    for l in range(3):
        for c in range(3):
            display_value = 0 if puzzle[l][c] == 0 else puzzle[l][c]
            print(f"{display_value:2}", end="  ")
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
                clausula = [get_proposicao(passo, linha, coluna, valor) for linha in range(3) for coluna in range(3)]
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

def exibir_solucao(modelo, passos_maximo):
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

    for passo in range(passos_maximo+1):
        print(f"\npasso: {passo}")
        if passo < passos_maximos:
            for i in solucao:
                if i.startswith(f"P_{passo}_A_"):
                    acao = i.split("_")[-1]
                    nome_da_acao = {'U': 'Cima', 'D': 'Baixo', 'L': 'Esquerda', 'R': 'Direita'}
                    print(nome_da_acao.get(acao, acao))
                    break

        puzzle = []

        for linha in range(3):
            nlinha = []
            for coluna in range(3):
                nlinha.append(-1)
            puzzle.append(nlinha)

        for i in solucao:
            if i.startswith(f"{passo}_P_"):
                acao = i.split("_")
                linha, coluna, valor = int(acao[2]), int(acao[3]), int(acao[4])
                puzzle[linha][coluna] = valor
        mostrar_puzzle(puzzle)

if __name__ == "__main__":
    passos_maximos = 20

    puzzle_inicial = [
        [3,2,1],
        [4,6,5],
        [8,7,0]
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


#Variavel utilizada salvar o estado de tentativa de resolução, ajudando na criação das fórmulas

'''
valor_peca = 1
# laço para criar as proposições com o 8-puzzle resolvido
for l in range(1,4):
    for c in range(1,4):
        for v in range(9):
            s = (f"{passo}_P_{l}_{c}_{v}")
            proposicoes[s] = valor_peca
            valor_peca += 1

# Mostrando as proposições
print("Proposições:")
for key, value in proposicoes.items():
    print(f"{key} : {value}")


peca_atual = 0
for l in range(3):
    linha = []
    for c in range(3):
        linha.append(peca_atual)
        peca_atual += 1
    puzzle.append(linha)


def mostrar_puzzle():
    print("Mostrando o Puzzle atual (matriz 3x3):")
    for l in range(3):
        for c in range(3):
            # Para o espaço vazio (geralmente representado por 0), exibe um '_'
            display_value = 0 if puzzle[l][c] == 0 else puzzle[l][c]
            # Usa f-string com formatação ':2' para alinhar os números
            print(f"{display_value:2}", end="  ")
        print() # Quebra de linha após cada linha do puzzle

mostrar_puzzle()


Anotações sobre o solver
g = Glucose3() # Instanciando o solver, g é o solver
g.add_clause([-1, 2]) # Aqui é uma clausola e ela é do estilo das clausolas da sala de aula (p V q V -n)
A proposição de cima significa (-p V q)
g.add_clause([-2, 3])
A proposição de cima significa (-q V r)

Exibindo o solver
print(g.solve())
print(g.get_model())
'''
