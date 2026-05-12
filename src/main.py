from data_loader import cargar_datos
from cleaning import limpiar_ventas_tienda, limpiar_ventas_online
from transformation import consolidar_ventas, calcular_metricas
from analysis import analizar_devoluciones
from visualization import generar_graficos

def main():

    df_tienda, df_online, df_catalogo, df_devoluciones = cargar_datos()

    df_tienda = limpiar_ventas_tienda(df_tienda)
    df_online = limpiar_ventas_online(df_online)

    df_consolidado = consolidar_ventas(
        df_tienda,
        df_online,
        df_catalogo
    )

    df_consolidado = calcular_metricas(df_consolidado)

    df_final = analizar_devoluciones(
        df_consolidado,
        df_devoluciones
    )

    generar_graficos(df_final)


if __name__ == "__main__":
    main()
