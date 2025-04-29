import streamlit as st
import pandas as pd
from datetime import datetime
import app
from collections import defaultdict
from datetime import datetime
from sample import data as sample_data
from app.core import get_payments

# from weasyprint import HTML
# import tempfile

# def generar_pdf(html_code, filename="volante.pdf"):
#     pdf = HTML(string=html_code).write_pdf()
#     temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
#     with open(temp_pdf.name, "wb") as f:
#         f.write(pdf)
#     return temp_pdf.name


def generar_html_volante(volante):
    """
    Genera el HTML dinámico para el volante de pago basado en los datos del volante.
    :param volante: Diccionario con los datos del volante.
    :return: Cadena de HTML.
    """
    # Crear filas dinámicas para los detalles del pago
    detalles_html = ""
    for detalle in volante["detalle"]:
        detalles_html += f"""
        <tr>
            <td>{detalle[1]}</td> <!-- Concepto -->
            <td style="text-align: right;">{detalle[4]}</td> <!-- Ingresos -->
            <td style="text-align: right;">{detalle[5]}</td> <!-- Descuentos -->
            <td style="text-align: right;">{detalle[6]}</td> <!-- Balance Anterior -->
            <td style="text-align: right;">{detalle[7]}</td> <!-- Balance Actual -->
        </tr>
        """

    # Crear el HTML completo
    html_code = f"""
    <div style="font-family: sans-serif; max-width: 800px; margin: auto; background: white; padding: 24px; border-radius: 8px;">
      <h2 style="text-align: center; color: #333;">Volante de Pago de Nómina</h2>
      <p style="text-align: center; color: #666;">{volante['periodo']}</p>
      <hr />
      <div style="margin-bottom: 16px;">
        <strong>Empleado:</strong> {st.session_state.employee.get('nombreCompletoEmpleado')}<br />
        <strong>ID:</strong> {st.session_state.employee.get('idEmpleado')}<br />
        <strong>Cargo:</strong> {st.session_state.employee.get('nombre_Puesto')}<br />
        <strong>Departamento:</strong> {st.session_state.employee.get('nombre_Departamento')}<br />
        <strong>Período de Pago:</strong> {volante['periodo']}
      </div>
      <h3 style="color: #333;">Detalles del Pago</h3>
      <table style="width: 100%; font-size: 14px; border-collapse: collapse; text-align: left;">
        <tr>
            <th>Concepto</th>
            <th style="text-align: right;">Ingresos (DOP)</th>
            <th style="text-align: right;">Descuentos (DOP)</th>
            <th style="text-align: right;">Balance Anterior (DOP)</th>
            <th style="text-align: right;">Balance Actual (DOP)</th>
        </tr>
        {detalles_html}
        <tr>
            <td><strong>Total</strong></td>
            <td style="text-align: right;"><strong>{volante['total_ingresos']}</strong></td>
            <td style="text-align: right;"><strong>{volante['total_descuentos']}</strong></td>
            <td style="text-align: right;"><strong>{volante['total_anterior']}</strong></td>
            <td style="text-align: right;"><strong>{volante['total_actual']}</strong></td>
        </tr>
      </table>
      <hr />
      <h3 style="text-align: right; color: #333;">Salario Neto: DOP {volante['total_a_cobrar']}</h3>
    </div>
    """
    return html_code

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


    
    
    


def loan_data(last=False, tipo_concepto=None):
    """
    Obtiene los volantes de pago de los empleados, agrupados por período.

    :param last: Si es True, devuelve solo el último volante.
    :param codigoConcepto: Filtra los datos por el código de concepto.
    :return: Lista de volantes de pago o el último volante si `last` es True.
    """
    #data = sample_data['result']
    #payments =  get_payments()
    payments = sample_data['result']
    
    if 'payments' not in st.session_state:
        st.session_state.payments = payments

    if not  payments:
        return []
    
    data = payments
    
    if tipo_concepto:
        data = [item for item in payments if item.get("tipo_Concepto") == tipo_concepto]



    # Ordenar los datos por idPeriodo en orden descendente
    sorted_data = sorted(data, key=lambda x: x["idDetallePeriodo"], reverse=True)

    # Agrupar los datos por idPeriodo
    grouped_by_id = group_payroll_data(sorted_data, "idDetallePeriodo")

    
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
               
                c.get("codigoAltConcepto", ""),
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
        fecha_inicio = datetime.fromisoformat(concepto[0].get("fechaInicioDetallePeriodo")).strftime('%d/%m/%Y')
        fecha_fin = datetime.fromisoformat(concepto[0].get("fechaFinDetallePeriodo")).strftime('%d/%m/%Y')

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
    
    # if not last:
    #     if st.button("⬅ Volver"):
    #         app.switch_page("home")
            
    # Obtener los datos de los volantes
    volantes = loan_data(last=last)

    if not volantes:
        if not last:

            if st.button(":gray[/ Inicio /] :blue[Pagos]", type="tertiary",  key="payment_volver_home"):
                app.switch_page("home")
            

        with st.container(border=False):
            st.caption("No tienes ningún volante de pago")
            
        return

    if last:
        volantes = [volantes]  # Convertir el último volante en una lista para reutilizar la lógica

    if not last:

        if st.button(":gray[/ Inicio /] :blue[Pagos]", type="tertiary"):
            app.switch_page("home")

        st.markdown(
            """
            <h1 style="font-size: 24px; font-weight: bold; color: #61a1af;">
                Volantes de Pago
            </h1>
            """,
            unsafe_allow_html=True
        )

        # Boton para mostrar/ocultar balances
        if st.button("🔐 Mostrar/ocultar balances"):
            st.session_state.mask_balances = not st.session_state.mask_balances
            st.session_state.mask_balances = True if 'mask_balances' not in st.session_state else st.session_state.mask_balances
    
    #agregar un dropdown para seleccionar el volante a mostrar por periodo
    if not last:
        periodo = st.selectbox("Selecciona el volante a mostrar", [f"{v['periodo']}" for v in volantes], index=0)
        volantes = [v for v in volantes if v['periodo'] == periodo]
        if not volantes:
            st.caption("No tienes ningún volante de pago")
            return
    
    # Mostrar los volantes
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
 

            st.markdown(
                f"""
                <p style="font-size: 16px; font-weight: bold; color: #61a1af;">
                    🏦 Total Recibido: RD$ {total_a_cobrar}
                </p>
                """,
                unsafe_allow_html=True
            )
            #volante = volantes[0]  # Ejemplo: usar el primer volante
            if not last:
                html_code = generar_html_volante(volante)
                # Mostrar el HTML en Streamlit
                st.components.v1.html(html_code, height=600, scrolling=True)

                        
                        


