import streamlit as st
import datetime         
from app.core import get_alerts
import logging
from app.util import tiempo_transcurrido
    

def verificar_alertas():
    """Verifica nuevas alertas y muestra un toast si hay nuevas."""
    



    try:
        # Obtener nuevas alertas
        alertas = get_alerts(save_in_session=False)
        if  alertas:
            # Filtrar alertas nuevas
            
            if "alerts" not in st.session_state:
                st.session_state.alerts = []
    
            notificaciones = st.session_state.alerts
            
            alertas_nuevas = []
            if notificaciones:
                #alertas_existentes_ids = {alerta["id"] for alerta in notificaciones[:len(nuevas_alertas) - 1]}
                alertas_existentes_ids = {alerta["id"] for alerta in notificaciones}
                alertas_nuevas = [alerta for alerta in alertas if alerta["id"] not in alertas_existentes_ids]

            else:
                alertas_nuevas = alertas
                
            for alerta in alertas_nuevas:
                st.toast(f"Nueva alerta: {alerta['message']}", icon=":material/notifications:")
                st.session_state.alerts = alertas
            
    except Exception as e:
        logging.error(f"Error al obtener alertas: {e}")

     
  

@st.fragment(run_every=60)
def render_notificaciones():
    """Muestra las notificaciones recientes en un diseño similar a actividades recientes."""
    
    verificar_alertas()
    
    with st.expander("🔔 Notificaciones Recientes", expanded=True):
        # Número inicial de registros a mostrar
        if 'alerts' in st.session_state and st.session_state.alerts:
            
            alertas = st.session_state.alerts
            if alertas:
                
                if "num_notificaciones" not in st.session_state:
                    st.session_state.num_notificaciones = 4  # Mostrar inicialmente 4 notificaciones

                # Ordenar las alertas por fecha (más recientes primero)
                alertas_ordenadas = sorted(
                    alertas,
                    key=lambda x: datetime.datetime.strptime(x['fullDate'], "%Y-%m-%dT%H:%M:%S.%f"),
                    reverse=True
                )

                # Limitar las notificaciones mostradas según el estado
                alertas_mostradas = alertas_ordenadas[:st.session_state.num_notificaciones]

                if not alertas_ordenadas:
                    st.caption("No hay notificaciones en este momento.")
                    return

                # Mostrar las notificaciones
                for alerta in alertas_mostradas:
                    # Parsear la fecha
                    fecha = datetime.datetime.strptime(alerta['fullDate'], "%Y-%m-%dT%H:%M:%S.%f").strftime("%d de %B de %Y, %H:%M")
                    tiempo = tiempo_transcurrido(datetime.datetime.strptime(alerta['fullDate'], "%Y-%m-%dT%H:%M:%S.%f"))

                    # Construir el título y el mensaje
                    titulo = f"{alerta['title']}"
                    mensaje = f"{alerta['message']}"

                    # Determinar el ícono según el tipo de alerta
                    icono = '<span class="material-symbols-outlined">notifications</span>'
                    # if alerta['categoryName'] == "error":
                    #     icono = '<span class="material-symbols-outlined" style="color: #EA3323;">error</span>'
                    # elif alerta['tipo'] == "warning":
                    #     icono = '<span class="material-symbols-outlined" style="color: #F7B801;">warning</span>'
                    # elif alerta['tipo'] == "success":
                    #     icono = '<span class="material-symbols-outlined" style="color: #48752C;">check_circle</span>'

                    # Mostrar la notificación
                    st.markdown(f"""
                        <div style="display: flex; flex-direction: row; align-items: center; margin-bottom: 8px; gap: 12px;">
                            <div style="display: flex; flex-direction: column; align-items: flex-start;">
                                <span style="font-size: 14px; font-weight: bold; color: #333;">{titulo}</span>
                                <span style="font-size: 12px; color: #666;">{mensaje}</span>
                                <span style="font-size: 12px; color: #999;">🕒 {tiempo} - 👤 De: {alerta['fromUserName']}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                # Botón dinámico para mostrar más o menos notificaciones
                if len(alertas_ordenadas) > 4:  # Mostrar el botón solo si hay más de 4 notificaciones
                    if st.session_state.num_notificaciones > 4:
                        button_label = ":red[Mostrar menos]"
                    else:
                        button_label = ":blue[Mostrar más]"

                    if st.button(button_label, type="tertiary", key="notificaciones_more_less"):
                        if st.session_state.num_notificaciones > 4:
                            st.session_state.num_notificaciones = 4  # Reducir a 4 notificaciones
                        else:
                            st.session_state.num_notificaciones += 4  # Incrementar en 4 notificaciones
                        st.rerun(scope="fragment")
            else:
                st.caption("No tienes notificaciones.")
        else:
            st.caption("No tienes notificaciones.")
@st.fragment(run_every=60)
def alerts():
    """Muestra las notificaciones del usuario en un diseño atractivo."""
    
    verificar_alertas()
    
    if 'alerts' in st.session_state and st.session_state.alerts:
        
        
        st.markdown("###### 🔔 Últimas Notificaciones")
        with st.container():
            if st.session_state.alerts:
                # Mostrar solo las 5 más recientes o todas según el estado
                if "show_all_alerts" not in st.session_state:
                    st.session_state.show_all_alerts = False

                alerts = st.session_state.alerts
                alerts_to_display = alerts if st.session_state.show_all_alerts else alerts[:5]

                for alert in alerts_to_display:
                    # Convertir la fecha al formato deseado
                    try:
                        fecha = datetime.datetime.strptime(alert['fullDate'], "%Y-%m-%dT%H:%M:%S").strftime("%d/%m/%Y %H:%M")
                    except ValueError:
                        fecha = alert['fullDate']  # Usar la fecha original si hay un error

                    # Mostrar cada notificación con un diseño atractivo
                    st.markdown(
                        f"""
                        <div style="border: 1px solid #ddd; border-radius: 8px; padding: 10px; margin-bottom: 10px; background-color: #f9f9f9;">
                            <p style="margin: 0; font-size: 16px; font-weight: bold; color: #333;">📌 {alert['title']}</p>
                            <p style="margin: 0; font-size: 14px; color: #555;">{alert['message']}</p>
                            <p style="margin: 0; font-size: 12px; color: #888;">🕒 {fecha} | Categoría: {alert['categoryName']}</p>
                            <p style="margin: 0; font-size: 12px; color: #888;">👤 De: {alert['fromUserName']}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                # Botón para alternar entre "Ver todas" y "Mostrar menos"
                if len(alerts) > 5:
                    if st.session_state.show_all_alerts:
                        if st.button(":blue[Mostrar menos]", type="tertiary", key="alertless"):
                            st.session_state.show_all_alerts = False
                    else:
                        if st.button(":blue[Ver todas]", type="tertiary", key="alertmore"):
                            st.session_state.show_all_alerts = True
    else:
        st.caption("No tienes notificaciones.")
   
