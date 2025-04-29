import streamlit as st
from datetime import datetime
import pandas as pd
import app
from streamlit_avatar import avatar
import json
    
def formato_fecha(fecha):
    """Convierte la fecha de formato ISO a dd/mm/yyyy"""
    if fecha:
        return datetime.strptime(fecha.split("T")[0], "%Y-%m-%d").strftime("%d/%m/%Y")
    return "N/A"


def save_cookies(cookies):
    """Guarda las cookies en el estado de la sesión"""
    
    cookies.save()

@st.dialog("Configuración", width="large")
@st.fragment()
def user_profile(cookies):
    """Función para mostrar el perfil del usuario"""
    # Obtener el perfil del usuario desde el estado de la sesión
    if 'user' in st.session_state:
        #user = st.session_state.user
        # Mostrar el perfil del usuario
        
        user = st.session_state.user
        # Mostrar la imagen del usuario

        imagen = f"https://ui-avatars.com/api/?background=random&name={user['FullUserName']}=100%bold=true&background=61a1af&color=fdfdfd"

        avatar(
            [
                {
                    "url": imagen,
                    "size": 100,
                    "title": f"{user['FullUserName']}",
                    "caption": f"{user['userId']} - {user['userEmail']}",
                    "key": f"{user['userId']}",
                }
            ]
        )
        # Organizar los campos en dos columnas

        st.text_input(label="Compañía", value=user['CompanyName'], disabled=True)
        #st.text_input(label="Departamento", value=user['officeName'], disabled=True)
        
        # #opcion parta mosrar volante de pago
        # if st.toggle("Mostrar volante de pago", value=True, key="_show_payroll"):
        #     cookies["cookies_show_payroll"] = str(True)
        #     st.session_state.show_payroll = True
        #     #cookies.save()
        # else:
        #     cookies["cookies_show_payroll"] = str(True)
        #     st.session_state.show_payroll = False
        #     #cookies.save()
           
        
        #opcion para mostrar volante de prestamo
        if st.toggle("Mostrar resumen de prestamo", value=True, key="_show_loan"):
            cookies["cookies_show_loan"] = str(True)
            st.session_state.show_loan = True
            #save_cookies(cookies)
        else:
            cookies["cookies_show_loan"] = str(True)
            st.session_state.show_loan = False
            #save_cookies(cookies)
            
        
        #opcion para mostrar volante de ahorro
        st.session_state.show_savings = st.toggle("Mostrar resumen de ahorro", value=True, key="_show_savings")
        
        # #opcion para mostrar volante  vacantes
        # st.session_state.show_vacancies = st.toggle("Mostrar volante de vacantes", value=True, key="_show_vacancies")
       
        # #opcion para mostrar Cumpleaños
        # st.session_state.show_birthdays = st.toggle("Mostrar Cumpleaños", value=True, key="_show_birthdays")
        
        # #opcion para mostrar promociones
        # st.session_state.show_promotions = st.toggle("Mostrar promociones", value=True, key="_show_promotions")

        st.markdown("&nbsp;")
        # cerrar la sesión
        if st.button("Cerrar sesión", type="primary", icon=":material/logout:"):
            # Limpiar el estado de la sesión
            # Redirigir a la página de inicio de sesión
            cookies["is_auth"] = str(False)
            del st.session_state.is_auth
            del st.session_state.user
            del st.session_state.employee
            del st.session_state.token
            del st.session_state.employeeId
            save_cookies(cookies)
            app.switch_page("login")
        
       

        
        

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
            
