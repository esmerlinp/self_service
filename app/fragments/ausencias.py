
import streamlit as st
from app.util import calcular_dias_laborales
from app.core import Core
import datetime

import time as t
import base64


db = Core()

#DATA EXAMPLE
    


@st.fragment()
@st.dialog("Solicitud de Permiso", width="large")
def solicitar_permiso():
    reason_code = 0
    dias = 0
    cantidad = 0
    tipos = ["Vacaciones", "Permiso hora", "Permiso día"]
    
    tipo_permiso = st.selectbox("Tipo de Permiso", tipos)
    if tipo_permiso == "Permiso hora":
        reason_code = 4

        desde = st.time_input("Hora desde", value=datetime.time(8, 0), step=1800)
        hasta = st.time_input("Hora hasta", value=datetime.time(17, 0), step=1800)
        
        fecha_desde = st.date_input("Fecha", min_value="today", format="DD/MM/YYYY")
        fecha_hasta = fecha_desde
        
        #calcular cantidad de horas
        if desde and hasta:
            # Convertir a datetime
            desde_dt = datetime.datetime.combine(fecha_desde, desde)
            hasta_dt = datetime.datetime.combine(fecha_desde, hasta)
            
            # Calcular diferencia en horas
            diferencia = hasta_dt - desde_dt
            
            # Obtener la cantidad de horas
            cantidad = diferencia.total_seconds() / 3600
        
        #concatenar fecha y hora
        fecha_desde = datetime.datetime.combine(fecha_desde, desde)
        fecha_hasta = datetime.datetime.combine(fecha_hasta, hasta)
        
        st.number_input("Cantidad horas", value=cantidad, disabled=True)
        
    else:
        reason_code = 1 if tipo_permiso == "Vacaciones" else 3
        fecha_desde = st.date_input("Fecha desde", min_value="today", format="DD/MM/YYYY", )
        fecha_hasta = st.date_input("Fecha hasta", min_value="today", format="DD/MM/YYYY",)
        
    

        #convertir feriados a arreglo de fechas ejemplo [date(2025, 4, 3), date(2025, 4, 7)]
        _feriados = st.session_state.get("feriados", [])
        feriados = []
        if _feriados:
            feriados = [datetime.datetime.strptime(f['fecha'], "%Y-%m-%dT%H:%M:%S").date() for f in _feriados]
        
        
        if fecha_hasta:
            cantidad = calcular_dias_laborales(
                                fecha_inicio=fecha_desde,
                                fecha_fin=fecha_hasta,
                                feriados=feriados
                            )

    
            st.number_input("Cantidad de días", value=cantidad, disabled=True)
    

          
    comment = st.text_area(label="Comentario")
    st.caption("⚠️ Esta solicitud está sujeta a aprobación previa por parte de su Supervisor.")
    
    
    if st.button("Envíar"):
        
        #ncabezado del comentario:
        encabezado =  f"Solicitud de {tipo_permiso} desde el {fecha_desde.strftime('%d/%m/%Y %H:%M')} hasta el {fecha_hasta.strftime('%d/%m/%Y %H:%M')}."
    
        # Agregar encabezado al comentario
        if comment:
            comment = f"{encabezado}\n\n\n Comentario del empleado: {comment}"
        else:
            comment = encabezado
            
        from_date = fecha_desde.strftime("%Y-%m-%dT%H:%M:%S")
        to_date = fecha_hasta.strftime("%Y-%m-%dT%H:%M:%S")
        
        result = db.set_ausencia(from_date=from_date, to_date=to_date, comment=comment, reason_code=reason_code, cantidad=cantidad)
        if result:
            st.success("Solicitud enviada satisfactoriamente")
            st.balloons()
            db.get_ausencias()
            st.rerun(scope="app")
            return
        else:
            st.warning("La solicitud no pudo ser procesada. Intenta de nuevo o contacta a soporte.")

          
@st.fragment
def resumen_permisos():
    """Muestra las solicitudes del usuario en un diseño atractivo."""
    with st.expander("📢 Solicitudes", expanded=True):
        if 'ausencias' in st.session_state:
            with st.container():
                if st.session_state.ausencias:
                    # Mostrar solo las 5 más recientes o todas según el estado
                    if "show_all_requests" not in st.session_state:
                        st.session_state.show_all_requests = False

                    requests = st.session_state.ausencias
                    request_to_display = requests if st.session_state.show_all_requests else requests[:3]

                    for req in request_to_display:
                        # Convertir la fecha al formato deseado
                        try:
                            fecha = datetime.datetime.strptime(req['fecha_Registro'], "%Y-%m-%dT%H:%M:%S").strftime("%d/%m/%Y %H:%M")
                        except ValueError:
                            fecha = req['fecha_Registro']  # Usar la fecha original si hay un error

                        estado = ""
                        # Asignar color según el estado de la solicitud
                        if req['codigo_Estado'] == 2: #Pendiente
                            estado_color = "#333"  # Gris oscuro
                            estado = "Pendiente"
                        elif req['codigo_Estado'] == 3: #Autorizada
                            estado_color = "green"  # Verde
                            estado = "Autorizada"
                        elif req['codigo_Estado'] == 4: #Rechazada
                            estado_color = "red"  # Naranja
                            estado = "Rechazada"
                        else:
                            estado_color = "#555"  # Color por defecto

                        #fecha_desde = datetime.datetime.strptime(req['fecha_Inicio'], "%Y-%m-%dT%H:%M:%S").strftime("%d/%m/%Y %H:%M")
                        #fecha_hasta = datetime.datetime.strptime(req['fecha_Fin'], "%Y-%m-%dT%H:%M:%S").strftime("%d/%m/%Y %H:%M")
                        #formatear fecha desde y hasta
                        
                        
                        
                        
                        fecha_desde = req['fecha_Inicio'].split("T")[0]
                        fecha_hasta = req['fecha_Fin'].split("T")[0]
                        tipo_cantidad = "días" if req['tipo_Ausencia'] != 4 else "horas"
                        # formatear fechas_desde a texto
                        fecha_desde = datetime.datetime.strptime(fecha_desde, "%Y-%m-%d").strftime(" %A %d de %B de %Y").upper()
                        fecha_hasta = datetime.datetime.strptime(fecha_hasta, "%Y-%m-%d").strftime(" %A %d de %B de %Y").upper()
                            
                            
                            
                        #fecha_hasta = datetime.datetime.strptime(req['fecha_Registro'], "%Y-%m-%dT%H:%M:%S").strftime("%d/%m/%Y %H:%M")
                        encabezado =  f"Desde el {fecha_desde} hasta el {fecha_hasta}. "
                       
                        # Mostrar cada solicitud con un diseño atractivo
                        if req['tipo_Ausencia'] == 4:
                            st.markdown(
                                f"""
                                <div style="border: 1px solid #ddd; border-radius: 8px; padding: 10px; margin-bottom: 10px; background-color: #f9f9f9;">
                                    <p style="margin: 0; font-size: 16px; font-weight: bold; color: #333;">{req['nombre_Tipo_Ausencia']}</p>
                                    <p style="margin: 0; font-size: 14px; color: #888;">🕒 {fecha_desde}</p>
                                    <p style="margin: 0; font-size: 14px; color: #888;">Cantidad: {req['cantidad']} {tipo_cantidad}</p>
                                    <p style="margin: 0; font-size: 14px; color: {estado_color};">Estado: {estado}</p>
                                </div>
                                """,
                                unsafe_allow_html=True  
                            )
                        else:
                            st.markdown(
                                f"""
                                <div style="border: 1px solid #ddd; border-radius: 8px; padding: 10px; margin-bottom: 10px; background-color: #f9f9f9;">
                                    <p style="margin: 0; font-size: 16px; font-weight: bold; color: #333;">{req['nombre_Tipo_Ausencia']}</p>
                                    <p style="margin: 0; font-size: 14px; color: #888;">DE: {fecha_desde}</p>
                                    <p style="margin: 0; font-size: 14px; color: #888;">A : {fecha_hasta}</p>
                                    <p style="margin: 0; font-size: 14px; color: #888;">Cantidad: {req['cantidad']} {tipo_cantidad}</p>
                                    <p style="margin: 0; font-size: 14px; color: {estado_color};">Estado: {estado}</p>
                                </div>
                                """,
                                unsafe_allow_html=True  
                            )
                        

                    # Botón para alternar entre "Ver todas" y "Mostrar menos"
                    if len(requests) > 3:
                        if st.session_state.show_all_requests:
                            if st.button(":blue[Mostrar menos]", type="tertiary"):
                                st.session_state.show_all_requests = False
                        else:
                            if st.button(":blue[Ver todas]", type="tertiary"):
                                st.session_state.show_all_requests = True
                else:
                    st.info("No tienes solicitudes.")
  


@st.fragment
@st.dialog(title="Solicitud de licencia médica", width="large")       
def solicitar_licencia_medica():
    """
    Solicitud de licencia médica"""
    tipo_licencia = st.selectbox("Tipo de licencia", ["Licencia médica", "Accidente Laboral"])
    desde = st.date_input("Fecha desde", min_value="today", format="DD/MM/YYYY", value="today")
    hasta = st.date_input("Fecha hasta", min_value="today", format="DD/MM/YYYY", value="today")
    dias = 0
    if hasta:
        # Horario de trabajo del empleado (Ejemplo: Lunes a Viernes de 08:00 a 17:00)

        dias = calcular_dias_laborales(
                    fecha_inicio=desde,
                    fecha_fin=hasta,
                    feriados=[]
                )
        
    st.number_input("Cantidad", value=dias, disabled=True) 
    comment = st.text_area("Comentario")
    uploaded_files = st.file_uploader("📄 **Sube el documento aval de licencia médica**", type=['pdf', 'png', 'jpg'], accept_multiple_files=True)
    
    
    st.caption("⚠️ Esta solicitud está sujeta a aprobación previa por parte de Recursos Humanos.")
    
    if st.button("Envíar"):
        
                
        #ncabezado del comentario:
        encabezado =  f"Solicitud de {tipo_licencia} desde el {desde.strftime('%d/%m/%Y %H:%M')} hasta el {desde.strftime('%d/%m/%Y %H:%M')}."
    
        # Agregar encabezado al comentario
        if comment:
            comment = f"{encabezado}\n\n\n Comentario del empleado: {comment}"
        else:
            comment = encabezado
            
        from_date = desde.strftime("%Y-%m-%dT%H:%M:%S")
        to_date = hasta.strftime("%Y-%m-%dT%H:%M:%S")
        result = db.set_ausencia(from_date=from_date, to_date=to_date, comment=comment, reason_code=2, cantidad=dias)
        
        if result:
            result = result[0]
           
            last_create = db.get_ausencias()
            if uploaded_files:
                
                for uploaded_file in uploaded_files:
                    # Leer el contenido del archivo
                    file_content = uploaded_file.read()

                    # Convertir el contenido a Base64
                    file_base64 = base64.b64encode(file_content).decode("utf-8")
                    
                    
                    respuesta = db.set_documento(id_transaccion=last_create[0]["id"], 
                                 archivoInBase64=file_base64,
                                 nombre_archivo=uploaded_file.name,
                                 extension=uploaded_file.type,
                                 fecha_creacion=datetime.datetime.now().strftime("%d/%m/%Y"),
                                 )
                    if not respuesta:
                        st.warning("La solicitud fue enviada pero el documento no pudo ser procesado. Intenta de nuevo o contacta a soporte.")
                       
            
                
            st.success("Solicitud enviada satisfactoriamente")
            st.snow()
            t.sleep(2)
            st.rerun(scope="app")
            return
        else:
            st.warning("La solicitud no pudo ser procesada. Intenta de nuevo o contacta a soporte.")
            


@st.fragment
def resumen_vacaciones():
    """Muestra un resumen de los días de vacaciones restantes y tomados del empleado."""
    # Días de vacaciones por año
    DIAS_POR_ANO = 14

    # Verificar si el JSON de vacaciones está en el session_state
    if "vacaciones" not in st.session_state:
        with st.expander("✈️ Resumen de Vacaciones", expanded=False):
            
            st.caption("No has tomado vacaciones en el año")
            if st.button(":blue[Solicitar vacaciones]", type="tertiary", icon="✈️"):
                solicitar_permiso()
            
        return

    # Obtener las vacaciones autorizadas
    vacaciones = [
        vaca for vaca in st.session_state.vacaciones
        if vaca["codigo_Estado"] == 3  # Solo solicitudes autorizadas
    ]

    if not vacaciones:
        st.info("No tienes vacaciones autorizadas registradas.")
        return

    # Calcular días tomados totales y por año
    dias_tomados_totales = sum(vaca["cantidad"] for vaca in vacaciones)
    dias_tomados_por_ano = {}

    for vaca in vacaciones:
        # Obtener el año de la fecha de inicio
        ano = datetime.datetime.strptime(vaca["fecha_Inicio"], "%Y-%m-%dT%H:%M:%S").year
        dias_tomados_por_ano[ano] = dias_tomados_por_ano.get(ano, 0) + vaca["cantidad"]

    # Ajustar los días si se tomaron más de los asignados en un año
    dias_restantes_totales = max(0, DIAS_POR_ANO * len(dias_tomados_por_ano) - dias_tomados_totales)

    # Obtener el año actual
    ano_actual = datetime.datetime.now().year

    # Mostrar el resumen
    with st.expander("📅 Resumen de Vacaciones", expanded=True):
        st.markdown("### 🏖️ Resumen de Vacaciones")
        
        # Mostrar progreso de días tomados y restantes
        porcentaje_tomado = (dias_tomados_totales / (DIAS_POR_ANO * len(dias_tomados_por_ano))) * 100
        
        # Indicar si no se han tomado vacaciones este año
        if ano_actual not in dias_tomados_por_ano:
            st.info(f"No has tomado vacaciones en el año {ano_actual}.")
        
        col1, _ ,col3 =   st.columns([3,2,2]) 
        
        col1.badge(f"Días tomados: {dias_tomados_totales}", color="red")
        col3.badge(f"Total: {dias_restantes_totales + dias_tomados_totales}", color="gray")
        st.progress(int(porcentaje_tomado), text=f":green[Restantes: {dias_restantes_totales}]")


        # Botón para ver detalles
        if st.button(":blue[Ver detalles]", type="tertiary"):
            detalles_vacaciones()



@st.dialog("Detalles de Vacaciones", width="large")
def detalles_vacaciones():
    """Muestra los detalles de las vacaciones tomadas por año y por registro en formato tipo reporte."""
    if "vacaciones" not in st.session_state or not st.session_state.vacaciones:
        st.info("No se encontraron datos de vacaciones.")
        return

    # Obtener las vacaciones autorizadas
    vacaciones = [
        vaca for vaca in st.session_state.vacaciones
        if vaca["codigo_Estado"] == 3  # Solo solicitudes autorizadas
    ]

    if not vacaciones:
        st.info("No tienes vacaciones autorizadas registradas.")
        return

    # Calcular días tomados por año
    dias_tomados_por_ano = {}
    for vaca in vacaciones:
        # Obtener el año de la fecha de inicio
        ano = datetime.datetime.strptime(vaca["fecha_Inicio"], "%Y-%m-%dT%H:%M:%S").year
        dias_tomados_por_ano[ano] = dias_tomados_por_ano.get(ano, 0) + vaca["cantidad"]

    # Ordenar las vacaciones por fecha (más recientes primero)
    vacaciones_ordenadas = sorted(
        vacaciones,
        key=lambda x: datetime.datetime.strptime(x["fecha_Inicio"], "%Y-%m-%dT%H:%M:%S"),
        reverse=True
    )

    # Mostrar los detalles
    st.markdown("### 🏖️ Detalles de Vacaciones")
    
    # Ordenar días tomados por año de mayor a menor
    dias_tomados_por_ano_ordenados = sorted(dias_tomados_por_ano.items(), key=lambda x: x[0], reverse=True)

    # Mostrar días tomados por año
    st.markdown("#### Días por Año")
    for ano, dias_tomados in dias_tomados_por_ano_ordenados:
        st.markdown(f"- **{ano}:** Tomados: {dias_tomados} días")

    # Crear un DataFrame para los registros de vacaciones
    import pandas as pd

    data = [
        {
            "Fecha Inicio": datetime.datetime.strptime(vaca["fecha_Inicio"], "%Y-%m-%dT%H:%M:%S").strftime("%d/%m/%Y"),
            "Fecha Fin": datetime.datetime.strptime(vaca["fecha_Fin"], "%Y-%m-%dT%H:%M:%S").strftime("%d/%m/%Y"),
            "Días Tomados": vaca["cantidad"],
            "Comentario": vaca["comentario"] or "Sin comentario"
        }
        for vaca in vacaciones_ordenadas
    ]

    df = pd.DataFrame(data)

    # Mostrar el DataFrame
    st.markdown("#### Registros de Vacaciones")
    st.dataframe(df, use_container_width=True)
    
    
    
    
    