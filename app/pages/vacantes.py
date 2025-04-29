import streamlit as st
import app
from app.util import show_alert
from app.core import aplicar_a_vacante


@st.fragment
def detalle_vacante():
    #print(st.session_state.vacante_apply)
    vacante = st.session_state.vacante_apply
    #vacante = st.session_state.requisiciones[0]
    _, col, _ = st.columns([0.5,3,0.5])
    with col.container():
        st.markdown(
            f"""
            <div style="border: 0px solid #ddd; border-radius: 12px; padding: 15px; margin-bottom: 10px; background-color: #f9f9f9; display: flex; flex-direction: column; justify-content: space-between;">
                <div>
                    <h4 style="margin: 0; font-size: 20px; font-weight: bold; color: #333;">{vacante['nombre_Requisicion'].upper()}</h4>
                    <p style="margin: 0; font-size: 14px; color: #555;">🏢 {vacante['nombreCompania']}</p>
                    <p style="margin: 0; font-size: 14px; color: #555;">💼 Departamento: {vacante['nombreDepartamento']}</p>
                    <p style="margin: 0; font-size: 14px; color: #555;">📋 Puesto: {vacante['nombre_Puesto']}</p>
                    <p style="margin: 0; font-size: 14px; color: #555;">📜 Contrato: {vacante['nombreTipoContrato']}</p>
                    <p style="margin: 0; font-size: 16px; font-weight: bold; margin-top: 10px;">Descripción</p>
                    <p style="margin: 0; font-size: 14px; color: #888;">{vacante['descripcion']}</p>
                    <p style="margin: 0; font-size: 16px;font-weight: bold; margin-top: 10px;">Requisitos</p>
                    <p style="margin: 0; font-size: 14px; color: #888;">{vacante.get('requisitosPuesto', '')}</p>
                    <p style="margin: 0; font-size: 16px;font-weight: bold; margin-top: 10px;">Responsabilidades</p>
                    <p style="margin: 0; font-size: 14px; color: #888;">{vacante.get('responsabilidadesPuesto', '')}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        apply = st.button(":blue[Aplicar]", type="secondary", key=f"apply_{vacante['id']}", help="Aplicar a la vacante", use_container_width=True)
        if apply:
            response = aplicar_a_vacante(id_requisicion=vacante['id'] )
            
            if response.get('error', False):
                show_alert(
                    "!Upsss!",
                    "Ocurrió un error interno al intentar aplicar a la vacante. Por favor, inténtalo nuevamente o contacta al soporte técnico.",
                    response['error']
                )   
            else:
                st.balloons()
                show_alert(
                    "Aplicación exitosa",
                    "Has aplicado a la vacante con éxito. Te deseamos mucha suerte en el proceso de selección."
                )    
                                        
        
   
@st.fragment
def vacantes(all=False):
    """Muestra las vacantes disponibles en un diseño atractivo estilo feed con tamaño fijo."""
    # Mostrar las vacantes
    
    if st.button(":gray[/ Inicio /] :blue[Vacantes]", type="tertiary",  key="vacante_volver_home"):
        app.switch_page("home")
         
            
    requisiciones = []
    if 'requisiciones' in st.session_state:
        if st.session_state.requisiciones:
            requisiciones = st.session_state.requisiciones
                
    expanded = len(requisiciones) > 0
    with st.expander("💼 Vacantes Disponibles", expanded=expanded):
        
        cant_columns = 1
        
        if requisiciones:
            requisiciones = st.session_state.requisiciones
            # Ordenar las vacantes por fecha de publicación (más recientes primero)
            requisiciones = sorted(
                requisiciones,
                key=lambda x: x["id"],
                reverse=True
            )
            
            if  all:
                cant_columns = 3
            else:
                requisiciones = requisiciones[:1]
        else:
            st.caption("No hay vacantes publicadas")
            return
                
        
        
                
        if requisiciones:

                
            cols = st.columns(cant_columns)  # Dividir en 2 columnas para simular un feed
            for idx, vacante in enumerate(requisiciones):
                with cols[idx % cant_columns]:  # Distribuir las vacantes en las columnas  
                    # Mostrar tarjeta estilo Instagram con tamaño fijo
                    with st.container():
                        st.markdown(
                            f"""
                            <div style="border: 0px solid #ddd; border-radius: 12px; padding: 15px; margin-bottom: 10px; background-color: #f9f9f9; height: 350px; display: flex; flex-direction: column; justify-content: space-between;">
                                <div>
                                    <h4 style="margin: 0; font-size: 20px; font-weight: bold; color: #333;">{vacante['nombre_Requisicion']}</h4>
                                    <p style="margin: 0; font-size: 14px; color: #555;">🏢 {vacante['nombreCompania']}</p>
                                    <p style="margin: 0; font-size: 14px; color: #555;">💼 Departamento: {vacante['nombreDepartamento']}</p>
                                    <p style="margin: 0; font-size: 14px; color: #555;">📋 Puesto: {vacante['nombre_Puesto']}</p>
                                    <p style="margin: 0; font-size: 14px; color: #555;">📜 Contrato: {vacante['nombreTipoContrato']}</p>
                                    <p style="margin: 0; font-size: 16px;">Descripción</p>
                                    <p style="margin: 0; font-size: 14px; color: #888;">{vacante['descripcion'][:400]}...</p>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        


                        if st.button(":blue[Ver detalles]", type="secondary", key=f"see_{vacante['id']}", help="Aplicar a la vacante", use_container_width=True):
                            #detalle_vacante(vacante=vacante)
                            st.session_state.vacante_apply = vacante
                            app.switch_page("detail", fragment_detail="detalle_vacante")
            
            if st.button(":blue[Ver todas]", type="tertiary", help="Ver todas las vacantes", use_container_width=True, disabled=all):
                app.switch_page("detail", fragment_detail="vacantes")  
               
        else:
            st.info("No hay vacantes disponibles en este momento.")
                
