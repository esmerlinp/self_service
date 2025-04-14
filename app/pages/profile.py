import streamlit as st
from datetime import datetime
import pandas as pd
import app

    
def formato_fecha(fecha):
    """Convierte la fecha de formato ISO a dd/mm/yyyy"""
    if fecha:
        return datetime.strptime(fecha.split("T")[0], "%Y-%m-%d").strftime("%d/%m/%Y")
    return "N/A"

def employee():
    """Muestra un resumen del perfil del empleado en una interfaz de Streamlit"""
           # Botón para volver a la página principal si se muestran todos los volantes
    if st.button("⬅ Volver"):
        app.switch_page("home")
        
    if 'employee' in st.session_state:
        e = st.session_state.employee


        #st.subheader(e["nombreCompletoEmpleado"])
            
        primerNombreEmpleado = e['primerNombreEmpleado']
        primerApellidoEmpleado = e['primerApellidoEmpleado']

        imagen = f"https://ui-avatars.com/api/?background=random&name={primerNombreEmpleado}+{primerApellidoEmpleado}=100%bold=true"  

        st.markdown(
            f"""
            <div style="display: flex; align-items: center; margin-bottom: 20px;">
                <img src="{imagen}" alt="User Image" style="width: 80px; height: 80px; border-radius: 50%; margin-right: 15px;">
                <div>
                    <h3 style="margin: 0; margin-bottom: 0px;">{e['nombreCompletoEmpleado']}</h3>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        
        # Organizar los campos en dos columnas
        col1, col2 = st.columns(2)
        with col1:
            st.text_input(label="Nombres", value=e['nombreCompletoEmpleado'], disabled=True)
            st.text_input(label="Identificación", value=e['datoIdentificacion'], disabled=True)
            st.text_input(label="Sucursal", value=e['nombre_Sucursal'], disabled=True)
            st.text_input(label="Departamento", value=e['nombre_Departamento'], disabled=True)
            st.text_input(label="Puesto", value=e['nombre_Puesto'], disabled=True)
            st.text_input(label="Tipo de Contrato", value=e['nombre_TipoContrato'], disabled=True)
        with col2:
            st.text_input(label="Fecha de Ingreso", value=e['fechaIngreso'], disabled=True)
            st.text_input(label="Salario Base", value=e['salarioBase'], disabled=True)
            st.subheader("Datos personales")
            st.text_input(label="Fecha de Nacimiento", value=e['fechaNacimiento'], disabled=True)
            st.text_input(label="Teléfono Personal", value=e['telefonoPersonal'], disabled=True)
            st.text_input(label="Nombre de Contacto de Emergencia", value=e['nombreContactoEmergencia'], disabled=True)
            st.text_input(label="Teléfono de Contacto de Emergencia", value=e['telefonoContactoEmergencia'], disabled=True)
        
        
        with st.expander("Herramientas"):
            st.write("example")
        with st.expander("Capasitaciones"):
            st.write("example")
        with st.expander("Ausencias"):
            if 'ausencias' in st.session_state:
                ausencias = st.session_state.ausencias    
                if ausencias:
                    aus = pd.DataFrame([
                        {
                            "Tipo de Ausencia": a['nombre_Tipo_Ausencia'],
                            "Fecha de Inicio": a['fecha_Inicio'],
                            "Fecha de Fin": a['fecha_Fin'],
                            "Cantidad": a['cantidad']
                        }
                        for a in ausencias if a['motivo_Razon'] != 1
                    ])
                    st.dataframe(aus)  # Mostrar el DataFrame en la interfaz de Streamlit
                else:
                    st.caption("Sin datos para mostrar")
            else:
                st.caption("Sin ausencias registradas")    
                
        with st.expander("Vacaciones"):
            
            if 'ausencias' in st.session_state:
                ausencias = st.session_state.ausencias  
                vacaciones = ausencias
                if vacaciones:
                    aus = pd.DataFrame([
                        {
                            "Tipo de Ausencia": a['nombre_Tipo_Ausencia'],
                            "Fecha de Inicio": a['fecha_Inicio'],
                            "Fecha de Fin": a['fecha_Fin'],
                            "Cantidad": a['cantidad']
                        }
                        for a in vacaciones if a['motivo_Razon'] == 1
                    ])
                    st.dataframe(aus)  # Mostrar el DataFrame en la interfaz de Streamlit
                else:
                    st.caption("Sin datos para mostrar")
            else:
                st.caption("Sin ausencias registradas") 
                
        with st.expander("Amonestaciones"):
            st.write("example")
            
