
###  Construir la imagen Docker

1. En la terminal, asegúrate de estar en la carpeta `self_service`.
2. Ejecuta el siguiente comando para construir la imagen Docker:

   ```bash
   docker build -t self_service .
   ```

   Esto creará una imagen Docker llamada `self_service`. Docker instalará todas las dependencias y preparará la imagen.

### Ejecutar el contenedor Docker

1. Una vez creada la imagen, ejecuta el siguiente comando para iniciar el contenedor:

   ```bash
   docker run -e COOKIES_PASSWORD="qaxriQ-kojky7-fenxeb" -e RRHH_BASE_URL="http://rrhh.administracionapi.camsoft.com.do:8086" -p 8501:8501 self_service
   ```

   Este comando:
   - Ejecuta el contenedor basado en la imagen `self_service`.
   - Mapea el puerto 8501 en tu máquina al puerto 8501 en el contenedor, permitiéndote acceder a la aplicación desde tu navegador.
   - -e COOKIES_PASSWORD="qaxriQ..."  crea variable de entorno 

2. Abre tu navegador y visita [http://localhost:8501](http://localhost:8501). Deberías ver tu aplicación de Streamlit corriendo dentro de Docker.

###  Detener el contenedor

Para detener el contenedor, abre una nueva terminal y usa el siguiente comando:

```bash
docker ps
```

Este comando muestra todos los contenedores en ejecución. Copia el `CONTAINER ID` correspondiente a tu contenedor y luego detén el contenedor con:

```bash
docker stop <CONTAINER_ID>
```

###  Guardar y compartir tu imagen Docker (opcional)

Si deseas compartir la imagen de Docker, puedes subirla a Docker Hub o guardarla en un archivo. Aquí tienes los pasos básicos:

1. **Para guardar la imagen en un archivo** (útil para moverla entre máquinas):

   ```bash
   docker save -o self_service.tar self_service
   ```

2. **Para compartir en Docker Hub** (requiere una cuenta en Docker Hub):

   - Inicia sesión en Docker desde la terminal:

     ```bash
     docker login
     ```

   - Luego, etiqueta y sube la imagen:

     ```bash
     docker tag self_service <your_dockerhub_username>/self_service
     docker push <your_dockerhub_username>/self_service
     ```

Con estos pasos, ya habrás creado un contenedor Docker para tu aplicación de Streamlit, que puedes ejecutar en cualquier máquina que tenga Docker instalado.
