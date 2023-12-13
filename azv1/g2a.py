import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class WebScraper:
    def __init__(self):
        self.base_url = "https://www.g2a.com"
        self.headers = {
            "User-Agent": "Tu Agente de Usuario Personal"
        }

    def extraer_datos_de_pagina(self, url):
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                title_element = soup.find('h1', class_='indexes__StyledTypography-wgki8j-13')
                title = title_element.text if title_element else "Título no encontrado"

                platform_element = soup.find('p', class_='indexes__StyledAttributeValue-wgki8j-4')
                platform = platform_element.text if platform_element else "Plataforma no encontrada"

                # Verificar si el elemento del precio existe antes de intentar obtener el texto
                price_element = soup.find('span', class_='sc-iqAclL sc-crzoAE dJFpVb frbZCR sc-bqGGPW gjCrxq')
                price = price_element.get_text(strip=True) if price_element else "Precio no encontrado"

                return {
                    "COMPETENCIA": "G2A",
                    "PRODUCTO": title,
                    "PLATAFORMA": platform,
                    "MEJOR_PRECIO": price,
                    "PRECIO_ORIGINAL": 0,
                    "PRECIO_SEMINUEVO": 0,
                    "REBAJA": 0,
                    "URL": url
                }

            else:
                print("La solicitud a la URL ha fallado")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Error al realizar la solicitud: {e}")
            return None

    def extraer_datos_de_categoria(self, category_url):
        try:
            response = requests.get(category_url, headers=self.headers)
            response.raise_for_status()

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                product_list = soup.find('ul', class_='GridContent_section-content--grid__3BOJd RegularProductsContent_products-content--regular__wrap__TsU3B')

                if product_list:
                    product_links = product_list.find_all('a', class_='indexes__Cover-h6zdws-6 indexes__StyledCover3-h6zdws-63 ICHIU iFTLxu')
                    for product_link in product_links:
                        product_url = self.base_url + product_link['href']
                        data = self.extraer_datos_de_pagina(product_url)
                        if data:
                            print("Datos extraídos:")
                            for key, value in data.items():
                                print(f"{key}: {value}")
                            print("\n")

                else:
                    print("Lista de productos no encontrada")

            else:
                print("La solicitud a la URL de categoría ha fallado")

        except requests.exceptions.RequestException as e:
            print(f"Error al realizar la solicitud: {e}")

    def ejecutar_scraper(self):
        category_url = "https://www.g2a.com/es/top-list/pc-games"
        self.extraer_datos_de_categoria(category_url)

if __name__ == "__main__":
    scraper = WebScraper()
    scraper.ejecutar_scraper()
