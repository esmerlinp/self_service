import streamlit as st
from streamlit_avatar import avatar
from streamlit_extras.floating_button import floating_button
from app.core import Core
from app.pages.payments import mostrar_volantes
from app.util import base64_to_image, show_alert
import datetime, time
import time as t
import app

from streamlit_navigation_bar import st_navbar

from app.fragments import ( resumen_prestamo, 
                            reingreso_empleado, team, chat_dialog, 
                           birthdays, promotions, vacantes, notifications, savings, ausencias as ausentismo)

#DATA

from sample import colaboradores

db = Core()

functions_to_run = [
    db.get_ausencias,
    db.get_loans,
    db.get_payments,
    db.get_alerts,
    db.get_requests,
    db.get_team_requests,
    db.get_birthdays,
    db.get_feriados,
    db.get_promociones,
    db.get_requisiciones,
]



if "mask_balances" not in st.session_state:
    st.session_state.mask_balances = True  # Por defecto, los balances  están enmascarados
    
    
st.fragment(run_every=30)
def verificar_alertas():
    """Verifica nuevas alertas y muestra un toast si hay nuevas."""
    # Simular un endpoint para obtener alertas
    if "alerts" not in st.session_state:
        st.session_state.alerts = []
    

    try:
        # Obtener nuevas alertas
        nuevas_alertas = db.get_alerts(save_in_session=False)

        # Filtrar alertas nuevas
        alertas_existentes_ids = {alerta["id"] for alerta in st.session_state.alerts}
        alertas_nuevas = [alerta for alerta in nuevas_alertas if alerta["id"] not in alertas_existentes_ids]

        # Si hay alertas nuevas, mostrarlas como toast y agregarlas al estado
        for alerta in alertas_nuevas:
            st.toast(f"📢 Nueva alerta: {alerta['message']}")
            st.session_state.alerts = nuevas_alertas
          
        

        
    except Exception as e:
        st.error(f"Error al obtener alertas: {e}")
  

def home():
    """Página principal para la autogestión del empleado"""


    st.markdown("""
    <style>
        section.stMain .block-container {
            padding-top: 0rem;
        }
    </style>

    """, unsafe_allow_html=True)
    # Verificar si el empleado está en sesión
    if not 'employee' in st.session_state:
        if db.get_employee():
                e = st.session_state.employee
                # Verificar si el empleado está en estado VACACIONES (4)
                if e.get("estadoEmpleado") == 4:
                    # Obtener ausencias del empleado
                    ausencias = db.get_ausencias()
                    ausencias = sorted(ausencias, key=lambda x: x.get("id", 0), reverse=True)
                    hoy = datetime.datetime.today().date()

                    # Filtrar la última ausencia de tipo vacaciones
                    ultima_vacacion = next(
                        (ausencia for ausencia in ausencias if ausencia["tipo_Ausencia"] == 1),
                        None
                    )

                    if ultima_vacacion:
                        fecha_inicio = datetime.datetime.strptime(ultima_vacacion["fecha_Inicio"],"%Y-%m-%dT%H:%M:%S").date()
                        fecha_fin = datetime.datetime.strptime(ultima_vacacion["fecha_Fin"], "%Y-%m-%dT%H:%M:%S").date()

                        # Validar si la fecha actual está fuera del rango de vacaciones
                        if hoy > fecha_fin:
                            reingreso_empleado()
                            return
                        elif hoy < fecha_inicio:
                            # Cambiar el estado del empleado a ACTIVO (1)
                            e["estadoEmpleado"] = 1
                            e["nombre_EstadoEmpleado"] = "ACTIVO"
                            st.session_state.employee = e
                        
                        elif fecha_inicio <= hoy <= fecha_fin:
                            # Si la fecha actual está dentro del rango, no hacer nada
                            st.info(f"✈️ Estás disfrutando de tus vacaciones. Tu periodo de descanso finaliza el **{fecha_fin.strftime('%A %d de %B de %Y').capitalize()}**. ¡Aprovecha tu tiempo libre!")
                        else:
                            # Si la fecha actual es posterior al fin de las vacaciones, mostrar el reingreso
                            reingreso_empleado()
                            return

    # Si el empleado está en sesión
    if 'employee' in st.session_state:
        # Cargar datos si no están cargados
        if 'data_loaded' not in st.session_state:
            start_time = t.time()  # Inicia el temporizador
            with st.spinner("Cargando datos, por favor espera..."):
                for func in functions_to_run:
                    func_start_time = t.time()  # Tiempo de inicio de la función
                    func()  # Ejecutar la función
                    func_end_time = t.time()  # Tiempo de finalización de la función
                    # Puedes habilitar este log para depuración:
                    # st.write(f"Función `{func.__name__}` cargada en {func_end_time - func_start_time:.2f} segundos.")
            end_time = t.time()  # Finaliza el temporizador
            # Puedes habilitar este log para depuración:
            # st.success(f"Datos cargados en {end_time - start_time:.2f} segundos.")
            st.session_state.data_loaded = True

        # Asignar colaboradores al estado de sesión
        st.session_state.employee['colaboradores'] = colaboradores
        e = st.session_state.employee


        # Configurar las pestañas según si hay colaboradores o no
        if 'colaboradores' in e:
            autoservicio_tab, colaboradores_tab, notificaciones_tab = st.tabs(
                ["🏠 Inicio", "👥 Colaboradores", "🔔 Notificaciones"]
            )
        else:
            autoservicio_tab, notificaciones_tab = st.tabs(["🏠 Inicio", "🔔 Notificaciones"])

        # Inicializar mensajes de chat en el estado de sesión
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": "Hello! How can I help you today?"}
            ]

        # Pestaña de autoservicio
        with autoservicio_tab:
            # Mostrar avatar del empleado
            if 'user_image' in st.session_state:
                profile_image = base64_to_image(st.session_state.user_image)

            nombre = e['primerNombreEmpleado']
            apellido = e['primerApellidoEmpleado']
            imagen = f"https://ui-avatars.com/api/?background=random&name={nombre}+{apellido}=100%bold=true&background=61a1af&color=fdfdfd"

            avatar(
                [
                    {
                        "url": imagen,
                        "size": 100,
                        "title": f"{e['nombreCompletoEmpleado']}",
                        "caption": f"{e['nombre_Puesto']} - {e['nombre_EstadoEmpleado']}",
                        "key": "avatar1",
                    }
                ]
            )

            # Mostrar mensaje de cumpleaños si aplica
            fecha_nacimiento = e.get("fechaNacimiento", "1988-04-07T00:00:00")
            try:
                fecha_nacimiento = datetime.datetime.strptime(fecha_nacimiento, "%Y-%m-%dT%H:%M:%S").date()
                hoy = datetime.datetime.today().date()
                if fecha_nacimiento.day == hoy.day and fecha_nacimiento.month == hoy.month:
                    st.warning("🎉 ¡Feliz cumpleaños! 🎂 Que tengas un día maravilloso lleno de éxitos y alegrías.")
                    if not 'balloons_show' in st.session_state:
                        st.session_state.balloons_show = True
                        st.balloons()
                        time.sleep(0.5)
                        st.balloons()
            except ValueError:
                print("❌ Error al procesar la fecha de nacimiento. Formato inválido.")

            # Opciones rápidas
            st.markdown("### ¿Qué deseas hacer?")


            # Opciones disponibles
            options = ["✈️ Solicitar Permiso", "🏥 Permiso por Enfermedad", "📄 Solicitar Carta", "💳 Registrar Gastos", "🔐 Ocultar/Mostrar Balances"]

            # Inicializar el estado si no existe
            if "pills_selection_home" not in st.session_state:
                st.session_state["pills_selection_home"] = None

            # Función para manejar el cambio de selección
            def handle_pills_home_change():
                selection = st.session_state["pills_selection_home"]
                if selection == "✈️ Solicitar Permiso":
                    ausentismo.solicitar_permiso()                    
                elif selection == "🏥 Permiso por Enfermedad":
                    ausentismo.solicitar_licencia_medica()
                elif selection == "📄 Solicitar Carta":
                   show_alert(
                        "¡Pronto disponible!",
                        "La opción de solicitar cartas estará disponible en futuras versiones. ¡Mantente atento!"
                    )
                   
                elif selection == "🙎🏽‍♂️ Perfil":
                    app.switch_page('profile')
                    
                elif selection == "💳 Registrar Gastos":
                    show_alert(
                        "¡Pronto disponible!",
                        "La opción de registro de gastos estará disponible en futuras versiones. ¡Mantente atento!"
                    )
                        
                elif selection == "🔐 Ocultar/Mostrar Balances":
                    st.session_state.mask_balances = not st.session_state.mask_balances
                
                st.session_state["pills_selection_home"] = None

                # Reiniciar la selección de las pills para que actúen como botones
               

            # Renderizar las pills con on_change
            st.pills(
                "",
                options,
                key="pills_selection_home",
                on_change=handle_pills_home_change,
                label_visibility="collapsed",
            )
           
           
            # Barra de progreso
            st.progress(100)

            # Sección de volante de pago y métricas
            cvolante, resumen_column = st.columns([2.5, 1])
            with cvolante:
                mostrar_volantes(last=True)
                vacantes.vacantes()
                birthdays.birthdays()
                promotions.promos()

            with resumen_column:
                ausentismo.resumen_vacaciones()
                resumen_prestamo()
                savings.resumen_ahorros()
                ausentismo.resumen_permisos()

        # Pestaña de notificaciones
        with notificaciones_tab:
            notifications.alerts()

        # Pestaña de colaboradores (si aplica)
        if 'colaboradores' in e:
            with colaboradores_tab:
                team()

        # Verificar alertas
        verificar_alertas()

        # Botón flotante para abrir el chat
        if floating_button("🙎🏽‍♂️ Perfil"):
            #chat_dialog()
            app.switch_page('profile')

