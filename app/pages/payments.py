import streamlit as st
import pandas as pd
from datetime import datetime
import app
from app.core import Core
from collections import defaultdict
from datetime import datetime
from streamlit_extras.dataframe_explorer import dataframe_explorer
from sample import data as sample_data
from app.util import dataframe_to_pdf


def group_payroll_data(data, group_by="idDetallePeriodo"):
    """
    Agrupa los datos de nómina por un campo específico.
    :param data: Lista de diccionarios con datos de nómina.
    :param group_by: Campo por el cual agrupar los datos.
    :return: Diccionario con los datos agrupados.
    """
    grouped_data = defaultdict(list)
    
    if not data:
        return []
    
    for item in data:
        key = item.get(group_by)
        if key is not None:
            grouped_data[key].append(item)
            
            
    return dict(grouped_data)

    



@st.cache_data(ttl=60 * 60 * 24)
def loan_data(last=False, tipo_concepto=None):
    """
    Obtiene los volantes de pago de los empleados, agrupados por período.

    :param last: Si es True, devuelve solo el último volante.
    :param codigoConcepto: Filtra los datos por el código de concepto.
    :return: Lista de volantes de pago o el último volante si `last` es True.
    """
    #TODO: Cambiar a la base de datos
    st.session_state.payments = sample_data['result']
    
    if 'payments' not in st.session_state:
        return []

    data = st.session_state.payments
    

    if tipo_concepto:
        data = [item for item in data if item.get("tipo_Concepto") == tipo_concepto]

    if not data:
        return []

    # Ordenar los datos por idPeriodo en orden descendente
    sorted_data = sorted(data, key=lambda x: x["idPeriodo"], reverse=True)

    # Agrupar los datos por idPeriodo
    grouped_by_id = group_payroll_data(sorted_data, "idPeriodo")
    if not grouped_by_id:
        return []

    # Formatear los volantes
    volantes = []
    for key, concepto in grouped_by_id.items():
        # Calcular totales
        total_horas = sum(c.get("cantidadHoras", 0) for c in concepto)
        total_ingresos = sum(c.get("valor", 0) for c in concepto if c.get("origen") == 1)
        total_descuentos = sum(c.get("valor", 0) for c in concepto if c.get("origen") == -1)
        total_anterior = sum(c.get("balanceAnterior", 0) for c in concepto)
        total_actual = sum(c.get("balanceActual", 0) for c in concepto)
        total_a_cobrar = total_ingresos - total_descuentos

        # Crear detalles del volante
        detalle = [
            [
               
                c.get("codigoConcepto", ""),
                c.get("nombreConcepto", ""),
                c.get("cantidadHoras", 0),
                c.get("tarifaPago", 0.00),
                c.get("valor", 0) if c.get("origen") == 1 else 0,
                c.get("valor", 0) if c.get("origen") == -1 else 0,
                c.get("balanceAnterior", 0.00),
                c.get("balanceActual", 0.00),
            ]
            for c in concepto
        ]

        # Obtener las fechas de inicio y fin del período
        fecha_inicio = datetime.fromisoformat(concepto[0].get("fechaInicio")).strftime('%d/%m/%Y')
        fecha_fin = datetime.fromisoformat(concepto[0].get("fechaFin")).strftime('%d/%m/%Y')

        # Agregar el volante formateado
        volantes.append({
            "periodo": f"{fecha_inicio} A {fecha_fin}",
            "total_recibido": total_ingresos - total_descuentos,
            "total_horas": total_horas,
            "total_ingresos": total_ingresos,
            "total_descuentos": total_descuentos,
            "total_anterior": total_anterior,
            "total_actual": total_actual,
            "total_a_cobrar": total_a_cobrar,
            "total_conceptos": len(concepto),
            "id_periodo": key,
            "detalle": detalle,
        })

    # Devolver solo el último volante si se solicita
    return volantes[0] if last and volantes else volantes



def mostrar_volantes(last=False):
    """
    Muestra los volantes de pago. Si `last` es True, muestra solo el último volante.
    """
    # Obtener los datos de los volantes
    volantes = loan_data(last=last)

    if not volantes:
        st.caption("No tienes ningún volante de pago")
        return

    if last:
        volantes = [volantes]  # Convertir el último volante en una lista para reutilizar la lógica

    # Botón para volver a la página principal si se muestran todos los volantes
    if not last and st.button("⬅ Volver"):
        app.switch_page("home")

    if not last:
        st.title("📄 Volantes de Pago")

    for volante in volantes:
        with st.container(border=True):
            # Crear el DataFrame con los detalles del volante
            
            df = pd.DataFrame(
                volante["detalle"],
                columns=["Código", "Concepto", "Cantidad de Horas", "Tarifa", "Ingresos", "Descuentos", "Balance Anterior", "Balance Actual"]
            )
            
            totales = df[["Cantidad de Horas", "Tarifa", "Ingresos", "Descuentos", "Balance Anterior", "Balance Actual"]].sum()

            # Enmascarar los balances del volante si es necesario
            if not 'mask_balances' in st.session_state:
                st.session_state.mask_balances = True
                
            if st.session_state.mask_balances:
                volante["detalle"] = [
                    ["****", "****", "****", "****", "****", "****", "****", "****"] for c in volante["detalle"]
                ]
            else:
                #formatear balances
                volante["detalle"] = [
                    [c[0], c[1],c[2],
                    f"$ {format(c[3], ',.2f')}",
                    f"$ {format(c[4], ',.2f')}",
                    f"$ {format(c[5], ',.2f')}",
                    f"$ {format(c[6], ',.2f')}",
                    f"$ {format(c[7], ',.2f')}"] for c in volante["detalle"]
                ]

            df = pd.DataFrame(
                volante["detalle"],
                columns=["Código", "Concepto", "Cantidad de Horas", "Tarifa", "Ingresos", "Descuentos", "Balance Anterior", "Balance Actual"]
            )


            # Calcular sumas y agregar fila de totales al final
            totales["Código"] = "****" if st.session_state.mask_balances else "Total Recibido"
            totales["Concepto"] = "****" if st.session_state.mask_balances else f"$ {format(volante['total_a_cobrar'], ',.2f')}"
            totales["Ingresos"] = "****" if st.session_state.mask_balances else f"$ {format(totales['Ingresos'], ',.2f')}"
            totales["Descuentos"] = "****" if st.session_state.mask_balances else f"$ {format(totales['Descuentos'], ',.2f')}"
            totales["Balance Anterior"] = "****" if st.session_state.mask_balances else f"$ {format(totales['Balance Anterior'], ',.2f')}"
            totales["Balance Actual"] = "****" if st.session_state.mask_balances else f"$ {format(totales['Balance Actual'], ',.2f')}"
            totales["Tarifa"] = "****" if st.session_state.mask_balances else f"$ {format(totales['Tarifa'], ',.2f')}"
            totales["Cantidad de Horas"] = "****" if st.session_state.mask_balances else f"{format(totales['Cantidad de Horas'], ',.2f')}"


            # Agregar la fila de totales al DataFrame
            df_con_totales = pd.concat([df, pd.DataFrame([totales])], ignore_index=True)

            # Mostrar el DataFrame
            st.markdown(f"###### 📅 Período {volante['periodo']}")
            st.dataframe(df_con_totales, use_container_width=True, hide_index=True)
            
            # Mostrar los balances enmascarados o visibles según el estado
            total_a_cobrar = "****" if st.session_state.mask_balances else f"RD$ {format(volante['total_a_cobrar'], ',.2f')}"
            #monto_pagado_text = "****" if st.session_state.mask_balances else f"RD$ {format(monto_pagado, ',.2f')}"


            # Mostrar el total recibido
            col1, _, col2, col3 = st.columns([3, 2, 1, 1])
            with col1:
                st.markdown(
                    f"""
                    <p style="font-size: 16px; font-weight: bold; color: #61a1af;">
                        🏦 Total Recibido: RD$ {total_a_cobrar}
                    </p>
                    """,
                    unsafe_allow_html=True
                )
            with col2:
                # Botón para descargar PDF
                st.download_button(
                    label=":blue[Descargar PDF]",
                    data=dataframe_to_pdf(df_con_totales),
                    file_name="reporte.pdf",
                    mime="application/pdf",
                    type="tertiary"
                )
            with col3:
                if last:
                    if st.button(":blue[Mostrar todos]", type='tertiary'):
                        app.switch_page("payments")