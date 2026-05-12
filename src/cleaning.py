import pandas as pd

def limpiar_ventas_tienda(df):
    #Eliminar duplicados
    df = df.drop_duplicates()
    df = df.reset_index(drop=True)

    #Unificar fecha
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')

    #Limpiar precio
    df['precio_unitario'] = pd.to_numeric(df['precio_unitario'].astype(str).str.strip().str.replace("$", "", regex=False), errors ='coerce')

    #Normalizar metodo de pago
    df['metodo_pago'] = df['metodo_pago'].str.capitalize()

    return df

def limpiar_ventas_online(df):

    #Eliminar duplicados
    df = df.drop_duplicates()
    df = df.reset_index(drop=True)

    #Unificar fecha
    df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')

    #Anular valores sin @
    df_invalidos = df[~df['customer_email'].str.contains('@', na=False)]
    df.loc[~df['customer_email'].str.contains('@', na=False), 'customer_email'] = None

    #Normalizar status
    df['status'] = df['status'].str.capitalize()

    return df
