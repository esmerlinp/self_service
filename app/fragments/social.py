import streamlit as st
import datetime
from app.core import get_comentarios, set_comentario, delete_comentario, get_promociones, get_post, get_birthdays
from bs4 import BeautifulSoup
from streamlit_avatar import avatar
import random
#funcion que muestra feed similar a instagram con las promociones y cumpleanos de los empleado

@st.fragment(run_every=60*5)
def feed():
    """Muestra un feed de promociones y cumpleaños de los empleados."""

    st.markdown("""
        <style>
        .custom-container {
            overflow: hidden !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    with st.container(border=False, height=1500):
        st.markdown(
            """
            <div class="custom-container">
            """,
            unsafe_allow_html=True
        )
        # Claves estándar para ambos tipos de datos
        standard_keys = {
            "type": None,
            "subtype": None,
            "codigo": None,
            "nombre": None,
            "date": None,
            "departamento": None,
            "puesto": None,
            "puestoAnterior": None,
            "puestoNuevo": None,
            "descripcionNuevoPuesto": None,
            "message": None,
            "imagenEmpleado": None,
            "date": None,
            "requisitosPuesto":None,
            "responsabilidadesPuesto": None,
            "urlPost": None,
            "owner": None
          
        }
        

        
        feed_data = []
        
        promociones = get_promociones()
        # requisiciones = []
        
        # if 'requisiciones' in st.session_state:
        #     requisiciones = st.session_state.requisiciones
            
        
        # for req in requisiciones:
        #     fecha = datetime.datetime.strptime(req.get("fecha_Creacion"), "%Y-%m-%dT%H:%M:%S.%f")
        #     feed_data.append({
        #         **standard_keys,  # Incluir todas las claves estándar
        #         "type": "vacante",
        #         "codigo": req.get("id"),
        #         "nombre": req.get("nombre_Requisicion"),
        #         "puesto": req.get("nombre_Puesto"),
        #         "departamento": req.get("nombreDepartamento"),
        #         "requisitosPuesto": req.get("requisitosPuesto", "").replace("\n", "") if req.get("requisitosPuesto") else "",
        #         "responsabilidadesPuesto": req.get("responsabilidadesPuesto", "").replace("\n", "") if req.get("responsabilidadesPuesto") else "",
        #         "date": fecha,
        #         "message": req.get('descripcion', ""),
        #     })


        posts = get_post()

        
        for post in posts:
            fecha = datetime.datetime.strptime(post.get("fecha_Creacion"), "%Y-%m-%dT%H:%M:%S.%f")
            nombres = f"{post['primerNombre']} {post['primerApellido']}"
            urlpost = ""
            extension = ""
            # Manejar el caso en el que haya archivos en "files"
            if post['files']:
                if len(post['files']) > 0:
                    urlpost = post['files'][0].get("url", "")
                    extension = post['files'][0].get("extension", "")

                
                

            feed_data.append({
                **standard_keys,  # Incluir todas las claves estándar
                "type": "post",
                "subtype":extension,
                "codigo": post.get("id"),
                "nombre": nombres,
                "date": fecha,
                "message": post.get('contenido', ""),
                "imagenEmpleado": post.get("urlImage", None),
                "urlPost": urlpost, 
                "owner": post.get("id_Registro")
            })
        
        # Obtener los datos de cumpleaños y promociones

        # if 'birthdays' in st.session_state:
        #     cumpleanos = st.session_state.birthdays
        
        cumpleanos = get_birthdays()    
        # Procesar cumpleaños
        for cumple in cumpleanos:
            fecha = datetime.datetime.strptime(cumple.get("fechaCumpleanios"), "%Y-%m-%dT%H:%M:%S")
            
            hoy = datetime.datetime.today().date()
            fecha = fecha.replace(year=hoy.year)
            if fecha.date() <= hoy:
                feed_data.append({
                    **standard_keys,  # Incluir todas las claves estándar
                    "type": "birthday",
                    "subtype": "birthday",
                    "codigo": cumple.get("codigo"),
                    "nombre": cumple.get("nombre"),
                    "puesto": cumple.get("nombrePuesto"),
                    "departamento": cumple.get("nombreDepartamento"),
                    "date": fecha,
                    "message": f"¡Feliz cumpleaños, {cumple.get('nombre')}! 🎉",
                    "imagenEmpleado": cumple.get("imagenEmpleado"),
                })


        # Procesar promociones
        if  promociones:
            for promo in promociones:
                fecha = datetime.datetime.strptime(promo.get("fechaPromocion"), '%Y-%m-%dT%H:%M:%S')
                feed_data.append({
                    **standard_keys,  # Incluir todas las claves estándar
                    "type": "promotion",
                    "subtype": promo.get("accion"),
                    "codigo": promo.get("codigo"),
                    "nombre": promo.get("nombreEmpleado"),
                    "puesto": promo.get("puestoNuevo"),
                    "date": fecha,
                    "puestoAnterior": promo.get("puestoAnterior"),
                    "descripcionNuevoPuesto": promo.get("descripcionPuesto"),
                    "message": f"¡Felicidades, {promo.get('nombreEmpleado')}! Ha sido promovido a {promo.get('puestoNuevo')}.",
                    "imagenEmpleado": promo.get("imagenEmpleado"),
                })
                
        # Eliminar duplicados de feed_data
        unique_feed_data = []
        seen = set()

        for item in feed_data:
            # Crear una clave única basada en los campos relevantes (por ejemplo, "codigo" y "type")
            unique_key = (item["codigo"], item["type"])
            if unique_key not in seen:
                seen.add(unique_key)
                unique_feed_data.append(item)

        feed_data = unique_feed_data
                
        # Ordenar feed_data por el campo "date" (más recientes primero)
        feed_data.sort(key=lambda x: x["date"], reverse=True)

        # Mostrar cada elemento del feed
        for feed in feed_data:
            feed_view(feed)
            
        st.markdown(
            """
            </div>
            """,
            unsafe_allow_html=True
        )
            
        
        
def feed_view(feed):

    if feed:
        imagen = ""
        if  feed['type'] != 'vacante':
            if feed['imagenEmpleado']:
                imagen = feed['imagenEmpleado']
            else:    
                nombres = feed["nombre"].split(" ")
                if len(nombres) >= 3:
                    imagen = f"https://ui-avatars.com/api/?name={nombres[0]}+{nombres[2]}=100"
                else:
                    imagen = f"https://ui-avatars.com/api/?background=random&name={nombres[0]}+{nombres[1]}=100%bold=true"


        if feed['type'] == "promotion":
            background_url = "https://img.freepik.com/vector-premium/mujer-alegre-celebrando-saludo-colorido-ilustracion-dos-tonos_647728-38.jpg?w=740"
            
        elif feed['type'] == "birthday":
            background_url = "https://png.pngtree.com/background/20210711/original/pngtree-birthday-confetti-balloon-vector-background-picture-image_1150107.jpg"    
            
        else:
            background_url = "" 
        
        with st.container(border=True):

            if  feed['type'] == "birthday":
                fecha_evento = feed["date"]

                st.markdown(
                    f"""
                    <div style="border: 0px solid #ddd; border-radius: 12px; padding: 10px; margin-bottom: 1px; 
                                margin-top: -15px;
                                background-image: url('{background_url}'); 
                                background-size: cover; background-position: center; text-align: center;">
                        <div style="margin-bottom: 1px;">
                            <img src="{imagen}" alt="Foto de {feed['nombre']}" style="width: 100px; height: 100px; border-radius: 50%; object-fit: cover;">
                        </div>
                        <p style="margin: 0; font-size: 20px; font-weight: bold; color: #333;">🎉 ¡Felíz Cumpleaños 🎉</p>
                        <p style="margin: 0; font-size: 32px; font-weight: bold; color: #333;">{feed['nombre']}</p>
                        <p style="margin: 0; font-size: 14px; color: #555;"> {feed['puesto']}</p>
                        <p style="margin: 0; font-size: 16px; font-weight: bold; color: #555;">{fecha_evento.strftime('%A %d de %B').capitalize()}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                

                    
            elif feed['type'] == 'post':
                nombre = feed.get('nombre', '')
                imagen_alt = f"https://ui-avatars.com/api/?background=random&name={nombre}=100%bold=true&background=61a1af&color=fdfdfd"
                
                imagen = feed.get('imagenEmpleado', imagen_alt)
            
                if not imagen:
                    imagen = imagen_alt
                    
                urlPost = feed.get('urlPost', '')
                subtype = feed.get('subtype', '')
                message = BeautifulSoup(feed.get('message', None), "html.parser").get_text()
   
                if subtype and subtype.lower() in ['.jpeg', '.jpg', '.png']:
                    if message:
                        st.markdown(f"""
                            <div style="background-color:#ffffff; border: 0px solid #ddd; border-radius:10px; padding:10px; font-family: Arial, sans-serif;">
                                <div style="display: flex; align-items: center; margin-bottom: 15px;">
                                    <img src="{imagen}" alt="Foto de {feed['nombre']}" 
                                        style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover; margin-right: 15px;">
                                    <div>
                                        <span style="font-weight: bold; font-size: 16px; color: #333;">{feed['nombre']}</span><br>
                                        <span style="font-size: 12px; color: #999;">{feed['date'].strftime('%d %b %Y, %H:%M')}</span>
                                    </div>
                                </div>
                                <div style="margin-bottom: 15px; font-size: 14px; color: #333; line-height: 1.6;">
                                    {message}
                                </div>
                                <div style="margin-bottom: 15px;">
                                    <img src="{urlPost}" alt="Contenido multimedia" style="width: 100%; border-radius: 10px; object-fit: cover;">
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                            <div style="background-color:#ffffff; border: 0px solid #ddd; border-radius:10px; padding:10px; font-family: Arial, sans-serif;">
                                <div style="display: flex; align-items: center; margin-bottom: 15px;">
                                    <img src="{imagen}" alt="Foto de {feed['nombre']}" 
                                        style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover; margin-right: 15px;">
                                    <div>
                                        <span style="font-weight: bold; font-size: 16px; color: #333;">{feed['nombre']}</span><br>
                                        <span style="font-size: 12px; color: #999;">{feed['date'].strftime('%d %b %Y, %H:%M')}</span>
                                    </div>
                                </div>
                                <div style="margin-bottom: 15px;">
                                    <img src="{urlPost}" alt="Contenido multimedia" style="width: 100%; border-radius: 10px; object-fit: cover;">
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                    
                elif subtype and subtype.lower() in['.mov', '.mp4', '.avi']:
                    if message:
                        st.markdown(f"""
                            <div style="background-color:#ffffff; border: 0px solid #ddd; border-radius:10px; padding:10px; font-family: Arial, sans-serif;">
                                <!-- Encabezado del post -->
                                <div style="display: flex; align-items: center; margin-bottom: 15px;">
                                    <img src="{imagen}" alt="Foto de {feed['nombre']}" 
                                        style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover; margin-right: 15px;">
                                    <div>
                                        <span style="font-weight: bold; font-size: 16px; color: #333;">{feed['nombre']}</span><br>
                                        <span style="font-size: 12px; color: #999;">{feed['date'].strftime('%d %b %Y, %H:%M')}</span>
                                    </div>
                                </div>
                                <!-- Contenido del post -->
                                <div style="margin-bottom: 15px; font-size: 14px; color: #333; line-height: 1.6;">
                                    {message}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                            <div style="background-color:#ffffff; border: 0px solid #ddd; border-radius:10px; padding:10px; font-family: Arial, sans-serif;">
                                <!-- Encabezado del post -->
                                <div style="display: flex; align-items: center; margin-bottom: 15px;">
                                    <img src="{imagen}" alt="Foto de {feed['nombre']}" 
                                        style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover; margin-right: 15px;">
                                    <div>
                                        <span style="font-weight: bold; font-size: 16px; color: #333;">{feed['nombre']}</span><br>
                                        <span style="font-size: 12px; color: #999;">{feed['date'].strftime('%d %b %Y, %H:%M')}</span>
                                    </div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    st.video(urlPost)
                else:
                    
                    
                    st.markdown(f"""
                        <div style="background-color:#ffffff; border: 0px solid #ddd; border-radius:10px; padding:10px; font-family: Arial, sans-serif; ">
                            <!-- Encabezado del post -->
                            <div style="display: flex; align-items: center; margin-bottom: 15px;">
                                <img src="{imagen}" alt="Foto de {feed['nombre']}" 
                                    style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover; margin-right: 15px;">
                                <div>
                                    <span style="font-weight: bold; font-size: 16px; color: #333;">{feed['nombre']}</span><br>
                                    <span style="font-size: 12px; color: #999;">{feed['date'].strftime('%d %b %Y, %H:%M')}</span>
                                </div>
                            </div>
                            <!-- Contenido del post -->
                            <div style="margin-bottom: 15px; font-size: 14px; color: #333; line-height: 1.6;">
                                {message}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    
                
            else:
                promocion_text = f"Promovido a:" if feed['subtype'] == "Cambio de Puesto" else "Nuevo Ingreso"
                promocion_text_header = f"🎉 ¡Felicidades, {feed['nombre']}! 🎉" if feed['subtype'] == "Cambio de Puesto" else f"🎉 Bienvenido, {feed['nombre']}! 🎉"
                st.markdown(
                    f"""
                    <div style="border: 0px solid #ddd; border-radius: 12px; padding: 20px; margin-bottom: 10px; 
                                background-color: #e3f2fd;  /* Fondo azul claro */
                                background-image: url('{background_url}'); 
                                background-size: cover; background-position: center; text-align: center;">
                        <div style="margin-bottom: 10px;">
                            <img src="{imagen}" alt="Foto de {feed['nombre']}" 
                                style="width: 120px; height: 120px; border-radius: 50%; object-fit: cover; background-color: #fff; padding: 5px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);">
                        </div>
                        <p style="margin: 0; font-size: 24px; font-weight: bold; color: #333;">{promocion_text_header}</p>
                        <p style="margin: 0; font-size: 16px; font-weight: bold; color: #555;">{promocion_text}</p>
                        <p style="margin: 0; font-size: 18px; font-weight: bold; color: #555;">{feed['puesto']}</p>
                        <p style="margin: 0; font-size: 14px; color: #888;">{feed['descripcionNuevoPuesto']}</p>
                        <p style="margin-top: 10px; font-size: 16px; font-weight: bold; color: #4caf50;">🎊 ¡Te deseamos mucho éxito en esta nueva etapa! 🎊</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )            
            
            # No muestra los comentarios si no hay cumpleaños el dia de hoy
            if feed['type'] != 'vacante':
                
                #if len(comentarios) > 0:
   
                
                # Crear un contenedor independiente para las columnas
                with st.container():
                    # Opciones de selección
                    options = [":blue[:material/comment:]", ":red[:material/favorite:]"]
                    e = st.session_state.employee
                    
                    if feed["type"] == "post":
                        owner = feed.get('owner')
                        employeeId = e.get("idEmpleado")
                        if owner == employeeId:
                            options.append(":red[:material/delete:]")
                        
                            
                            

                    # Inicializar el estado si no existe
                    if f"pills_selection_{feed['type']}_{feed['codigo']}" not in st.session_state:
                        st.session_state[f"pills_selection_{feed['type']}_{feed['codigo']}"] = None

                    # Función para manejar el cambio de selección
                    def handle_pills_change():
                        selection = st.session_state[f"pills_selection_{feed['type']}_{feed['codigo']}"]
                        
                        if selection == ":blue[:material/comment:]":
                             modal_detalle_promocion(feed)  
                            
                        elif selection == ":red[:material/delete:]":
                            if delete_comentario(feed['codigo']):
                                st.rerun(scope="app")
                            
                        elif selection == ":red[:material/favorite:]":
                            
                            if feed["type"] == "birthday":
                                #nuevo_comentario = f"🎉 {e['nombreCompletoEmpleado']} felicitó a {feed['nombre']} por su promoción. ¡Enhorabuena! 🎉"
                                nuevo_comentario = f"🎉 {e['nombreCompletoEmpleado']} felicitó a {feed['nombre']} por su cumpleaños. ¡Muchas felicidades! 🎂"
                            
                            elif feed["type"] == "promotion":
                                #nuevo_comentario = f"🎉 {e['nombreCompletoEmpleado']} felicitó a {feed['nombre']} por su promoción. ¡Enhorabuena! 🎉"
                                nuevo_comentario = f"🎉 {e['nombreCompletoEmpleado']} felicitó a {feed['nombre']} por su promoción. ¡Enhorabuena! 🎊"
                            else:
                                
                                nuevo_comentario = f"A {e['nombreCompletoEmpleado']} le gusta esta publicación 👍"


                            response = set_comentario(id_empleado_festejado=feed['codigo'], contenido=nuevo_comentario, entidad="Promociones")
                            if response:
                                st.balloons()
                                st.rerun()
                            else:
                                st.snow()
                        
                        # Reiniciar la selección de las pills
                        st.session_state[f"pills_selection_{feed['type']}_{feed['codigo']}"] = None

                    # Renderizar las pills con on_change
                    caption =  "🎉 Felicitar al cumpleañero o 💬 agregar un comentario." if feed['type'] == "birthday" else "🎉 Felicitar al promovido o 💬 agregar un comentario." 
                    caption = ""
                    
                    st.pills(
                        caption,
                        options,
                        key=f"pills_selection_{feed['type']}_{feed['codigo']}",
                        on_change=handle_pills_change,
                    )
                
                st.markdown("**Comentarios**") 
                comentarios = get_comentarios(idEmpleado=feed['codigo'], entidad="Promociones")
                comentarios_view_card_promocion(comentarios, feed)






@st.fragment
@st.dialog("Detalles de Promoción", width="large")
def modal_detalle_promocion(promocion):
    """Muestra los detalles de una promoción, incluyendo comentarios y la opción de agregar nuevos."""
    # Mostrar la tarjeta del empleado promocionado
    fecha_promocion = promocion["date"]
    imagen = promocion['imagenEmpleado'] or f"https://ui-avatars.com/api/?name={promocion['nombre']}&background=random"

    st.markdown(
        f"""
        <div style="text-align: center;">
            <img src="{imagen}" alt="Foto de {promocion['nombre']}" style="width: 100px; height: 100px; border-radius: 50%; object-fit: cover;">
            <p><strong style="font-size: 24px;">{promocion['nombre']}</strong></p>
            <p style="font-size: 18px;">🎉 {fecha_promocion.strftime('%A %d de %B').capitalize()}</p>
            <p style="font-size: 16px;">💼 {promocion['message']}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Mostrar comentarios
    st.markdown("### 💬 Comentarios")

    comentarios = get_comentarios(idEmpleado=promocion['codigo'], entidad="Promociones")
    if 'comentarios_promocion' not in st.session_state:
        st.session_state.comentarios_promocion = comentarios
    comentarios_view_detail_promocion(comentarios, promocion)




@st.fragment
def comentarios_view_card_promocion(comentarios, promocion):  
    if comentarios:
        # Mostrar solo el último comentario inicialmente
        if f"show_all_comments_promocion_{promocion['codigo']}" not in st.session_state:
            st.session_state[f"show_all_comments_promocion_{promocion['codigo']}"] = False

        # Determinar si mostrar todos los comentarios o solo el último
        if st.session_state[f"show_all_comments_promocion_{promocion['codigo']}"]:
            comentarios_a_mostrar = comentarios
        else:
            comentarios_a_mostrar = comentarios[-1:]  # Mostrar solo el último comentario

        for comentario in comentarios_a_mostrar:
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
                        "key": f"detalle_comment_{promocion['type']}_{promocion['codigo']}_{comentario['id']}",
                    }
                ]
            )




@st.fragment
def comentarios_view_detail_promocion(comentarios, promocion): 
    nuevo_comentario = st.text_area("Agregar un nuevo comentario", key=f"nuevo_comentario_promocion_{promocion['codigo']}", max_chars=200, placeholder="Escribe tu comentario aquí...")
    if st.button("Publicar", icon=":material/send:", key=f"enviar_comentario_promocion_{promocion['codigo']}"):
        if nuevo_comentario.strip():
            with st.spinner("Publicando comentario..."):
                response = set_comentario(id_empleado_festejado=promocion['codigo'], contenido=nuevo_comentario, entidad="Promociones")
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
                
                # col1, col2 = st.columns([5, 0.4])
                
                # with col1:
                #     avatar(
                #         [
                #             {
                #                 "url": imagen,
                #                 "size": 50,
                #                 "title": nombreCompletoEmpleado,
                #                 "caption": texto_plano,
                #                 "key": f"comment_promocion_{promocion['codigo']}_{comentario['id']}",
                #             }
                #         ]
                #     )
                
                # with col2:
                #     if comentario['id_Usuario'] == st.session_state.user['userId']:
                #         if st.button("🗑️", key=f"eliminar_comentario_promocion_{promocion['codigo']}_{comentario['id']}"):
                #             response = delete_comentario(id_comentario=comentario['id'])
                #             if response:
                #                 # Remover el comentario de la lista
                #                 comentarios.remove(comentario)
                #                 # Actualizar el estado de los comentarios
                #                 st.session_state.comentarios_promocion = comentarios
                #                 st.rerun(scope="app")
                
                
                col7, col8 = st.columns([5, 0.4])
                with col7:
                    st.markdown(f"""
                        <div style="display: flex; flex-direction: row; align-items: center; margin-bottom: 8px; gap: 12px;">
                            <div>
                                <img src="{imagen}" style="width: 30px; height: 30px; border-radius: 50%; object-fit: cover;">
                            </div>
                            <div style="display: flex; flex-direction: column; align-items: flex-start;">
                                <span style="font-size: 14px; color: #333;">{nombreCompletoEmpleado}</span>
                                <span style="font-size: 12px; color: #666;">{texto_plano}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)


                        
                        
                        
                        
                if col8.button(":red[:material/delete:]", key=f"eliminar_comentario_promocion_{promocion['codigo']}_{comentario['id']}", help="Eliminar Comentario"):
                    response = delete_comentario(id_comentario=comentario['id'])
                    if response:
                        # Remover el comentario de la lista
                        comentarios.remove(comentario)
                        # Actualizar el estado de los comentarios
                        st.session_state.comentarios_promocion = comentarios
                        st.rerun(scope="app")

        else:
            st.info("No hay comentarios para esta promoción.")

