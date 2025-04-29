import streamlit as st
from app.pages import home, login, loans, payments, profile, detail, vacantes, empleado
from st_cookies_manager import EncryptedCookieManager
import os, json
import locale
from app.util import jwt_decode


# Configuración de la página
st.set_page_config(
    page_title="SelfService",
    page_icon="./app/assets/logo.png",
    layout="wide"
)

# Establecer el idioma en español
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')  # Para sistemas basados en Unix
except locale.Error:
    locale.setlocale(locale.LC_TIME, '')  # fallback
    

# Inicializar el administrador de cookies
cookies = EncryptedCookieManager(
    prefix="camsoft/self-service",  # Prefijo para las cookies
    password=os.environ.get("COOKIES_PASSWORD", "qaxriQ-kojky7-fenxeb"),
)


if not cookies.ready():
    # Wait for the component to load and send us current cookies.
    st.spinner()
    st.stop()



# # Inicializar el estado de autenticación
st.session_state.is_auth = cookies.get("is_auth", str(False))
st.session_state.token = cookies.get("token", "")
#st.session_state.mask_balances = True

st.session_state.show_payroll = cookies.get("cookies_show_payroll", str(True))
st.session_state.show_loan = cookies.get("cookies_show_loan", str(True))
st.session_state.show_savings = cookies.get("cookies_show_savings", str(True))

# Intentar recuperar los datos del usuario desde las cookies

if "user" not in st.session_state and st.session_state.is_auth == str(True):
    try:
        st.session_state.user = jwt_decode(st.session_state.token)
    except (json.JSONDecodeError, TypeError):
        st.session_state.user = None
        st.session_state.is_auth = str(False)

# # Si el usuario no está autenticado, redirigir a la página de login

if not 'page' in st.session_state:
    if not st.session_state.is_auth == str(True) or not st.session_state.token:
        st.session_state.page = {"page":"login", "params": None}
    else:
        st.session_state.page = {"page":"home", "params": None}


# Obtener parámetros de la URL
# query_params = st.query_params
# if query_params:
    
#     page = query_params.get("page", [st.session_state.page["page"]])  # Predeterminado al valor actual de la sesión
#     employee_id = query_params.get("employeeId", [None])
#     from_screen = query_params.get("from_screen", [None])
#     # Actualizar la lógica de enrutamiento con los parámetros de la URL
#     if page == "empleado" and employee_id:
#         st.session_state.page = {"page": "empleado", "params": {"employeeId": employee_id, "from_screen": from_screen}}
#         empleado.employee_detail(employeeId=int(employee_id), from_screen=from_screen)
#         st.stop()
#     elif page != st.session_state.page["page"]:
#         st.session_state.page = {"page": page, "params": None}



page = st.session_state.page["page"]
params = st.session_state.page["params"]

if page == "login":
    login.login(cookies)  # Renderiza la página de login
elif page == "home":
    home.home(cookies)  # Renderiza la página de inicio
elif page == "loans":
    loans.loans()  # Renderiza la página de préstamos
elif page == "payments":
    payments.mostrar_volantes()  # Renderiza la página de pagos
elif page == "vacantes":
    vacantes.vacantes(all=True)  # Renderiza la página de pagos
elif page == "profile":
    profile.user_profile()  # Renderiza la página de perfil
elif page == "detail":
    detail.show_fragment()
elif page == "empleado":
    empleado.employee_detail(**params)