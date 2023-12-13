from flask import Flask, render_template, request
import pandas as pd
from mezcla import WebScraper
import mysql.connector
import os

app = Flask(__name__)

# Define las URL de los conjuntos de productos
product_urls_set1 = [
    "https://www.eneba.com/es/store/games",
    "https://www.instant-gaming.com/en/search/?system=playstation&version=2&page=",
]

@app.route('/')
def index():
    # Esta función es para la página de inicio que ya tenías
    scraper = WebScraper(product_urls_set1)  # Cambia a product_urls_set1 para mostrar el primer conjunto
    scraper.scrape_data()
    product_data = scraper.get_data()
    return render_template('index.html', data=product_data)


@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.form.get('url')  # Obtiene la URL del formulario HTML

    if url:
        # Crea una instancia de WebScraper y llama a scrape_data para obtener los datos
        scraper = WebScraper(url)
        scraper.scrape_data()
        product_data = scraper.get_data()
        return render_template('index.html', product_data=product_data)
    else:
        return render_template('index.html', product_data=None)
    
def load_cheapest_products_from_excel(excel_filename, sheet_name):
    cheapest_products_list = []
    try:
        df = pd.read_excel(excel_filename, sheet_name=sheet_name)
        if not df.empty:
            cheapest_products_list = df.to_dict(orient='records')
    except Exception as e:
        print(f"Error al cargar datos desde Excel: {str(e)}")

    return cheapest_products_list



@app.route('/productos_baratos')
def productos_baratos():
    # Tu código para encontrar los productos más baratos y exportarlos a un archivo Excel
    # Asegúrate de definir la variable cheapest_products_list
    cheapest_products_list = load_cheapest_products_from_excel('C:/Users/administrator/Documents/mezcla.xlsx', 'MEZCLA')

    # Ordena la lista de productos por el campo MEJOR_PRECIO
    cheapest_products_list.sort(key=lambda product: product['MEJOR_PRECIO'])

    return render_template('productos_baratos.html', products=cheapest_products_list)

@app.route('/orden_productos')
def orden_productos():
    # Tu código para encontrar los productos más baratos y exportarlos a un archivo Excel
    # Asegúrate de definir la variable cheapest_products_list

    cheapest_products_list = load_cheapest_products_from_excel('C:/Users/administrator/Documents/mezcla.xlsx', 'MEZCLA')

    # Ordena la lista de productos alfabéticamente por el nombre del producto
    cheapest_products_list.sort(key=lambda product: product['PRODUCTO'])  # Suponiendo que el nombre del producto se encuentra en la clave 'nombre'

    return render_template('productos_ordenados.html', products=cheapest_products_list)

@app.route('/mezcla')
def mezcla():
    # Carga los datos de la hoja "MEZCLA"
    cheapest_products_list = load_cheapest_products_from_excel('C:/Users/administrator/Documents/mezcla.xlsx', 'MEZCLA')
    return render_template('productos.html', products=cheapest_products_list)

@app.route('/datos_mysql')
def datos_mysql():
    try:
        # Configura la conexión a la base de datos MySQL
        connection = mysql.connector.connect(
            user='root',
            password='javi',
            host='localhost',
            database='bdmysql'
        )

        if connection.is_connected():
            # Realiza una consulta SQL para obtener datos de la base de datos
            cursor = connection.cursor()
            query = "SELECT * FROM clase"
            cursor.execute(query)
            rows = cursor.fetchall()

            # Muestra los datos en la interfaz web
            df = pd.DataFrame(rows, columns=[desc[0] for desc in cursor.description])
            data_from_mysql = df.to_dict(orient='records')

            return render_template('datos_mysql.html', data=data_from_mysql)

    except mysql.connector.Error as e:
        print("Error al conectarse a la base de datos MySQL:", e)
        return render_template('error.html', message='Error al conectarse a la base de datos MySQL.')

    finally:
        # Cierra la conexión a la base de datos
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Conexión MySQL cerrada")

if __name__ == '__main__':
    app.run(debug=True)
