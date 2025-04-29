import streamlit as st
from app.core import sign_in, reest_password
import app
import json
import datetime
from app.util import jwt_decode, get_base64_image


def login(cookies):
    
    
    container = st.container(border=False)
    with container:
        for _ in range(3):  # Ajusta el rango para controlar el espacio vertical
            st.markdown("&nbsp;")  # Espacio vacío
                    
        _, colimage, colmain, _ = st.columns([0.5, 3, 2, 0.5])  # Mantiene el formulario centrado
        with colimage:
            st.image("./app/assets/10030694.jpg", use_container_width=True)
            
        with colmain:
            #for _ in range(1):  # Ajusta el rango para controlar el espacio vertical
            #st.markdown("&nbsp;")  # Espacio vacío
            image_base64 = get_base64_image("app/assets/logo.png")

            with st.container():
                #titulo markdown con imagen al lado del titulo ./app/assets/logo.png
                st.markdown(
                    """
                    <style>
                        .title-container {
                            display: flex;
                            align-items: center;
                            gap: 10px; /* Espaciado entre la imagen y el texto */
                        }
                        .title-container img { /* Solo afecta a las imágenes dentro de .title-container */
                            width: 40px; /* Ajusta el tamaño de la imagen */
                            height: 40px;
                        }
                        .title {
                            font-size: 2rem;
                            font-weight: bold;
                            color: #0073e6; /* Cambia el color según tu preferencia */
                        }
                    </style>
                    <div class="title-container">
                        <img src="https://i.postimg.cc/sX9zSNPz/temp-Image5l-GHl-R.avif" >
                        <h2 class="title">Portal Autogestión</h2>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

             
                st.caption("Para acceder al Autoservicio, ingresa tu usuario y contraseña. Si es tu primer acceso, usa la opción 'Restablecer contraseña'.")
                
                email = st.text_input("Nombre de usuario", placeholder="jdoe", value="esmerlinep")
                passwd = st.text_input("Contraseña", type="password", value="Hol@0000")
                recordarme = st.checkbox("Recordarme", value=True, disabled=True)
                
   
         

                submitted = st.button(":blue[Iniciar sesión]", icon=":material/login:", use_container_width=True)
                
                if submitted:
                    st.session_state.data_loaded = False
                    with st.spinner(text='In progress'):
                        
                        user = sign_in(email=email, password=passwd)
            
                        if user:
                            
                            cookies["is_auth"] = str(True)
                            cookies["token"] = user["access_Token"]
                            cookies.save()
                            app.switch_page("home")
                        else:
                            st.session_state.is_auth = str(False)
                            cookies["is_auth"] = str(False)
                            cookies["token"] = ""
                            cookies.save()
                            st.warning("Usuario o contraseña inválidos")

                with st.container():
                    _, col2, _ = st.columns([1,2,1])
                    with col2:
                        if st.button(":red[Restablecer contraseña]", type="tertiary", icon=":material/passkey:", use_container_width=True):
                            modal_restablecer_contrasena()   
                            
        st.markdown("&nbsp;")
        st.markdown("&nbsp;")
        st.caption("© 2025 Camsoft. S.R.L - Todos los derechos reservados.")
    return container



# Modal para restablecer contraseña
@st.dialog("Restablecer contraseña", width="large")
def modal_restablecer_contrasena():
    with st.container(height=400, border=False):
        st.subheader("Restablecer contraseña")
        st.markdown("""Por favor, ingresa tu correo electrónico registrado. Te enviaremos un enlace para actualizar tu contraseña.
                    Si no recibes el correo, revisa tu carpeta de spam o intenta nuevamente.""")

        st.markdown("&nbsp;")  # Espacio vacío
        # Campo para ingresar el correo electrónico
        email = st.text_input("Correo electrónico", placeholder="jdoe@mail.com", help="Ingrese su correo electrónico registrado")

        # Botón para enviar el enlace de restablecimiento
        if st.button("Enviar enlace"):
            if email.strip():
                with st.spinner("Enviando enlace..."):
                    
                    success = reest_password(email=email)
                    
                if success:
                    st.success("El enlace para restablecer tu contraseña ha sido enviado a tu correo electrónico.")
                else:
                    st.error("El correo ingresado no está registrado en nuestro sistema. Por favor, verifica e intenta nuevamente.")
            else:
                st.warning("Por favor, ingresa un correo electrónico válido.")