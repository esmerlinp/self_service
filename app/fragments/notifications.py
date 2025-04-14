import streamlit as st
import datetime         


@st.fragment()
def alerts():
    """Muestra las notificaciones del usuario en un diseño atractivo."""
    
    if 'alerts' in st.session_state:
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
   
