from dotenv import load_dotenv
import os
from pathlib import Path

from playwright.sync_api import Locator, Page, sync_playwright

load_dotenv()

is_menu_present: bool = True
user_email: str = str(os.getenv("USER_EMAIL"))
user_password: str = str(os.getenv("USER_PASSWORD"))
path_to_download: str = f"{Path.home()}/Desktop"
unidade_consumidora: str = ""

def is_modal_open(modal: Locator):
    return modal.count() > 0 and modal.is_visible()

if is_menu_present:
    from menu import show_menu, unidade_consumidoras

    uc_selected = show_menu()
    unidade_consumidora: str = unidade_consumidoras[uc_selected - 1]
else:
    unidade_consumidora: str = str(input("Insira a unidade consumidora: "))

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
    )
    
    page: Page = browser.new_page()
    
    # Abre a página de login do EDP
    page.goto("https://www.edponline.com.br/para-sua-casa/login")
    
    print("Página de login da EDP")

    # Processo de login
    page.get_by_placeholder("Digite seu e-mail").fill(user_email)
    page.get_by_placeholder("Digite sua senha").fill(user_password)
    page.locator("button").get_by_text("Aceitar todos os cookies",exact=True).click()
    page.locator("label").get_by_text("São Paulo", exact=True).check()
    page.locator("button").get_by_text("Entrar", exact=True).click()
    print("Login efetuado")

    print("Páginas de selecionar as unidades consumidoras")
        
    div: Locator = page.locator("#grid-instalacoes")
    div.wait_for(state="attached", timeout=15000)
    print("div=", div.count())
    
    table: Locator = div.get_by_role("table")
    table.wait_for(state="attached", timeout=15000)
    print("table=", table.count())
    
    table_rows: Locator = table.locator("tr")
    print("table_rows=", table_rows.count())
    
    print("---")
    for i in range(table_rows.count()):
        row: Locator = table_rows.nth(i)
        
        # UC = Unidade consumidora
        link_uc: Locator = row.get_by_role("link", name=unidade_consumidora)
        print("link_uc=", link_uc.count())
        
        # CA = Contrato ativo
        cell_ca: Locator = row.locator("td").filter(has_text="CONTRATO ATIVO")
        print("cell_ca=", cell_ca.count())
        
        print("---")
        if link_uc.count() > 0 and cell_ca.count() > 0:
            print("Encontrou a unidade consumidora")
            link_uc.click()
            break

    print("Página da unidade consumidora selecionada")

    modal_alteracao_cadastral: Locator = page.locator("#modal-alteracao-cadastral")
    for tentativa in range(5):
        print(f"{tentativa + 1}° tentativa:", modal_alteracao_cadastral.count())
        if is_modal_open(modal_alteracao_cadastral):
            modal_alteracao_cadastral.locator("a").get_by_text("Mais tarde",exact=True).click()
            modal_alteracao_cadastral.wait_for(state="hidden", timeout=15000)
            print("Modal alteração cadastral fechado")
        page.wait_for_timeout(500)

    modal_pix_auto: Locator = page.locator("#modal-oferta-pix-automatico")
    for tentativa in range(5):
        print(f"{tentativa + 1}° tentativa:", modal_pix_auto.count())
        if is_modal_open(modal_pix_auto):        
            modal_pix_auto.locator("button").get_by_text("Agora não",exact=True).click()
            modal_pix_auto.wait_for(state="hidden", timeout=15000)
            print("Modal oferta pix automático fechado")
        page.wait_for_timeout(500)

    page.locator("#fast-menu-bt").locator('a').filter(has_text="Extrato e 2ª Via de Conta").click()
    
    print("Página extrato e 2º via de conta")
    
    modal_aviso: Locator = page.locator("#modal-aviso-impedimento")
    for tentativa in range(5):
        print(f"{tentativa + 1}° tentativa:", modal_aviso.count())
        if modal_aviso.count() > 0:
            modal_aviso.locator('button[data-dismiss="modal"]').click()
            modal_aviso.wait_for(state="hidden", timeout=15000)
            print("Modal aviso impedimento fechado")
        page.wait_for_timeout(500)

    modal_email: Locator = page.locator("#modal-conta-email")
    for tentativa in range(5):
        print(f"{tentativa + 1}° tentativa:", modal_email.count())
        if is_modal_open(modal_email):
            modal_email.locator("a").get_by_text("Não me cadastrar", exact=True).click()
            modal_email.wait_for(state="hidden", timeout=15000)
            print("Modal conta email fechado")
        page.wait_for_timeout(500)

    button: Locator = page.locator("button").filter(has_text="Ver mais faturas")
    while button.count() > 0 and button.is_visible():
        button.click()

    tab_content: Locator = page.locator("#extrato-de-contas").locator('div[class="tab-content"]')
    cards: Locator = tab_content.locator('div[class="row"]')
    print(f"Encontrou {cards.count()} faturas")
    
    for i in range(cards.count()):
        card: Locator = cards.nth(i)
        paragraph_vencida: Locator = card.locator("p", has_text="Vencida")
        paragraph_pendente: Locator = card.locator("p", has_text="Aguardando Pagamento")
        n_conta = 0
        if paragraph_vencida.count() > 0 or paragraph_pendente.count() > 0:
            print(f"A {i + 1}ª conta vencida ou pendente será baixada")
            
            # Abrir o modal da fatura
            card.locator('a').filter(has_text="Visualizar fatura").click()
            print("Abrindo o modal da fatura")
            
            # Localiza o box
            box_dados_fatura: Locator = page.locator('#box-dados-fatura')
            
            # Espera box ficar visivel
            box_dados_fatura.wait_for(state="attached")
                        
            # Processo de download
            with page.expect_download() as download_info:
                box_dados_fatura.locator("a", has_text="Baixar").click()

            download = download_info.value

            n_conta = n_conta + 1
            download.save_as(f"{path_to_download}/fatura_edp_luz_{unidade_consumidora}_{n_conta + 1}.pdf")
            print("Download concluído")
            
            # Localiza o modal
            modal_fatura: Locator = page.locator('div[class="modal fade show"]')
            
            # Fecha o modal
            modal_fatura.locator('i[data-dismiss="modal"]').click()
            print("Fechando o modal da fatura")
            
            # Espera modal fechar
            modal_fatura.wait_for(state="detached")
    
    input("Pressione ENTER para fechar o navegador...")

    browser.close()
