import pandas as pd

class ProductDataLoader:
    def __init__(self, excel_path):
        self.product_data_df = pd.read_excel(excel_path)

    def search_product(self, product_name):
        # Filtra los productos por el nombre ingresado
        found_products = self.product_data_df[self.product_data_df['PRODUCTO'].str.contains(product_name, case=False)]
        return found_products.to_dict(orient='records') if not found_products.empty else None
