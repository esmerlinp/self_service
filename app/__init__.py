import streamlit as st




# Función para cambiar de página
def switch_page(page_name, params=None, fragment_detail=None):
    """
    Cambia la página actual a la especificada por `page_name`.
    Si se proporciona `fragment_detail`, se establece en el estado de la sesión.
    """
    
    if fragment_detail:
        st.session_state.fragment = fragment_detail

    page = {"page": page_name, "params": params}
    st.session_state.page = page
    
    st.rerun()
    
