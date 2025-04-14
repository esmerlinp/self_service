import streamlit as st
import app
from app.pages import home, login, loans, payments, profile, detail
from st_cookies_manager import EncryptedCookieManager
import os, json
import locale


# Configuración de la página
st.set_page_config(
    page_title="SelfService",
    page_icon="👋",
    layout="wide"
)

st.markdown("""
<style>
    section.stMain .block-container {
        padding-top: 0rem;
    }
</style>

""", unsafe_allow_html=True)


# Establecer el idioma en español
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')  # Para sistemas basados en Unix
except locale.Error:
    locale.setlocale(locale.LC_TIME, '')  # fallback

# Inicializar el administrador de cookies
cookies = EncryptedCookieManager(
    prefix="camsoft/self-service",  # Prefijo para las cookies
    #password=os.environ.get("COOKIES_PASSWORD", "My secret password"),
    password="Hol@12340000"  # Cambia esto por una contraseña segura
)

if not 'is_auth' in st.session_state:


    if not cookies.ready():
        # Wait for the component to load and send us current cookies.
        st.spinner()
        st.stop()



    # # Inicializar el estado de autenticación
    st.session_state.is_auth = cookies.get("is_auth", str(False))

    # Intentar recuperar los datos del usuario desde las cookies

    if "user" not in st.session_state and st.session_state.is_auth == str(True):
        try:
            st.session_state.user = json.loads(cookies.get("user", "{}"))
        except (json.JSONDecodeError, TypeError):
            st.session_state.user = None
            st.session_state.is_auth = False


# # Si el usuario no está autenticado, redirigir a la página de login
if not 'page' in st.session_state:
    if not st.session_state.is_auth == str(True):
        st.session_state.page = "login"
    else:
        st.session_state.page = "home"


if st.session_state.page == "login":
    login.login(cookies)  # Renderiza la página de login
elif st.session_state.page == "home":
    home.home()  # Renderiza la página de inicio
elif st.session_state.page == "loans":
    loans.loans()  # Renderiza la página de préstamos
elif st.session_state.page == "payments":
    payments.mostrar_volantes()  # Renderiza la página de pagos
elif st.session_state.page == "profile":
    profile.employee()  # Renderiza la página de perfil
elif st.session_state.page == "detail":
    detail.show_fragment()