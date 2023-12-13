import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import mysql.connector
import time
from selenium.common.exceptions import TimeoutException
from urllib.parse import urlparse, parse_qs



class WebScraper:
    def __init__(self, base_urls):
        self.base_urls = base_urls
        self.product_data = []
        self.paginasT = 1
        self.url2 = None
        self.url3 = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        self.setup_database()

    def setup_database(self):
        try:
            conexion = mysql.connector.connect(
                user='root',
                password='javi',
                host='localhost',
                database='bdmysql'
            )
            cursor = conexion.cursor()

            drop_table_query = "DROP TABLE IF EXISTS clase"
            cursor.execute(drop_table_query)

            # Crear la tabla si no existe
            create_table_query = """
            CREATE TABLE IF NOT EXISTS `clase` (
                `ID` int NOT NULL AUTO_INCREMENT,
                `COMPETENCIA` varchar(45) NOT NULL,
                `PRODUCTO` varchar(120) NOT NULL,
                `PLATAFORMAS` varchar(60) NOT NULL,
                `MEJOR_PRECIO` FLOAT NOT NULL,
                `PRECIO_ORIGINAL` FLOAT NOT NULL,
                `PRECIO_SEMINUEVO` FLOAT NOT NULL,
                `REBAJA` varchar(10) NOT NULL,
                `URL` varchar(330) NOT NULL,
                PRIMARY KEY (`ID`)
            )
            """
            cursor.execute(create_table_query)
            conexion.commit()

        except mysql.connector.Error as err:
            print(f'Error al conectar con la base de datos: {err}')

        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

    def setup_selenium(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--mute-audio')
        chrome_options.add_argument('--disable-logging')
        chrome_options.add_argument('--log-level=3')
        return webdriver.Chrome(options=chrome_options)

    def extraer_datos_de_pagina(self, urls):
        for url in urls:
            if 'eneba' in url:
                self.extraer_datos_eneba(url)
            elif 'instant-gaming' in url:
                self.extraer_datos_instant_gaming(url)
            else:
                print("No se lee la URL")

    def extraer_datos_eneba(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            driver = self.setup_selenium()

            pagina = 1
            while pagina <= 2: # 500 páginas
                pagina_url = f"{url}?page={pagina}"
                j = 0
                print("-----------------------------------------------------------------")
                print(f"Leyendo página {pagina}: {pagina_url} - URL TOTALES LEIDAS: {self.paginasT}")
                print("-----------------------------------------------------------------")
                pagina += 1
                driver.get(pagina_url)

                # Espera única para la carga de la página
                try:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 3);")
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "footer")))
                except TimeoutException:
                    print("Timeout al esperar la carga de la página.")
                    break

                
                    

                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'lxml')
                article_links = soup.find_all('a', class_='oSVLlh')

                for link in article_links:
                    print(f"Leyendo URL {j + 1}: {'https://www.eneba.com' + link['href']}")
                    product_data = {
                        "COMPETENCIA": None,
                        "PRODUCTO": None,
                        "PLATAFORMAS": None,
                        "MEJOR_PRECIO": None,
                        "PRECIO_ORIGINAL": None,
                        "PRECIO_SEMINUEVO": None,
                        "REBAJA": None,
                        "URL": None,
                    }
                    self.url2 = 'https://www.eneba.com' + link['href']
                    self.extraer_datos_de_articulo(product_data)
                    j += 1

                time.sleep(3)
                self.paginasT += 1

            driver.quit()
        else:
            print(f'Error al realizar la solicitud GET para la URL: {url}')

    def extraer_datos_instant_gaming(self, url):
        title_url_mapping = {}  # Diccionario para mapear títulos a URLs
        num_pages = 1
        max_pages_per_url = 10 # 4 Play - 173 PC - 32 XBOX - 10 SWITCH

        for page_number in range(1, max_pages_per_url + 1):
            url_page = f"{url}{page_number}"
            self.url3 = url_page # para despues cojer la plataforma
            r = requests.get(url_page, headers=self.headers)

            if r.status_code == 200:  
                data = r.text
                soup = BeautifulSoup(data, 'lxml')
                product_elements = soup.find_all('div', class_='item force-badge')
                # Verifica si no hay más productos en la página
                sorry_message = soup.find('div', class_='noresult-browse')
                if sorry_message:
                #    print(sorry_message.find('h3').text.strip())
                    print("No hay más datos de esta URL")
                    break
                print("-----------------------------------------------------------------")
                print(f"Leyendo página {num_pages}: {url_page} - URL TOTALES LEIDAS: {self.paginasT}")
                print("-----------------------------------------------------------------")
                i = 0

                for product_element in product_elements:
                    product_data = {
                        "COMPETENCIA": None,
                        "PRODUCTO": None,
                        "PLATAFORMAS": None,
                        "MEJOR_PRECIO": None,
                        "PRECIO_ORIGINAL": None,
                        "PRECIO_SEMINUEVO": None,
                        "REBAJA": None,
                        "URL": None,
                    }
                    title_element = product_element.find('span', class_='title')
                    if title_element:
                        title = title_element.text.strip()
                        if title in title_url_mapping:
                            if url not in title_url_mapping[title]:
                                title_url_mapping[title].add(url)
                                product_data['PRODUCTO'] = title
                            else:
                                product_data['PRODUCTO'] = ""
                                continue
                        else:
                            title_url_mapping[title] = {url}
                            product_data['PRODUCTO'] = title
                    else:
                        product_data['PRODUCTO'] = ""

                    discount_element = product_element.find('div', class_='discount')
                    if discount_element:
                        product_data['REBAJA'] = discount_element.text.strip()
                    else:
                        product_data['REBAJA'] = 0

                    product_link = product_element.find('a', class_='cover')
                    if product_link:
                        self.url2 = product_link['href']
                        print(f"Leyendo URL {i + 1}: {self.url2}")
                    else:
                        break

                    i += 1
                    self.extraer_datos_de_articulo(product_data)
                    self.product_data.append(product_data)      

                num_pages += 1
                self.paginasT += 1
            else:
                break          

    def extraer_datos_de_articulo(self, product_data):

        if 'eneba' in self.url2:
            response = requests.get(self.url2)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')

                product_data['COMPETENCIA'] = "ENEBA"
                product_data['URL'] = self.url2
                product_data['PRECIO_SEMINUEVO'] = 0

                nombre_element = soup.find('h1', class_='C68dpx')
                if nombre_element:
                    product_data['PRODUCTO'] = nombre_element.text
                else:
                    product_data['PRODUCTO'] = ""

                precio_element = soup.find('span', class_='L5ErLT')
                if precio_element:
                    product_data['MEJOR_PRECIO'] = precio_element.text.replace("€", "").strip().replace(",", ".")
                else:
                    product_data['MEJOR_PRECIO'] = 0

                div_element = soup.find('div', class_='onFZLe')
                if div_element:
                    li_elements = div_element.find_all('li')
                    plataformas = [li.text for li in li_elements]
                    plataformas = ['PC' if plataforma == 'Windows' else plataforma for plataforma in plataformas]
                    product_data['PLATAFORMAS'] = ', '.join(plataformas)
                else:
                    product_data['PLATAFORMAS'] = ""

                precio_original_element = soup.find('div', class_='gcTFLF')
                if precio_original_element:
                    precio_original_element = precio_original_element.find('span', class_='L5ErLT').text.replace(",", ".")
                    product_data['PRECIO_ORIGINAL'] = precio_original_element.replace("€", "").strip()
                else:
                    product_data['PRECIO_ORIGINAL'] = 0

                descuento_element = soup.find('div', class_='MjI1ZB')
                if descuento_element:
                    descuento_element = descuento_element.text.strip()
                    descuento_element = descuento_element.replace("Ahorra ", "")
                    product_data['REBAJA'] = descuento_element
                else:
                    product_data['REBAJA'] = 0

                self.product_data.append(product_data)
                self.insert_product_into_database(product_data)
            else:
                print(f'Error al realizar la solicitud GET para la URL: {self.url2}')

        elif 'instant-gaming' in self.url2:
            r = requests.get(self.url2, headers=self.headers)
            if r.status_code == 200:
                data = r.text
                soup = BeautifulSoup(data, 'lxml')

                notifstock_div = soup.find('div', class_='notifstock')
                if notifstock_div:
                    print("Div 'notifstock' encontrado. Saltando este producto.")
                    return  # Salir de la función sin procesar más datos
                else:

                    total_price_element = soup.find('div', class_='total')
                    if total_price_element:
                        product_data['MEJOR_PRECIO'] = total_price_element.text.replace("€", "").strip()
                    else:
                        product_data['MEJOR_PRECIO'] = 0

                    product_data['URL'] = self.url2
                    product_data['COMPETENCIA'] = "INSTANT-GAMING"

                    
                    
                    plataforma_instant_gaming = self.obtener_plataforma_instant_gaming(self.url3)
                    if plataforma_instant_gaming:
                        product_data['PLATAFORMAS'] = plataforma_instant_gaming
                    else:
                        product_data['PLATAFORMAS'] = "a"


                    discounts_element = soup.find('div', class_='discounts')
                    if discounts_element:
                        original_price = discounts_element.find('div', class_='retail')
                        if original_price:
                            original_price_text = original_price.text.replace("€", "").strip()
                            product_data['PRECIO_ORIGINAL'] = float(original_price_text)
                        else:
                            product_data['PRECIO_ORIGINAL'] = 0
                    else:
                        product_data['PRECIO_ORIGINAL'] = 0
                    product_data['PRECIO_SEMINUEVO'] = 0

                    self.insert_product_into_database(product_data)
            else:
                print("No se encuentra la URL")
    
    def obtener_plataforma_instant_gaming(self,url):
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        sistema = query_params.get('system', None)
        if sistema != None:
            return str(sistema).replace("[","").replace("]","").replace("'","").strip()
        plataforma = query_params.get('platform[0]', None) or query_params.get('platform%5B0%5D', None)
        if plataforma != None:
            return str(plataforma).replace("[","").replace("]","").replace("'","").strip()
        return ""
        
        

    

    def insert_product_into_database(self, product_data):
        if product_data['MEJOR_PRECIO'] != 0:
            try:
                conexion = mysql.connector.connect(
                    user='root',
                    password='javi',
                    host='localhost',
                    database='bdmysql'
                )
                cursor = conexion.cursor()

                insert_query = """
                INSERT INTO clase (COMPETENCIA, PRODUCTO, PLATAFORMAS, MEJOR_PRECIO, PRECIO_ORIGINAL, PRECIO_SEMINUEVO, REBAJA, URL)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """

                values = (
                    product_data['COMPETENCIA'],
                    product_data['PRODUCTO'],
                    product_data['PLATAFORMAS'],
                    product_data['MEJOR_PRECIO'],
                    product_data['PRECIO_ORIGINAL'],
                    product_data['PRECIO_SEMINUEVO'],
                    product_data['REBAJA'],
                    product_data['URL']
                )

                cursor.execute(insert_query, values)
                conexion.commit()

            except mysql.connector.Error as err:
                print(f'Error al conectar con la base de datos: {err}')

            finally:
                if 'conexion' in locals() and conexion.is_connected():
                    cursor.close()
                    conexion.close()

if __name__ == '__main__':
    urls = [
      #  "https://www.eneba.com/es/store/games",
        "https://www.instant-gaming.com/en/search/?system=playstation&version=2&page=",
        "https://instant-gaming.com/en/search/?platform%5B0%5D=pc&version=2&page=",
        "https://instant-gaming.com/en/search/?system=xbox&version=2&page=",
        "https://www.instant-gaming.com/en/search/?system=nintendo&platform%5B0%5D=switch&version=2&page="
        # Agrega aquí más URLs según sea necesario
    ]

    scraper = WebScraper(urls)
    scraper.extraer_datos_de_pagina(urls)