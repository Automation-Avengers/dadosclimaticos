from botcity.web import WebBot, Browser, By
from botcity.maestro import *
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import matplotlib.pyplot as plt
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By as SeleniumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from datetime import datetime, timedelta
import seaborn as sns

BotMaestroSDK.RAISE_NOT_CONNECTED = False

class Bot(WebBot):
    def action(self, execution=None):
        cidade = "São Paulo"
        
        # URL direta do site weather.com para Manaus
        self.browse("https://weather.com/pt-BR/clima/hoje/l/BRXX0043:1:BR")
        
        try:
            # Extração dos atributos climáticos
            temperatura_element = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((SeleniumBy.XPATH, "//span[@data-testid='TemperatureValue']"))
            )
            temperatura = temperatura_element.text

            umidade_element = self.find_element("span[data-testid='PercentageValue']", By.CSS_SELECTOR)
            umidade = umidade_element.text

            vento_element = self.find_element("span[data-testid='Wind']", By.CSS_SELECTOR)
            vento = vento_element.text

            descricao_element = self.find_element("div[data-testid='wxPhrase']", By.CSS_SELECTOR)
            descricao = descricao_element.text

            # Limpeza e conversão dos dados
            temperatura = int(temperatura.replace('°', ''))
            umidade = int(umidade.replace('%', ''))
            vento = vento.split()[0]  # Ex.: '11 km/h' => '11'

            print(f"Temperatura: {temperatura}°C, Umidade: {umidade}%, Vento: {vento} km/h, Condição: {descricao}")

            # Definir arquivo Excel e data atual
            arquivo_excel = 'dados_climaticos_weather.xlsx'
            data_atual = datetime.now().strftime('%Y-%m-%d')

            # Verifica se o arquivo Excel já existe
            if os.path.exists(arquivo_excel):
                # Se existir, carrega o DataFrame existente
                df_existente = pd.read_excel(arquivo_excel)

                # Adiciona novos dados
                novos_dados = {
                    'Cidade': [cidade],
                    'Data': [data_atual],
                    'Temperatura': [temperatura],
                    'Umidade': [umidade],
                    'Vento': [vento],
                    'Condição': [descricao]
                }
                df_novos_dados = pd.DataFrame(novos_dados)

                # Concatena os dados novos com os existentes
                df = pd.concat([df_existente, df_novos_dados], ignore_index=True)
            else:
                # Se não existir, cria um novo DataFrame
                dados = {
                    'Cidade': [cidade],
                    'Data': [data_atual],
                    'Temperatura': [temperatura],
                    'Umidade': [umidade],
                    'Vento': [vento],
                    'Condição': [descricao]
                }
                df = pd.DataFrame(dados)

            # Salvando no arquivo Excel
            df.to_excel(arquivo_excel, index=False)

            # Filtro dos últimos 7 dias para os gráficos
            df['Data'] = pd.to_datetime(df['Data'])
            ultima_semana = df[df['Data'] >= (datetime.now() - timedelta(days=7))]

            # Geração de gráficos para cada atributo (últimos 7 dias)
            plt.figure(figsize=(10,10))

            # Gráfico da temperatura
            plt.subplot(2, 2, 1)
            plt.plot(ultima_semana['Data'], ultima_semana['Temperatura'], marker='o', color='r', label='Temperatura')
            plt.title('Variação da Temperatura (últimos 7 dias)')
            plt.xlabel('Data')
            plt.ylabel('Temperatura (°C)')
            plt.xticks(rotation=45)
            plt.grid(True)
            plt.legend()

            # Gráfico da umidade
            plt.subplot(2, 2, 2)
            plt.plot(ultima_semana['Data'], ultima_semana['Umidade'], marker='o', color='b', label='Umidade')
            plt.title('Variação da Umidade (últimos 7 dias)')
            plt.xlabel('Data')
            plt.ylabel('Umidade (%)')
            plt.xticks(rotation=45)
            plt.grid(True)
            plt.legend()

            # Gráfico da velocidade do vento
            plt.subplot(2, 2, 3)
            plt.plot(ultima_semana['Data'], ultima_semana['Vento'], marker='o', color='g', label='Vento (km/h)')
            plt.title('Variação da Velocidade do Vento (últimos 7 dias)')
            plt.xlabel('Data')
            plt.ylabel('Velocidade do Vento (km/h)')
            plt.xticks(rotation=45)
            plt.grid(True)
            plt.legend()

            # Gráfico da condição climática (mudança de descrição ao longo dos dias)
            plt.subplot(2, 2, 4)
            plt.plot(ultima_semana['Data'], ultima_semana['Condição'], marker='o', color='y', label='Condição')
            plt.title('Condição Climática (últimos 7 dias)')
            plt.xlabel('Data')
            plt.xticks(rotation=45)
            plt.grid(True)
            plt.legend()

            plt.tight_layout()
            plt.show()

        except Exception as e:
            print(f"Erro ao coletar dados ou interagir com a página: {e}")

    def not_found(self, label):
        print(f"Elemento não encontrado: {label}")

def main():
    bot = Bot()
    bot.headless = False

    # Configurações do navegador Chrome
    chrome_options = Options()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36")

    bot.browser = Browser.CHROME
    bot.driver_path = ChromeDriverManager().install()
    bot.chrome_options = chrome_options.to_capabilities()

    # Iniciar navegador
    bot.start_browser()

    bot.action()
    bot.wait(3000)

    # Fechar navegador
    bot.stop_browser()

    file_path = 'dados_climaticos_weather.xlsx'  # Substitua pelo caminho correto
    df = pd.read_excel(file_path)

    cidade1 = 'Manaus'  # Substitua pelo nome da primeira cidade
    cidade2 = 'São Paulo'  # Substitua pelo nome da segunda cidade

    dados_cidade1 = df[df['Cidade'] == cidade1]
    dados_cidade2 = df[df['Cidade'] == cidade2]
    
    plt.figure(figsize=(10, 6))
    sns.lineplot(x='Data', y='Temperatura', data=dados_cidade1, label=cidade1)
    sns.lineplot(x='Data', y='Temperatura', data=dados_cidade2, label=cidade2)
 


    plt.title('Comparação de Temperaturas entre Cidades')
    plt.xlabel('Data')
    plt.ylabel('Temperatura (°C)')
    plt.legend()
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    main()
