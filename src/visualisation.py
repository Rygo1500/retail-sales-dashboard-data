import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
from config import output_folder, graficos_folder

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
