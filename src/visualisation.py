import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
from config import output_folder, graficos_folder

def generar_graficos(df):

    os.makedirs(graficos_folder, exist_ok=True)

    ventas_canal = (
        df.groupby('canal')['total_venta']
        .sum()
        .reset_index()
    )

    plt.figure()
    plt.bar(ventas_canal['canal'], ventas_canal['total_venta'])
    plt.title("Ventas por canal")

    plt.savefig(os.path.join(graficos_folder, "ventas_por_canal.png"))
    plt.close()

    # Evolución ventas
    fecha_max = df['fecha_venta'].max()

    ultimos_30 = df[
        df['fecha_venta'] >= fecha_max - pd.Timedelta(days=30)
    ]

    ventas_diarias = (
        ultimos_30.groupby('fecha_venta')['total_venta']
        .sum()
        .reset_index()
    )

    plt.figure()
    plt.plot(ventas_diarias['fecha_venta'], ventas_diarias['total_venta'])

    plt.savefig(os.path.join(graficos_folder, "evolucion_ventas.png"))
    plt.close()

    # Heatmap
    df['hora'] = pd.to_datetime(df['hora'], errors='coerce')
    df['hora_heatmap'] = df['hora'].dt.hour

    heatmap_data = df.pivot_table(
        values='total_venta',
        index='dia_semana',
        columns='hora_heatmap',
        aggfunc='sum',
        fill_value=0
    )

    plt.figure()
    sns.heatmap(heatmap_data)

    plt.savefig(os.path.join(graficos_folder, "heatmap_ventas.png"))
    plt.close()
