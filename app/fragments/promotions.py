import streamlit as st
import datetime
from streamlit_avatar import avatar
from bs4 import BeautifulSoup
import app
from app.core import Core

db = Core()

@st.fragment
def promos(all=False):
    """Muestra las promociones recientes con opciones de interacción."""
    
    if not 'promotions' in st.session_state or not st.session_state.promotions:
        with st.expander("🎉 Promociones Recientes", expanded=True):
            st.caption("Sin promociones recientes")
            return
    
    data = st.session_state.promotions
    promociones = []
    #validar si hay promociones duplicadas con el mismo codigo en data
    for promo in data:
        if promo['codigo'] not in [p['codigo'] for p in promociones]:
            promociones.append(promo)
        
    
        
    cant_columns = 2

    if all:
        cant_columns = 3
    else:
        promociones = promociones[:2]

    # Mostrar las promociones
    with st.expander("🎉 Promociones Recientes", expanded=True):
        col1, _, col2 = st.columns([3, 2, 1])
        col1.markdown("### 🏆 Celebraciones de Promociones")
        if col2.button(":blue[Ver todas]", type="tertiary", help="Ver todas las promociones", use_container_width=True, disabled=all):
            app.switch_page("detail", fragment_detail="promos")
                
        if promociones:
            cols = st.columns(cant_columns)  # Dividir en columnas para simular un feed
            for idx, promo in enumerate(promociones):
                # Obtener imagen del empleado
                if promo['imagenEmpleado']:
                    imagen = promo['imagenEmpleado']
                else:    
                    nombres = promo["nombreEmpleado"].split(" ")
                    if len(nombres) >= 3:
                        imagen = f"https://ui-avatars.com/api/?name={nombres[0]}+{nombres[2]}=100"
                    else:
                        imagen = f"https://ui-avatars.com/api/?background=random&name={nombres[0]}+{nombres[1]}=100%bold=true"

                with cols[idx % cant_columns]:  # Distribuir las promociones en las columnas
                    # Mostrar tarjeta estilo Instagram
                    if promo['accion'] == "Cambio de Puesto":
                        background_url = ""
                    elif promo['accion'] == "Reconocimiento":
                        background_url = "https://via.placeholder.com/300x150?text=Reconocimiento"
                    else:
                        background_url = "" 
                    
                    with st.container(border=True, height=480):
                        st.markdown(
                            f"""
                            <div style="border: 0px solid #ddd; border-radius: 12px; padding: 10px; margin-bottom: 10px; 
                                        background-image: url('{background_url}'); 
                                        background-size: cover; background-position: center; text-align: center;">
                                <div style="margin-bottom: 10px;">
                                    <img src="{imagen}" alt="Foto de {promo['nombreEmpleado']}" 
                                        style="width: 100px; height: 100px; border-radius: 50%; object-fit: cover; background-color: #fff; padding: 5px;">
                                </div>
                                <p style="margin: 0; font-size: 20px; font-weight: bold; color: #333;">{promo['nombreEmpleado']}</p>
                                <p style="margin: 0; font-size: 14px; color: #555;">📅 {datetime.datetime.strptime(promo['fechaPromocion'], '%Y-%m-%dT%H:%M:%S').strftime('%d/%m/%Y')}</p>
                                <p style="margin: 0; font-size: 16px; font-weight: bold; color: #555;">💼 {promo['puestoAnterior']} → {promo['puestoNuevo']}</p>
                                <p style="margin: 0; font-size: 12px; color: #888;">{promo['descripcionPuesto']}</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        # No muestra los comentarios si no hay cumpleaños el dia de hoy
                        st.markdown("**Comentarios**")    
                        comentarios = db.get_comentarios(idEmpleado=promo['codigo'], entidad="Promociones")
                        comentarios_view_card_promocion(comentarios, promo)
        else:
            st.info("No hay promociones recientes.")
            
            

@st.fragment
@st.dialog("Detalles de Promoción", width="large")
def modal_detalle_promocion(promocion):
    """Muestra los detalles de una promoción, incluyendo comentarios y la opción de agregar nuevos."""
    # Mostrar la tarjeta del empleado promocionado
    fecha_promocion = datetime.datetime.strptime(promocion["fechaPromocion"], "%Y-%m-%dT%H:%M:%S")
    imagen = promocion['imagenEmpleado'] or f"https://ui-avatars.com/api/?name={promocion['nombreEmpleado']}&background=random"

    st.markdown(
        f"""
        <div style="text-align: center;">
            <img src="{imagen}" alt="Foto de {promocion['nombreEmpleado']}" style="width: 150px; height: 150px; border-radius: 50%; object-fit: cover;">
            <p><strong style="font-size: 24px;">{promocion['nombreEmpleado']}</strong></p>
            <p style="font-size: 18px;">🎉 {fecha_promocion.strftime('%A %d de %B').capitalize()}</p>
            <p style="font-size: 16px;">💼 {promocion['puestoAnterior']} → {promocion['puestoNuevo']}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Mostrar comentarios
    st.markdown("### 💬 Comentarios")

    comentarios = db.get_comentarios(idEmpleado=promocion['codigo'], entidad="Promociones")
    if 'comentarios_promocion' not in st.session_state:
        st.session_state.comentarios_promocion = comentarios
    comentarios_view_detail_promocion(comentarios, promocion)


@st.fragment
def comentarios_view_card_promocion(comentarios, promocion):  
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
                        "key": f"detalle_comment_promocion_{promocion['codigo']}_{comentario['id']}",
                    }
                ]
            )

    # Crear un contenedor independiente para las columnas
    with st.container():
        # Opciones de selección
        options = ["💬", "🎉"]

        # Inicializar el estado si no existe
        if f"pills_selection_promocion_{promocion['codigo']}" not in st.session_state:
            st.session_state[f"pills_selection_promocion_{promocion['codigo']}"] = None

        # Función para manejar el cambio de selección
        def handle_pills_change():
            selection = st.session_state[f"pills_selection_promocion_{promocion['codigo']}"]
            if selection == "💬":
                modal_detalle_promocion(promocion)
            elif selection == "🎉":
                e = st.session_state.employee
                nuevo_comentario = f"🎉 {e['nombreCompletoEmpleado']} felicita a {promocion['nombreEmpleado']} por su promoción. ¡Enhorabuena! 🎉"
                response = db.set_comentario(id_empleado_festejado=promocion['codigo'], contenido=nuevo_comentario, entidad="Promociones")
                if response:
                    st.balloons()
                    st.rerun()
                else:
                    st.snow()
            
            # Reiniciar la selección de las pills
            st.session_state[f"pills_selection_promocion_{promocion['codigo']}"] = None

        # Renderizar las pills con on_change
        st.pills(
            "🎉 Felicitar al promovido o 💬 agregar un comentario.",
            options,
            key=f"pills_selection_promocion_{promocion['codigo']}",
            on_change=handle_pills_change,
        )


@st.fragment
def comentarios_view_detail_promocion(comentarios, promocion): 
    nuevo_comentario = st.text_area("Agregar un nuevo comentario", key=f"nuevo_comentario_promocion_{promocion['codigo']}", max_chars=200, placeholder="Escribe tu comentario aquí...")
    if st.button("Publicar", icon=":material/send:", key=f"enviar_comentario_promocion_{promocion['codigo']}"):
        if nuevo_comentario.strip():
            with st.spinner("Publicando comentario..."):
                response = db.set_comentario(id_empleado_festejado=promocion['codigo'], contenido=nuevo_comentario, entidad="Promociones")
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
                                "caption": texto_plano,
                                "key": f"comment_promocion_{promocion['codigo']}_{comentario['id']}",
                            }
                        ]
                    )
                
                with col2:
                    if comentario['id_Usuario'] == st.session_state.user['id']:
                        if st.button("🗑️", key=f"eliminar_comentario_promocion_{promocion['codigo']}_{comentario['id']}"):
                            response = db.delete_comentario(id_comentario=comentario['id'])
                            if response:
                                # Remover el comentario de la lista
                                comentarios.remove(comentario)
                                # Actualizar el estado de los comentarios
                                st.session_state.comentarios_promocion = comentarios
                                st.rerun(scope="app")
\
        else:
            st.info("No hay comentarios para esta promoción.")