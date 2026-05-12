import pandas as pd
import os
from config import output_folder

def consolidar_ventas(df_tienda, df_online, df_catalogo):

    #Estandarizar columnas
    
    df_tienda.columns = ['fecha_venta', 'hora', 'id_transaccion', 'sucursal', 'nombre_producto', 'cantidad', 'precio_unitario', 'vendedor', 'metodo_pago']
    df_online.columns = ['fecha_venta', 'id_transaccion', 'nombre_producto', 'cantidad', 'precio_unitario', 'customer_email', 'city', 'status', 'shipping_cost']

    #Añadir canal
    df_tienda['canal'] = 'Tienda'
    df_online['canal'] = 'Online'

    #Añadir info de producto
    df_tienda = pd.merge(df_tienda, df_catalogo, left_on="nombre_producto", right_on="producto", how="left")
    df_online = pd.merge(df_online, df_catalogo, left_on="nombre_producto", right_on="producto", how="left")

    #Consolidar df
    df_consolidado = pd.concat([df_tienda, df_online], axis = 0, ignore_index = True)

    return df_consolidado


def calcular_metricas(df):

    df['total_venta'] = df['cantidad'] * df['precio_unitario']
    df['costo_total'] = df['cantidad'] * df['costo']
    df['margen_bruto'] = df['total_venta'] - df['costo_total']
    df['margen_porcentual'] = (df['margen_bruto'] / df['total_venta']) * 100

    #Calcular dia de la semana en español usando mapeo
    
    dias = {
    'Monday': 'Lunes',
    'Tuesday': 'Martes',
    'Wednesday': 'Miércoles',
    'Thursday': 'Jueves',
    'Friday': 'Viernes',
    'Saturday': 'Sábado',
    'Sunday': 'Domingo'
    }

    df['dia_semana'] = df['fecha_venta'].dt.day_name().map(dias)

    #Calcular numero semana del mes

    df['semana_del_mes'] = df['fecha_venta'].apply(lambda x: (x.day + x.replace(day=1).weekday()) // 7+1)

    #Calcular hora del dia

    df['hora_num'] = pd.to_datetime(
        df['hora'],
        errors='coerce'
    ).dt.hour

    df['hora_del_dia'] = df['hora_num'].apply(
        lambda h: 'mañana' if pd.notna(h) and 6 <= h <12
        else 'tarde' if pd.notna(h) and 12 <= h < 18
        else 'noche' if pd.notna(h)
        else None
    )

    df.drop(columns='hora_num', inplace=True)

    #Guardar df
    ruta = os.path.join(output_folder, "ventas_consolidadas.csv")
    df.to_csv(ruta, index=False)

    return df
