import streamlit as st



# Función para cambiar de página
def switch_page(page_name, fragment_detail=None):
    """
    Cambia la página actual a la especificada por `page_name`.
    Si se proporciona `fragment_detail`, se establece en el estado de la sesión.
    """
    
    print("switching page", page_name)
    if fragment_detail:
        st.session_state.fragment = fragment_detail

    st.session_state.page = page_name
    st.rerun()
    
