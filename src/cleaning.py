import pandas as pd

def limpiar_ventas_tienda(df):

    df = df.drop_duplicates().reset_index(drop=True)

    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')

    df['precio_unitario'] = pd.to_numeric(
        df['precio_unitario']
        .astype(str)
        .str.strip()
        .str.replace("$", "", regex=False),
        errors='coerce'
    )

    df['metodo_pago'] = df['metodo_pago'].str.capitalize()

    return df


def limpiar_ventas_online(df):

    df = df.drop_duplicates().reset_index(drop=True)

    df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')

    df.loc[
        ~df['customer_email'].str.contains('@', na=False),
        'customer_email'
    ] = None

    df['status'] = df['status'].str.capitalize()

    return df
