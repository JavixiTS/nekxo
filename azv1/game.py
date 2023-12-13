import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

# Configurar las opciones del navegador para el modo headless
chrome_options = Options()
chrome_options.add_argument('--headless')

# Inicializa un navegador web en modo headless (puedes usar Chrome, Firefox, etc.)
driver = webdriver.Chrome(options=chrome_options)

# URL de la página web que deseas rascar
url = 'https://www.game.es/buscar/juegos%20ps4'

# Realizar una solicitud HTTP para obtener el contenido HTML (con Selenium)
driver.get(url)

# Espera a que los elementos dinámicos se carguen (ajusta el tiempo según sea necesario)
wait = WebDriverWait(driver, 15)
wait.until(EC.presence_of_element_located((By.ID, 'searchItemsWrap')))

# Número máximo de desplazamientos
max_scrolls = 150

# Crear listas para almacenar los datos
data = []

# Crear un conjunto para mantener un registro de títulos únicos
titulos_unicos = set()

# Iterar a través de cada elemento para extraer título, precio y URL
nuevos_elementos_encontrados = True
while nuevos_elementos_encontrados:
    # Parsear el contenido HTML utilizando Beautiful Soup
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # Buscar cada elemento de la clase 'search-item'
    elementos = soup.find_all(class_="search-item")

    if not elementos:
        break  # Si no se encuentran elementos en esta iteración, salir del bucle

    # Marcar que se han encontrado nuevos elementos en esta iteración
    nuevos_elementos_encontrados = False

    for elemento in elementos:
        url_element = elemento.find('a')
        if url_element and 'href' in url_element.attrs:
            titulo = elemento.find(class_="title").find('a').text.strip()
            
            # Verificar si el título ya existe en el conjunto de títulos únicos
            if titulo not in titulos_unicos:
                titulos_unicos.add(titulo)  # Agregar el título al conjunto
                url = url_element['href']
                url_completa = "https://www.game.es" + url

                # Encontrar el precio para el producto nuevo ("buy-new")
                precio_nuevo_element = elemento.find('div', class_='price buy-shared-xxs buy-new')
                if precio_nuevo_element:
                    int_part = precio_nuevo_element.find(class_="int").text
                    decimal_part = precio_nuevo_element.find(class_="decimal").text
                    int_part = int_part.strip().replace('€', '')
                    decimal_part = decimal_part.strip().replace('€', '')
                    precio_nuevo = f"{int_part}.{decimal_part}".replace("'", "")
    
                    if precio_nuevo == "3.":
                        titulo += " - Reservar"
                else:
                    precio_nuevo = "x"
    
                # Encontrar el precio para el producto seminuevo ("buy-preowned")
                precio_seminuevo_element = elemento.find('div', class_='price buy-shared-xxs buy-preowned')
                if precio_seminuevo_element:
                    int_part = precio_seminuevo_element.find(class_="int").text
                    decimal_part = precio_seminuevo_element.find(class_="decimal").text
                    int_part = int_part.strip().replace('€', '')
                    decimal_part = decimal_part.strip().replace('€', '')
                    precio_seminuevo = f"{int_part}.{decimal_part}".replace("'", "")
                else:
                    precio_seminuevo = "x"
    
                # Encontrar el elemento que contiene la información de la plataforma
                plataforma_element = elemento.find('a', class_='btn-link btn-sm')
                # Verificar si se ha encontrado el elemento
                if "PLAYSTATION-4" in url:
                    plataforma = "PS4"
                else:
                    plataforma = "ª"
    
                
    
                # Agregar los datos a la lista
                data.append({
                    "COMPETENCIA": "GAME",
                    "TITULO": titulo,
                    "Plataforma": plataforma,
                    "PRECIO NUEVO": precio_nuevo,
                    "PRECIO Seminuevo": precio_seminuevo,
                    "URL": url_completa
                })
    
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Desplazarse hacia abajo
    time.sleep(5)  # Esperar a que se carguen nuevos elementos
    
    # Obtener el número actual de elementos "search-item"
    elementos_actuales = driver.find_elements(By.CLASS_NAME, "search-item")
    
    # Comparar si el número de elementos ha cambiado
    if len(elementos) != len(elementos_actuales):
        nuevos_elementos_encontrados = True

# Cierra el navegador web
driver.quit()

# Crear un DataFrame de Pandas con los datos
df = pd.DataFrame(data)

# Guardar los datos en un archivo Excel con dos hojas
excel_path = r'C:\Users\administrator\Documents\datos_game.xlsx'
with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
    df.to_excel(writer, sheet_name='Datos sin ordenar', index=False)

    # Ordenar los datos por título y guardarlos en la segunda hoja
    df.sort_values(by='TITULO', inplace=True)
    df.to_excel(writer, sheet_name='Datos ordenados por título', index=False)

    # Abre el archivo Excel
    workbook = writer.book
    worksheet = writer.sheets['Datos sin ordenar']

    # Ajustar el ancho de las columnas (puedes ajustar los valores según tus necesidades)
    worksheet.set_column('A:A', 15)  # Columna A
    worksheet.set_column('B:B', 25)  # Columna B
    worksheet.set_column('C:C', 20)  # Columna C
    worksheet.set_column('D:D', 15)  # Columna D
    worksheet.set_column('E:E', 50)  # Columna E

# Nota: writer.close() no es necesario, ya que el contexto ya se encarga de cerrarlo

print(f'Datos guardados en {excel_path}')
