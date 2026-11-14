# APÓS PREENCHER ESTE ARQUIVO COM OS SEUS DADOS DA EDP
# MUDE O VALOR DA VARIÁVEL is_menu_present PARA True NO ARQUIVO automacao_edp.py
# TROQUE O NOME DESTE ARQUIVO PARA menu.py PARA USÁ-LO

from typing import Sequence

unidade_consumidoras: Sequence[str] = [
    "Insert_your_uc",
    "Insert_your_uc",
    "Insert_your_uc",
]

def show_menu() -> int:
    print("""AUTOMAÇÃO EDP

    Escolha o número correspondente a unidade consumidora (UC) e endereço
    1) UC: Insert_your_uc, Endereço: xxx

    2) UC: Insert_your_uc, Endereço: xxx

    3) UC: Insert_your_uc, Endereço: xxx
    """)
    
    uc_selected: int = int(input("UC: "))
    uc_validation(uc_selected)
    return uc_selected

# Verifica se UC não está no intervalo determinado pela lista
def uc_validation(uc_selected: int):
    while uc_selected < 1 or uc_selected > len(unidade_consumidoras):
        print("Ops, este valor está inválido, tente outra vez!")
        uc_selected = int(input("UC: "))
