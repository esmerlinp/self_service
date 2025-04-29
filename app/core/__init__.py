import requests as r
import streamlit as st
import datetime
import logging
from app.models.evento_model import EventoModel
from app.util import jwt_decode

# Configuración básica del logger
logging.basicConfig(
    filename="app_errors.log",  # Archivo donde se guardarán los errores
    level=logging.ERROR,        # Nivel de registro
    format="%(asctime)s - %(levelname)s - %(message)s"  # Formato del mensaje
)

# Constantes
#URL_BASE = "http://192.168.62.23:8093"
URL_BASE = "http://rrhh.administracionapi.camsoft.com.do:8086"
DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "x-ui-culture": "es-DO",
    "x-api-key": "002002032323232320002SSS"
}


        
def _get_headers(custom_headers=None):
    """
    Genera los encabezados HTTP para las solicitudes.
    """
    headers = DEFAULT_HEADERS.copy()
    # if self.authorization:
    #     headers["Authorization"] = f"Bearer {self.authorization}"
    
        
    if st.session_state.is_auth == str(True):
        token  = st.session_state.token   
        headers["Authorization"] = f"Bearer {token}"
        
    if custom_headers:
        headers.update(custom_headers)
    
        
    return headers





def fetch_data(endpoint, method="GET", params=None, body_params=None, headers=None, timeout=30):
    """
    Función genérica para realizar solicitudes HTTP.

    :param endpoint: Endpoint de la API.
    :param method: Método HTTP (GET, POST, etc.).
    :param params: Parámetros de consulta.
    :param body_params: Datos del cuerpo de la solicitud.
    :param headers: Encabezados adicionales.
    :param timeout: Tiempo de espera en segundos.
    :return: Respuesta en formato JSON o texto.
    """
    try:
        url = f"{URL_BASE}/{endpoint}"
        headers = _get_headers(headers)
        
        
        response = r.request(method, url, params=params, json=body_params, headers=headers, timeout=timeout)
        if response.status_code > 300:
            logging.error(f"API Error: {response.json()}")  # Registrar el error en el logger
            
        response.raise_for_status()

        # Verificar si la respuesta es JSON
        if response.headers.get("Content-Type", "").startswith("application/json"):
            data = response.json()

            # Manejar errores específicos del esquema
            if "errorCode" in data:
                logging.error(f"API Error: {data}")  # Registrar el error en el logger
                return {
                    "error": True,
                    "errorCode": data.get("errorCode"),
                    "errorId": data.get("errorId"),
                    "message": data.get("message"),
                    "detail": data.get("detail"),
                    "statuscode": data.get("statuscode"),
                    "redirectUrl": data.get("redirectUrl"),
                }

            return data  # Retornar la respuesta JSON si no hay errores
            
        return response.text  # Retornar texto si no es JSON

    except r.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")  # Registrar el error HTTP
        return {"error": f"HTTP error occurred: {http_err}"}
    except r.exceptions.RequestException as req_err:
        logging.error(f"Request error occurred: {req_err}")  # Registrar el error de solicitud
        return {"error": f"Request error occurred: {req_err}"}




def get_employee(user_id=None):
    """
    Obtiene información de un empleado por su user_id.
    """
    try:
        print(st.session_state.user)
        if not user_id:
            user_id = st.session_state.user['userId']
            
        employee =  fetch_data(endpoint=f"empleados/empleados/usuarios/{user_id}")
        data = employee.get("result", None)
        
        if data:
            st.session_state.employee = data
            st.session_state.employeeId = data['idEmpleado']
            
        return data
    
    except Exception as e:
        logging.error(f"an error has occurred: {e}")
        return {"error": str(e)}
    
    
def get_employee_by_id(employeeId):
    """
    Obtiene información de un empleado por su user_id.
    """
    try:

        employee =  fetch_data(endpoint=f"empleados/empleados/{employeeId}")
        print(employee)
        data = employee.get("result", None)
        
        return data
    
    except Exception as e:
        logging.error(f"an error has occurred: {e}")
        return {"error": str(e)}





def get_loans():
    """
    Obtiene información de un empleado por su ID.
    """
    try:
        response = fetch_data(endpoint=f"empleados/PrestamosEmpleado/detalle-prestamo/{st.session_state.employeeId}")
        loans = response.get("result", None)
        
        if loans:
            loans_vigentes = [x for x in loans if x['id_Estado'] == 1]
            st.session_state.loans = loans_vigentes[0] if len(loans_vigentes) > 0 else []
            return loans_vigentes
        
        
        return loans
    except Exception as e:
        logging.error(f"an error has occurred: {e}")
        return {"error": str(e)}
    
    
    

def get_payments():
    try:
        payments = fetch_data(endpoint=f"nomina/utilreportenomina/pagos-empleado/{st.session_state.employeeId}")
        data =  payments.get("result", None) 

        if data:
            sorted_data = sorted(data, key=lambda x: x["idDetallePeriodo"], reverse=True)
            st.session_state.payments = sorted_data         
            return sorted_data

        
        return data
    except Exception as e:
        logging.error(f"an error has occurred: {e}")
        return {"error": str(e)}
    
    

def get_ausencias(employeeId=None):
    try:
        if not employeeId:
            employeeId = st.session_state.employeeId
        
        ausencias = fetch_data(endpoint=f"empleados/empleados/ausencias/{employeeId}")
        data =  ausencias.get("result", None)  

        if data:
            order_data = sorted(data, key=lambda x: x["id"], reverse=True)
            st.session_state.ausencias = order_data   
            st.session_state.vacaciones = [item for item in order_data if item['tipo_Ausencia'] == 1]   
            
            return order_data

                
        return data
    except Exception as e:
        logging.error(f"an error has occurred: {e}")
        return {"error": str(e)}


def get_vacaciones_by_id(idempleado, vacaciones:bool=True):
    try:
        ausencias = fetch_data(endpoint=f"empleados/empleados/ausencias/{idempleado}")
        data =  ausencias.get("result", None)  

        if data:
            order_data = sorted(data, key=lambda x: x["id"], reverse=True)
            #st.session_state[f"requests_{idempleado}"] = order_data
            if vacaciones:
                filter_data = [item for item in order_data if item['tipo_Ausencia'] == 1]   
                return filter_data
            else: 
                return order_data
            

                
        return data
    except Exception as e:
        logging.error(f"an error has occurred: {e}")
        return {"error": str(e)}
    
    
    
def get_requisiciones():
    try:
        company = st.session_state.employee['idcompania']
        requisiciones = fetch_data(endpoint=f"/reclutamiento/Requisicion/compania/{company}/3")
        data =  requisiciones.get("result", None)  
        if data:
            st.session_state.requisiciones = data          
        return data
    except Exception as e:
        logging.error(f"an error has occurred: {e}")
        return {"error": str(e)}
    
    
def get_alerts(save_in_session=True):
    try:
        response = fetch_data(endpoint=f"administracion/fmk/Notifications/user")
        data =  response.get("result", None) 
        
        if data:
            sorted_data = sorted(data, key=lambda x: x["id"], reverse=True)
            if save_in_session:
                st.session_state.alerts = sorted_data   
            return sorted_data
        
        return data
    except Exception as e:
        logging.error(f"an error has occurred: {e}")
        return {"error": str(e)}
    
@st.cache_data(ttl=60*60*24, show_spinner=False)
def get_feriados(year=datetime.datetime.now().year):
    try:
        param = { 'año': year }
        holydays = fetch_data(endpoint=f"empleados/selfservice/holidays", params=param)
        data =  holydays.get("result", None)   
        st.session_state.feriados = data   

        return data
    except Exception as e:
        logging.error(f"an error has occurred: {e}")
        return {"error": str(e)}
    

def get_requests():
    try:
        requests = fetch_data(endpoint=f"administracion/Autorizaciones/usuario-actual")
        data =  requests.get("result", None)  
        if data: 
            filtered_data = [r for r in data if r['accion'] == "Ausencia"]
            order_data = sorted(filtered_data, key=lambda x: x["id"], reverse=True)
            st.session_state.requests = order_data   
                    
        return data
    except Exception as e:
        logging.error(f"an error has occurred: {e}")
        return {"error": str(e)}
    
    
#@st.cache_data(ttl=60*60, show_spinner=False)
def get_team_requests():
    try:
        requests = fetch_data(endpoint=f"empleados/selfservice/autorizaciones/asignadas")
        data = requests.get("result", [])
        
        if data:
            # Usar un conjunto para rastrear solicitudes únicas
            unique_requests = {}
            for req in data:
                unique_key = req["id"]  # Usar el campo "id" como clave única
                if unique_key not in unique_requests:
                    unique_requests[unique_key] = req

            # Convertir el diccionario de solicitudes únicas a una lista
            order_data = sorted(unique_requests.values(), key=lambda x: x["id"], reverse=True)
            st.session_state.team_requests = order_data
            return order_data

        return data
    except Exception as e:
        logging.error(f"an error has occurred: {e}")
        return {"error": str(e)}
    
    
    
@st.cache_data(ttl=60*60*24, show_spinner=False)
def get_birthdays():
    try:
        requests = fetch_data(endpoint=f"empleados/selfservice/birthdays")
        data =  requests.get("result", [])  
        
        
        eventos = []
        if data:
            st.session_state.birthdays = data  
            for item in data:
                evento = EventoModel(
                    type="birthday",
                    code=item['idEmpleado'],
                    name=item['nombre'],
                    date=item['fechaCumpleanios'],
                    department=item['nombreDepartamento'],
                    positionName=item['nombrePuesto'],
                    image=item['imagenEmpleado'],
                )
                eventos.append(evento)
            #Ordenar los eventos por fecha
            eventos.sort(key=lambda x: x.date, reverse=True)
            
                   
        return data
    except Exception as e:
        logging.error(f"an error has occurred: {e}")  #
        return {"error": str(e)}
    
    
    
#@st.cache_data(ttl=60*60, show_spinner=False)
def get_promociones():
    try:
        requests = fetch_data(endpoint=f"empleados/selfservice/promotions")
        
        if not isinstance(requests, dict):
            logging.error("El resultado de fetch_data no es un diccionario.")
            return {"error": "Invalid data format"}

        data =  requests.get("result", None)  
        
        eventos = []
        if data:
            

            unique_requests = {}
            for req in data:
                unique_key = req["codigo"]  # Usar el campo "id" como clave única
                if unique_key not in unique_requests:
                    unique_requests[unique_key] = req
            
            order_data = sorted(unique_requests.values(), key=lambda x: x["codigo"], reverse=True)
                    
            # for item in order_data:
            #     evento = EventoModel(
            #         type="promotion",
            #         code=item['codigo'],
            #         name=item['nombreEmpleado'],
            #         date=item['fechaPromocion'],
            #         department="",
            #         oldPosition=item['puestoAnterior'],
            #         positionName=item['puestoNuevo'],
            #         positionDescription=item['descripcionPuesto'],
            #         image=item['imagenEmpleado'],
            #         accion=item['accion'],
            #     )
            #     eventos.append(evento)
            
            # eventos.sort(key = lambda x: x.date, reverse=True)
            
            # Guardar los eventos en el estado de la sesión    
            st.session_state.promotions = order_data   
            return order_data
                    
        return data
    except Exception as e:
        logging.error(f"an error has occurred: {e}")
        return {"error": str(e)}
    


def set_ausencia(from_date, to_date, comment, reason_code, cantidad):
    """
    Establece una ausencia para un empleado.
    param from_date: Fecha de inicio de la ausencia.
    param to_date: Fecha de fin de la ausencia.
    param comment: Comentario sobre la ausencia.
    param reason_code: Código de la razón de la ausencia (int).
    reason_codes:         
        "vacaciones: 1,
        "licencia": 2,
        "permiso_dias": 3,
        "permiso_horas": 4,
        "excusa": 5
    """
    
    
    employee_id =  st.session_state.employee.get('idEmpleado')
    supervisor = st.session_state.employee.get('user_id_supervisor', None)

    body = [{
        "Id_AccionWeb": 12,
        "Id_Registro_Relacionado": employee_id,
        "Fecha_Inicio": from_date,
        "Fecha_Fin": to_date,
        "Comentario": comment,
        "Tipo_Ausencia": reason_code,
        "Cantidad": cantidad,
        "Persona_Asignada": supervisor,
    }]
    
    
    response = fetch_data(endpoint="empleados/TransaccionAccionPersonalEmpleado", method="POST", body_params=body)
    data  = response.get("result", None)
    
    return data



def set_reincorporacion(employee, from_date, comment):
    try:
        body = [{
            "id_AccionWeb": 14,
            "id_Registro_Relacionado": employee,
            "fecha_Efectiva": from_date,
            "Comentario": comment,
            "aprobar_Inmediatamente": True
        }]

        response = fetch_data(endpoint="empleados/TransaccionAccionPersonalEmpleado", method="POST", body_params=body)
        data  = response.get("result", None)
        
        return data
    except Exception as e:
        logging.error(f"an error has occurred: {e}")
        return {"error": str(e)}
    

def aplicar_a_vacante(id_requisicion):
    
    employee  = st.session_state.employee
    
    #obtener la requisicion con el id_requisicion del session_sate
    requisicion = [r for r in st.session_state.requisiciones if r['id'] == id_requisicion]
    requisicion = requisicion[0]

    body = [{"tipo_Identificacion":employee['idTipoIdentificacion'],
                "identificacion":employee['datoIdentificacion'],
                "primer_Nombre":employee['primerNombreEmpleado'],
                "segundo_Nombre":employee["segundoNombreEmpleado"],
                "primer_Apellido":employee['primerApellidoEmpleado'],
                "segundo_Apellido":employee['segundoApellidoEmpleado'],
                "email":employee['email_trabajo'],
                "telefono":employee['telefonoPersonal'],
                "id_GradoAcademico":employee['idGradoAcademico'],
                "etiqueta":"",
                "id_Requisicion":id_requisicion,
                "origen_Solicitante":1,
                }]
    

    
    response = fetch_data(endpoint="reclutamiento/SolicitudEmpleo", method="POST", body_params=body)
    if response.get("error", None):
        return response
    else:
        st.print("Solicitud enviada con éxito")
    return response



# def get_image():
#     """Obtiene la foto del empleado por id
        
#     # Mostramos la imagen usando Streamlit
#     st.image(image, caption='Imagen cargada desde Base64', use_column_width=True)
#     """

#     response = fetch_data(endpoint=f"empleados/ArchivoEmpleado/{st.session_state.employeeId}", method="GET")
#     result = response.get("result", None)
    
#     if result:
#         archivoInBase64 = result['archivoInBase64']
#         #extension = data['extension']
#         #image = base64_to_image(archivoInBase64)
#         st.session_state.user_image = archivoInBase64
#         return archivoInBase64
        
#     else:
#         return None
                

# @st.cache_data(ttl=60*60, show_spinner=False)
# def get_acciones():
#     """Obtiene los acciones de un empleado por id"""

#     try:
#         response = fetch_data(endpoint=f"empleados/TransaccionAccionPersonalEmpleado/AI/{st.session_state.employeeId}")
#         loans = response.get("result", None)
#         if loans:
#             st.session_state.loans = loans
            
#         return loans
#     except Exception as e:
#         return {"error": str(e)}
    
    
# def get_amonestaciones():
#     """Obtiene los acciones de un empleado por id"""

#     try:
#         response = fetch_data(endpoint=f"empleados/transaccionaccionpersonalempleado/{st.session_state.employeeId}/11")
#         loans = response.get("result", None)
#         if loans:
#             st.session_state.loans = loans
            
#         return loans
#     except Exception as e:
#         return {"error": str(e)}
    
    


def get_comentarios(idEmpleado, entidad):
    """
    Obtiene los comentarios de un empleado por id
    :param idEmpleado: ID del empleado. type int
    :param entidad: Entidad a la que pertenece el empleado. type str
    :return: Comentarios del empleado.
    :rtype: list

    """
    
    body = {
            "id": idEmpleado,
            "entidad": entidad
        }

    response = fetch_data(endpoint="administracion/comentarios/obtener", method="POST", body_params=body)
    data  = response.get("result", [])
    
    return data



def set_comentario(id_empleado_festejado, contenido, entidad):
    """
    Guarda un comentario para un empleado específico.
    """
    # Obtener el id del usuario de la sesión        
    id_usuario = st.session_state.user['userId']


    body = {
        "Contenido": f"<p>{contenido}</p>",
        "Entidad": entidad,
        "Id_Registro": id_empleado_festejado,
        "Id_Usuario": id_usuario
    }
    
    response = fetch_data(endpoint="administracion/comentarios", method="POST", body_params=body)
    data  = response.get("result", None)
    if data:
        get_comentarios(id_empleado_festejado, entidad)
    
    return data



def set_post(idpost, contenido, file=None):
    """
    Guarda un post para un empleado específico.
    """
    # Obtener el id del usuario de la sesión        
    id_usuario = st.session_state.user['userId']
    entidad = "Post"
    files = []
    if file:
        files.append(file)
    body = {
        "Contenido": f"<p>{contenido}</p>",
        "Entidad": entidad,
        "Id_Registro": idpost,
        "Id_Usuario": id_usuario,
        "files": files
    }
    
    response = fetch_data(endpoint="administracion/comentarios", method="POST", body_params=body)
    data  = response.get("result", None)
    if data:
        get_post()
    
    return data

def get_post():
    entidad = "Post"
    body = {
            "id": 0,
            "entidad": entidad
        }

    response = fetch_data(endpoint="administracion/comentarios/obtener", method="POST", body_params=body)
    data  = response.get("result", [])
    
    return data

def update_autorizacion(solicitudes, accion = "Autorizar"):
    """Permite autorizar o rechazar una solicitud pendiente de aprobacion """
    
    # Obtener el id del usuario de la sesión        
    id_usuario = st.session_state.user['userId']

    body = solicitudes
    response = None
    
    if accion == "Autorizar":
        response = fetch_data(endpoint="reclutamiento/SolicitudAprobacion/autorizar", method="POST", body_params=body)
    else:
        response = fetch_data(endpoint="reclutamiento/SolicitudAprobacion/rechazar", method="POST", body_params=body)

    data  = response.get("result", None)
    if data:
        #get_team_requests.clear()
        get_team_requests()
    
    return data


def set_documento(id_transaccion, archivoInBase64, nombre_archivo,  extension, fecha_creacion=datetime.datetime.now()):
    """
    Guarda un documento para un empleado específico.
    """
    
    body2 = {
        "id_transaccion": id_transaccion,
        "ArchivoInBytes": archivoInBase64[0:100],
        "nombreArchivo": nombre_archivo,
        "fechaCreacion": fecha_creacion,
        "extension": extension,
        
    }
    
    print(body2)

    body = {
        "id_transaccion": id_transaccion,
        "ArchivoInBytes": archivoInBase64,
        "nombreArchivo": nombre_archivo,
        "fechaCreacion": fecha_creacion,
        "extension": extension.split("/")[1],
        
    }
    
    response = fetch_data(endpoint="empleados/ArchivoAusencia", method="POST", body_params=body)
    data  = response.get("result", None)
    
    return data


def get_documento(employeeId):
    """
    Guarda un documento para un empleado específico.
    """
    
    #TODO: verificar cual es el tipo de  doc Licencia
    
    tipo = 2 #Analisis medico

    response = fetch_data(endpoint=f"empleados/ArchivoEmpleado/documentos/{employeeId}/{tipo}", method="GET")
    data  = response.get("result", [])
    
    return data

def get_documento_by_id(id_documento):
    """
    Guarda un documento para un empleado específico.
    """

    response = fetch_data(endpoint=f"empleados/documentos/{id_documento}/", method="GET")
    data  = response.get("result", [])
    
    return data


def delete_comentario(id_comentario):
    """
    Elimina un comentario para un empleado específico.
    """

    response = fetch_data(endpoint=f"administracion/comentarios/{id_comentario}", method="DELETE")
    data  = response.get("result", None)
    return data




def reest_password(email):
    """Reestablece la contraseña del usuario por su email"""
    # Obtener el id del usuario de la sesión        

    body = {
        "Email": email
    }
    
    response = fetch_data(endpoint="empleados/selfservice/register-user", method="POST", body_params=body)
    data  = response.get("result", None)
    return data

        
def sign_in(email, password):
    """
    Inicia sesión con las credenciales proporcionadas.
    """
    try:
        params = {"UserName": email, "Password": password}
        data = fetch_data(endpoint="administracion/fmk/users/Authenticate", method="POST", body_params=params)
        
        if "error" in data:
            return False
        
        st.session_state.is_auth = str(True)
        st.session_state.token = data["access_Token"]
        st.session_state.user = jwt_decode(st.session_state.token)
        
        user = st.session_state.user
        employee = get_employee(user_id=user['userId'])
        
        if employee:
            print(st.session_state.employee)
            # st.session_state.employee =  employee
            # st.session_state.employeeId = employee['idEmpleado']


        return  data
    except Exception as e:
        logging.error(f"Error en la autenticación: {e}")
        return {"error": str(e)}

