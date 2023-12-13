import requests
from bs4 import BeautifulSoup
import pandas as pd

class WebScraper:
    def __init__(self, urls):
        self.base_urls = urls  # Cambiar el nombre a "base_urls" para denotar que es una lista
        self.product_data = []


        self.url2 = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }

    def scrape_data(self):
        title_url_mapping = {}  # Diccionario para mapear títulos a URLs
        
        for base_url in self.base_urls:
            num_pages = 1  # Reiniciar num_pages para cada URL
            max_pages_per_url = 2  # Establecer el número máximo de páginas por URL
            for page_number in range(1, max_pages_per_url + 1):
                url = f"{base_url}{page_number}"
                r = requests.get(url, headers=self.headers)

                if r.status_code == 200:
                    data = r.text
                    soup = BeautifulSoup(data, 'lxml')
                    product_elements = soup.find_all('div', class_='item force-badge')
                    i = 0

                    for product_element in product_elements:
                        print(f"Leyendo URL {i + 1}: {url}")
                        product_data = {
                        "COMPETENCIA": None,
                        "TITULO": None,
                        "PLATAFORMAS": None,
                        "MEJOR_PRECIO": None,
                        "PRECIO_ORIGINAL": None,
                        "PRECIO_SEMINUEVO": None,
                        "REBAJA": None,
                        "URL": None
                        }

                        title_element = product_element.find('span', class_='title')
                        if title_element:
                            title = title_element.text.strip()
                            # Verifica si el título ya existe en el diccionario
                            if title in title_url_mapping:
                                # Verifica si la URL ya está asociada con el título
                                if url not in title_url_mapping[title]:
                                    title_url_mapping[title].add(url)
                                    self.titulo = title      
                                else:
                                    continue  # Salta a la siguiente iteración si ya hemos procesado esta URL
                            else:
                                    # Crea un nuevo conjunto para la URL si el título no existe en el diccionario
                                title_url_mapping[title] = {url}
                                product_data['TITULO'] = title

                        discount_element = product_element.find('div', class_='discount')
                        if discount_element:
                            product_data['REBAJA']  = discount_element.text.strip()
                        else:
                            product_data['REBAJA']  = 0

                        product_link = product_element.find('a', class_='cover')
                        if product_link:
                            self.url2 = product_link['href']

                        self.scrape_product_details(product_data)
                        self.product_data.append(product_data)
                        i +=1

                    num_pages += 1

                    if num_pages >= max_pages_per_url:
                        num_pages = 1
                        # Si hemos leído 10 páginas, rompemos el bucle y pasamos a la siguiente URL
                        break


    def scrape_product_details(self, product_data):
        r = requests.get(self.url2, headers=self.headers)
        if r.status_code == 200:
            data = r.text
            soup = BeautifulSoup(data, 'lxml')

            total_price_element = soup.find('div', class_='total')
            if total_price_element:
                product_data['MEJOR_PRECIO'] = total_price_element.text.replace("€","").strip()
            else:
                    return False  # Devuelve False si no se agrega el producto
            
            
            product_data['URL'] = self.url2

            product_data['COMPETENCIA'] = "INSTANT-GAMING"
            platform_list = soup.find('select', id='platforms-choices')
            if platform_list:
                platforms = [option.text.strip() for option in platform_list.find_all('option')]
                product_data['PLATAFORMAS'] = platforms
            elif "steam" in product_data['URL'] or "pc" in product_data['URL']:
                product_data['PLATAFORMAS'] = "['PC']"
            elif "playstation-4" in product_data['URL'] and "playstation-5" in product_data['URL']:
                product_data['PLATAFORMAS'] = "['PS4','PS5']"
            elif "playstation-4" in product_data['URL'] or "ps4" in product_data['URL']:
                product_data['PLATAFORMAS'] = "['PS4']"
            elif "playstation-5" in product_data['URL'] or "ps5" in product_data['URL']:
                product_data['PLATAFORMAS'] = "['PS5']"
            elif "xbox-one-xbox-series-x-s" in product_data['URL']:
                product_data['PLATAFORMAS'] = "['Xbox One', 'Xbox Series X|S']"
            elif "switch" in product_data['URL']:
                product_data['PLATAFORMAS'] = "['Switch']"
            else:
                product_data['PLATAFORMAS'] = 'a'

            
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

    def get_data(self):
        return self.product_data
    

def export_to_excel(data, excel_filename):
    df = pd.DataFrame(data).sort_values(by='TITULO')
    df.drop_duplicates(subset=['TITULO'], keep='first', inplace=True)  # Elimina duplicados basados en el título

    excel_filename = r'C:\Users\administrator\Documents\productos_instant_gaming.xlsx'
    writer = pd.ExcelWriter(excel_filename, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')

    workbook = writer.book
    worksheet = writer.sheets['Sheet1']

    for i, column in enumerate(df.columns):
        column_len = max(df[column].astype(str).str.len().max(), len(column)) + 2
        worksheet.set_column(i, i, column_len)
        center_format = workbook.add_format({'align': 'center', 'valign': 'vcenter'})
        worksheet.set_column(i, i, column_len, center_format)
    writer.close()

if __name__ == '__main__':
    urls = [
        "https://www.instant-gaming.com/en/search/?platform%5B0%5D=pc&version=2&page=",
        "https://www.instant-gaming.com/en/search/?system=playstation&version=2&page=",
        "https://www.instant-gaming.com/en/search/?system=xbox&version=2&page=",
        "https://www.instant-gaming.com/en/search/?system=nintendo&platform%5B0%5D=switch&version=2&page="  
        # Agrega aquí más URLs según sea necesario
    ]
    

    scraper = WebScraper(urls)
    scraper.scrape_data()
    product_data = scraper.get_data()

    if product_data:
        
        excel_filename = r'C:\Users\administrator\Documents\productos_instant_gaming.xlsx'
        export_to_excel(product_data, excel_filename)
        print(f"Los datos se han exportado a '{excel_filename}'")
    else:
        print("No se encontraron productos en las URL proporcionadas.")
