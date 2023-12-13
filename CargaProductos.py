import pandas as pd
import re

class CargaProductos:
    def __init__(self, excel_filename):
        self.excel_filename = excel_filename
        self.product_data = self.load_data_from_excel()

    def load_data_from_excel(self):
        df = pd.read_excel(self.excel_filename, sheet_name='MEZCLA')
        return df.to_dict(orient='records')

    def search_product(self, term, filter_type, competencia=None):
        patterns = [re.compile(rf'.*{re.escape(keyword)}.*', re.I) for keyword in term.split()]
        matching_products = []

        try:
            # Si la competencia es mixta, considerar todos los productos directamente
            if competencia and competencia.lower() == 'mixtas':
                filtered_by_competencia = self.product_data
            else:
                # Filtrar por competencia si se proporciona
                filtered_by_competencia = [product for product in self.product_data if
                                            competencia and competencia.lower() == str(product.get("COMPETENCIA", "")).lower()]

            # Aplicar la búsqueda específica según el filter_type y el término
            for product in filtered_by_competencia:

                if filter_type == "mixta":
                    # Si filter_type es "mixta", agregar todos los productos
                    matching_products.append(product)
                elif filter_type != "Competencia" and all(pattern.search(str(product.get(filter_type, ''))) for pattern in patterns):
                    matching_products.append(product)
        except KeyError as e:
            print(f"Error: Clave faltante ({e}) en un producto.")

        return matching_products








