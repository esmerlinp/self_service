import streamlit as st
from app.core import get_team_requests, get_vacaciones_by_id
import datetime
from streamlit_extras.dataframe_explorer import dataframe_explorer
import pandas as pd
from streamlit_avatar import avatar
from app.util import tiempo_transcurrido
from app.core import  get_team_requests, update_autorizacion
import time as t
import app



@st.fragment(run_every=60*60)
def colaboradores():
    
    """Muestra los colaboradores y las solicitudes pendientes de autorización."""

    st.write(
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" />',
        unsafe_allow_html=True,
    ) 
    
    e = st.session_state.employee
    colaboradores = e['colaboradores']
    
    # Obtener solicitudes pendientes del session_state
    #solicitudes = st.session_state.get("team_requests", [])
    solicitudes = get_team_requests()
    
    #filtrar solo las de estado pendientes
    solicitudes_pendientes = [solicitud for solicitud in solicitudes if solicitud['estado'] == 0 and  not solicitud['cantidad'] == None and  not solicitud['fecha_Hasta'] == None]
    
    #filtrar solicitudes  en estado diferente a pendiente
    solicitudes_aut_rech = [solicitud for solicitud in solicitudes if solicitud['estado'] != 0 and  not solicitud['cantidad'] == None and  not solicitud['fecha_Hasta'] == None]
    

    col1, col2 = st.columns([1.5, 4])

    # Columna 1: Avatares de los colaboradores
    with col1:
        
        with st.expander(label="Mi Equipo", expanded=True):
            st.markdown("### Mi Equipo")
            
            mostrar_inactivos = st.toggle("Mostrar colaboradores inactivos", value=False)

            for member in colaboradores:
                
                if not mostrar_inactivos and member['nombre_EstadoEmpleado'].lower() == "inactivo":
                    continue  # Saltar colaboradores inactivos si el toggle está desactivado

                imagen = member.get('imageUrl')
                #imagen = None
                nombres = member["nombreCompletoEmpleado"].split(" ")
                name = ""
                
                if len(nombres) >= 3:
                    name = f"{nombres[0]} {nombres[2]}"
                else:
                    name = f"{nombres[0]} {nombres[1]}"


                if not imagen:
                    imagen = f"https://ui-avatars.com/api/?background=random&name={name}=100%bold=true"   

                
                col7, col8 = st.columns([5, 0.8])
                with col7:
                    
                    # Determinar el color del estado según el estado del colaborador
                    estado = member['nombre_EstadoEmpleado'].lower()
                    if estado == "activo":
                        color_estado = "#28a745"  # Verde
                    elif estado == "pendiente":
                        color_estado = "#ffc107"  # Amarillo
                    elif estado == "inactivo":
                        color_estado = "#dc3545"  # Rojo
                    else:
                        color_estado = "#6c757d"  # Gris (por defecto)
                        
                    st.markdown(f"""
                        <div style="display: flex; flex-direction: row; align-items: center; margin-bottom: 8px; gap: 12px;">
                            <div>
                                <img src="{imagen}" alt="Foto de {nombres}" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover;">
                            </div>
                            <div style="display: flex; flex-direction: column; align-items: flex-start;">
                                <span style="font-weight: bold; font-size: 14px; color: #333;">{member['nombreCompletoEmpleado']}</span>
                                <span style="font-size: 12px; color: #666;">{member['nombre_Puesto']}</span>
                                <span style="font-size: 12px; font-weight: bold; color: {color_estado};">{member['nombre_EstadoEmpleado']}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                
                if col8.button(":material/person:", key=f"member_{member['idEmpleado']}",  help="Detalles del empleado"):
                    #empleado.employee_detail(employeeId=member['idEmpleado'])
                    params = {"employeeId":member['idEmpleado']}
                    app.switch_page(page_name="empleado", params=params)
                    

                   

    # Columna 2: Opciones y solicitudes
    with col2:
        
        options_container = st.container(border=False)
        with options_container:            
            # Opciones para las pills
            options = ["👨🏼‍🎓 Solicitar Colaborador"]

            # Inicializar el estado si no existe
            if "pills_selection_team" not in st.session_state:
                st.session_state["pills_selection_team"] = None

            # Función para manejar el cambio de selección
            def handle_pills_team_change():
                selection = st.session_state["pills_selection_team"]
                if selection == "👨🏼‍🎓 Solicitar Colaborador":
                    modal_solicitar_colaborador()

                # Reiniciar la selección de las pills
                st.session_state["pills_selection_team"] = None

            # Renderizar las pills
            st.pills(
                "Qué deseas hacer ?",
                options,
                key="pills_selection_team",
                on_change=handle_pills_team_change,
                disabled=True
            )
            

        render_actividades_recientes(solicitudes, colaboradores)
        render_solicitudes_pendientes(solicitudes_pendientes)

        

        #Mostrsr solicitudes autorizadas o rechazadas
        with st.expander("Ver solicitudes autorizadas/rechazadas", expanded=False):
            if solicitudes_aut_rech:
                # Convertir las solicitudes en un DataFrame
                df_solicitudes_aut_rech = pd.DataFrame(solicitudes_aut_rech)

                # Filtrar columnas relevantes para mostrar en el DataFrame
                columnas_mostrar = [
                    "id", "usuario", "nombreEmpleado", "apellidoEmpleado", "fecha_Desde", "fecha_Hasta", "cantidad", "accion", "descripcion", 
                    "nombre_estado", "comentario", "prioridad", "fecha"
                ]
                df_solicitudes_aut_rech = df_solicitudes_aut_rech[columnas_mostrar]

                # Mostrar el DataFrame con selección múltiple
                filtered_df_solicitudes_aut_rech = dataframe_explorer(df_solicitudes_aut_rech, case=False)
                st.dataframe(filtered_df_solicitudes_aut_rech, use_container_width=True, 
                            hide_index=True)
                
            else:
                st.info("No hay solicitudes pendientes.")




def historial_vacaciones(empleadoid):
    
    vacaciones = get_vacaciones_by_id(empleadoid)
    
    if not vacaciones:
        st.info("No tienes vacaciones autorizadas registradas.")
        return

    vacaciones = [v for v in vacaciones if  v['fecha_Inicio']]
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


    # Crear un DataFrame para los registros de vacaciones
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
    
        
    # Ordenar días tomados por año de mayor a menor
    dias_tomados_por_ano_ordenados = sorted(dias_tomados_por_ano.items(), key=lambda x: x[0], reverse=True)

    # Mostrar días tomados por año
    st.markdown("#### Días por Año")
    for ano, dias_tomados in dias_tomados_por_ano_ordenados:
        st.markdown(f"- **{ano}:** Tomados: {dias_tomados} días")
    
    
@st.dialog("Autorizar/Rechazar Solicitud", width="large")
def autorizar_solicitudes(solicitud):
    """Muestra el detalle de la solicitud en un diseño HTML y CSS."""
    
    
    
    # Detalles de la solicitud
    titulo = f"Solicitud de {solicitud['nombreTipoAusencia']} para {solicitud['nombreEmpleado']} {solicitud['apellidoEmpleado']}"

    # Determinar unidad
    unidad = "hora" if solicitud["tipoAusencia"] == 4 else "día"
    cantidad = f"{int(solicitud['cantidad'])} {unidad}" + ("s" if solicitud["cantidad"] > 1 else "")

    # Parsear fechas
    fecha_desde = datetime.datetime.strptime(solicitud["fecha_Desde"], "%Y-%m-%dT%H:%M:%S").strftime("%d de %B de %Y")
    fecha_hasta = datetime.datetime.strptime(solicitud["fecha_Hasta"], "%Y-%m-%dT%H:%M:%S").strftime("%d de %B de %Y")

    # Generar rango de fechas si no es "PERMISOS HORA"
    if solicitud["tipoAusencia"] == 4:
        fecha_texto = f"Fecha  {fecha_desde}"
    else:
        fecha_texto = f"Desde  {fecha_desde} hasta  {fecha_hasta}"
        
        
    st.subheader(f"{solicitud['nombreTipoAusencia']} - {solicitud['nombreEmpleado']} {solicitud['apellidoEmpleado']}")

    st.markdown(f"""
    <div style="display: flex; flex-direction: row; align-items: center; margin-bottom: 8px; gap: 12px;">
        <div style="display: flex; flex-direction: column; align-items: flex-start;">
            <span style="font-size: 14px; color: #333;">{titulo}</span>
            <span style="font-size: 14px; color: #666;">{fecha_texto}</span>
            <span style="font-size: 14px; color: #666;">Duración {cantidad} {unidad}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    
    fecha_solicitud = f"Fecha de Solicitud: {solicitud['fecha']}"
    st.caption(fecha_solicitud)
    
    if solicitud['tipoAusencia'] == 1 : #Vacaciones
        historial_vacaciones(solicitud['idEmpleado'])
    
    comment = st.text_area("Comentario")
    

    # Botones para autorizar o rechazar
    col_aut, _, col_rech = st.columns([1, 4, 1])
    if col_aut.button("Autorizar", key=f"autorizar_{solicitud['id']}"):
        
        hoy = datetime.datetime.today().date()
        
        body = [{
            "IdAut": solicitud["id"],
            "UserId": st.session_state.user['userId'],
            "Date": hoy.strftime("%Y-%m-%dT%H:%M:%S"),
            "comment": comment
        }]
        response = update_autorizacion(body)
        if response:
            st.success("Solicitud autorizada correctamente.")
            t.sleep(2)
            st.rerun(scope="fragment")
        else:
            st.error("Error al autorizar la solicitud.")
    
    if col_rech.button("Rechazar", key=f"rechazar_{solicitud['id']}", type="primary"):
        hoy = datetime.datetime.today().date()

        body = [{
            "IdAut": solicitud["id"],
            "UserId": st.session_state.user['userId'],
            "Date": hoy.strftime("%Y-%m-%dT%H:%M:%S"),
            "comment": comment
        }]
        response = update_autorizacion(body, accion="rechazar")
        if response:
            st.warning("Solicitud rechazada correctamente.")
            t.sleep(2)
            st.rerun(scope="fragment")
        else:
            st.error("Error al rechazar la solicitud.")
            





@st.fragment(run_every=60*60)
def render_solicitudes_pendientes(solicitudes_pendientes):
    with st.expander("Solicitudes Pendientes", expanded=True):
        # Actividades recientes
        if not solicitudes_pendientes:
            st.caption("No tienes solicitudes pendientes de autorización")
            return

        # Número inicial de registros a mostrar
        if "num_registros_pendientes" not in st.session_state:
            st.session_state.num_registros_pendientes = 5  # Mostrar inicialmente 5 registros
        
    
        solicitudes_mostradas = solicitudes_pendientes[:st.session_state.num_registros_pendientes]

        # Mostrar las solicitudes filtradas
        for sol in solicitudes_mostradas:
            
            if sol['accion'] == "Ausencia"  and not sol['cantidad'] == None and not sol['fecha_Hasta'] == None:
                imagen = sol.get('fotoURL')
                nombres = f"{sol['nombreEmpleado']} {sol['apellidoEmpleado']}"

                if not imagen:
                    imagen = f"https://ui-avatars.com/api/?background=random&name={nombres}=100%bold=true"
                    


                # Determinar unidad
                unidad = "hora" if sol["tipoAusencia"] == 4 else "día"
                cantidad = f"{int(sol['cantidad'])} {unidad}" + ("s" if sol["cantidad"] > 1 else "")

                # Parsear fechas
                fecha_desde = datetime.datetime.strptime(sol["fecha_Desde"], "%Y-%m-%dT%H:%M:%S").strftime("%d de %B de %Y")
                fecha_hasta = datetime.datetime.strptime(sol["fecha_Hasta"], "%Y-%m-%dT%H:%M:%S").strftime("%d de %B de %Y")

                # Generar rango de fechas si no es "PERMISOS HORA"
                if sol["tipoAusencia"] == 4:
                    fecha_texto = f"con fecha del {fecha_desde}"
                else:
                    fecha_texto = f"con fecha desde el {fecha_desde} hasta el {fecha_hasta}"

                # Construcción del título y subtítulo
                titulo = f"Solicitud de  <b>{sol['nombreTipoAusencia'].capitalize()}</b> para <b>{sol['nombreEmpleado']} {sol['apellidoEmpleado']}</b>"
                subtitulo = (
                    f"Se ha registrado una solicitud de {sol['nombreTipoAusencia'].lower()} "
                    f"{fecha_texto} por {cantidad}."
                )
                    
                col7, col8 = st.columns([5, 0.4])
                with col7:
                    fecha = datetime.datetime.strptime(sol['fecha'], "%Y-%m-%dT%H:%M:%S").strftime("%d-%m-%Y %H:%M")
                    st.markdown(f"""
                        <div style="display: flex; flex-direction: row; align-items: center; margin-bottom: 8px; gap: 12px;">
                            <div>
                                <img src="{imagen}" alt="Foto de {nombres}" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover;">
                            </div>
                            <div style="display: flex; flex-direction: column; align-items: flex-start;">
                                <span style="font-size: 16px; color: #333;">{titulo}</span>
                                <span style="font-size: 14px; color: #666;">{subtitulo}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)


                        
                        
                        
                        
                if col8.button(":green[:material/tv_options_edit_channels:]", key=f"done_all_2{sol['id']}_{sol['codigo_solicitud']}", help="Ver mas detalles de la solicitud"):
                   autorizar_solicitudes(solicitud=sol)
                   
                    # body = []
                    # body.append({
                    #     "IdAut": sol["id"],
                    #     "UserId": st.session_state.user['userId'],
                    #     "Date": None,
                    #     "comment": ""
                    # })
                        
                    # response = update_autorizacion(body, accion="Rechazar")
                    # if response:
                    #     st.session_state.num_registros = 4
                    #     st.rerun(scope="fragment")
                    #     show_alert("Solicitud aceptada correctamente.", "Solicitud aceptada correctamente.")
                    # else:
                    #     show_alert("Upss!", "Error al Autorizar la solicitud.")
                    


            
        # Botón dinámico para mostrar más o menos registros
        if len(solicitudes_pendientes) > 5:  # Mostrar el botón solo si hay más de 5 registros
            if st.session_state.num_registros_pendientes > 5:
                button_label = ":red[Mostrar menos]"
            else:
                button_label = ":blue[Mostrar más]"

            if st.button(button_label, type="tertiary",  key=f"show_more_less"):
                if st.session_state.num_registros_pendientes > 5:
                    st.session_state.num_registros_pendientes = 5  # Reducir a 5 registros
                else:
                    st.session_state.num_registros_pendientes += 5  # Incrementar en 5 registros
                st.rerun(scope="fragment")

     
@st.fragment(run_every=60*60)
def render_actividades_recientes(solicitudes, colaboradores):
     
        with st.container(border=True):
            # Actividades recientes
            st.markdown("🕒 **Actividades Recientes**")
            
            # Número inicial de registros a mostrar
            if "num_registros" not in st.session_state:
                st.session_state.num_registros = 4  # Mostrar inicialmente 5 registros

            # Filtrar las solicitudes pendientes para incluir solo las de los colaboradores
            solicitudes_filtradas = sorted(
                [
                    sol for sol in solicitudes 
                    if sol['idEmpleado'] in [member['idEmpleado'] for member in colaboradores] and not sol['cantidad'] == None and  not sol['fecha_Hasta'] == None
                ],
                key=lambda x: datetime.datetime.strptime(x['fecha_autorizacion'], "%Y-%m-%dT%H:%M:%S") if x['fecha_autorizacion'] else datetime.datetime.strptime(x['fecha'], "%Y-%m-%dT%H:%M:%S"),  # Ordenar por fecha
                reverse=True  # Mostrar las más recientes primero
            )[:10] #10 registros maximos
            
            solicitudes_mostradas = solicitudes_filtradas[:st.session_state.num_registros]

            # Mostrar las solicitudes filtradas
            for sol in solicitudes_mostradas:   
                if sol['accion'] == "Ausencia":
                    
                      
                    imagen = sol.get('imageUrl')
                    nombres = f"{sol['nombreEmpleado']} {sol['apellidoEmpleado']}"

                    if not imagen:
                        imagen = f"https://ui-avatars.com/api/?background=random&name={nombres}=100%bold=true"
                    
                    span = '<span class="material-symbols-outlined">approval_delegation</span>'
                    
                    if sol['estado'] == 1:
                        span = '<span class="material-symbols-outlined" style="color: #48752C;">done_all</span>'
                    elif sol['estado'] == 2:
                        span = '<span class="material-symbols-outlined" style="color: #EA3323;">remove_done</span>'

                                    

                    # Determinar unidad
                    unidad = "hora" if sol["tipoAusencia"] == 4 else "día"
                    cantidad = f"{int(sol['cantidad'])} {unidad}" + ("s" if sol["cantidad"] > 1 else "")

                    # Parsear fechas
                    fecha_desde = datetime.datetime.strptime(sol["fecha_Desde"], "%Y-%m-%dT%H:%M:%S").strftime("%d de %B de %Y")
                    fecha_hasta = datetime.datetime.strptime(sol["fecha_Hasta"], "%Y-%m-%dT%H:%M:%S").strftime("%d de %B de %Y")

                    # Generar rango de fechas si no es "PERMISOS HORA"
                    if sol["tipoAusencia"] == 4:
                        fecha_texto = f"con fecha del {fecha_desde}"
                    else:
                        fecha_texto = f"con fecha desde el {fecha_desde} hasta el {fecha_hasta}"

                    # Construcción del título y subtítulo
                    #fecha = datetime.datetime.strptime(sol['fecha'], "%Y-%m-%dT%H:%M:%S").strftime("%d-%m-%Y")
                    fecha = tiempo_transcurrido(datetime.datetime.strptime(sol['fecha'], "%Y-%m-%dT%H:%M:%S"))
                    span_fecha = f"""<span style="font-size: 12px; color: #666;"> {fecha} </span>"""
                    titulo = f"<b>{sol['usuario']}</b> creó  una solicitud de  <b>{sol['nombreTipoAusencia'].strip()}</b> "
                    subtitulo = (
                        f"Se ha registrado una solicitud de {sol['nombreTipoAusencia'].lower()} "
                        f"para <b>{sol['nombreEmpleado']} {sol['apellidoEmpleado']}</b> "
                        f"{fecha_texto} por {cantidad}."
                    )
                    
                    
                    # Agregar línea de autorización si existe
                    aditional_text = ""
                    if sol["fecha_autorizacion"]:
                        fecha_aut = datetime.datetime.strptime(sol["fecha_autorizacion"], "%Y-%m-%dT%H:%M:%S").strftime("%d de %B de %Y")
                        if sol["estado"] == 1:
                            aditional_text = f" * La solicitud fue autorizada el {fecha_aut}."
                        elif sol["estado"] == 2:
                            aditional_text = f" * La solicitud fue rechazada el {fecha_aut}."

                    st.markdown(f"""
                        <div style="display: flex; flex-direction: row; align-items: center; margin-bottom: 8px; gap: 12px;">
                            <div>
                                {span}
                            </div>
                            <div style="display: flex; flex-direction: column; align-items: flex-start;">
                                <span style="font-size: 14px; color: #333;">{span_fecha} {titulo} </span>
                                <span style="font-size: 12px; color: #666;">{subtitulo}</span>
                                <span style="font-size: 12px; color: #666;">{aditional_text}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                                

               
            # Botón dinámico para mostrar más o menos registros
            if len(solicitudes_filtradas) > 4:  # Mostrar el botón solo si hay más de 5 registros
                if st.session_state.num_registros > 4:
                    button_label = ":red[Mostrar menos]"
                else:
                    button_label = ":blue[Mostrar más]"

                if st.button(button_label, type="tertiary"):
                    if st.session_state.num_registros > 4:
                        st.session_state.num_registros = 4  # Reducir a 5 registros
                    else:
                        st.session_state.num_registros += 4  # Incrementar en 5 registros
                    st.rerun(scope="fragment")




# Modal para Desvinculación de Personal
@st.dialog("Desvinculación de Personal", width="large")
def modal_desvinculacion():
    """Modal para gestionar la desvinculación de un colaborador."""
    # Seleccionar colaborador
    colaborador = st.selectbox(
        "Selecciona un colaborador",
        [col['nombreCompleto'] for col in st.session_state.employee['colaboradores']]
    )
    
    # Campos adicionales
    motivo_razon = st.text_area("Motivo o Razón de la Desvinculación")
    fecha_aplicacion = st.date_input("Fecha de Aplicación")

    # Botón para enviar la solicitud
    if st.button("Enviar Desvinculación"):
        # Crear el cuerpo de la solicitud
        body = [
            {
                "Id_AccionWeb": 12,
                "Comentario": motivo_razon,
                "Tipo_Ausencia": 3,
                "Id_Registro_Relacionado": 8,  # ID del colaborador seleccionado
                "Fecha_Inicio": fecha_aplicacion.strftime("%d/%m/%Y"),
                "Fecha_Fin": fecha_aplicacion.strftime("%d/%m/%Y")  # Usar la misma fecha para inicio y fin
            }
        ]
        
        # Simular el envío al API
        response = True
        if response:
            st.success("Desvinculación enviada correctamente.")
        else:
            st.error("Error al enviar la desvinculación.")


# Modal para Solicitar un Colaborador
@st.dialog("Solicitar un Colaborador", width="large")
def modal_solicitar_colaborador():
    """Modal para gestionar la solicitud de un nuevo colaborador."""
    st.markdown("### 📝 Solicitud de Colaborador")
    puesto = st.selectbox("Puesto", ["Desarrollador", "Testing", "Analista"])

    # Dividir los campos en dos columnas
    col1, col2 = st.columns(2)
    e = st.session_state.employee
    
    with col1:
        id_compania = st.text_input("Compañía", value=e['nombre_Compania'], disabled=True)
        id_departamento = st.text_input("Departamento", value=e['nombre_Departamento'], disabled=True)
        modalidad = st.selectbox("Modalidad", ["Remota", "Presencial", "Hibrida"])  # Opciones simuladas
        cant_empleado = st.number_input("Cantidad de Empleados", min_value=1)
        ind_rotativo = st.toggle("¿Es Rotativo?", value=False)
    with col2:
        id_sucursal = st.text_input("Sucursal", value=e['nombre_Sucursal'], disabled=True)
        razon_solicitud = st.selectbox("Razón de la Solicitud", ["Creacion", "Sustitución"])  # Opciones simuladas
        tipo_contrato = st.selectbox("Tipo de Contrato", ["Fijo", "Temporal", "Pasantia", "Por servicio"])  # Opciones simuladas
        id_horario = st.number_input("ID del Horario", min_value=1)
        
        


    # Campos adicionales en una sola columna
    id_supervisor = st.text_input("Supervisor", value=e['nombreCompletoEmpleado'], disabled=True)
    comentario = st.text_area("Comentario")

    # Botón para enviar la solicitud
    if st.button("Enviar Solicitud"):
        # Crear el cuerpo de la solicitud
        body = {
            "Nombre_Requisicion": "nombre_requisicion",
            "Id_Compania": id_compania,
            "Id_Sucursal": id_sucursal,
            "Id_Departamento": id_departamento,
            "Id_Puesto": 1,
            "Id_Reclutador": 1,
            "Fecha_Creacion": datetime.datetime.date().today().strftime("%d-%m-%Y"),
            "Razon_Solicitud": razon_solicitud,
            "Tipo_Contrato": tipo_contrato,
            "Id_Horario": id_horario,
            "Ind_Rotativo": ind_rotativo,
            "Cant_Empleado": cant_empleado,
            "Id_Supervisor": id_supervisor,
            "Descripcion": "descripcion",
            "Comentario": comentario,
            "Ind_Estado": 1,
            "hrecreqdets": [{"empemp_aSustituir": 8}]
        }

        # Simular el envío al API
        response = True
        if response:
            st.success("Solicitud de colaborador enviada correctamente.")
        else:
            st.error("Error al enviar la solicitud.")



# Modal para Solicitar Herramienta de Trabajo
@st.dialog("Solicitar Herramienta de Trabajo", width="large")
def modal_solicitar_herramienta():
    colaborador = st.selectbox("Selecciona un colaborador", [col['nombreCompleto'] for col in st.session_state.employee['colaboradores']])
    herramienta = st.text_input("Herramienta solicitada")
    motivo = st.text_area("Motivo de la solicitud")

    if st.button("Enviar Solicitud"):
        st.success(f"Solicitud de herramienta '{herramienta}' para {colaborador} enviada correctamente.")



    colaborador = st.selectbox("Selecciona un colaborador", [col['nombreCompleto'] for col in st.session_state.employee['colaboradores']])
    herramienta_actual = st.text_input("Herramienta actual")
    herramienta_nueva = st.text_input("Nueva herramienta")
    motivo = st.text_area("Motivo de la sustitución")

    if st.button("Enviar Solicitud"):
        st.success(f"Sustitución de herramienta '{herramienta_actual}' por '{herramienta_nueva}' para {colaborador} enviada correctamente.")
    """Muestra los colaboradores y las solicitudes pendientes de autorización."""
    e = st.session_state.employee
    colaboradores = e['colaboradores']

    # Simular solicitudes pendientes de autorización
    solicitudes_pendientes = [
        {
            "id": 1,
            "colaborador": "Juan Pérez",
            "tipo": "Vacaciones",
            "fecha_solicitud": "2025-04-01",
            "detalle": "Solicitud de vacaciones del 10/04/2025 al 20/04/2025.",
            "estado": "Pendiente"
        },
        {
            "id": 2,
            "colaborador": "María López",
            "tipo": "Permiso por enfermedad",
            "fecha_solicitud": "2025-04-02",
            "detalle": "Permiso por enfermedad del 05/04/2025 al 07/04/2025.",
            "estado": "Pendiente"
        }
    ]

    col1, col2 = st.columns([1,3])

    # Columna 1: Avatares de los colaboradores
    with col1:
        with st.container(border=True):
            st.markdown("### 👥 Colaboradores")
            avatar_list = []
            for member in colaboradores:
                imagen = member.get('imageUrl')
                imagen = None
                if not imagen:
                    nombre = member['primerNombreEmpleado']
                    apellido = member['primerApellidoEmpleado']
                    imagen = f"https://ui-avatars.com/api/?background=random&name={nombre}+{apellido}=100%bold=true"  

                obj = {
                    "url": imagen,
                    "size": 50,
                    "title": member['nombreCompleto'],
                    "caption": f"{member['nombre_Puesto']} - {member['nombre_EstadoEmpleado']}",
                    "key": f"{member['idEmpleado']}",
                }
                avatar_list.append(obj)

            avatar(avatar_list)

    # Columna 2: Solicitudes pendientes de autorización
    with col2:
        with st.container(border=True):
            st.markdown("### 📋 Solicitudes Pendientes")
            if solicitudes_pendientes:
                for solicitud in solicitudes_pendientes:
                    with st.expander(f"Solicitud de {solicitud['colaborador']} ({solicitud['tipo']})", expanded=False):
                        st.markdown(f"**Fecha de Solicitud:** {solicitud['fecha_solicitud']}")
                        st.markdown(f"**Detalle:** {solicitud['detalle']}")
                        st.markdown(f"**Estado:** {solicitud['estado']}")

                        # Botones para autorizar o rechazar
                        col_autorizar, col_rechazar = st.columns(2)
                        if col_autorizar.button("Autorizar", key=f"autorizar_{solicitud['id']}"):
                            st.success(f"Solicitud de {solicitud['colaborador']} autorizada.")
                            solicitud['estado'] = "Autorizada"
                            st.experimental_rerun()
                        if col_rechazar.button("Rechazar", key=f"rechazar_{solicitud['id']}"):
                            st.warning(f"Solicitud de {solicitud['colaborador']} rechazada.")
                            solicitud['estado'] = "Rechazada"
                            st.experimental_rerun()
            else:
                st.info("No hay solicitudes pendientes.") 