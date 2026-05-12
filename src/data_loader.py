import pandas as pd
import os
from config import input_folder

def cargar_datos():
    df_tienda = pd.read_csv(os.path.join(input_folder, "proyecto1_ventas_tienda_fisica.csv"))
    df_online = pd.read_excel(os.path.join(input_folder, "proyecto1_ventas_online.xlsx"))
    df_catalogo = pd.read_csv(os.path.join(input_folder, "proyecto1_catalogo_productos.csv"))
    df_devoluciones = pd.read_csv(os.path.join(input_folder, "proyecto1_devoluciones.csv"))

    return df_tienda, df_online, df_catalogo, df_devoluciones
