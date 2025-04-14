import streamlit as st
from app.core import Core
import datetime
import app
from streamlit_extras.dataframe_explorer import dataframe_explorer
import pandas as pd

# from dataframe_with_button import static_dataframe
# from dataframe_with_button import editable_dataframe
from streamlit_avatar import avatar


db = Core()


          
           
@st.fragment
def resumen_prestamo():
    if not "loans" in st.session_state:
        with st.expander("Resumen de Préstamo", expanded=False):
            _, colp, _ = st.columns([2, 3, 1])
            colp.button(":blue[No tienes préstamos]", type="tertiary", icon=":material/account_balance:")
            return

    loans = st.session_state.loans

    with st.expander("Resumen de Préstamo", expanded=True):
        if loans:
            monto_inicial = loans['monto_Inicial']
            balance_actual = loans['balance_Prestamo_Actual']
            monto_pagado = monto_inicial - balance_actual
            concepto_descripcion = loans['nombre_Concepto_Nomina']

            # Calcular porcentaje pagado
            porcentaje_pagado = (balance_actual / monto_inicial) * 100

            # Mostrar los balances enmascarados o visibles según el estado
            balance_text = "****" if st.session_state.mask_balances else f"RD$ {format(balance_actual, ',.2f')}"
            monto_pagado_text = "****" if st.session_state.mask_balances else f"RD$ {format(monto_pagado, ',.2f')}"

            # CSS personalizado para estilizar el texto
            st.markdown("""
                <style>
                    .prestamo-text {
                        font-size: 16px;
                        font-weight: bold;
                        color: #333;
                        margin-top: 0px;
                        margin-bottom: 0px;
                    }
                    .caption-text {
                        font-size: 14px;
                        color: #666;
                        margin-top: -8px;
                        margin-bottom: 0px;
                    }
                    .amount-text {  
                        font-size: 30px;
                        font-weight: bold;
                        color: #007BFF;
                        margin-top: 0px;
                    }
                </style>
            """, unsafe_allow_html=True)

            # Mostrar los textos con clases personalizadas
            st.markdown(f'<p class="prestamo-text">{concepto_descripcion}</p>', unsafe_allow_html=True)
            st.markdown('<p class="caption-text">Deuda a la fecha</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="amount-text">{balance_text}</p>', unsafe_allow_html=True)

            progress_text = f"Monto pagado {monto_pagado_text}"
            st.progress(int(porcentaje_pagado), text=progress_text)



                  
# Chat dialog using decorator
@st.dialog("Chat Support", width="large")
def chat_dialog():
    # Create a container for chat messages with fixed height
    messages_container = st.container(height=400, border=False)

    # Display messages in the container
    with messages_container:
        # Display all messages from session state
        for message in st.session_state.messages:
            st.chat_message(message["role"]).write(message["content"])

    # Chat input (placed below the messages container in the UI)
    user_input = st.chat_input("Type a message...")

    # Handle new user input
    if user_input:
        messages_container.chat_message("user").write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Add bot response to chat history
        messages_container.chat_message("assistant").write(
            "Thanks for your message! This is a demo response."
        )
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": "Thanks for your message! This is a demo response.",
            }
        )
          









@st.dialog("Reingreso del Empleado", width="large")
def reingreso_empleado():
    """Muestra un disclaimer para el reingreso del empleado si está en estado VACACIONES."""
    
    e = st.session_state.employee
    st.markdown("### 📋 Reingreso del Empleado")

    st.warning(
        """
        ⚠️ **Aviso Importante:**  
        Actualmente estás registrado en estado de **VACACIONES**.  
        Para reincorporarte a tus labores y acceder nuevamente a las funcionalidades de la plataforma, es necesario aceptar el siguiente aviso:
        """
    )

    st.markdown(
        f"""
        **Información del Empleado:**  
        - 🏢 **Compañía:** {e['nombre_Compania']}  
        - 👤 **Empleado:** {e['nombreCompletoEmpleado']}  
        - 💼 **Puesto:** {e['nombre_Puesto']}  
        - 🏢 **Departamento:** {e['nombre_Departamento']} 
        """
    )
    st.subheader("Declaración de Reingreso")
    st.caption("""Al aceptar, confirmo que he regresado de mis vacaciones y estoy listo para retomar mis responsabilidades laborales.  
        Este registro se utilizará como constancia oficial de mi reincorporación.""")


    col, col1 = st.columns(2)
    if col1.button("Rechazar Reincorporación", type="primary"):
        st.session_state.clear()
        app.switch_page("login")
        
    
    comment = """confirmo que he regresado de mis vacaciones y estoy listo para retomar mis responsabilidades laborales.  
        Este registro se utilizará como constancia oficial de mi reincorporación."""
    # Botón para aceptar el disclaimer
    if col.button(":blue[Aceptar y Reincorporarme]", type="secondary"):
        # Simular la ejecución de un endpoint para cambiar el estado del empleado
        try:
            # Simular el cambio de estado del empleado
            hoy = datetime.datetime.today().date().strftime("%d/%m/%Y")
            if db.set_reincorporacion(hoy, comment=comment):   
                st.session_state.employee["estadoEmpleado"] = 1  # Cambiar estado localmente
                st.success("¡Reincorporación exitosa! Ahora puedes continuar con tus labores.")
            st.rerun()
            
            
            result = db.set_reincorporacion(hoy, comment=comment)
            if result:
                del st.session_state["user_data"]
                st.success("¡Reincorporación exitosa! Ahora puedes continuar con tus labores.")
                st.balloons()
                st.rerun()
            else:
                st.warning("La solicitud no pudo ser procesada. Intenta de nuevo o contacta a soporte.")
                st.stop()
                
        except Exception as e:
            st.error(f"Error al procesar tu reincorporación: {e}")
        st.stop()  # Detener la ejecución si no acepta el disclaimer



@st.fragment
def team():
    """Muestra los colaboradores y las solicitudes pendientes de autorización."""
    e = st.session_state.employee
    colaboradores = e['colaboradores']
    
    # Obtener solicitudes pendientes del session_state
    solicitudes = st.session_state.get("team_requests", [])
    
    #filtrar solo las de estado pendientes
    solicitudes_pendientes = [solicitud for solicitud in solicitudes if solicitud['estado'] == 0]
    
    #filtrar solicitudes  en estado diferente a pendiente
    solicitudes_aut_rech = [solicitud for solicitud in solicitudes if solicitud['estado'] != 0]
    
    # si hay solicitudes, agregar un campo de selección  por defaul false a cada registro, el campo se llamara sel
    if solicitudes_pendientes:
        for solicitud in solicitudes_pendientes:
            solicitud['sel'] = False
            #formatear la fecha
            #fecha = datetime.datetime.strptime(solicitud['fecha'], "%Y-%m-%dT%H:%M:%S")
            #solicitud['fecha'] = fecha.strftime("%d/%m/%Y %H:%M")
            


    col1, col2 = st.columns([1, 4])

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

    # Columna 2: Opciones y solicitudes
    with col2:
        with st.container(border=True):
            st.markdown("### 📋 Opciones y Solicitudes")

            # Opciones para las pills
            options = ["🚯 Desvinculación", "👨🏼‍🎓 Solicitar Colaborador", "🛠️ Herramientas de Trabajo"]

            # Inicializar el estado si no existe
            if "pills_selection_team" not in st.session_state:
                st.session_state["pills_selection_team"] = None

            # Función para manejar el cambio de selección
            def handle_pills_team_change():
                selection = st.session_state["pills_selection_team"]
                if selection == "🚯 Desvinculación":
                    modal_desvinculacion()
                elif selection == "👨🏼‍🎓 Solicitar Colaborador":
                    modal_solicitar_colaborador()
                elif selection == "🛠️ Herramientas de Trabajo":
                    modal_solicitar_herramienta()

                # Reiniciar la selección de las pills
                st.session_state["pills_selection_team"] = None

            # Renderizar las pills
            st.pills(
                "",
                options,
                key="pills_selection_team",
                on_change=handle_pills_team_change,
            )


            # Solicitudes pendientes de autorización
            st.markdown("#### Solicitudes Pendientes")

            if solicitudes_pendientes:
                # Convertir las solicitudes en un DataFrame
                
                df_solicitudes = pd.DataFrame(solicitudes_pendientes)

                # Filtrar columnas relevantes para mostrar en el DataFrame
                columnas_mostrar = [
                    "sel", "id", "usuario", "accion", "descripcion", 
                     "nombre_estado", "comentario", "prioridad", "fecha"
                ]
                df_solicitudes = df_solicitudes[columnas_mostrar]

                # Agregar un DataFrame Explorer para filtrar datos
                
                filtered_df = dataframe_explorer(df_solicitudes, case=False)

                # Mostrar el DataFrame con selección múltiple
                # selected_rows = st.dataframe(
                #     filtered_df,
                #     use_container_width=True,
                #     height=400,
                # )
                
                
    

                
                # result = static_dataframe(filtered_df, clickable_column="id")
                
                # print(result)
                
                data_editor = st.data_editor(filtered_df, hide_index=True)
                
                
                

                # Botones para aceptar o rechazar solicitudes
                col_rechazar, _,  col_aceptar= st.columns([2,4,1])
                with col_aceptar:
                    #filtrar datos del data_editor con sel == True

                    
                    if st.button(":blue[Aceptar Solicitudes]"):
                        #buscar los registros seleccionados por el campo sel
                        selected_rows = data_editor[data_editor['sel'] == True]

                        # Si hay registros seleccionados, aceptar
                        # Si no hay registros seleccionados, mostrar un mensaje
                        if selected_rows.empty:
                            st.warning("No se seleccionaron solicitudes para aceptar.")
                        else:
                            # Aceptar las solicitudes seleccionadas
                            ids = selected_rows['id'].tolist()
                            for id in ids:
                                st.toast(f"Solicitud {id} aceptada.")
                                



                with col_rechazar:
                    if st.button("Rechazar Solicitudes", type="primary"):
                        #buscar los registros seleccionados por el campo sel
                        selected_rows = data_editor[data_editor['sel'] == True]
                        # Si hay registros seleccionados, rechazar
                        # Si no hay registros seleccionados, mostrar un mensaje
                        if selected_rows.empty:
                            st.warning("No se seleccionaron solicitudes para rechazar.")
                        else:
                            # Aceptar las solicitudes seleccionadas
                            ids = selected_rows['id'].tolist()
                            for id in ids:
                                st.toast(f"Solicitud {id} rechazada.")


                
                
            #Mostrsr solicitudes autorizadas o rechazadas
            st.markdown("#### Solicitudes Autorizadas/Rechazadas")
            with st.expander("Ver solicitudes autorizadas/rechazadas", expanded=False):
                if solicitudes_aut_rech:
                    # Convertir las solicitudes en un DataFrame
                    df_solicitudes_aut_rech = pd.DataFrame(solicitudes_aut_rech)

                    # Filtrar columnas relevantes para mostrar en el DataFrame
                    columnas_mostrar = [
                        "id", "usuario", "accion", "descripcion", 
                        "nombre_estado", "comentario", "prioridad", "fecha"
                    ]
                    df_solicitudes_aut_rech = df_solicitudes_aut_rech[columnas_mostrar]

                    # Mostrar el DataFrame con selección múltiple
                    filtered_df_solicitudes_aut_rech = dataframe_explorer(df_solicitudes_aut_rech, case=False)
                    st.dataframe(filtered_df_solicitudes_aut_rech, use_container_width=True, 
                                hide_index=True)
                    
                else:
                    st.info("No hay solicitudes pendientes.")


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
        response = db.set_desvinculacion(body)
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
        response = db.set_requisicion(body)
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