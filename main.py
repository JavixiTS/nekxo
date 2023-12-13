from tkinter import Tk, Button, Frame, filedialog, messagebox, Toplevel, Listbox, Scrollbar, VERTICAL, Label, Radiobutton, IntVar
import mysql.connector
from mysql.connector import Error
from scripts.ProductSearchApp import  ProductSearchApp
from scripts.ProductDataLoader import ProductDataLoader
from flask import Flask
import webbrowser
import os
import threading
import openpyxl
import subprocess
import time



class MainGUI:
    def __init__(self, master):
        self.master = master
        master.title("Menú Principal")
        self.product_loader = ProductDataLoader('C:/Users/administrator/Documents/mezcla4.xlsx')
        self.web_view_opened = False
        self.show_web_button_created = False
        

        # Crear un marco para centrar los botones horizontalmente
        frame = Frame(master)
        frame.pack(pady=20)

        # Crear y agregar los botones al marco
        buttons_data = [
            ("Iniciar Web Scraping", self.BaseDeDatos),
            ("Buscar Productos", self.search_products),
            ("Buscar Productos WEB", self.filtrajeweb),
            ("Mostrar Datos MySQL", self.mostrarSQL),
            ("Mostrar Datos Excel", self.cargardatosExcel),
            ("Salir", master.destroy),
        ]

        for col, (text, command) in enumerate(buttons_data):
            Button(frame, text=text, command=command).grid(row=0, column=col, padx=10)

        # Crear una barra de desplazamiento para la lista
        self.scrollbar = Scrollbar(master, orient=VERTICAL)
        self.scrollbar.pack(side='right', fill='y')

        # Crear una lista con scrollbar
        self.product_list = Listbox(master, yscrollcommand=self.scrollbar.set)
        self.product_list.pack(fill='both', expand=True)
        self.scrollbar.config(command=self.product_list.yview)

    def filtrajeweb(self):
        # Lógica para cargar la base de datos SQL (puedes implementarla aquí)
        print("Cargando URL para filtraje")
        ruta = r'C:\Users\administrator\Documents\proyecto\clase\filtro.py'
        subprocess.run(["python", ruta])

    def mostrarSQL(self):
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
                query = "SELECT * FROM clase2"
                cursor.execute(query)
                rows = cursor.fetchall()

                # Muestra los datos en la interfaz gráfica
                self.product_list.delete(0, 'end')  # Limpia la lista

                for row in rows:
                    product_info = f"ID: {row[0]} - COMPETENCIA: {row[1]} | PRODUCTO: {row[2]} | PLATAFORMAS: {row[3]} | MEJOR_PRECIO: {row[4]} | PRECIO_ORIGINAL: {row[5]} | PRECIO_SEMINUEVO: {row[6]} | REBAJA: {row[7]} | URL: {row[8]}"
                    self.product_list.insert('end', product_info)

                messagebox.showinfo("Carga Exitosa", "Datos cargados desde la base de datos exitosamente.")

                # Agrega un botón para mostrar los datos en la web
                if not self.show_web_button_created:
                    self.sql = True
                    show_web_button = Button(self.master, text="Mostrar en Web", command=self.show_in_web)
                    show_web_button.pack()
                    self.show_web_button_created=True

        except Error as e:
            print("Error al conectarse a la base de datos:", e)
        finally:
            # Cierra la conexión a la base de datos
            if connection.is_connected():
                cursor.close()
                connection.close()
                print("Conexión cerrada")

    def show_in_web(self):
        # Ejecuta app.py o appsql.py según la selección del usuario
        print(f"Ejecutando {'carga de datos en excel' if not self.sql else 'carga de datos SQL'}...")
        ruta = r'C:\Users\administrator\Documents\proyecto\clase\scripts\cargaweb.py'
            
        def run_flask():
            subprocess.run(["python", ruta])

        # Utiliza la clase threading para manejar el hilo del servidor Flask
        flask_thread = threading.Thread(target=run_flask)
        flask_thread.start()


        # Mostrar la web directamente
        if self.sql is None:  # Verifica si es None
            excel_filename = 'C:/Users/administrator/Documents/mezcla4.xlsx'
            self.sql = not os.path.exists(excel_filename)  # Si no existe el archivo Excel, es SQL

        if self.sql:
            # Abre la URL de SQL
            webbrowser.open("http://127.0.0.1:5000/datos_mysql", new=2)
           
        else:
            # Abre automáticamente la URL de Excel
            time.sleep(2)
            webbrowser.open("http://127.0.0.1:5000/mezcla", new=2)
            webbrowser.open("http://127.0.0.1:5000/productos_baratos", new=2)
            webbrowser.open("http://127.0.0.1:5000/orden_productos", new=2)

    def BaseDeDatos(self):
        print("Cargando la base de datos...")
        ruta = r'C:\Users\administrator\Documents\proyecto\clase\scripts\mezcla.py'
        subprocess.run(["python", ruta])

    def cargardatosExcel(self):
        # Cargar datos desde el archivo Excel
        excel_filename = 'C:/Users/administrator/Documents/mezcla4.xlsx'
        if os.path.exists(excel_filename):
            workbook = openpyxl.load_workbook(excel_filename)
            worksheet = workbook.active

            # Obtener todas las filas en el archivo Excel
            rows = list(worksheet.iter_rows(values_only=True))

            # Muestra los datos en la interfaz gráfica
            self.product_list.delete(0, 'end')  # Limpia la lista

            for row in rows:
                product_info = f"COMPETENCIA: {row[0]} | PRODUCTO: {row[1]} | PLATAFORMAS: {row[2]} | MEJOR_PRECIO: {row[3]} | PRECIO_ORIGINAL: {row[4]} | PRECIO_SEMINUEVO: {row[5]} | REBAJA: {row[6]} | URL: {row[7]}"
                self.product_list.insert('end', product_info)
            # Agrega un botón para mostrar los datos en la web
            if not self.show_web_button_created:
                self.sql=None
                show_web_button = Button(self.master, text="Mostrar en Web", command=self.show_in_web)
                show_web_button.pack()
                self.show_web_button_created = True
        else:
            # Si el archivo no existe, muestra un mensaje de error
            messagebox.showerror("Error", "El archivo Excel no se encontró en la ruta especificada.")

    def search_products(self):
        search_window = Toplevel(self.master)
        app = ProductSearchApp(search_window, self.product_loader)

# Si ejecutas este script directamente, crea una instancia de Tk y abre la ventana principal
if __name__ == '__main__':
    root = Tk()
    app = MainGUI(root)
    root.mainloop()
