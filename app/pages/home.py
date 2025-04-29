import streamlit as st
from streamlit_extras.floating_button import floating_button
from app.core import *
from app.pages import empleado
from app.pages.profile import user_profile
from app.util import  show_alert
import datetime, time
import time as t
import app


from app.fragments import ( resumen_prestamo, 
                            reingreso_empleado, social, team, notifications, post,
                           savings, ausencias as ausentismo, error_fragment, accesos_directos)





if "mask_balances" not in st.session_state:
    st.session_state.mask_balances = True  # Por defecto, los balances  están enmascarados
    


def load_data():
    """
    Carga los datos necesarios para la aplicación, ejecutando solo las funciones necesarias.
    """
    
    if 'data_loaded' not in st.session_state or not st.session_state.data_loaded:
        start_time = t.time()  # Inicia el temporizador
        ramdom_icons = ["👩🏽‍💻", "✈️", "🏦", "💰", "🔔", "🚀", "🎉", "🥳", "🎓", "⏲️", "⌛", "🕰️", "🕑", "🕒", "🕓", "🕔"]

        # Crear un marcador de posición para el contenido temporal
        placeholder = st.empty()
        icon_placeholder = st.empty()  # Marcador de posición para el icono
        func_placeholder = st.empty()

        # Diccionario que mapea las funciones a claves en st.session_state
        functions_to_run = {
            "ausencias": get_ausencias,
            "loans": get_loans,
            "payments": get_payments,
            "alerts": get_alerts,
            "requests": get_requests,
            "team_requests": get_team_requests,
            "birthdays": get_birthdays,
            "feriados": get_feriados,
            "promociones": get_promociones,
            "requisiciones": get_requisiciones,
        }

        with placeholder.container():
            # Crear un contenedor para centrar el contenido
            _, col2, _ = st.columns([1, 1, 1])  # Crear columnas para centrar horizontalmente
            with col2:
                # Crear espacio dinámico para centrar verticalmente
                for _ in range(6):  # Ajusta el rango para controlar el espacio vertical
                    st.markdown("&nbsp;")  # Espacio vacío

                # Ejecutar solo las funciones necesarias
                for i, (key, func) in enumerate(functions_to_run.items()):
                    if key not in st.session_state:  # Solo ejecutar si no está en session_state
                        ramdom_icon = ramdom_icons[i % len(ramdom_icons)]
                        print(f"Cargando datos... {func.__name__} {ramdom_icon}")
                        icon_placeholder.markdown(
                            f"""
                            <h1 style="font-size: 56px; font-weight: bold; color: #61a1af; text-align: center;">
                                    {ramdom_icon}
                            </h1>
                            <p style="font-size: 18px; color: #61a1af; font-weight: bold; text-align: center;">
                                Estamos preparando todo para ti... 🚀
                            </p>
                            <p style="font-size: 16px; color: #61a1af; text-align: center;">
                                Esto puede tomar unos segundos. Por favor, no cierres esta ventana. 
                            </p>
                            <p style="font-size: 12px; text-align: center;">
                               {func.__name__} 
                            </p>
                            """,
                            unsafe_allow_html=True
                        )

                        func_start_time = t.time()  # Tiempo de inicio de la función
                        try:
                            st.session_state[key] = func()  # Ejecutar la función y guardar el resultado
                        except Exception as e:
                            st.error(f"Error al cargar {key}: {e}")
                        func_end_time = t.time()  # Tiempo de finalización de la función

                        # func_placeholder.markdown(
                        #     f"""
                        #     <p style="font-size: 12px; text-align: center;">
                        #         Función `{func.__name__}` cargada en {func_end_time - func_start_time:.2f} segundos.
                        #     </p>
                        #     """,
                        #     unsafe_allow_html=True
                        # )

        # Limpiar el marcador de posición después de cargar los datos
        icon_placeholder.empty()
        func_placeholder.empty()
        placeholder.empty()

        end_time = t.time()  # Finaliza el temporizador
        st.session_state.data_loaded = True
        
        
        
def render_styles():
    """Aplica estilos personalizados a la página."""
    
    custom_styles = """ 
        <style>
            .block-container {
                padding-top: 0rem;
            }
        </style>
    """


    st.markdown(custom_styles, unsafe_allow_html=True)


def verificar_estado_empleado(cookies):
    """Verifica el estado del empleado y maneja las vacaciones."""
    
    if 'employee' in st.session_state:
        e = st.session_state.employee

        if e['estadoEmpleado'] == 4:
           
            if 'ausencias' in st.session_state:
                ausencias = st.session_state.ausencias
               
                ausencias = sorted(ausencias, key=lambda x: x.get("id", 0), reverse=True)
                hoy = datetime.datetime.today().date()

                ultima_vacacion = next(
                    (ausencia for ausencia in ausencias if ausencia["tipo_Ausencia"] == 1 and ausencia['codigo_Estado'] == 3) ,
                    None
                )
                if ultima_vacacion:
                    fecha_inicio = datetime.datetime.strptime(ultima_vacacion["fecha_Inicio"], "%Y-%m-%dT%H:%M:%S").date()
                    fecha_fin = datetime.datetime.strptime(ultima_vacacion["fecha_Fin"], "%Y-%m-%dT%H:%M:%S").date()
                    
                    if hoy > fecha_fin:
                        reingreso_empleado(cookies)
                        return
                    elif hoy < fecha_inicio:
                        e["estadoEmpleado"] = 1
                        e["nombre_EstadoEmpleado"] = "ACTIVO"
                        st.session_state.employee = e
                    elif fecha_inicio <= hoy <= fecha_fin:
                        st.info(f"✈️ Estás disfrutando de tus vacaciones. Tu periodo de descanso finaliza el **{fecha_fin.strftime('%A %d de %B de %Y').capitalize()}**. ¡Aprovecha tu tiempo libre!")
                    else:
                        reingreso_empleado(cookies)
                        return



def render_autoservicio_tab(autoservicio_tab):
    """Renderiza el contenido de la pestaña de autoservicio."""
    

        
    with autoservicio_tab:
        if 'employee' in st.session_state:
            e = st.session_state.employee

            nombre = e['primerNombreEmpleado']
            apellido = e['primerApellidoEmpleado']
            imagen = f"https://ui-avatars.com/api/?background=random&name={nombre}+{apellido}=100%bold=true&background=61a1af&color=fdfdfd"

            _, profile, cvolante, resumen_column, _ = st.columns([0.1, 1, 2.5, 1.6, 0.1 ])
            
            with profile:
                with st.container(border=True):
                    st.markdown(f"""
                        <div style="display: flex; flex-direction: row; align-items: center; margin-bottom: 5px; gap: 12px;">
                            <div style="display: flex; flex-direction: column; align-items: flex-start;">
                                <img src="{imagen}" style="width: 70px; height: 70px; border-radius: 50%; object-fit: cover;">
                                <span style="font-weight: bold; font-size: 16px; color: #333;">{nombre} {apellido}</span>
                                <span style="font-size: 12px; color: #666;">{e['nombre_Puesto']}</span>
                                <span style="font-size: 12px; color: #666;">{e['nombre_Compania']}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    

                    if st.button(":blue[Mi Perfil]", type="tertiary", icon=":material/person:"):
                        #empleado.employee_detail(e['idEmpleado'], from_screen="home")
                        params = {"employeeId":e['idEmpleado'], "from_screen":"home"}
                        app.switch_page(page_name="empleado", params=params)
                        # employee_id = e['idEmpleado']
                        # st.markdown(
                        #     f'<a href="/?page=empleado&employeeId={employee_id}&from_screen=home" target="_blank" style="text-decoration: none;">Abrir perfil en nueva pestaña</a>',
                        #     unsafe_allow_html=True
                        # )

                        
                
                
                #if 'show_loan' in st.session_state and st.session_state.show_loan:
                accesos_directos()
                ausentismo.resumen_vacaciones()
                resumen_prestamo()
                savings.resumen_ahorros()
                
  

            with cvolante:
                # if 'show_payroll' in st.session_state and st.session_state.show_payroll:
                #     mostrar_volantes(last=True)
                

                
                # Opciones rápidas
                with st.container(border=False):
                    render_opciones_rapidas()

                    # Barra de progreso
                    st.progress(100)
                    
                # Mostrar mensaje de cumpleaños si aplica
                mostrar_mensaje_cumpleaños(e)
            
                social.feed()


            with resumen_column:
                
                
                notifications.render_notificaciones()
                
                solicitudes = []   
                solicitudes = get_vacaciones_by_id(e['idEmpleado'], vacaciones=False)  
                
                empleado.render_actividades_recientes(solicitudes)
                
                


def mostrar_mensaje_cumpleaños(e):
    """Muestra un mensaje de cumpleaños si aplica."""
    fecha_nacimiento = e.get("fechaNacimiento", "1988-04-07T00:00:00")
    #fecha_nacimiento = "1988-04-24T00:00:00"

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



@st.fragment()
def render_opciones_rapidas():
    """Renderiza las opciones rápidas disponibles."""
    
    st.markdown("##### ¿Qué deseas hacer?")
    options = [":blue[:material/account_circle_off:] Solicitar Permiso", 
               ":red[:material/emergency:] Permiso por Enfermedad", 
               ":blue[:material/mail:] Solicitar Carta", 
               ":green[:material/shopping_cart:] Registrar Gastos", 
               ":red[:material/image:] :blue[Publicar contenido]"
            ]

    if "pills_selection_home" not in st.session_state:
        st.session_state["pills_selection_home"] = None

    # Diccionario que mapea las opciones a sus respectivas acciones
    options_actions = {
        ":blue[:material/account_circle_off:] Solicitar Permiso": ausentismo.solicitar_permiso,
        ":red[:material/emergency:] Permiso por Enfermedad": ausentismo.solicitar_licencia_medica,
        ":blue[:material/mail:] Solicitar Carta": lambda: show_alert(
            "¡Pronto disponible!",
            "La opción de solicitar cartas estará disponible en futuras versiones. ¡Mantente atento!"
        ),
        ":green[:material/shopping_cart:] Registrar Gastos": lambda: show_alert(
            "¡Pronto disponible!",
            "La opción de registro de gastos estará disponible en futuras versiones. ¡Mantente atento!"
        ),
        ":red[:material/image:] :blue[Publicar contenido]": post.create_media_post,
    }

    def handle_pills_home_change():
        selection = st.session_state["pills_selection_home"]    
        
        
        if selection in options_actions:
            options_actions[selection]()  # Ejecutar la acción correspondiente
            
        st.session_state["pills_selection_home"] = None

    st.pills(
        "Opciones rápidas",
        options,
        key="pills_selection_home",
        on_change=handle_pills_home_change,
        label_visibility="collapsed", 
    )
    
    
    

def render_notificaciones_tab(notificaciones_tab):
    """Renderiza el contenido de la pestaña de notificaciones."""
    with notificaciones_tab:
        notifications.alerts()
        
        
def render_experimental_tab(experimental_tab):
    """Renderiza el contenido de la pestaña de experimental_tab."""
    with experimental_tab:
        social.feed()


def render_colaboradores_tab(colaboradores_tab):
    """Renderiza el contenido de la pestaña de colaboradores."""
    with colaboradores_tab:
        team.colaboradores()


def home(cookies):
    """Página principal para la autogestión del empleado."""
    
    render_styles()
    
    load_data()
    
    if not 'employee' in st.session_state or not st.session_state.employee:
        error_fragment(cookies=cookies)
        st.stop()
        return
    
    if 'employee' in st.session_state:

                
        verificar_estado_empleado(cookies) # Verifica el estado del empleado y maneja las vacaciones

        if 'reingreso_pendiente' in st.session_state:
            if st.session_state.reingreso_pendiente:
                st.rerun()

        if "colaboradores" not in st.session_state:
            st.session_state.colaboradores = st.session_state.employee['colaboradores']
        

            
        options = [":red[:material/home_app_logo:] Inicio", ":material/groups: Colaboradores"] if st.session_state.colaboradores else [":material/home_app_logo: Inicio"]
        tabs = st.tabs(options)

        # Renderizar contenido de las pestañas
        autoservicio_tab = tabs[0]
        render_autoservicio_tab(autoservicio_tab)
        
        if len(tabs) > 1:
            colaboradores_tab = tabs[1]
            render_colaboradores_tab(colaboradores_tab)
            
        
        # Renderizar el botón flotante para abrir el perfil

        # Botón flotante para abrir el perfil
        if floating_button("", icon=":material/settings:"):
            user_profile(cookies)
        
        # if floating_button("", icon=":material/autorenew:"):
        #    st.rerun()