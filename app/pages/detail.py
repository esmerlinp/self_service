import streamlit as st
import app
from app.fragments import birthdays, promotions
from app.fragments import (
    resumen_prestamo,
    savings,
    ausencias,
    
)
from app.pages import vacantes

#pagina de standard para mostrar mas detalles de todos los fragments, recibe  el fragment a mostrar  en una pagina independiente.

def show_fragment():
    """
    Muestra un fragmento específico en una página independiente.
    """
    
    # Botón para volver a la página principal si se muestran todos los volantes
    if st.button("⬅ Volver"):
        app.switch_page("home")
        
    if 'fragment' not in st.session_state:
        st.session_state.fragment = "employee"
        
    fragment = st.session_state.fragment
    
    if fragment == "resumen_prestamo":
        resumen_prestamo()
    elif fragment == "resumen_ahorros": 
        savings.resumen_ahorros()
    elif fragment == "detalle_vacante":
        vacantes.detalle_vacante()
    elif fragment == "user_requests":
        ausencias.resumen_permisos()
    elif fragment == "birthdays":
        birthdays.birthdays(all=True)
    elif fragment == "promos":
        promotions.promos(all=True)

    else:
        st.error("Fragmento no reconocido.")
        st.stop()