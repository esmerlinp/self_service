# Usa la imagen base de Python para Apple Silicon
FROM python:3.9-slim

# Configura el directorio de trabajo en el contenedor
WORKDIR /app

# Copia los archivos locales al contenedor
COPY . /app

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Agrega una variable de entorno
#ENV RRHH_API_KEY="AJEFTSLBSUXBTIILJPQKSNNXTETCMFRRWHQSLIHBDJQVBFELRO"

#docker run -e  RRHH_BASE_URL="http://rrhh.administracionapi.camsoft.com.do:8086" -p 8501:8501 self_service


# Expone el puerto en el que Streamlit corre
EXPOSE 8501

# Comando para ejecutar la aplicación de Streamlit
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
