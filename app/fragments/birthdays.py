import streamlit as st
import datetime
from streamlit_avatar import avatar
from bs4 import BeautifulSoup
from app.core import Core
import app



db = Core()

@st.fragment
def birthdays(all=False):
    """Muestra los cumpleaños próximos en un diseño atractivo estilo feed de Instagram."""

    if 'birthdays' in st.session_state:
        # Datos de cumpleaños
        eventos = st.session_state.birthdays
        eventos_ordenados = []
        eventos_filtrados = []
    
        # Obtener la fecha actual
        hoy = datetime.datetime.today()


        
        if not all:
            #busco los cumpleaños de hoy
            eventos_filtrados = [
                evento for evento in eventos
                if (hoy.month == datetime.datetime.strptime(evento["fechaCumpleanios"], "%Y-%m-%dT%H:%M:%S").month and
                    datetime.datetime.strptime(evento["fechaCumpleanios"], "%Y-%m-%dT%H:%M:%S").day == hoy.day)
            ]
            
            #sino hay cumpleaños de hoy busco los próximos
            if not eventos_filtrados:
                eventos_filtrados = [
                    evento for evento in eventos
                    if (hoy.month == datetime.datetime.strptime(evento["fechaCumpleanios"], "%Y-%m-%dT%H:%M:%S").month and
                        datetime.datetime.strptime(evento["fechaCumpleanios"], "%Y-%m-%dT%H:%M:%S").day > hoy.day)
                ]
                #indico que son los proximos cumpleaños
                st.session_state.proximos = True
            
        else:
            eventos_filtrados = [
                    evento for evento in st.session_state.birthdays
                    if (hoy.month == datetime.datetime.strptime(evento["fechaCumpleanios"], "%Y-%m-%dT%H:%M:%S").month)
                ]
            
            
        eventos_ordenados = sorted(
                eventos_filtrados,
                key=lambda x: datetime.datetime.strptime(x["fechaCumpleanios"], "%Y-%m-%dT%H:%M:%S"),
                reverse=False
            )
        
        eventos_ordenados = eventos_ordenados if all else eventos_ordenados[:6]
        
        cant_columnas = 2 if len(eventos_ordenados) < 3 else 3  

        
        # Mostrar los cumpleaños
        with st.expander("🎉 Cumpleaños", expanded=True):
            
            col1,_ ,col2 = st.columns([3, 2, 1])
            if  not st.session_state.proximos:
                col1.markdown("#### 🎂 Cumpleaños de Hoy")
            else:
                col1.markdown("#### 🎂 Próximos Cumpleaños")    

            if col2.button(":blue[Ver todos]", type="tertiary", help="Ver todos los cumpleaños", use_container_width=True, disabled=all):
                
                app.switch_page("detail", fragment_detail="birthdays")
                
                
            if eventos_ordenados:
                cols = st.columns(cant_columnas)  # Dividir en 3 columnas para simular un feed
                for idx, evento in enumerate(eventos_ordenados):
                    with cols[idx % cant_columnas]:  # Distribuir los eventos en las columnas
                        fecha_evento = datetime.datetime.strptime(evento["fechaCumpleanios"], "%Y-%m-%dT%H:%M:%S")
                        
                        imagen = evento['imagenEmpleado']
                        if not imagen:
                            nombres = evento["nombre"].split(" ")
                            if len(nombres) >= cant_columnas:
                                imagen = f"https://ui-avatars.com/api/?name={nombres[0]}+{nombres[2]}=100"
                            else:
                                imagen = f"https://ui-avatars.com/api/?background=random&name={nombres[0]}+{nombres[1]}=100%bold=true"  

                        # Validar si la fecha del evento es igual a la fecha actual
                        if fecha_evento.date().day == hoy.date().day:
                            background_url = "https://png.pngtree.com/background/20210711/original/pngtree-birthday-confetti-balloon-vector-background-picture-image_1150107.jpg"
                        else:
                            background_url = ""

                  
                        with st.container(border=True):
                            st.markdown(
                                f"""
                                <div style="border: 0px solid #ddd; border-radius: 12px; padding: 10px; margin-bottom: 1px; 
                                            margin-top: -15px;
                                            background-image: url('{background_url}'); 
                                            background-size: cover; background-position: center; text-align: center;">
                                    <div style="margin-bottom: 1px;">
                                        <img src="{imagen}" alt="Foto de {evento['nombre']}" style="width: 100px; height: 100px; border-radius: 50%; object-fit: cover;">
                                    </div>
                                    <p style="margin: 0; font-size: 20px; font-weight: bold; color: #333;">{evento['nombre']}</p>
                                    <p style="margin: 0; font-size: 16px; color: #555;">{fecha_evento.strftime('%A %d de %B').capitalize()}</p>
                                    <p style="margin: 0; font-size: 14px; color: #555;"> 💼 {evento['nombrePuesto']}</p>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                            

                            # No muestra los comentarios si no hay cumpleaños el dia de hoy
                            if not st.session_state.proximos:
                                st.markdown("**Comentarios**")    
                                comentarios = db.get_comentarios(idEmpleado=evento['idEmpleado'], entidad="Cumpleanios")
                               

                                comentarios_view_card(comentarios, evento)
                                


                                
            else:
                st.info("No hay cumpleaños programados para los próximos días.")
    else:
        with st.expander("🎉 Próximos Cumpleaños", expanded=True):
            st.caption("No hay cumpleaños programados para los próximos días.")
        
      
        
@st.fragment
@st.dialog("Detalles de Cumpleaños", width="large")
def modal_detalle_cumpleanios(evento):
    """Muestra los detalles de cumpleaños de un empleado, incluyendo comentarios y la opción de agregar nuevos."""
    # Mostrar la tarjeta del empleado
    fecha_evento = datetime.datetime.strptime(evento["fechaCumpleanios"], "%Y-%m-%dT%H:%M:%S")
    imagen = evento['imagenEmpleado'] or f"https://ui-avatars.com/api/?name={evento['nombre']}&background=random"

    st.markdown(
        f"""
        <div style="text-align: center;">
            <img src="{imagen}" alt="Foto de {evento['nombre']}" style="width: 150px; height: 150px; border-radius: 50%; object-fit: cover;">
            <p><strong style="font-size: 24px;">{evento['nombre']}</strong></p>
            <p style="font-size: 18px;">🎂 {fecha_evento.strftime('%A %d de %B').capitalize()}</p>
            <p style="font-size: 16px;">💼 {evento['nombrePuesto']}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Mostrar comentarios
    st.markdown("### 💬 Comentarios")

    
    comentarios = db.get_comentarios(idEmpleado=evento['idEmpleado'], entidad="Cumpleanios")
    if 'comentarios' not in st.session_state:
        st.session_state.comentarios = comentarios
    comentarios_view_detail(comentarios, evento)
    



@st.fragment
def comentarios_view_card(comentarios, evento):  
    if comentarios:
        for comentario in comentarios[:1]:
            texto_plano = BeautifulSoup(comentario['contenido'], "html.parser").get_text()
            if comentario['urlImage']:
                imagen = comentario['urlImage']
            else:
                nombre = comentario['primerNombre']
                apellido = comentario['primerApellido']
                imagen = f"https://ui-avatars.com/api/?background=random&name={nombre}+{apellido}=100%bold=true&background=61a1af&color=fdfdfd"
            
            nombreCompletoEmpleado = f"{comentario['primerNombre']} {comentario['primerApellido']}"
            avatar(
                [
                    {
                        "url": imagen,
                        "size": 50,
                        "title": nombreCompletoEmpleado,
                        "caption": texto_plano,
                        "key": f"detalle_comment_{evento['idEmpleado']}_{comentario['id']}",
                    }
                ]
            )

    # Crear un contenedor independiente para las columnas
    with st.container():
        # Opciones de selección
        options = ["💬", "🎉"]

        # Inicializar el estado si no existe
        if f"pills_selection_{evento['idEmpleado']}" not in st.session_state:
            st.session_state[f"pills_selection_{evento['idEmpleado']}"] = None

        # Función para manejar el cambio de selección
        def handle_pills_change():
            selection = st.session_state[f"pills_selection_{evento['idEmpleado']}"]
            if selection == "💬":
                modal_detalle_cumpleanios(evento)
            elif selection == "🎉":
                e = st.session_state.employee
                nuevo_comentario = f"🎉 {e['nombreCompletoEmpleado']} te envía sus mejores deseos en tu cumpleaños. ¡Que tengas un día increíble! 🎂"
                response = db.set_comentario(id_empleado_festejado=evento['idEmpleado'], contenido=nuevo_comentario, entidad="Cumpleanios")
                if response:
                    st.balloons()
                else:
                    st.snow()
            
            # Reiniciar la selección de las pills
            st.session_state[f"pills_selection_{evento['idEmpleado']}"] = None


        # Renderizar las pills con on_change
        st.pills(
            "🎉 Felicitar al cumpleañero o 💬 agregar un comentario.",
            options,
            key=f"pills_selection_{evento['idEmpleado']}",
            on_change=handle_pills_change,
        )
            




@st.fragment
def comentarios_view_detail(comentarios, evento): 
 
    
    nuevo_comentario = st.text_area("Agregar un nuevo comentario", key=f"nuevo_comentario_{evento['idEmpleado']}", max_chars=200, placeholder="Escribe tu comentario aquí...")
    if st.button("Publicar", icon=":material/send:", key=f"enviar_comentario_{evento['idEmpleado']}"):
        if nuevo_comentario.strip():
            response = db.set_comentario(id_empleado_festejado=evento['idEmpleado'], contenido=nuevo_comentario, entidad="Cumpleanios")
            if response:
                st.rerun(scope="app")
        else:
            st.warning("El comentario no puede estar vacío.")
     
    with st.container(height=300, border=False):
        if comentarios:
            for comentario in comentarios:
            
                texto_plano = BeautifulSoup(comentario['contenido'], "html.parser").get_text()

                
                if comentario['urlImage']:
                    imagen = comentario['urlImage']
                else:
                    nombre = comentario['primerNombre']
                    apellido = comentario['primerApellido']
                    imagen = f"https://ui-avatars.com/api/?background=random&name={nombre}+{apellido}=100%bold=true&background=61a1af&color=fdfdfd"
                
                nombreCompletoEmpleado = f"{comentario['primerNombre']} {comentario['primerApellido']}"
                
                col1, col2 = st.columns([5, 0.4])
                
                with col1:
                    avatar(
                        [
                            {
                                "url": imagen,
                                "size": 50,
                                "title": nombreCompletoEmpleado,
                                "caption":texto_plano,
                                "key": f"comment_{evento['idEmpleado']}_{comentario['id']}",
                            }
                        ]
                    )
                
                with col2:
                    if comentario['id_Usuario'] == st.session_state.user['id']:
                        if st.button("🗑️", key=f"eliminar_comentario_{evento['idEmpleado']}_{comentario['id']}"):
                            response = db.delete_comentario(id_comentario=comentario['id'])
                            if response:
                                #remover el comentario de la lista
                                comentarios.remove(comentario)
                                # Actualizar el estado de los comentarios
                                st.session_state.comentarios = comentarios
                                st.rerun(scope="app")
        else:
            st.info("No hay comentarios para este cumpleaños.")


    
