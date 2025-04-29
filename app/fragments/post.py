import streamlit as st
from app.core import set_post
import base64
import datetime

@st.dialog("Publicar contenido", width="large")
@st.fragment()
def create_media_post():
   
    
    if not 'post_step' in st.session_state:
        st.session_state.post_step = 1
    
    if not 'uploaded_file' in st.session_state:
        st.session_state.uploaded_file = {}
        
        
    if st.session_state.post_step == 1:
        _, col, _ = st.columns([0.5,4,0.5])
        with col:
            with st.container():
                _, col1, _ = st.columns([1,4,1])
                col1.image("./app/assets/8582984.jpg", width=300)
                    
                col1.header("Selecciona archivos para empezar")
                col1.caption("Comparte imágenes o un solo vídeo en tu publicación.")
                
                
            # Tamaño máximo permitido en bytes (5 MB)
            MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
            
            uploaded_file = st.file_uploader("Comparte imágenes o un solo vídeo en tu publicación.", type=["jpg", "jpeg", "png", "mp4", "mov", "avi"], accept_multiple_files=False)
            
            
            col, _, col2 = st.columns(3)
        
            if col.button("Descartar Cambios", type="primary", use_container_width=True):
                if 'uploaded_file' in st.session_state:
                    del st.session_state.uploaded_file
                if 'file_content' in st.session_state:
                    del st.session_state.file_content
                    
                del st.session_state.post_step
                st.rerun()
            
            
            if col2.button(":blue[Siguiente]", use_container_width=True):
                if uploaded_file:
                    
                    file_size = uploaded_file.size  # Tamaño del archivo en bytes
                    if file_size > MAX_FILE_SIZE:
                        st.error(f"El archivo excede el tamaño máximo permitido de {MAX_FILE_SIZE / (1024 * 1024):.2f} MB.")
                        #st.stop()

                    
                    
                    file_content = uploaded_file.read()
                    # Convertir el contenido a Base64
                    archivoInBytes = base64.b64encode(file_content).decode("utf-8")
                    
            
                    archivo = {
                            "ArchivoInBytes":archivoInBytes,
                            "NombreArchivo": uploaded_file.name,
                            "extension": uploaded_file.type,
                            "fecha_creacion": datetime.datetime.now().strftime("%d/%m/%Y"),
                        }
                    
   
                    st.session_state.uploaded_file = archivo
                    st.session_state.file_content = file_content

                st.session_state.post_step = 2
                st.rerun(scope="fragment")
                return
                
                    
    elif st.session_state.post_step == 2:
        
        if 'employee' in st.session_state:
            e = st.session_state.employee
            
        nombre = e.get('primerNombreEmpleado', '')
        apellido = e.get('primerApellidoEmpleado', '')
        nombre_Puesto = e.get('nombre_Puesto', '')
        
        imagen_alt = f"https://ui-avatars.com/api/?background=random&name={nombre}+{apellido}=100%bold=true&background=61a1af&color=fdfdfd"
        
        
        imagen = e.get('imageUrl', imagen_alt)


        st.markdown(f"""
            <div style="background-color:#ffffff; border: 0px solid #ddd; border-radius:10px; padding:10px; font-family: Arial, sans-serif; margin-bottom: 20px;">
                <!-- Encabezado del post -->
                <div style="display: flex; align-items: center; margin-bottom: 15px;">
                    <img src="{imagen}" 
                        style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover; margin-right: 15px;">
                    <div>
                        <span style="font-weight: bold; font-size: 16px; color: #333;">{nombre} {apellido}</span><br>
                        <span style="font-size: 12px; color: #666;">{nombre_Puesto}</span><br>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
                    
        # Título descriptivo
        st.subheader("Crea tu publicación")

        # Límite de caracteres
        max_chars = 1000

        # Text area con contador de caracteres
        texto = st.text_area(
            "Escribe algo interesante:",
            placeholder="¿Qué tienes en mente? Comparte tus ideas, pensamientos o actualizaciones aquí...",
            max_chars=max_chars,
            key="post_text_area"
        )

        
        uploaded_file = None
        
        if 'uploaded_file' in st.session_state:
            uploaded_file = st.session_state.uploaded_file
           
            if uploaded_file:            
                file_type = uploaded_file["extension"]
                tipo = file_type.split("/")[0]
                
                if 'file_content' in st.session_state:
                    file_content = st.session_state.file_content
                    if tipo == "image":
                        st.image(file_content)
                    elif tipo == 'video':
                        st.video(file_content)
            
        
        
        col, _, col2 = st.columns(3)
        
        if col.button("Descartar Cambios", type="primary"):
            if 'uploaded_file' in st.session_state:
                del st.session_state.uploaded_file
            if 'file_content' in st.session_state:
                del st.session_state.file_content
                
            del st.session_state.post_step
            st.rerun()
            
        if col2.button(":blue[Publicar]", use_container_width=True):
                
            result = set_post(e['idEmpleado'], texto, file=uploaded_file)
            if result:
                st.balloons()
                
                if 'uploaded_file' in st.session_state:
                    del st.session_state.uploaded_file
                if 'file_content' in st.session_state:
                    del st.session_state.file_content
                    
                del st.session_state.post_step
                st.rerun(scope="app")
                return
            else:
                if 'uploaded_file' in st.session_state:
                    del st.session_state.uploaded_file
                if 'file_content' in st.session_state:
                    del st.session_state.file_content
                    
                del st.session_state.post_step
                st.error("No se pudo publicar el contendo")
            
            
