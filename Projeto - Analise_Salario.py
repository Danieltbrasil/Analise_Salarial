from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import requests

# Abrindo o navegador
driver = webdriver.Chrome()

site = "https://remotar.com.br/"
# Abrindo o site
driver.get(site)
time.sleep(5)

# Esperando um anuncio aparecer e fechando o anuncio
while len(driver.find_elements(By.ID, 'clever_71053_stickyfooter_close')) < 1:
    time.sleep(1)
time.sleep(1)

driver.find_element(By.ID, 'clever_71053_stickyfooter_close').click()

# Clicando no botão "áreas de atuação"
driver.find_element(By.XPATH, '//*[@id="main-search-form"]/div[2]/div/div[1]/button').click()

# Fazendo a pesquisa de "Programação", depois "Outros" e "Somente vagas com salário disponível"
driver.find_element(By.XPATH, '//*[@id="main-search-form"]/div[2]/div/div[1]/div/div[2]/div/fieldset/div[15]/label/span').click()
time.sleep(2)
driver.find_element(By.XPATH, '//*[@id="main-search-form"]/div[2]/div/div[3]/button').click()
time.sleep(2)
driver.find_element(By.XPATH, '//*[@id="main-search-form"]/div[2]/div/div[3]/div/div[2]/div/div/div[1]/label').click()
time.sleep(2)
driver.find_element(By.XPATH, '//*[@id="main-search-form"]/div[2]/div/div[3]/div/div[2]/div/footer/button[2]').click()

# Esperando o anuncio e fechando ele
while len(driver.find_elements(By.ID, 'clever_71053_stickyfooter_close')) < 1:
    time.sleep(1)
time.sleep(1)

driver.find_element(By.ID, 'clever_71053_stickyfooter_close').click()

# Definindo função que trata o texto dos salários
def tratar_lista(lista):
    lista_tratada = []
    for item in lista:
        item = item.replace("$", "")
        item = item.replace("combinar", "")
        item = item.replace("a", "")
        item = item.replace(",", "")
        item = item.replace(".", "")
        item = item.replace("A", "")
        item = item.split()
        lista_tratada.append(item) 
    return lista_tratada


# Definindo função que pega a cotação do dolar
def cotacao_dolar():
    requisicao = requests.get("https://economia.awesomeapi.com.br/last/USD-BRL,EUR-BRL,BTC-BRL")
    requisicao_dic = requisicao.json()
    cotacao_dolar = requisicao_dic['USDBRL']['bid']
    dolar_num = cotacao_dolar.replace(".", "")
    dolar = int(dolar_num) / 10000
    return dolar

# Definindo função que pega a cotação do euro
def cotacao_euro():
    requisicao = requests.get("https://economia.awesomeapi.com.br/last/USD-BRL,EUR-BRL,BTC-BRL")
    requisicao_dic = requisicao.json()
    cotacao_euro = requisicao_dic['EURBRL']['bid']
    euro_num = cotacao_euro.replace(".", "")
    euro = int(euro_num) / 10000
    return euro

# Função que pega a cotação do Dólar canadense (CAD)
# def cotacao_cad(currency_code):
#     c = CurrencyRates()
#     cad = c.get_rate('CAD', currency_code)
#     return cad


# Definindo função que Transforma o salário de acordo com o tipo de moeda e frequencia mensal
def transformar_salario(lista_salario, tipo_salario):
    dolar = cotacao_dolar()
    euro = cotacao_euro()
    # cad = cotacao_cad('BRL')
    salario_transformado = []
    for i,salario in enumerate(lista_salario):
        if "USD" in tipo_salario[i]:
            salario = salario * dolar
        if "EUR" in tipo_salario[i]:
            salario = salario * euro
        # if "CAD" in tipo_salario[i]:
        #     salario = salario * cad
        if "Mensal" in tipo_salario[i]:
            salario *= 12
        salario_transformado.append(salario)
    return salario_transformado

salarios = []
tipos_moeda = []

# Pegando o salário da primeira página
salarios += driver.find_elements(By.CLASS_NAME, "info-salary-box")
tipos_moeda += driver.find_elements(By.CLASS_NAME, "salary-type")

# pegando o elemento que guarda outras possíveis páginas
pag = driver.find_element(By.CLASS_NAME, "search-pagination")

# Pegando o link das possíveis páginas
links = pag.find_elements(By.TAG_NAME, "a")

# Inicialização das listas fora do loop
moedas_lista = []
salario_lista = []

# Pegando o texto das moedas da primeira página
moedas_lista += [moeda.text for moeda in tipos_moeda]
salario_lista += [salario.text for salario in salarios]

# Percorrendo os links e extraindo cada um
for i in range(2, len(links) + 1):
    url = f"https://remotar.com.br/search/jobs?q=&c=13&s=1&p={i}"
    driver.get(url)
    time.sleep(4)
    
    # Atualização das listas em cada iteração do loop
    salarios = driver.find_elements(By.CLASS_NAME, "info-salary-box")
    tipos_moeda = driver.find_elements(By.CLASS_NAME, "salary-type")

    # Preenchimento das listas
    moedas_lista += [moeda.text for moeda in tipos_moeda]
    salario_lista += [salario.text for salario in salarios]

    # Tratando os salários coletados
    texto_do_salario = tratar_lista(salario_lista)

    # Pegando o menor dos dois salários fornecidos e transformando em inteiro 
    lista_de_salarios = [[int(numero) for numero in sublista] for sublista in texto_do_salario]


    salario_final = []
    # Tratando cada salário e transformando em numeros reais
    for item in lista_de_salarios:
        if item:
            salario_final.extend([item[0] / 100])

    salario_transformado = transformar_salario(salario_final, moedas_lista)

# Printando o resultado
media = sum(salario_transformado) / len(salario_transformado)
print(f"De acordo com as vagas disponíveis no site {site}, A media minima de salário de programador por ano é de R${int(media)} reais... e a media mensal é de R${int(media / 12)} reais")