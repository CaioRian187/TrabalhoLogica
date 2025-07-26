from pysat.solvers import Glucose3


'''g = Glucose3()
g.add_clause([-1, 2])
g.add_clause([-2, 3])
print(g.solve())
print(g.get_model())'''

puzzle = []
proposicoes = {}

passo = 1
#Variavel utilizada salvar o estado de tentativa de resolução, ajudando na criação das fórmulas


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

'''
Anotações sobre o solver
g = Glucose3() # Instanciando o solver, g é o solver
g.add_clause([-1, 2]) # Aqui é uma clausola e ela é do estilo das clausolas da sala de aula (p V q V -n)
A proposição de cima significa (-p V q)
g.add_clause([-2, 3])
A proposição de cima significa (-q V r)


print(g.solve())
print(g.get_model())
'''