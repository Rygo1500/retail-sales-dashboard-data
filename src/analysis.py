import os
from config import output_folder

def analizar_devoluciones(df_ventas,df_devoluciones):

    #Normaliszar campos
    df_devoluciones['motivo'] = df_devoluciones['motivo'].str.capitalize()
    df_devoluciones['reembolsado'] = df_devoluciones['reembolsado'].str.capitalize()

    #Guardar df
    ruta = os.path.join(output_folder, "devoluciones.csv")
    df_devoluciones.to_csv(ruta, index=False)

    #Merge ventas y devoluciones
    df_analizado = df_ventas.merge(
        df_devoluciones,
        left_on='id_transaccion',
        right_on='ticket_referencia',
        how='left'
    )

    #Verificar si la transaccion fue devuelta
    df_analizado['fue_devuelto'] = df_analizado['ticket_referencia'].notna()
    df_analizado = df_analizado.drop(columns='ticket_referencia')

    #Calcular tasas de devolucion
    df_analizado['tasa_devolucion_producto'] = df_analizado.groupby('nombre_producto')['fue_devuelto'].transform('mean')
    df_analizado['tasa_devolucion_canal'] = df_analizado.groupby('canal')['fue_devuelto'].transform('mean')

    return df_analizado
