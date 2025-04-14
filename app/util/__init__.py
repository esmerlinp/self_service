from datetime import date, timedelta, time
from datetime import datetime
from io import BytesIO
from PIL import Image
import pytz, os, base64
#import jwt
import uuid
import re, json
import streamlit as st
from datetime import date, timedelta, time
from typing import Dict, Tuple
from babel.dates import format_date
from fpdf import FPDF
import io


@st.dialog("Notificaciones", width="small")
def show_alert(title, message, additional_info=None):
    """Muestra las notificaciones del usuario en un diseño atractivo."""
    # Mostrar cada notificación con un diseño atractivo
    st.subheader(title)
    st.caption(message)
    if additional_info:
        st.error(additional_info, icon="⚠️")
           
    # Agregar un botón para cerrar la notificación
    if st.button("Cerrar", type="secondary"):
        st.session_state.show_alert = False
        st.session_state.alerts = []
 
 
        


def calcular_dias_laborales(
    fecha_inicio: date,
    fecha_fin: date,
    feriados: list[date]
) -> int:
    """
    Calcula la cantidad de días laborables entre dos fechas, considerando el horario de trabajo
    del empleado y excluyendo los días feriados.

    :param fecha_inicio: Fecha de inicio del cálculo.
    :param fecha_fin: Fecha de fin del cálculo.
    :param horario_trabajo: Diccionario con el horario de trabajo (ej: {"lunes": (08:00, 17:00)}).
    :param feriados: Lista de fechas feriadas a excluir.
    :return: Cantidad de días laborables según el horario de trabajo.
    """
    
    horario = st.session_state.employee['horario_trabajo']
    # Validaciones de entrada
    if not isinstance(fecha_inicio, date) or not isinstance(fecha_fin, date):
        raise ValueError("fecha_inicio y fecha_fin deben ser objetos de tipo date.")
    if not isinstance(horario, dict):
        raise ValueError("horario_trabajo debe ser un diccionario con nombres de días como claves.")
    feriados = set(feriados)  # Eliminar duplicados en la lista de feriados

    dias_laborales = 0
    fecha_actual = min(fecha_inicio, fecha_fin)
    fecha_final = max(fecha_inicio, fecha_fin)

    while fecha_actual <= fecha_final:
        # Obtener el nombre del día en español
        dia_semana = format_date(fecha_actual, "EEEE", locale="es").lower()
        #remover acento del miercoles para compatibilidad con el diccionario de horarios
        if dia_semana == 'miércoles':
            dia_semana = 'miercoles'
            
        if dia_semana in horario and fecha_actual not in feriados:
            dias_laborales += 1
            
        fecha_actual += timedelta(days=1)

    return dias_laborales





# Función para crear PDF desde DataFrame
def dataframe_to_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Agrega encabezados
    col_width = pdf.w / (len(df.columns) + 1)
    for col in df.columns:
        pdf.cell(col_width, 10, str(col), border=1)
    pdf.ln()

    # Agrega filas
    for index, row in df.iterrows():
        for item in row:
            pdf.cell(col_width, 10, str(item), border=1)
        pdf.ln()

    # Retorna los datos del PDF en memoria
    # pdf_buffer = io.BytesIO()
    # pdf.output(pdf_buffer)
    # pdf_buffer.seek(0)
    
    
    pdf_buffer = BytesIO()
    pdf_content = pdf.output(dest='S').encode('latin1')  # retorna el contenido como bytes
    pdf_buffer.write(pdf_content)
    pdf_buffer.seek(0)

    return pdf_buffer




def is_base64(input_string):
    # Verifica si el input es una cadena
    if not isinstance(input_string, str):
        return False

    # Remueve posibles espacios en blanco
    input_string = input_string.strip()

    # Revisa que la longitud de la cadena sea múltiplo de 4
    if len(input_string) % 4 != 0:
        return False

    # Usa regex para validar que solo tenga caracteres válidos para base64
    base64_pattern = re.compile('^[A-Za-z0-9+/]*={0,2}$')
    if not base64_pattern.match(input_string):
        return False

    try:
        # Intenta decodificar la cadena para confirmar que es base64
        base64.b64decode(input_string, validate=True)
        return True
    except Exception:
        return False
    

def png_to_base64(image_path):
    # Abre la imagen con PIL
    with Image.open(image_path) as image:
        # Crea un objeto BytesIO para almacenar la imagen en memoria
        buffered = BytesIO()
        # Guarda la imagen en formato PNG dentro de Buffered
        image.save(buffered, format="PNG")
        # Codifica los bytes de la imagen en base64
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
    return img_base64




def clear_history(chat_history):
    filtered_messages = []
    for message in chat_history:
        if not is_base64(message["content"]) and not es_json_valido(message["content"]):
            filtered_messages.append(message)
    
    return filtered_messages      
                

def validate_params(self, args, required_params):
    """
    Valida los parámetros requeridos en la solicitud.

    Args:
        args (dict): Un diccionario de parámetros que contiene los datos de la solicitud.
        required_params (list): Una lista de los nombres de los parámetros requeridos.

    Returns:
        tuple: Un valor booleano indicando si todos los parámetros requeridos están presentes,
                y un mensaje con información sobre parámetros faltantes si corresponde.
    """
    missing_params = [param for param in required_params if param not in args]

    if missing_params:
        return False, f"Faltan los siguientes parámetros requeridos: {', '.join(missing_params)}"
        return True, ""
    
def display_base64_image(base64_string):
    # Decodifica la cadena base64
    image_data = base64.b64decode(base64_string)
    
    # Usa BytesIO para convertir los datos en una imagen
    image = Image.open(BytesIO(image_data))
    
    return image
    
    # Muestra la imagen en Streamlit
    #st.image(image, caption="Imagen desde base64", use_column_width=True)
    
    
def get_guid():
    return uuid.uuid4()



def es_ruta(ruta):
    # Verificar si el string es una ruta absoluta y si existe
    return os.path.isabs(ruta) and os.path.exists(ruta)



def es_json_valido(string):
    try:
        # Intentar cargar el string como JSON
        parsed = json.loads(string)
        
        # Verificar si es un objeto JSON (diccionario en Python)
        if isinstance(parsed, dict):
            return True
        else:
            return False
    except ValueError:
        return False
    
# def validar_tokens(texto: str, modelo: str, limite: int) -> bool:
#     """
#     Valida si el número de tokens de un texto excede el límite especificado para un modelo dado.

#     Args:
#         texto (str): El texto a validar.
#         modelo (str): El modelo que se está utilizando (ej. "gpt-4", "gpt-3.5-turbo").
#         limite (int): El límite máximo de tokens permitido.

#     Returns:
#         bool: True si el texto está dentro del límite, False si excede el límite.
#     """
#     try:
#         # Cargar el codificador/tokenizador para el modelo especificado
#         encoding = tiktoken.encoding_for_model(modelo)
        
#         # Tokenizar el texto
#         tokens = encoding.encode(texto)
        
#         # Obtener el número de tokens
#         num_tokens = len(tokens)
        
#         # Verificar si el número de tokens está dentro del límite
#         if num_tokens <= limite:
#             print(f"Texto válido. Número de tokens: {num_tokens}/{limite}.")
#             return True
#         else:
#             print(f"Texto excede el límite. Número de tokens: {num_tokens}/{limite}.")
#             return False
#     except KeyError:
#         print(f"Modelo '{modelo}' no reconocido. Verifica el nombre del modelo.")
#         return False





# def truncar_texto(texto: str, modelo: str, limite: int) -> str:
#     """Trunca el texto a la longitud permitida para el modelo especificado."""
    
#     if not texto:
#         return ""
    
#     encoding = tiktoken.encoding_for_model(modelo)
#     tokens = encoding.encode(texto)

#     if len(tokens) > limite:
#         # Truncar el texto al límite de tokens
#         tokens = tokens[:limite]
#         # Decodificar los tokens truncados de nuevo a texto
#         texto_truncado = encoding.decode(tokens)
#         return texto_truncado
    
#     return texto



def convertir_a_iso8601(fecha_str, formato_entrada="%Y-%m-%d %H:%M:%S", zona_horaria="UTC"):
    """
    Convierte una fecha en formato string a formato ISO 8601.
    
    Parámetros:
    - fecha_str (str): La fecha en formato string.
    - formato_entrada (str): El formato en que se encuentra la fecha (por defecto: "%Y-%m-%d %H:%M:%S").
    - zona_horaria (str): La zona horaria a aplicar (por defecto: None). Ejemplo: "UTC", "America/Santo_Domingo".
    
    Retorna:
    - str: Fecha en formato ISO 8601.
    
    # Ejemplo de uso
        fecha_original = "14/10/2024 08:30:00"
        formato_original = "%d/%m/%Y %H:%M:%S"
        zona_horaria = "UTC"  # Opcional

        fecha_iso = convertir_a_iso8601(fecha_original, formato_entrada=formato_original, zona_horaria=zona_horaria)
        print(fecha_iso)  # Salida: 2024-10-14T08:30:00+00:00
    
    """
    # Convertir el string a un objeto datetime usando el formato de entrada
    fecha_dt = datetime.strptime(fecha_str, formato_entrada)
    
    # Si se proporciona una zona horaria, agregarla
    if zona_horaria:
        zona = pytz.timezone(zona_horaria)
        fecha_dt = zona.localize(fecha_dt)
    
    # Convertir la fecha a formato ISO 8601
    return fecha_dt.isoformat()




# Función que toma una cadena Base64 y retorna la imagen decodificada
def base64_to_image(base64_string: str) -> Image.Image:
    """
    # Ejemplo de cadena Base64 (reemplázala con tu cadena)
    base64_string = 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAAA...'

    # Llamamos a la función para obtener la imagen
    image = base64_to_image(base64_string)

    # Mostramos la imagen usando Streamlit
    st.image(image, caption='Imagen cargada desde Base64', use_column_width=True)
    """
    #mod_base64_string = f"data:image/{ext};base64,/{base64_string}"
    # Si la cadena incluye la cabecera como 'data:image/jpeg;base64,', eliminamos esa parte
    #base64_data = base64_string.split(',')[1]
    base64_data = base64_string

    
    # Decodificamos la cadena Base64
    image_data = base64.b64decode(base64_data)
    
    # Convertimos los bytes en una imagen
    image = Image.open(BytesIO(image_data))
    
    return image



def base64_to_file_content(base64_string: str) -> bytes:
    """
    Convierte una cadena Base64 y retorna su contenido.

    Args:
    - base64_string (str): Cadena en formato Base64.

    Returns:
    - bytes: Contenido decodificado de la cadena Base64.
    """
    # Si la cadena incluye la cabecera 'data:image/jpeg;base64,' o similar, la eliminamos
    if ',' in base64_string:
        base64_data = base64_string.split(',')[1]
    else:
        base64_data = base64_string

    # Decodificamos la cadena Base64
    file_data = base64.b64decode(base64_data)

    return file_data








def base64_to_file_content(base64_string: str, output_file: str) -> bytes:
    """
    Convierte una cadena Base64 al archivo original y retorna su contenido.

    Args:
    - base64_string (str): Cadena en formato Base64.
    - output_file (str): Nombre del archivo de salida (con la extensión deseada).

    Returns:
    - bytes: Contenido del archivo leído.
    """
    # Si la cadena incluye la cabecera 'data:image/jpeg;base64,' o similar, la eliminamos
    if ',' in base64_string:
        base64_data = base64_string.split(',')[1]
    else:
        base64_data = base64_string

    # Decodificamos la cadena Base64
    file_data = base64.b64decode(base64_data)

    # Guardamos el archivo con la extensión especificada
    with open(output_file, 'wb') as file:
        file.write(file_data)

    # Leemos el contenido del archivo y lo retornamos
    with open(output_file, 'rb') as file:
        content = file.read()

    # Opcional: Eliminar el archivo después de leerlo
    os.remove(output_file)

    return content



# def jwt_decode(token):
#     # Decodificar el token
#     try:
#         X = "X" * 34
#         A = "A" * 33
#         B = "B" * 4
#         C = "C" * 26
#         decoded = jwt.decode(token, key=X + A + B + C, algorithms=["HS256"])
#         if decoded:
#             userdata = {"userId":decoded["UserID"], "userName": decoded["nameid"], "FullUserName": decoded["FullUserName"], "userEmail": decoded["Email"], "isadmin":decoded["isadmin"], "userCompany": decoded["CompanyId"], "CompanyName": decoded["CompanyName"], "role": decoded["role"]}
#             return userdata
#         return None
#     except jwt.ExpiredSignatureError:
#         return None
#     except jwt.InvalidTokenError:
#         return None
        
# if __name__ == "__main__":
#     jwt_decode("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1laWQiOiJlc21lcmxpbmVwIiwidW5pcXVlX25hbWUiOiJlc21lcmxpbmVwIiwicm9sZSI6IlVzZXIiLCJVc2VySUQiOiIzMjQ2IiwiRnVsbFVzZXJOYW1lIjoiRXNtZXJsaW4gUGFuaWFndWEiLCJEYXRlVXRsQWNjZXNzIjoiIiwiQ29tcGFueUlkIjoiMiIsIkNvbXBhbnlHcm91cElkIjoiMSIsIkNsaWVudElkIjoiIiwiQnJhbmNoT2ZmaWNlSWQiOiIiLCJDb21wYW55TmFtZSI6IkRyZXMuIE1hbGzDqW4gR3VlcnJhIiwiT2ZmaWNlTmFtZSI6IiIsIkVtYWlsIjoiZXNtZXJsaW5lcEBnbWFpbC5jb20iLCJpc2FkbWluIjoiVHJ1ZSIsIm5iZiI6MTcyOTYzMTYyMCwiZXhwIjoxNzMxNzkxNjIwLCJpYXQiOjE3Mjk2MzE2MjB9.6ldWOlCohhRaIjroXFd2poWzXcKia0kHrW2IH8ScV20")        