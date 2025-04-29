import streamlit as st
from app.core import set_reincorporacion, get_loans
import datetime
import app
from app.fragments import ausencias



def error_fragment(cookies = None):
    """Muestra un mensaje de error si no se encuentra el fragmento."""

    with st.container():
        # Crear un contenedor para centrar el contenido
        _, col2, _ = st.columns([1.2, 2, 1.2])  # Crear columnas para centrar horizontalmente
        with col2:
            # Crear espacio dinámico para centrar verticalmente
            for _ in range(4):  # Ajusta el rango para controlar el espacio vertical
                st.markdown("&nbsp;")  # Espacio vacío
            
            st.image("./app/assets/3804918.jpg", width=300)    
            st.markdown("#### No se pudo cargar la información del empleado. Por favor, inicia sesión nuevamente.")
            if st.button("Iniciar sesión nuevamente", type="primary", icon=":material/login:"):
                if cookies:
                    cookies["is_auth"] = str(False)
                    
                st.session_state.is_auth = str(False)
                st.session_state.token = ""
                st.session_state.user = None
                app.switch_page("login")
            
                

           
@st.fragment
def resumen_prestamo():
    if not 'mask_balances' in st.session_state:
        st.session_state.mask_balances = True
    
    if not "loans" in st.session_state:
        with st.expander(":material/real_estate_agent: Resumen de Préstamo", expanded=False):
            st.button(":blue[No tienes préstamos]", type="tertiary", icon=":material/account_balance:")
    else:
        loans = {}    
        loans_array = st.session_state.loans
        if len(loans_array) > 0:
            loans = loans_array[0]
        #loans = get_loans()
        with st.expander(":material/real_estate_agent: Resumen de Préstamo", expanded=False):
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
            else:
                st.button(":blue[No tienes préstamos]", type="tertiary", icon=":material/account_balance:", key="key_pre_label")
                


                  
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
def reingreso_empleado(cookies):
    """Muestra un disclaimer para el reingreso del empleado si está en estado VACACIONES."""
    
     # Inicializar el estado si no existe
    if "reingreso_pendiente" not in st.session_state:
        st.session_state["reingreso_pendiente"] = True
        
        
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


    col, _, col1 = st.columns(3)
    if col1.button("Rechazar Reincorporación", type="primary"):
        cookies["is_auth"] = str(False)
        st.session_state.is_auth = str(False)
        st.session_state.token = ""
        st.session_state.user = None
        cookies.save()
        app.switch_page("login")
        
    
    comment = """confirmo que he regresado de mis vacaciones y estoy listo para retomar mis responsabilidades laborales.  
        Este registro se utilizará como constancia oficial de mi reincorporación."""
    # Botón para aceptar el disclaimer
    if col.button(":blue[Aceptar y Reincorporarme]", type="secondary"):
        # Simular la ejecución de un endpoint para cambiar el estado del empleado
        try:
            # Simular el cambio de estado del empleado
            hoy = datetime.datetime.today().date().strftime("%Y-%m-%dT%H:%M:%S")
            # if set_reincorporacion(hoy, comment=comment):   
            #     st.session_state.employee["estadoEmpleado"] = 1  # Cambiar estado localmente
            #     st.success("¡Reincorporación exitosa! Ahora puedes continuar con tus labores.")
            #     st.session_state.need_accept_disclaimer = False
            # st.rerun()
            
            
            result = set_reincorporacion(e['idEmpleado'], hoy, comment=comment)
            if result:
                st.session_state["reingreso_pendiente"] = False  # Marcar como resuelto
                e["estadoEmpleado"] = 1
                e["nombre_EstadoEmpleado"] = "ACTIVO"
                st.session_state.employee = e
                st.rerun()
            else:
                st.warning("La solicitud no pudo ser procesada. Intenta de nuevo o contacta a soporte.")
                st.stop()
                
        except Exception as e:
            st.error(f"Error al procesar tu reincorporación: {e}")
        st.stop()  # Detener la ejecución si no acepta el disclaimer



    
@st.fragment()
def accesos_directos():
    with st.container(border=True):
        if st.button("Historial de solicitudes", type="tertiary", icon=":material/read_more:"):
            ausencias.resumen_permisos_dialog()

        if st.button("Vacantes disponibles", icon=":material/person_apron:", type="tertiary"):
            app.switch_page('vacantes')

        if st.button("Volantes de pago", icon=":material/account_balance_wallet:", type="tertiary"):
            app.switch_page('payments')