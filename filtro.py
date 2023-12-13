from flask import Flask, render_template, request, session, jsonify
from CargaProductos import CargaProductos
import mysql.connector
import webbrowser
import pandas as pd
import subprocess
import queue
import threading
from flask_socketio import SocketIO

app = Flask(__name__)
app.secret_key = 'javi'  # Cambia esto por una clave secreta segura
socketio = SocketIO(app)  # Inicializa SocketIO

output_queue = queue.Queue()
output_thread = None

# Ruta para la página principal con el formulario
@app.route('/')
def index():
    # Lógica de búsqueda en MySQL para mostrar resultados por defecto
    default_category = "Competencia"  # Puedes ajustar esto según tu necesidad
    default_term = session.get('term', '')
    resultados_mysql = buscar_en_mysql(default_category, default_term, session.get('competencia', ''))

    return render_template('web.html', resultados=resultados_mysql)

# Ruta para procesar la búsqueda desde el formulario
@app.route('/buscar', methods=['POST'])
def buscar():
    source = request.form['source']
    category = request.form['category']
    term = request.form['term'].lower()
    if 'competencia' not in request.form:
        # Manejar el caso en el que 'competencia' no está presente en el formulario
        return render_template('web.html', mensaje="Error: competencia no especificada en el formulario.")
    else:
        competencia = request.form['competencia']

    # Almacenar el término de búsqueda y la categoría en la sesión
    session['term'] = term
    session['category'] = category
    session['source'] = source
    session['competencia'] = competencia  # Almacenar la competencia seleccionada

    if source == "MySQL":
        # Lógica de búsqueda en MySQL
        resultados = buscar_en_mysql(category, term, competencia)
    elif source == "Excel":
        # Lógica de búsqueda en Excel
        productos_loader = CargaProductos('C:/Users/administrator/Documents/mezcla.xlsx')
        resultados = buscar_en_excel(productos_loader, category, term, competencia)

    # Renderizar la página de resultados
    return render_template('web.html', resultados=resultados)


@app.route('/carga_mysql', methods=['GET'])
def cargasql():
    # Conectar a la base de clase (utilizando la configuración de Flask)
    connection = mysql.connector.connect(
        user='root',
        password='javi',
        host='localhost',
        database='bdmysql'
    )
        
    query = "SELECT * FROM clase6"
           
    with connection.cursor(dictionary=True) as cursor:
        cursor.execute(query)
        results = cursor.fetchall()

    return render_template('filtraje.html', es_excel=False, resultados=results)

@app.route('/abrir_excel', methods=['GET'])
def abrir_excel():
    # Lógica para abrir el archivo Excel
    # Puedes utilizar openpyxl u otra biblioteca para manipular archivos Excel
    resultados = cargarExcel('C:/Users/administrator/Documents/mezcla6.xlsx','MEZCLA')

    return render_template('filtraje.html',es_excel=True, resultados=resultados)

def cargarExcel(excel_filename, sheet_name):
    cheapest_products_list = []
    try:
        df = pd.read_excel(excel_filename, sheet_name=sheet_name)
        if not df.empty:
            cheapest_products_list = df.to_dict(orient='records')
    except Exception as e:
        print(f"Error al cargar datos desde Excel: {str(e)}")

    return cheapest_products_list


# En la función buscar_en_mysql
def buscar_en_mysql(category, term, competencia):
    # Conectar a la base de clase (utilizando la configuración de Flask)
    connection = mysql.connector.connect(
        user='root',
        password='javi',
        host='localhost',
        database='bdmysql'
    )

    try:
        if competencia and competencia.lower() == 'mixtas':
            # Si la competencia es "Mixtas"
            if term == "":
                # Si no hay término de búsqueda, muestra todos los datos excepto los que no tienen competencia
                query = "SELECT * FROM clase WHERE COMPETENCIA IS NOT NULL AND COMPETENCIA != ''"
                params = None
            else:
                # Si hay un término de búsqueda, ajusta la lógica para buscar en las columnas correspondientes a las categorías "Producto", "Disco_Duro" y "Memoria"
                query = f"SELECT * FROM clase WHERE {category} LIKE %(term)s"
                params = {'term': f'%{term}%'}

        else:
            # En otros casos, aplica el filtro según la lógica anterior
            query = "SELECT * FROM clase WHERE "
            if term:
                query += f"{category} LIKE %(term)s AND (COMPETENCIA = %(competencia)s OR COMPETENCIA IS NULL OR COMPETENCIA = '')"
                params = {'term': f'%{term}%', 'competencia': competencia}
            else:
                query += "1"  # True para seleccionar todos los registros
                params = None

        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(query, params)
            results = cursor.fetchall()

    finally:
        connection.close()

    return results

def search_excel_results(productos_loader, filter_type, search_term):
    if filter_type == "Competencia":
        found_products = productos_loader.search_product(search_term, "COMPETENCIA")
    elif filter_type == "Producto":
        found_products = productos_loader.search_product(search_term, "PRODUCTO")
    elif filter_type == "Plataformas":
        found_products = productos_loader.search_product(search_term, "PLATAFORMAS")
    else:
        found_products = []
    # Puedes realizar acciones adicionales aquí, si es necesario

    return found_products  # Devuelve los resultados de la búsqueda

def buscar_en_excel(productos_loader, category, term, competencia):
    if category == "Producto":
        found_products = productos_loader.search_product(term, "PRODUCTO", competencia)
    elif category == "Plataformas":
        found_products = productos_loader.search_product(term, "PLATAFORMAS", competencia)
    else:
        found_products = []

    # Puedes realizar acciones adicionales aquí, si es necesario

    return found_products

@app.route('/ejecutar_mezcla', methods=['POST'])
def ejecutar_mezcla():
    global output_thread
    output_thread = threading.Thread(target=run_mezcla_script)
    output_thread.start()

    # Esperar a que el script haya terminado antes de devolver la respuesta
    output_thread.join()

    # Ahora que el script ha terminado, configurar la variable para mostrar los formularios
    mostrar_formularios = True

    # Devolver una respuesta JSON
    return jsonify({'mensaje': "Proceso completado.", 'mostrar_formularios': mostrar_formularios})


# Ruta para obtener la salida del script mezcla.py
@app.route('/get_output', methods=['GET'])
def get_output():
    lines = []
    while not output_queue.empty():
        lines.append(output_queue.get())
    return jsonify({'output': lines})

# Función para manejar la conexión del socket
@socketio.on('connect')
def handle_connect():
    print('Client connected')

# Función para manejar la desconexión del socket
@socketio.on('disconnect')
def handle_disconnect():
    
    print('Client disconnected')

def run_mezcla_script():
    try:
        process = subprocess.Popen(
            ['python', '-u', 'clase\\scripts\\mezcla.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        for line in process.stdout:
            socketio.emit('output', {'data': line.strip()})
            print(line, end='', flush=True)
        process.wait()
        if process.returncode == 0:
            socketio.emit('output', {'data': 'Script mezcla.py ejecutado con éxito.'})
        else:
            socketio.emit('output', {'data': f"Error al ejecutar el script mezcla.py. Código de salida: {process.returncode}"})
    except Exception as e:
        socketio.emit('output', {'data': f"Error inesperado: {str(e)}"})

if __name__ == '__main__':
    webbrowser.open('http://localhost:5000')
    socketio.run(app, debug=True)