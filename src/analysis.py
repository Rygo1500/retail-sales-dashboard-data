import os
from config import output_folder

def analizar_devoluciones(df_ventas, df_devoluciones):

    df_devoluciones['motivo'] = df_devoluciones['motivo'].str.capitalize()
    df_devoluciones['reembolsado'] = df_devoluciones['reembolsado'].str.capitalize()

    ruta = os.path.join(output_folder, "devoluciones.csv")
    df_devoluciones.to_csv(ruta, index=False)

    df_analizado = df_ventas.merge(
        df_devoluciones,
        left_on='id_transaccion',
        right_on='ticket_referencia',
        how='left'
    )

    df_analizado['fue_devuelto'] = df_analizado['ticket_referencia'].notna()
    df_analizado.drop(columns='ticket_referencia', inplace=True)

    df_analizado['tasa_devolucion_producto'] = (
        df_analizado.groupby('nombre_producto')['fue_devuelto'].transform('mean')
    )

    df_analizado['tasa_devolucion_canal'] = (
        df_analizado.groupby('canal')['fue_devuelto'].transform('mean')
    )

    return df_analizado
