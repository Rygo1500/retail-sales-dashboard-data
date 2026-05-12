#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
import logging


# 1. Configuracion

# In[2]:


input_folder = "data/input"
output_folder = "data/output"
os.makedirs(output_folder, exist_ok=True)
graficos_folder = "data/output/graficos"
os.makedirs(graficos_folder, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

log_path = os.path.join(output_folder, f"ejecucion_{timestamp}.log")

logging.basicConfig(
     filename=log_path,
     level=logging.INFO,
     format='%(asctime)s - %(levelname)s - %(message)s'
)


# 2. Funciones de limpieza

# In[3]:


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


# 3. Funciones de integracion

# In[4]:


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


# 4. Funciones de calculo

# In[5]:


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


# 5. Funciones de analisis

# In[6]:


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


# 6. Funciones de visualizacion

# In[7]:


def generar_graficos(df):

    #Generar tabla resumen
    df_resumen = (
        df
        .groupby('canal')
        .agg(
            total_ventas=('precio_unitario', 'sum'),
            cantidad_transacciones=('id_transaccion', 'count'),
            ticket_promedio=('precio_unitario','mean'),
            margen_promedio=('margen_porcentual','mean')
        )
        .reset_index()
    )

    df_resumen['total_ventas'] = df_resumen['total_ventas'].round(2)
    df_resumen['ticket_promedio'] = df_resumen['ticket_promedio'].round(2)
    df_resumen['margen_promedio'] = df_resumen['margen_promedio'].round(2)

    df_resumen = df_resumen.sort_values(by='total_ventas', ascending=False)

    df_resumen.columns = [
    'Canal',
    'Total Ventas',
    'Transacciones',
    'Ticket Promedio',
    'Margen Promedio'
    ]

    #Generar tabla top 10
    df_top_productos = (
        df
        .groupby(['nombre_producto', 'categoria'])
        .agg(
            unidades_vendidas=('cantidad', 'sum'),
            ingresos=('total_venta', 'sum'),
            margen=('margen_bruto', 'sum')
        )
        .reset_index()
    )

    df_top_productos = df_top_productos.sort_values(by='ingresos', ascending=False).head(10)

    df_top_productos = df_top_productos.round(2)

    df_top_productos.columns = [
        'Producto',
        'Categoría',
        'Unidades Vendidas',
        'Ingresos',
        'Margen'
    ]

    #Generar tabla tiendas

    df_tiendas = df[df['canal'] == 'Tienda']

    ventas_vendedor = (
        df_tiendas
        .groupby(['sucursal', 'vendedor'])['total_venta']
        .sum()
        .reset_index()
    )

    mejor_vendedor = ventas_vendedor.loc[
    ventas_vendedor.groupby('sucursal')['total_venta'].idxmax()
    ]

    df_sucursal = (
        df_tiendas
        .groupby('sucursal')
        .agg(
            total_ventas=('total_venta', 'sum'),
            transacciones=('id_transaccion', 'count'),
            tickeckt_promedio=('total_venta', 'mean')
        )
        .reset_index()
    )

    df_sucursal = df_sucursal.merge(
        mejor_vendedor[['sucursal', 'vendedor']],
        on='sucursal',
        how='left'
    )

    df_sucursal = df_sucursal.round(2)

    df_sucursal.columns = [
        'Sucursal',
        'Total Ventas',
        'Transacciones',
        'Ticket Promedio',
        'Mejor Vendedor'
    ]

    #Leer devoluciones y unificar tablas en excel

    ruta_devoluciones = os.path.join(output_folder, "devoluciones.csv")

    df_devoluciones = pd.read_csv(ruta_devoluciones)

    ruta_excel = os.path.join(output_folder, "reporte_final.xlsx")

    with pd.ExcelWriter(ruta_excel, engine='openpyxl') as writer:

        df_resumen.to_excel(
            writer,
            sheet_name='Resumen General',
            index=False
        )

        df_top_productos.to_excel(
            writer,
            sheet_name='Top Productos',
            index=False
        )

        df_sucursal.to_excel(
            writer,
            sheet_name='Por Surcursal',
            index=False
        )

        df_devoluciones.to_excel(
            writer,
            sheet_name='Devoluciones',
            index=False
        )
    os.remove(ruta_devoluciones)

    #Crear y guardar grafico ventas por canal

    ventas_canal = (
        df
        .groupby('canal')['total_venta']
        .sum()
        .reset_index()
    )

    plt.figure(figsize=(8,5))

    plt.bar(
        ventas_canal['canal'],
        ventas_canal['total_venta']
    )

    plt.title("Ventas por canal")
    plt.xlabel("Canal")
    plt.ylabel("Total Ventas")

    ruta_grafico = os.path.join(graficos_folder, "ventas_por_canal.png")

    plt.savefig(ruta_grafico, bbox_inches='tight')

    plt.close()

    #Crear y guardar grafico de evolucion de ventas

    fecha_max = df['fecha_venta'].max()

    ultimos_30 = df[
        df['fecha_venta'] >= fecha_max - pd.Timedelta(days=30)
    ]

    ventas_diarias = (
        ultimos_30
        .groupby('fecha_venta')['total_venta']
        .sum()
        .reset_index()
    )

    plt.figure(figsize=(10,5))

    plt.plot(
        ventas_diarias['fecha_venta'],
        ventas_diarias['total_venta']
    )

    plt.title("Evolucion de Ventas")
    plt.xlabel("Fecha")
    plt.ylabel("Ventas")
    plt.xticks(rotation=45)

    plt.tight_layout()

    ruta_grafico = os.path.join(graficos_folder, "evolucion_ventas.png")

    plt.savefig(ruta_grafico, bbox_inches='tight')

    plt.close()

    #Crear y guardar grafico top productos

    top_productos = (
        df
        .groupby('nombre_producto')['total_venta']
        .sum()
        .reset_index()
        .sort_values(by='total_venta', ascending=True)
        .head(10)
    )

    plt.figure(figsize=(10,6))

    plt.barh(
        top_productos['nombre_producto'],
        top_productos['total_venta']
    )

    plt.title("Top 10 Productos porr Ventas")
    plt.xlabel("Ingresos")
    plt.ylabel("Producto")

    plt.tight_layout()

    ruta_grafico = os.path.join(graficos_folder, "top_10_productos.png")

    plt.savefig(ruta_grafico, bbox_inches='tight')

    plt.close()

    #Crear y guardar grafico de distribucion de ventas

    ventas_categoria = (
        df
        .groupby('categoria')['total_venta']
        .sum()
        .reset_index()
    )

    plt.figure(figsize=(8,8))

    plt.pie(
        ventas_categoria['total_venta'],
        labels=ventas_categoria['categoria'],
        autopct='%1.1f%%'
    )

    plt.title("Distribución de Ventas por Categoría")

    ruta_grafico = os.path.join(graficos_folder, "ventas_por_categoria.png")

    plt.savefig(ruta_grafico, bbox_inches='tight')

    plt.close()

    #Crear y guardar grafico ventas dias de la semana vs hora del dia

    df['hora'] = pd.to_datetime(
        df['hora'],
        format='%H:%M',
        errors='coerce'
    )

    df['hora_heatmap'] = df['hora'].dt.hour

    heatmap_data = df.pivot_table(
        values='total_venta',
        index='dia_semana',
        columns='hora_heatmap',
        aggfunc='sum',
        fill_value=0
    )

    orden_dias = [
        'Lunes',
        'Martes',
        'Miércoles',
        'Jueves',
        'Viernes',
        'Sábado',
        'Domingo'
    ]

    heatmap_data = heatmap_data.reindex(orden_dias)

    plt.figure(figsize=(12,6))

    sns.heatmap(
        heatmap_data,
        annot=False,
        cmap='Blues'
    )


    plt.title("Heatmap de Ventas por Día y Hora")
    plt.xlabel("Hora")
    plt.ylabel("Día")

    ruta_grafico = os.path.join(graficos_folder, "heatmap_ventas.png")

    plt.savefig(ruta_grafico, bbox_inches='tight')

    plt.close()

    #Generar y guardar grafico top devoluciones

    tasa_devolucion = (
        df
        .groupby('nombre_producto')['fue_devuelto']
        .mean()
        .reset_index()
    )

    tasa_devolucion['tasa_devolucion'] = (
        tasa_devolucion['fue_devuelto'] *100
    )

    top_devoluciones=(
        tasa_devolucion
        .sort_values(by='tasa_devolucion', ascending=True)
        .head(10)
    )

    plt.figure(figsize=(10,6))

    plt.barh(
        top_devoluciones['nombre_producto'],
        top_devoluciones['tasa_devolucion']
    )

    plt.title("Top 10 Productos con Mayor Tasa de Devolución")
    plt.xlabel("Tasa de Devolución (%)")
    plt.ylabel("Producto")

    plt.tight_layout()

    ruta_grafico = os.path.join(graficos_folder, "grafico_devoluciones.png")

    plt.savefig(ruta_grafico, bbox_inches='tight')

    plt.close()

    pass


# 7. Funcion principal

# In[8]:


def main():

    logging.info(f"Iniciando proceso: {datetime.now()}")

    #======================
    #1. CARGAR DATOS
    #======================

    df_tienda = pd.read_csv(
        os.path.join(input_folder, "proyecto1_ventas_tienda_fisica.csv")
    )

    df_online = pd.read_excel(
        os.path.join(input_folder, "proyecto1_ventas_online.xlsx")
    )

    df_catalogo = pd.read_csv(
        os.path.join(input_folder, "proyecto1_catalogo_productos.csv")
    )

    df_devoluciones = pd.read_csv(
        os.path.join(input_folder, "proyecto1_devoluciones.csv")
    )

    logging.info("Datos cargados")

    #======================
    #2. LIMPIAR DATOS
    #======================

    df_tienda = limpiar_ventas_tienda(df_tienda)

    df_online = limpiar_ventas_online(df_online)

    logging.info("Datos limpiados")

    #======================
    #3. CONSOLIDAR DATOS
    #======================

    df_consolidado = consolidar_ventas(
        df_tienda,
        df_online,
        df_catalogo
    )

    logging.info("Datos consolidados")


    #======================
    #4. CALCULAR METRICAS
    #======================

    df_consolidado = calcular_metricas(df_consolidado)

    logging.info("Metricas calculadas")

    #======================
    #5. ANALIZAR DEVOLUCIONES
    #======================

    df_final = analizar_devoluciones(df_consolidado,df_devoluciones)

    logging.info("Devoluciones analizadas")

    #======================
    #5. GENERAR REPORTES    
    #======================

    generar_graficos(df_final)

    logging.info("Graficos creados")

    logging.info("Proceso completado")

if __name__ == "__main__":
    main()

