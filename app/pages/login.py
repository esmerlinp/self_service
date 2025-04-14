import streamlit as st
from app.core import Core
import app
import json


def login(cookies):
    
    container = st.container()
    with container:
        colimage, colmain, _ = st.columns([3, 3, 0.5])  # Mantiene el formulario centrado
        with colimage:
            st.image("./app/assets/loginImage.png", use_container_width=True)
            
        with colmain:
            
            with st.form("login_form", enter_to_submit=True, clear_on_submit=True):
                st.subheader("Portal Autogestión")
                st.caption("Para acceder al Autoservicio, ingresa tu usuario y contraseña. Si es tu primer acceso, usa la opción 'Restablecer contraseña'.")
                
                email = st.text_input("Correo electrónico", placeholder="jdoe@mail.com", help="Ingrese su correo electrónico", value="esmerlinep")
                passwd = st.text_input("Contraseña", type="password", value="Hol@0000")
               

                submitted = st.form_submit_button("Iniciar sesión")
                
                if submitted:
                    with st.spinner(text='In progress'):
                        core = Core()
                        user = core.sign_in(email=email, password=passwd)
                        
                    if user:
                        
                        st.session_state.user = user
                        st.session_state.is_auth = str(True)
            
                         # Actualizar cookies
                        cookies["is_auth"] = str(True)
                        cookies["user"] = json.dumps(user)
                        cookies.save()
                        
                        print(cookies)
                        app.switch_page("home")
                    else:
                        st.session_state.is_auth = str(False)
                        cookies["is_auth"] = str(False)
                        #cookies["user"] = json.dumps(user)
                        cookies.save()
                        st.warning("Usuario o contraseña inválidos")

            with st.container():
                col1, col2 = st.columns([3,2])
                with col1:
                    st.checkbox("Recordarme", value=True)
                with col2:
                    if st.button(":blue[Restablecer contraseña]", type="tertiary", icon=":material/passkey:"):
                        modal_restablecer_contrasena()   
                    
    return container



# Modal para restablecer contraseña
@st.dialog("Restablecer contraseña", width="large")
def modal_restablecer_contrasena():
    st.subheader("Restablecer contraseña")
    st.caption("Por favor, ingresa tu correo electrónico registrado. Te enviaremos un enlace para actualizar tu contraseña.")
    st.caption("📧 Si no recibes el correo, revisa tu carpeta de spam o intenta nuevamente.")

    # Campo para ingresar el correo electrónico
    email = st.text_input("Correo electrónico", placeholder="jdoe@mail.com", help="Ingrese su correo electrónico registrado")

    # Botón para enviar el enlace de restablecimiento
    if st.button("Enviar enlace"):
        if email.strip():
            with st.spinner("Enviando enlace..."):
                core = Core()
                success = core.reest_password(email=email)
                
            if success:
                st.success("El enlace para restablecer tu contraseña ha sido enviado a tu correo electrónico.")
            else:
                st.error("El correo ingresado no está registrado en nuestro sistema. Por favor, verifica e intenta nuevamente.")
        else:
            st.warning("Por favor, ingresa un correo electrónico válido.")