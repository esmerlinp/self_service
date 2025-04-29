import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import app



    
    
def generar_tabla_cuotas(monto_total=10000.0, cuotas_totales=24, cuotas_pagadas=6, fecha_inicio=datetime.today()):
    """Genera una tabla con las cuotas del préstamo."""
    
    monto_cuota = monto_total / cuotas_totales  # Monto fijo por cuota (sin interés compuesto)
    
    # Crear una lista de cuotas
    cuotas = []
    for i in range(1, cuotas_totales + 1):
        estado = "Pagada" if i <= cuotas_pagadas else "Pendiente"
        fecha_pago = fecha_inicio + timedelta(days=30 * (i - 1))  # Simulación de pago mensual
        cuotas.append([i, f"${monto_cuota:,.2f}", fecha_pago.strftime("%d-%m-%Y"), estado])

    # Convertir la lista en un DataFrame de Pandas
    df = pd.DataFrame(cuotas, columns=["N° Cuota", "Monto", "Fecha de Pago", "Estado"])
    
    return df


def loan_chart():
    # Datos del préstamo
    pagado = 60  # Porcentaje pagado
    pendiente = 100 - pagado  # Porcentaje restante

    # Crear gráfico de anillo (doughnut chart)
    fig = go.Figure(data=[go.Pie(
        labels=["Pagado", "Pendiente"],
        values=[pagado, pendiente],
        hole=0.7,  # Tamaño del agujero central
        marker=dict(colors=["#4CAF50", "#FF9800"]),  # Colores
        textinfo="percent+label"
    )])

    # Configurar diseño
    fig.update_layout(
        title_text="Estado del Préstamo",
        showlegend=False,
        annotations=[dict(
            text=f"{pagado}%",  # Texto en el centro
            x=0.5, y=0.5,  # Posición centrada
            font_size=20,
            showarrow=False
        )]
    )

    st.plotly_chart(fig, use_container_width=True)
    
    
def loans():
        # Botón para volver a la página principal

    if st.button(":gray[/ Inicio /] :blue[Préstamos]", type="tertiary"):
        app.switch_page("home")
        
    st.title("Seguimiento de Pago de Préstamo")



    loan_chart()
    

    
    # Obtener los datos del préstamo
    # Mostrar el gráfico
    

    # Mostrar la tabla de cuotas
    st.subheader("Cuotas del Préstamo")
    df_cuotas = generar_tabla_cuotas()
    st.dataframe(df_cuotas, use_container_width=True)
