import requests
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class WebScraper:
    def __init__(self):
        self.product_data = []

    def extraer_datos_de_pagina(self, url):


        if 'eneba' in url:
            response = requests.get(url)
            if response.status_code == 200:
                # Configurar las opciones del navegador para el modo headless
                chrome_options = Options()
                chrome_options.add_argument('--headless')

                # Eliminar mensajes de deprecación
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--disable-software-rasterizer')
                chrome_options.add_argument('--mute-audio')
                chrome_options.add_argument('--disable-logging')
                chrome_options.add_argument('--log-level=3')

                # Inicializa un navegador web en modo headless (puedes usar Chrome, Firefox, etc.)
                driver = webdriver.Chrome(options=chrome_options)

                for pagina in range(1, 4):  # Cambia el rango para ajustar el número de páginas a leer - hay 500 paginas
                    pagina_url = f"{url}?page={pagina}"
                    print(f"Leyendo página {pagina}: {pagina_url}")
                    j=0

                    # Abre la página en el navegador
                    driver.get(pagina_url)

                    # Realiza scroll hacia abajo para cargar más contenido
                    for i in range(2):  # Realiza scroll 2 veces (ajusta según tus necesidades)
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 3);")
                        # Espera a que cargue el contenido (ajusta si es necesario)
                        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "footer")))

                    # Obtiene el HTML completo de la página después de cargar todo el contenido
                    page_source = driver.page_source

                    # Analiza el HTML con BeautifulSoup
                    soup = BeautifulSoup(page_source, 'lxml')

                    # Encuentra los enlaces a los artículos en la página de categoría
                    article_links = soup.find_all('a', class_='oSVLlh')

                    # Recorre cada enlace de artículo para extraer y mostrar las URLs
                    for link in article_links:
                        print(f"Leyendo URL {j + 1}: {'https://www.eneba.com'+link['href']}")
                        product_data = {
                            "COMPETENCIA": None,
                            "TITULO": None,
                            "PLATAFORMAS": None,
                            "MEJOR_PRECIO": None,
                            "PRECIO_ORIGINAL": None,
                            "PRECIO_SEMINUEVO": None,
                            "REBAJA": None,
                            "URL": None,
                        }
                        article_url = 'https://www.eneba.com' + link['href']
                        self.extraer_datos_de_articulo(article_url, product_data)
                        j +=1

                # Pausa antes de pasar a la siguiente página
                time.sleep(3)

                # Cierra el navegador
                driver.quit()

            else:
                print(f'Error al realizar la solicitud GET para la URL: {url}')

    def extraer_datos_de_articulo(self, url, product_data):

        if 'eneba' in url:
            response = requests.get(url)
            if response.status_code == 200:
                # Analizar el contenido HTML de la página
                soup = BeautifulSoup(response.text, 'lxml')

                product_data['COMPETENCIA'] = "ENEBA"
                product_data['URL'] = url

                # Encontrar el elemento <h1> con la clase "C68dpx"
                nombre_element = soup.find('h1', class_='C68dpx')
                if nombre_element:
                    product_data['TITULO'] = nombre_element.text

                # Encontrar el elemento con la clase "L5ErLT" que contiene el precio
                precio_element = soup.find('span', class_='L5ErLT')
                if precio_element:
                    product_data['MEJOR_PRECIO'] = precio_element.text.replace("€", "").strip()

                # Encontrar el div de plataformas
                div_element = soup.find('div', class_='onFZLe')
                if div_element:
                    li_elements = div_element.find_all('li')
                    product_data['PLATAFORMAS'] = [li.text for li in li_elements]

                # Encontrar el div que contiene la lista de idiomas
                idiomas_div = soup.find('div', class_='URplpg', string='Idiomas')
                if idiomas_div:
                    idiomas_list = idiomas_div.find_next('ul', class_='r1iAKt')
                    li_elements = idiomas_list.find_all('li')
                    product_data['IDIOMAS'] = [li.text for li in li_elements]

                # Encontrar el precio original y el descuento
                precio_original_element = soup.find('div', class_='gcTFLF')
                if precio_original_element:
                    product_data['PRECIO_ORIGINAL'] = precio_original_element.find('span', class_='L5ErLT').text
                else:
                    product_data['PRECIO_ORIGINAL'] = 0

                descuento_element = soup.find('div', class_='MjI1ZB')
                if descuento_element:
                    product_data['REBAJA'] = descuento_element.text.strip()
                else:
                    product_data['REBAJA'] = 0

                self.product_data.append(product_data)
            else:
                print(f'Error al realizar la solicitud GET para la URL: {url}')
        
        else:
            print("No se encuentra la URL")

    def mostrar_datos(self):
        for producto in self.product_data:
            print("Competencia:", producto['COMPETENCIA'])
            print("Título:", producto['TITULO'])
            print("Plataformas:", producto['PLATAFORMAS'])
            print("Mejor Precio:", producto['MEJOR_PRECIO'])
            print("Precio Original:", producto['PRECIO_ORIGINAL'])
            print("Descuento:", producto['REBAJA'])
            print("URL:", producto['URL'])
            print("-----------------------------------")

if __name__ == '__main__':
    # Define la URL de la página de categoría que deseas rastrear
    categoria_url = 'https://www.eneba.com/es/store/games'

    # Crea una instancia de la clase WebScraper
    scraper = WebScraper()

    # Llama a la función para extraer datos de la página de categoría
    scraper.extraer_datos_de_pagina(categoria_url)

    # Muestra los datos
    scraper.mostrar_datos()
