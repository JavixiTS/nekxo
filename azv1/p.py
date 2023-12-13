import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests
import pandas as pd
import re
import mysql.connector

class WebScraper:
    def __init__(self, url):
        self.url = url
        self.soup = None
        self.product_data = []
        self.variable = None
        self.sustito = "X"


    def extraer_datos_de_pagina(self, urls,conexion):
        for url in urls:
            if "borax" in url:
                self.extraer_datos_borax(url,conexion)
            elif "jetcomputer" in url:
                self.extraer_datos_jetcomputer(url,conexion)
            elif "info-computer" in url:
                self.extraer_datos_info_computer(url,conexion)
            elif "backmarket" in url:
                self.extraer_datos_backmarket(url,conexion)
            elif "compulease" in url:
                self.extraer_datos_compulease(url,conexion)
            else:
                print(f"No se reconoce la URL: {url}")


    def extraer_datos_borax(self, url,conexion):
        response = requests.get(url)
        if response.status_code == 200:
            self.soup = BeautifulSoup(response.text, 'lxml')  # Establece self.soup aquí
            product_elements = self.soup.find_all('h3', class_='h3 product-title', itemprop='name')

            i = 0  # Inicializa el contador
            for product_element in product_elements:
                print(f"Leyendo URL {i + 1}: {url}")
                product_data = {
                    'COMPETENCIA': "BORAX",
                    'PRODUCTO': None,
                    'PROCESADOR': None,
                    'DISCO_DURO': None,
                    'MEMORIA': None,
                    'DIMENSIONES': None,
                    'GARANTIA': None,
                    'MEJOR_PRECIO': None,
                    'PRECIO_ORIGINAL': None,
                    'REBAJA': None,
                    'GRADO': None,
                    'URL': None,
                }

                
                
                producto = product_element.text.strip()
                    # Realiza limpieza del texto
                producto = re.sub(r'Ordenadores segunda mano|Ordenadores completos segunda mano |Ordenadores segunda mano baratos|Ordenador segunda mano|ordenadores segunda mano|ordenadores completos segunda mano|core|ordenador segunda mano|ordenadores baratos|portatiles segunda mano|Lote de|Core.*|Pentium.*', '', producto)
                producto = producto.strip().replace("baratos","").upper()
                producto = producto.split('I5')[0].strip()
                producto = producto.split('AMD')[0].strip()
                producto = producto.split('SFF')[0].strip()
                product_data['PRODUCTO'] = producto

                product_url_element = product_element.find('a')
                if product_url_element:
                    product_data['URL'] = urljoin(url, product_url_element['href'])

                    i += 1
                    self.extraer_datos_de_articulo(product_data,conexion)

    def extraer_datos_backmarket(self, url,conexion):
        i = 0
        response = requests.get(url)
        if response.status_code == 200:
            self.soup = BeautifulSoup(response.text, 'lxml')  # Establece self.soup aquí
            product_elements = self.soup.find_all('div', class_='productCard col-span-full')
            for product_element in product_elements:
                print(f"Leyendo URL {i + 1}: {self.url}")
                product_data = {
                    'COMPETENCIA': None,
                    'PRODUCTO': None,
                    'PROCESADOR': None,
                    'DISCO_DURO': None,
                    'MEMORIA': None,
                    'DIMENSIONES': None,
                    'GARANTIA': None,
                    'MEJOR_PRECIO': None,
                    'PRECIO_ORIGINAL': None,
                    'REBAJA': None,
                    'GRADO': None,
                    'URL': None,
                }
                product_link = product_element.find('a', href=True)
                if product_link:
                    product_data['URL'] = 'https://www.backmarket.es' + product_link['href']
                i += 1
                self.extraer_datos_de_articulo(product_data,conexion)
            for page_number in range(1, 2):  # Hay 34
                page_url = f"{self.url}?page={page_number}"             
                for product_element in product_elements:
                    print(f"Leyendo URL {i + 1}: {page_url}")
                    product_data = {
                        'COMPETENCIA': None,
                        'PRODUCTO': None,
                        'PROCESADOR': None,
                        'DISCO_DURO': None,
                        'MEMORIA': None,
                        'DIMENSIONES': None,
                        'GARANTIA': None,
                        'MEJOR_PRECIO': None,
                        'PRECIO_ORIGINAL': None,
                        'REBAJA': None,
                        'GRADO': None,
                        'URL': None,
                    }
                    product_link = product_element.find('a', href=True)
                    if product_link:
                        product_data['URL'] = urljoin(page_url, product_link['href'])

                    i += 1
                                    
                    self.extraer_datos_de_articulo(product_data,conexion)                        
            else:
                print(f"No he querido entrar: URL {self.url}, Variable {self.variable}")          
        
    def extraer_datos_info_computer(self, url,conexion):
        response = requests.get(url)
        i = 0
        if response.status_code == 200:
            max_data_per_page = 4 # Solo cojer 65 datos
            self.soup = BeautifulSoup(response.text, 'lxml')  # Establece self.soup aquí
            product_elements = self.soup.find_all('a', class_='thumbnail product-thumbnail')

            for product_element in product_elements:
                print(f"Leyendo URL {i + 1}: {self.url}")
                product_data = {
                    'COMPETENCIA': None,
                    'PRODUCTO': None,
                    'PROCESADOR': None,
                    'DISCO_DURO': None,
                    'MEMORIA': None,
                    'DIMENSIONES': None,
                    'GARANTIA': None,
                    'MEJOR_PRECIO': None,
                    'PRECIO_ORIGINAL': None,
                    'REBAJA': None,
                    'GRADO': None,
                    'URL': None,
                }
                if  i == 4: #solo cojet 65 datos
                    break
                product_data['URL'] = product_element['href']
                i += 1
                self.extraer_datos_de_articulo(product_data,conexion)
            
            for page_number in range(2, 3):  # Hay 48 paginas
                    page_url = f"{self.url}?page={page_number}"
                    
                    data_collected = 0  # Contador para los datos recopilados en esta página

                    for product_element in product_elements:
                        if data_collected >= max_data_per_page:
                            break  # Detén la recopilación si se han recopilado suficientes datos en esta página

                        print(f"Leyendo URL {data_collected + 1}: {page_url}")
                        product_data = {
                            'COMPETENCIA': None,
                            'PRODUCTO': None,
                            'PROCESADOR': None,
                            'DISCO_DURO': None,
                            'MEMORIA': None,
                            'DIMENSIONES': None,
                            'GARANTIA': None,
                            'MEJOR_PRECIO': None,
                            'PRECIO_REBAJA': None,
                            'REBAJA': None,
                            'GRADO': None,
                            'URL': None,
                        }

                        product_data['URL'] = urljoin(self.url, product_element['href'])
                        data_collected += 1  # Incrementa el contador de datos recopilados en esta página
                        self.extraer_datos_de_articulo(product_data,conexion)
                    else:
                        print(f"No he querido entrar: URL {self.url}, Variable {self.variable}")      

    def extraer_datos_jetcomputer(self, url,conexion):
        response = requests.get(url)
        if response.status_code == 200:
            self.soup = BeautifulSoup(response.text, 'lxml')  # Establece self.soup aquí
            i = 0  # Inicializa el contador
            product_elements = self.soup.find_all('h2', class_='h3 product-title')

            for product_element in product_elements:
                print(f"Leyendo URL {i + 1}: {self.url}")
                product_data = {
                    'COMPETENCIA': None,
                    'PRODUCTO': None,
                    'PROCESADOR': None,
                    'DISCO_DURO': None,
                    'MEMORIA': None,
                    'DIMENSIONES': None,
                    'GARANTIA': None,
                    'MEJOR_PRECIO': None,
                    'PRECIO_ORIGINAL': None,
                    'REBAJA': None,
                    'GRADO': None,
                    'URL': None,
                }

                product_element = product_element.find('a')  
                product_data['URL'] = product_element['href'] 

                i += 1
                self.extraer_datos_de_articulo(product_data,conexion)

    def extraer_datos_compulease(self, url,conexion):
        response = requests.get(url)
        if response.status_code == 200:
            self.soup = BeautifulSoup(response.text, 'lxml')  # Establece self.soup aquí
            i = 0  # Inicializa el contador  
            product_elements = self.soup.find_all('li', class_='product')       
            for product_element in product_elements:
                print(f"Leyendo URL {i + 1}: {self.url}")
                product_data = {
                    'COMPETENCIA': None,
                    'PRODUCTO': None,
                    'PROCESADOR': None,
                    'DISCO_DURO': None,
                    'MEMORIA': None,
                    'DIMENSIONES': None,
                    'GARANTIA': None,
                    'MEJOR_PRECIO': None,
                    'PRECIO_ORIGINAL': None,
                    'REBAJA': None,
                    'GRADO': None,
                    'URL': None,
                }  
                
                product_link = product_element.find('a', class_='woocommerce-LoopProduct-link')
                if product_link and 'href' in product_link.attrs:
                    product_data['URL'] = product_link['href']
                i += 1
                self.extraer_datos_de_articulo(product_data,conexion)

    def extraer_datos_de_articulo(self, product_data, conexion):
        r = requests.get(product_data['URL'])
        if r.status_code == 200:
            data = r.text
            soup = BeautifulSoup(data, 'lxml')

            if "borax" in self.url:
                product_data['PRECIO_ORIGINAL'] = 0
                product_data['REBAJA'] = 0
                product_data['COMPETENCIA'] = "BORAX"
                product_data['PORCENTAJE'] = "X"

                
                price_elements = soup.find_all('span', itemprop='price')
                if price_elements:
                    price = price_elements[0].text.strip().replace(",",".")
                    price = price.replace("€","").strip()
                    product_data['MEJOR_PRECIO'] = price
                grado_elements = soup.find_all('div', class_='tag-icon-tooltip')
                for grado_element in grado_elements:
                    strong_element = grado_element.find('strong')
                    if strong_element:
                        grade_text = strong_element.text.strip()
                        if grade_text.startswith('Grado'):
                            product_data['GRADO'] = grade_text.replace('Grado', '').strip()
                procesador_element = soup.find('dt', string='Procesador:')
                if procesador_element:
                    product_data['PROCESADOR'] = procesador_element.find_next('dd').text.strip().upper()
                disco_duro_element = soup.find('dt', string='Disco duro interno:')
                if disco_duro_element:
                    disco = disco_duro_element.find_next('dd').text.strip().upper()
                    disco = re.sub(r'[^a-zA-Z ]', '', disco)
                    disco = disco.replace("GB","")
                    product_data['DISCO_DURO'] = disco
                memoria_element = soup.find('dt', string='Memoria RAM:')
                if memoria_element:
                    memoria_name = memoria_element.find_next('dd').text.strip()
                    product_data['MEMORIA'] = memoria_name
                dimensiones_element = soup.find('dt', string='Pantalla:')
                if dimensiones_element:
                    product_data['DIMENSIONES'] = dimensiones_element.find_next('dd').text.strip()
                else:
                    product_data['DIMENSIONES'] = "X"
                garantia_element = soup.find('dt', string='Garantía:')
                if garantia_element:
                    garantia_text = garantia_element.find_next('dd').text.strip()
                    match = re.search(r'(\d+)\s+años', garantia_text)
                    if match:
                        years = match.group(1)
                        if years.lower() != "no":
                            product_data['GARANTIA'] = years
                self.product_data.append(product_data)

            if "jetcomputer" in self.url:
                product_data['PRECIO_ORIGINAL'] = 0
                product_data['REBAJA'] = 0
                product_data['COMPETENCIA'] = "JET COMPUTER"
                product_data['PORCENTAJE'] = "X"

                
                
                nombre_producto_element = soup.find('div', class_='nombre-producto')
                if nombre_producto_element:
                    nombre = nombre_producto_element.get_text(strip=True)
                    if "LOTE" in nombre:
                        product_data['PRODUCTO'] = nombre
                    else:
                        nombre = nombre.split('|')[0].strip()
                        nombre = nombre.split('+')[0].strip()
                        nombre = nombre.split('DM')[0].strip()
                        nombre = nombre.split('SFF')[0].strip()
                        nombre = nombre.split('TWR')[0].strip()
                        nombre = nombre.split('Core')[0].strip()
                        nombre = nombre.split('XEON')[0].strip()
                        product_data['PRODUCTO'] = nombre
                else:
                    name_element = soup.find('h1', class_='h1 page-title')
                    if name_element:
                        nombre = name_element.get_text(strip=True)
                        if "LOTE" in nombre:
                            product_data['PRODUCTO'] = nombre
                        else:
                            nombre = nombre.split('|')[0].strip()
                            nombre = nombre.split('+')[0].strip()
                            nombre = nombre.split('DM')[0].strip()
                            nombre = nombre.split('SFF')[0].strip()
                            nombre = nombre.split('TWR')[0].strip()
                            nombre = nombre.split('Core')[0].strip()
                            nombre = nombre.split('XEON')[0].strip()
                            product_data['PRODUCTO'] = nombre

                price_elements = soup.find_all('span', class_='current-price-value')
                if price_elements:
                    price = price_elements[0].text.strip().replace('\xa0', ' ').replace(",",".")
                    price = price.replace("€","").strip()
                    product_data['MEJOR_PRECIO'] = price
                grado_elements = soup.find_all('dt', string='Grado')
                if grado_elements:
                    product_data['GRADO'] = grado_elements[0].find_next('dd').text.strip()
                else:
                    product_data['GRADO'] = "X"
                procesador_element = soup.find('dt', string='Procesador')
                if procesador_element:
                    procesador = procesador_element.find_next('dd').text.strip().upper()
                    if "CORE I5" in procesador:
                        product_data['PROCESADOR'] = "INTEL CORE I5" 
                    elif "CORE  I3" in procesador:
                        product_data['PROCESADOR'] = "INTEL CORE I3" 
                    elif "CORE I7" in procesador:
                        product_data['PROCESADOR'] = "INTEL CORE I7" 
                    else:      
                        product_data['PROCESADOR'] = procesador.split('-')[0]
                else:
                    product_data['PROCESADOR'] = "X"
                disco_duro_element = soup.find('dt', string='Tipo Disco Duro')
                if disco_duro_element:
                    disco = disco_duro_element.find_next('dd').text.strip()
                    disco = disco.replace("INTENSO","")
                    if "SATA HDD" in disco:
                        disco = "SATA + HDD"
                    elif "SATA SSD" in disco:
                        disco = "SATA + SSD"
                    elif "NVME SSD" in disco:
                        disco = "NVME + SSD"
                    elif "M2 MVME" in disco:
                        disco = "M2 + MVME"
                    product_data['DISCO_DURO'] = disco
                else:
                    product_data['DISCO_DURO'] = "X"
                memoria_element = soup.find('dt', string='Memoria')
                if memoria_element:
                    product_data['MEMORIA'] = memoria_element.find_next('dd').text.strip()
                else:
                    product_data['MEMORIA'] = "X"
                dimensiones_element = soup.find('dt', string='Dimensiones')
                if dimensiones_element:
                    product_data['DIMENSIONES'] = dimensiones_element.find_next('dd').text.strip().upper()
                else:
                    product_data['DIMENSIONES'] = "X"
                product_data['GARANTIA'] = "1"
                self.product_data.append(product_data)

            if "info-computer" in self.url:

                # Encontrar el elemento que contiene el precio con descuento
                reduction_element = self.soup.find('span', class_='reduction')

                # Encontrar el elemento que contiene el precio base
                regular_price_element = self.soup.find('span', class_='block-regular-price')

                # Extraer los valores de precio con descuento y precio base
                precio_descuento = reduction_element.text.strip().replace("€","").replace(",",".").replace("AHORRA","")
                precio_base = regular_price_element.text.strip().replace(",",".").replace("€","")

                product_data['PRECIO_ORIGINAL'] = precio_base.strip()
                product_data['REBAJA'] = precio_descuento.strip()
                
                
                product_data['COMPETENCIA'] = "INFO-COMPUTER"
                product_data['GRADO'] = "X"


                # Encuentra el contenedor de los detalles del producto
                product_details = soup.find('div', {'id': 'product-details'})
                li_elements = soup.find_all('li')

                if product_details:
                    # Procesador
                    procesador_element = soup.find('span', {'class': 'value'},)
                    if procesador_element:
                        procesador = procesador_element.get_text(strip=True).upper()
                        product_data['PROCESADOR'] = procesador.split('-')[0]

                nombre = soup.find('h1', class_='h1 product_name')
                if nombre:
                    producto = nombre.text.strip()
                    patrones = [r'Core.*', r'AMD.*', r'I5.*', r'\|.*', r'Celeron.*',r'C2D.*']
                    for patron in patrones:
                        producto = re.sub(patron, '', producto, flags=re.I)  # flags=re.I para hacer coincidencias sin distinción entre mayúsculas y minúsculas
                    product_data['PRODUCTO'] = producto.strip().upper()       

                price_element = soup.find("span", class_="price_with_tax price_pvp")
                if price_element:
                    price = price_element.text.strip().replace(",",".")
                    product_data['MEJOR_PRECIO'] = price.replace("€","").strip()

                #  Calcular el porcentaje de descuento
                precio_descuento = float(product_data['MEJOR_PRECIO'])
                precio_base = float(product_data['PRECIO_ORIGINAL'])
                # Calcula el porcentaje de descuento
                descuento = (float(precio_base) - float(precio_descuento)) / float(precio_base) * 100

                # Redondea el porcentaje de descuento a dos decimales y ajusta el segundo decimal
                descuento_redondeado = round(descuento)
                porcentaje_descuento = str(descuento_redondeado)
                product_data['PORCENTAJE'] = porcentaje_descuento + " %"
                    
        
                etiquetas = soup.find_all('span', class_='value')
                for etiqueta in etiquetas:
                    texto = etiqueta.text   
                    if "año de garantía" in texto:
                        garantia = re.search(r'\d+', texto)
                        product_data["GARANTIA"] = int(garantia.group(0))   
                    else: 
                        garantia_element = soup.find('p', class_='garantia_text')
                        garantia_text = garantia_element.find('strong').get_text().replace("garantía asegurada durante","").replace(" años","").strip()
                        garantia = re.search(r'\d+', garantia_text)
                        if garantia:
                            product_data["GARANTIA"] = int(garantia.group(0))
                    if "GB RAM" in texto:
                            product_data["MEMORIA"] = texto.replace("RAM", "").upper()
                    elif "Pixeles" in texto:
                        product_data["DIMENSIONES"] = texto.upper()
                    else:
                        if"Pulgadas" in texto:
                            product_data["DIMENSIONES"] = texto.upper()
            
                 

                    for li in li_elements:
                        li_text = li.get_text()
                        if li_text.startswith("Disco Duro:"):
                            disco = li.text.replace("Disco Duro:","")
                            disco = disco.replace("TB","")
                            disco = disco.replace("Nuevo","")
                            disco = re.sub(r'[^a-zA-Z ]', '', disco).strip()
                            if "SSD" and "M" in disco:
                                disco = "SSD + M.2"
                            elif "M" and not "SSD" and not "M.2" in disco:
                                disco = disco + ".2"
                            product_data["DISCO_DURO"] = disco
                        elif "SSD" in texto:
                            disco = texto
                            disco = re.sub(r'[^a-zA-Z ]', '', disco).strip()
                            disco = disco.replace("M","")
                            product_data["DISCO_DURO"] = disco
                        elif "HDD" in texto:
                            disco = texto
                            disco = re.sub(r'[^a-zA-Z ]', '', disco)
                            product_data["DISCO_DURO"] = disco
                        elif "M.2" in texto:
                            disco = texto
                          
                            product_data["DISCO_DURO"] = disco
                        elif "NVE" in texto:
                            disco = texto
                            disco = re.sub(r'[^a-zA-Z ]', '', disco)
                            product_data["DISCO_DURO"] = disco
                        elif "NVME" in texto:
                            disco = texto
                            disco = re.sub(r'[^a-zA-Z ]', '', disco)
                            product_data["DISCO_DURO"] = disco
                        elif "eMMC" in texto:
                            disco = texto
                            disco = re.sub(r'[^a-zA-Z ]', '', disco)
                            product_data["DISCO_DURO"] = disco.upper()
                self.product_data.append(product_data)

            elif "backmarket" in self.url:

                product_data['GRADO'] = "X"
                product_data['COMPETENCIA'] = "BACK MARKET"

                descripcion_producto_element = soup.find('div', class_='text-grey-500')
                if descripcion_producto_element:
                    descripcion_producto = descripcion_producto_element.text.strip()

                

                # NOMBRE
                nombre_producto_element = soup.find('h2', class_='body-1-bold mb-6')
                if nombre_producto_element:
                    nombre = nombre_producto_element.text.split()
                    nombre_producto = ' '.join(nombre[:4])
                    if "Lenovo" in nombre_producto:
                        nombre_producto = ' '.join(nombre[:3])
                    elif "Dell" in nombre_producto:
                        nombre_producto = ' '.join(nombre[:3])
                    if nombre_producto:
                        product_data['PRODUCTO'] = nombre_producto.upper()

                # Precios
                
                price_element = soup.find('div', {'data-test': 'normal-price'})
                if price_element:
                    price = price_element.get_text().strip().replace(",", ".").replace("€", "")
                    # Reemplaza '\xa0' por un espacio en blanco en el precio
                    product_data['MEJOR_PRECIO'] = price.replace('\xa0', ' ').strip()

                precio_descuento_element = soup.find('span', class_='body-1-light-striked')
                precio_descuento_text = precio_descuento_element.text.strip().replace('€', '').replace("nueve", "")
                precio_descuento_text = precio_descuento_text.replace(",", ".")
                

                # Convertir los valores de precio a números
                precio_original = float(product_data['MEJOR_PRECIO'].replace("€", "").strip())
                precio_descuento = float(precio_descuento_text)
                product_data['PRECIO_ORIGINAL'] = precio_descuento

                # Comparar ambos precios
                if precio_descuento > precio_original:
                    descuento =  precio_descuento - precio_original 
                    descuento = "{:.2f}".format(descuento)
                    product_data['REBAJA'] = str(descuento).replace(",", ".")
                else:
                    product_data['REBAJA'] = "Sin descuento"
                
                #  Calcular el porcentaje de descuento
                precio_descuento = float(product_data['MEJOR_PRECIO'])
                precio_base = float(product_data['PRECIO_ORIGINAL'])
                # Calcula el porcentaje de descuento
                descuento = (float(precio_base) - float(precio_descuento)) / float(precio_base) * 100

                # Redondea el porcentaje de descuento a dos decimales y ajusta el segundo decimal
                descuento_redondeado = round(descuento)

                # Convierte el porcentaje redondeado a un string 
                porcentaje_descuento = str(descuento_redondeado)
                product_data['PORCENTAJE'] = porcentaje_descuento + " %"


                # DISCO DURO
                if "Tipo de almacenamiento :" in descripcion_producto:
                    disco_duro_line = descripcion_producto.split("Tipo de almacenamiento :")[1].strip()
                    # La variable 'disco_duro_line' ahora contiene el valor del disco duro
                    product_data['DISCO_DURO'] = disco_duro_line.split('\n')[0].strip()

                if "Memoria RAM :" in descripcion_producto:
                    inicio_ram = descripcion_producto.index("Memoria RAM :")
                    fin_modelo = descripcion_producto.find("Modelo :", inicio_ram)
                    fin_tipo_memoria = descripcion_producto.find("Tipo de memoria :", inicio_ram)

                    if fin_modelo != -1 and (fin_tipo_memoria == -1 or fin_modelo < fin_tipo_memoria):
                        # Si encuentra "Modelo :" o "Modelo :" aparece antes de "Tipo de memoria :"
                        product_data['MEMORIA'] = descripcion_producto[inicio_ram + len("Memoria RAM :"):fin_modelo].strip()
                    elif fin_tipo_memoria != -1:
                        # Si encuentra "Tipo de memoria :"
                        product_data['MEMORIA'] = descripcion_producto[inicio_ram + len("Memoria RAM :"):fin_tipo_memoria].strip()


                if "Tamaño pantalla (pulgadas) :" in descripcion_producto:
                    inicio = descripcion_producto.index("Tamaño pantalla (pulgadas) :")
                    tarjeta_grafica_index = descripcion_producto.find("Almacenamiento :", inicio)
                    product_data['DIMENSIONES'] = descripcion_producto[inicio + len("Tamaño pantalla (pulgadas) :"):tarjeta_grafica_index].strip() + " Pulgadas".upper()
                
                if "Procesador :" in descripcion_producto:
                    disco_duro_line = descripcion_producto.split("Procesador :")[1].strip()
                    # La variable 'disco_duro_line' ahora contiene el valor del disco duro
                    procesador = disco_duro_line.split('\n')[0].strip().upper()
                    if "CORE I5" in procesador:
                        product_data['PROCESADOR'] = "INTEL CORE I5" 
                    elif "CORE I3" in procesador:
                        product_data['PROCESADOR'] = "INTEL CORE I3" 
                    elif "CORE I7" in procesador:
                        product_data['PROCESADOR'] = "INTEL CORE I7" 
                    else:      
                        product_data['PROCESADOR'] = procesador.split('-')[0]

                # Garantía
                garantia_element = soup.find("span", {"id": "reassurance_service_warranty"})
                if garantia_element:
                    # Extraer el valor de garantía
                    valor_garantia = garantia_element.get_text(strip=True)
                    # Separar las palabras y encontrar el número
                    palabras = valor_garantia.split()
                    for palabra in palabras:
                        if palabra.isdigit():
                            product_data['GARANTIA'] = palabra
                self.product_data.append(product_data)

            elif "compulease" in self.url :

                disco = ""
                memoria = ""
                product_data['COMPETENCIA'] = "COMPULEASE"
                product_data['DIMENSIONES'] = "X"
                product_data['GRADO'] = "X"

                # Obtener el precio del producto
                # Obtener el precio del producto
                price_element = soup.find('p', class_='price')
                if price_element:
                    precio_ins = price_element.find('ins').find('bdi').get_text()
                    precio_del = price_element.find('del').find('bdi').get_text()
                    
                    # Limpiar y convertir los precios a números
                    precio_ins = float(precio_ins.replace("€", "").replace(",", "."))
                    precio_del = float(precio_del.replace("€", "").replace(",", "."))

                    # Calcular la diferencia
                    diferencia = precio_del - precio_ins

                    # Formatear
                    # Formatear los precios con dos decimales
                    precio_ins = "{:.2f}".format(precio_ins)
                    precio_del = "{:.2f}".format(precio_del)
                    diferencia = "{:.2f}".format(diferencia)

                    # Almacenar los precios y la diferencia en el diccionario product_data
                    product_data['MEJOR_PRECIO'] = precio_ins
                    product_data['PRECIO_ORIGINAL'] = precio_del
                    product_data['REBAJA'] = diferencia
                
                #  Calcular el porcentaje de descuento
                precio_descuento = float(product_data['MEJOR_PRECIO'])
                precio_base = float(product_data['PRECIO_ORIGINAL'])
                # Calcula el porcentaje de descuento
                descuento = (float(precio_base) - float(precio_descuento)) / float(precio_base) * 100

                # Redondea el porcentaje de descuento a dos decimales y ajusta el segundo decimal
                descuento_redondeado = round(descuento)
                porcentaje_descuento = str(descuento_redondeado)
                product_data['PORCENTAJE'] = porcentaje_descuento + " %"
                
                producto = soup.find('h1', class_='product_title entry-title')
                producto = producto.get_text().replace("PORTÁTIL","")
                producto = producto.replace("PORTATIL","")
                producto = producto.split('G4')[0]
                producto = producto.split('I5')[0]
                producto = producto.split('I3')[0]
                producto = producto.split('i3')[0]
                producto = producto.split('i5')[0]
                producto = producto.split('SFF')[0]
                product_data['PRODUCTO'] = producto
                


                description_element = soup.find('div', {'id': 'tab-description'})
                # Obtener el texto dentro del elemento
                description_text = description_element.get_text()


                # Busca la garantía en la descripción
                garantia = soup.find('div', class_='woocommerce-product-details__short-description')
                if garantia:
                    # Extraer el texto del elemento p dentro de la descripción
                    garantia = garantia.find('p').get_text().replace("*","")
                    garantia = garantia.replace("AÑO DE GARANTIA","")
                    product_data['GARANTIA'] = garantia.replace("AÑOS DE GARANTIA","")
                else:
                    garantia_match = re.search(r'(\d+\s*AÑOS\s*DE\s*GARANTIA)', description_text)
                    product_data['GARANTIA'] = garantia_match.group(1).replace("AÑOS DE GARANTIA","") if garantia_match else "x"

                # Encontrar la MEMORIA
                memory_match = re.search(r'MEMÓRIA:\s*(\d+GB\s*RAM)', description_text)
                if memory_match:
                    memory = memory_match.group(1) if memory_match else "No encontrado"
                    memoria = memory.replace("RAM","")
                    product_data['MEMORIA'] = memoria
                else:
                    ram_match = re.search(r'(\d+\s*GB\s*DE\s*RAM)', description_text)
                    if ram_match:
                        memoria = ram_match.group(1) if ram_match else "x"
                        product_data['MEMORIA'] = memoria.replace("DE RAM","").replace("RAM","")
                    else:
                        ram_match = re.search(r'(\d+\s*GB\s*DDR[0-9]+)',description_text)
                        memoria = ram_match.group(1) if ram_match else "x"
                        product_data['MEMORIA'] = memoria.replace("DDR4","")

                # Encontrar el DISCO DURO
                disk_match = re.search(r'DISCO DURO: (.*?)\n', description_text)

                disk = disk_match.group(1) if disk_match else "No encontrado"
                disco = re.sub(r'[^a-zA-Z ]', '', disk)
                product_data['DISCO_DURO'] = disco
                if disk == "No encontrado":
                    disk_match = re.search(r'DISCO DURO (.*?)\n', description_text)
                    if disk_match:
                        disco = disk_match.group(1)
                        disco = re.sub(r'[^a-zA-Z ]', '', disco)
                        product_data['DISCO_DURO'] = disco
                    else:
                            storage_match = re.search(r'(\d+\s*GB\s*SSD)', description_text)
                            disco = storage_match.group(1) if storage_match else "x"
                            disco = re.sub(r'[^a-zA-Z ]', '', disco)
                            product_data['DISCO_DURO'] = disco.replace("GB","")


                

                if disco == "x" and memoria == "x":
                    # Encontrar el elemento que contiene la descripción
                    description_element = soup.find('div', {'id': 'tab-description'})

                    # Obtener el texto dentro del elemento
                    description_text = description_element.get_text()

                    # Usar expresiones regulares para encontrar las cadenas que contienen GB RAM y SSD
                    pattern = r'(\d+\s?GB RAM)|(\d+\s?SSD)'
                    matches = re.findall(pattern, description_text)

                    # Variables para almacenar las coincidencias
                    ram = None

                    # Recorrer las coincidencias y asignarlas a las variables correspondientes
                    for match in matches:
                        if match[0]:
                            ram = match[0].strip()
                            if "RAM" in ram:
                                product_data['MEMORIA'] = ram.replace("DE RAM","").replace("RAM","")
                            else:               
                                p_tags = soup.find('div', {'id': 'tab-description'}).find_all('p')
                                # Encuentra la etiqueta que contiene "MEMORIA RAM" y extrae su contenido
                                memoria_ram_tag = next((tag for tag in p_tags if "MEMORIA RAM" in tag.get_text()), None)
                                product_data['MEMORIA'] = memoria_ram_tag.text if memoria_ram_tag else "No encontrado"
                        if match[1]:
                            disco = match[1].strip()
                            disco = re.sub(r'[^a-zA-Z ]', '', disco)
                            product_data['DISCO_DURO'] = disco
                

                if product_data['DISCO_DURO'] == "x":
                    resultado = re.search(r'/(\d+\s*SSD)/', description_text)
                    if resultado:
                        disco = resultado.group(1)
                        disco = re.sub(r'[^a-zA-Z ]', '', disco)
                        product_data['DISCO_DURO'] = disco

                if memoria == "x":
                    memoria_ram_paragraph = soup.find('p', string=re.compile(r'MEMORIA RAM', re.IGNORECASE))
                    if memoria_ram_paragraph:
                            memoria = memoria_ram_paragraph.get_text().replace("DE MEMORIA RAM","").replace("DDR4","")
                            product_data['MEMORIA'] = memoria

                if product_data['GARANTIA'] == "x":
                    if "1 AÑO DE GARANTIA" in description_text:
                        product_data['GARANTIA'] = "1" 
                
                if product_data['MEMORIA'] == "x":
                    table = soup.find('table', {'class': 'woocommerce-product-attributes'})
                    memoria_row = table.find('tr', {'class': 'woocommerce-product-attributes-item--attribute_pa_memoria'})
                    if memoria_row:
                        memoria = memoria_row.find('td', {'class': 'woocommerce-product-attributes-item__value'}).text
                        product_data['MEMORIA'] = memoria
                    else:
                        print("x")

                # PROCESADOR"
                model_match = re.search(r'\d+\s[A-Z][^\n]*', description_text)
                model = model_match.group() if model_match else "No encontrado" if model_match else "No encontrado"
                if "i5" or "I5" in model:
                    product_data['PROCESADOR']= "INTEL CORE I5"
                elif "NVME" in model:
                    product_data['PROCESADOR'] = "x"
                else:
                    product_data['PROCESADOR'] = model
                self.product_data.append(product_data)

            self.insert_product_into_database(product_data, conexion)
    
    def insert_product_into_database(self, product_data, conexion):
        cursor = conexion.cursor()
        
        # Define la sentencia SQL de inserción
        insert_query = """
        INSERT INTO datos (COMPETENCIA, PRODUCTO, PROCESADOR, DISCO_DURO, MEMORIA, DIMENSIONES, GARANTIA, MEJOR_PRECIO, PRECIO_ORIGINAL, REBAJA, PORCENTAJE, GRADO, URL)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Obtén los valores de las columnas
        values = (
            product_data['COMPETENCIA'],
            product_data['PRODUCTO'],
            product_data['PROCESADOR'],
            product_data['DISCO_DURO'],
            product_data['MEMORIA'],
            product_data['DIMENSIONES'],
            product_data['GARANTIA'],
            product_data['MEJOR_PRECIO'],
            product_data['PRECIO_ORIGINAL'],
            product_data['REBAJA'],
            product_data['PORCENTAJE'],
            product_data['GRADO'],
            product_data['URL']
        )

        
        # Ejecuta la sentencia SQL de inserción
        cursor.execute(insert_query, values)
        
        # Confirma la transacción
        conexion.commit()
        
        # Cierra el cursor
        cursor.close()
    
    def get_data(self):
        return self.product_data


if __name__ == '__main__':
    product_urls = [
        "https://www.borax.es/3-ordenadores-segunda-mano",
        "https://www.jetcomputer.net/ordenadores",
        "https://www.info-computer.com/portatiles/",
        "https://www.backmarket.es/es-es/l/portatiles-qwerty-espanol/412cd750-89e2-4605-ab7e-f1e289d39765",
        "https://www.compulease.es/categoria-producto/portatiles/",
        "https://www.compulease.es/categoria-producto/sobremesa/"
        
    ]

    # Establece una conexión a la base de datos
    conexion = mysql.connector.connect(
        user='root',
        password='javi',
        host='localhost',
        database='bdmysql'
    )

    # Crea un cursor para ejecutar sentencias SQL
    cursor = conexion.cursor()

    # Ejecuta un DROP TABLE para reiniciar la tabla
    drop_table_query = "DROP TABLE IF EXISTS datos"
    cursor.execute(drop_table_query)

    # Crea la tabla datos
    create_table_query = """
    CREATE TABLE `datos` (
    `ID` int NOT NULL AUTO_INCREMENT,
    `COMPETENCIA` varchar(45) NOT NULL,
    `PRODUCTO` varchar(120) NOT NULL,
    `PROCESADOR` varchar(45) NOT NULL,
    `DISCO_DURO` varchar(45) NOT NULL,
    `MEMORIA` varchar(45) NOT NULL,
    `DIMENSIONES` varchar(45) NOT NULL,
    `GARANTIA` varchar(45) NOT NULL,
    `MEJOR_PRECIO` FLOAT NOT NULL,
    `PRECIO_ORIGINAL` FLOAT NOT NULL,
    `REBAJA` FLOAT NOT NULL,
    `PORCENTAJE` varchar(45) NOT NULL,
    `GRADO` varchar(45) NOT NULL,
    `URL` varchar(330) NOT NULL,
    PRIMARY KEY (`ID`)
    )
    """

    cursor.execute(create_table_query)

    # Commit los cambios en la base de datos
    conexion.commit()

    scraped_data = []

    for url in product_urls:
        scraper = WebScraper(url)
        scraper.extraer_datos_de_pagina([url],conexion)
        product_data = scraper.get_data()
        scraped_data.extend(product_data)
    if scraped_data:
        cheapest_products = {}

        for i, product in enumerate(scraped_data):
            product_name = product['PRODUCTO']
            product_price = product['MEJOR_PRECIO']

            # Verifica si el precio es un valor numérico antes de comparar
            if product_price is not None and cheapest_products.get(product_name) is not None:
                current_cheapest_price = cheapest_products[product_name]['MEJOR_PRECIO']

                # Verifica si el precio actual es un valor numérico
                if current_cheapest_price is not None:
                    if product_price < current_cheapest_price:
                        cheapest_products[product_name] = {'MEJOR_PRECIO': product_price, 'URL': product['URL'], 'ID': i}
                else:
                    cheapest_products[product_name] = {'MEJOR_PRECIO': product_price, 'URL': product['URL'], 'ID': i}
            elif product_price is not None:
                cheapest_products[product_name] = {'MEJOR_PRECIO': product_price, 'URL': product['URL'], 'ID': i}

        # Lista de productos más baratos con todos los detalles
        cheapest_products_list = [scraped_data[product_info['ID']] for product_info in cheapest_products.values()]

        # Ordenar los productos por nombre
        scraped_data_sorted = sorted(cheapest_products_list, key=lambda x: x['PRODUCTO'])

        excel_filename = 'C:/Users/administrator/Documents/productos_finales3.xlsx'

        with pd.ExcelWriter(excel_filename, engine='xlsxwriter') as writer:
            # Exporta los datos de la mezcla a la hoja 'MEZCLA'
            pd.DataFrame(scraped_data).to_excel(writer, sheet_name='MEZCLA', index=False)

            # Exporta los datos de los productos más baratos a la hoja 'ProductosFinales'
            pd.DataFrame(cheapest_products_list).to_excel(writer, sheet_name='ProductosFinales', index=False)

            # Exporta los datos de los productos ordenados alfabéticamente a la hoja 'ProductosOrdenados'
            pd.DataFrame(scraped_data_sorted).to_excel(writer, sheet_name='ProductosOrdenados', index=False)

            # Obtén el libro de Excel y ambas hojas
            workbook = writer.book
            worksheet_mezcla = writer.sheets['MEZCLA']
            worksheet_productos_finales = writer.sheets['ProductosFinales']
            worksheet_ordenados = writer.sheets['ProductosOrdenados']

            # Define un formato con un fondo gris para los títulos
            title_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bg_color': '#D3D3D3', 'border': 1})

            # Aplica el formato a la primera fila (que contiene los títulos) en ambas hojas
            for sheet_name in [worksheet_mezcla, worksheet_productos_finales]:
                sheet_name.set_row(0, None, title_format)

            # Define un formato para centrar y agregar un borde a las celdas
            cell_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1})

            # Aplica el formato a todas las celdas en ambas hojas
            for sheet_name in [worksheet_mezcla, worksheet_productos_finales, worksheet_ordenados]:
                for col_num, value in enumerate(cheapest_products_list[0].keys()):
                    sheet_name.write(0, col_num, value, title_format)  # Aplica el formato a los títulos
                    max_len = max([len(str(cheapest_products_list[i][value])) for i in range(len(cheapest_products_list))])
                    sheet_name.set_column(col_num, col_num, max_len + 2, cell_format)  # Aplica el formato a las celdas

        print(f"Los datos se han exportado a '{excel_filename}'")
    else:
        print("No se encontraron productos en las URL.")
    