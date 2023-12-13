from tkinter import Tk,Label, Entry, Button, Listbox, Scrollbar, VERTICAL
from tkinter import Tk, Label, Entry, Button, Listbox, Scrollbar, VERTICAL
import os
import pandas as pd
from tkinter import simpledialog
from scripts.ProductDataLoader import ProductDataLoader

class ProductSearchApp:
    def __init__(self, master, product_loader=None):
        self.master = master
        master.title("Búsqueda de Productos")

        # Ajusta el tamaño de la ventana principal
        master.geometry("800x400")

        self.label = Label(master, text="Nombre del Producto:")
        self.label.pack()

        self.entry = Entry(master)
        self.entry.pack()

        self.search_button = Button(master, text="Buscar", command=self.search_product)
        self.search_button.pack()

        self.save_to_excel_button = Button(master, text="Guardar a Excel", state="disabled", command=self.save_to_excel)
        self.save_to_excel_button.pack()

        self.load_from_excel_button = Button(master, text="Cargar desde Excel", command=self.load_from_excel)
        self.load_from_excel_button.pack()

        # Crea un scrollbar para la lista
        self.scrollbar = Scrollbar(master, orient=VERTICAL)
        self.scrollbar.pack(side='right', fill='y')

        # Crea una lista con scrollbar
        self.product_list = Listbox(master, yscrollcommand=self.scrollbar.set)
        self.product_list.pack(fill='both', expand=True)
        self.scrollbar.config(command=self.product_list.yview)

        # Almacena la referencia al product loader
        self.product_loader = product_loader

        self.results = []  # Almacena los resultados de la búsqueda

    def search_product(self):
        product_name = self.entry.get()
        self.product_list.delete(0, 'end')  # Limpia la lista

        # Busca el producto en los datos cargados
        found_products = self.product_loader.search_product(product_name)
        if found_products:
            for product in found_products:
                product_info = f"COMPETENCIA: {product['COMPETENCIA']} | PRODUCTO: {product['PRODUCTO']} | PLATAFORMAS: {product['PLATAFORMAS']} | MEJOR_PRECIO: {product['MEJOR_PRECIO']} | PRECIO_ORIGINAL: {product['PRECIO_ORIGINAL']} | PRECIO_SEMINUEVO: {product['PRECIO_SEMINUEVO']} | REBAJA: {product['REBAJA']} | URL: {product['URL']}"
                self.product_list.insert('end', product_info)
            self.save_to_excel_button["state"] = "active"  # Activa el botón Guardar a Excel
            self.results = found_products  # Almacena los resultados de la búsqueda
        else:
            print(f"No se encontraron productos con el nombre {product_name}")

    def save_to_excel(self):
        if self.results:
            # Crea un DataFrame de pandas con los resultados
            df = pd.DataFrame(self.results)

            # Guarda el DataFrame en un archivo Excel
            excel_filename = 'C:/Users/administrator/Documents/productos_busqueda.xlsx'

            with pd.ExcelWriter(excel_filename, engine='xlsxwriter') as writer:
                # Exporta los datos a la hoja 'MEZCLA'
                df.to_excel(writer, sheet_name='MEZCLA', index=False)
                # Obtén el libro de Excel y la hoja
                workbook = writer.book
                worksheet_mezcla = writer.sheets['MEZCLA']
                # Define un formato con un fondo gris para los títulos
                title_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bg_color': '#D3D3D3', 'border': 1})
                # Aplica el formato a la primera fila (que contiene los títulos) en la hoja 'MEZCLA'
                for col_num, value in enumerate(df.columns.values):
                    worksheet_mezcla.write(0, col_num, value, title_format)
                # Define un formato para centrar y agregar un borde a las celdas
                cell_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1})
                # Aplica el formato a todas las celdas en la hoja 'MEZCLA'
                for col_num, value in enumerate(df.columns.values):
                    max_len = max([len(str(value))] + [len(str(i)) for i in df.iloc[:, col_num]])
                    worksheet_mezcla.set_column(col_num, col_num, max_len + 2, cell_format)
            print(f"Resultados guardados en '{excel_filename}'")

    def load_from_excel(self):
        # Cargar datos desde el archivo Excel
        excel_filename = 'C:/Users/administrator/Documents/productos_busqueda.xlsx'
        if os.path.exists(excel_filename):
            os.system('start excel.exe "{}"'.format(excel_filename))
        else:
            # Si el archivo no existe, muestra un mensaje de error
            print("El archivo Excel no se encontró en la ruta especificada.")

if __name__ == '__main':
    
    root = Tk()
    app = ProductSearchApp(root)
    root.mainloop()
