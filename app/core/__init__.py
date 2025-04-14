import requests as r
import streamlit as st
import datetime

# Constantes
#URL_BASE = "http://192.168.62.23:8093"
URL_BASE = "http://rrhh.administracionapi.camsoft.com.do:8086"
DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "x-ui-culture": "es-DO",
    "x-api-key": "002002032323232320002SSS"
}
ID_EMPLOYEE= None




class Core:
    def __init__(self, authorization=None):
        """
        Inicializa la clase Core con un token de autorización opcional.
        """
        self.authorization = authorization



    def _get_headers(self, custom_headers=None):
        """
        Genera los encabezados HTTP para las solicitudes.
        """
        headers = DEFAULT_HEADERS.copy()
        # if self.authorization:
        #     headers["Authorization"] = f"Bearer {self.authorization}"
        if st.session_state.is_auth == str(True):
            token  = st.session_state.user['access_Token']    
            headers["Authorization"] = f"Bearer {token}"
            
        if custom_headers:
            headers.update(custom_headers)
        return headers

    def fetch_data(self, endpoint, method="GET", params=None, body_params=None, headers=None, timeout=30):
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
            headers = self._get_headers(headers)
            response = r.request(method, url, params=params, json=body_params, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response.json() if response.headers.get("Content-Type", "").startswith("application/json") else response.text
        except r.exceptions.HTTPError as http_err:
            return {"error": f"HTTP error occurred: {http_err}"}
        except r.exceptions.RequestException as req_err:
            return {"error": f"Request error occurred: {req_err}"}

    st.cache_data(ttl=60*60, show_spinner=True)
    def get_employee(self):
        """
        Obtiene información de un empleado por su user_id.
        """
        try:
            user_id = st.session_state.user['id']
            
            
            employee =  self.fetch_data(endpoint=f"empleados/empleados/usuarios/{user_id}")
            data = employee.get("result", None)
            
            
            if data:
                st.session_state.employee = data
                global ID_EMPLOYEE
                ID_EMPLOYEE = data['idEmpleado']
    
            
            return data
        
        except Exception as e:
            return {"error": str(e)}
    
    
    st.cache_data(ttl=60*60, show_spinner=True)   
    def get_loans(self):
        """
        Obtiene información de un empleado por su ID.
        """
        try:
            response = self.fetch_data(endpoint=f"empleados/PrestamosEmpleado/detalle-prestamo/{ID_EMPLOYEE}")
            loans = response.get("result", None)
            
            if loans:
                loans_vigentes = [x for x in loans if x['id_Estado'] == 1]
                st.session_state.loans = loans_vigentes[0] if len(loans_vigentes) > 0 else []
                
            return loans
        except Exception as e:
            return {"error": str(e)}
        

    st.cache_data(ttl=60*60, show_spinner=True)
    def get_payments(self):
        try:
            payments = self.fetch_data(endpoint=f"nomina/utilreportenomina/pagos-empleado/{ID_EMPLOYEE}")
            data =  payments.get("result", None)   
            if data:
                sorted_data = sorted(data, key=lambda x: x["idPeriodo"], reverse=True)
                st.session_state.payments = sorted_data         
                return sorted_data
            return None
        except Exception as e:
            return {"error": str(e)}
        
       

    def get_ausencias(self):
        try:
            ausencias = self.fetch_data(endpoint=f"/empleados/empleados/ausencias/{ID_EMPLOYEE}")
            data =  ausencias.get("result", None)  

            if data:
                order_data = sorted(data, key=lambda x: x["id"], reverse=True)
                st.session_state.ausencias = order_data   
                return order_data

                    
            return data
        except Exception as e:
            return {"error": str(e)}
     
     
    st.cache_data(ttl=60*60, show_spinner=True) 
    def get_requisiciones(self):
        try:
            company = st.session_state.employee['idcompania']
            requisiciones = self.fetch_data(endpoint=f"/reclutamiento/Requisicion/compania/{company}/3")
            data =  requisiciones.get("result", None)  
            if data:
                st.session_state.requisiciones = data          
            return data
        except Exception as e:
            return {"error": str(e)}
     
        
    #st.cache_data(ttl=60*60, show_spinner=True)
    def get_alerts(self, save_in_session=True):
        try:
            alerts = self.fetch_data(endpoint=f"administracion/fmk/Notifications/user")
            data =  alerts.get("result", None)   
            if data:
                sorted_data = sorted(data, key=lambda x: x["id"], reverse=True)
                if save_in_session:
                    st.session_state.alerts = sorted_data   
                return sorted_data
            
            return None
        except Exception as e:
            return {"error": str(e)}
        
    st.cache_data(ttl=60*60, show_spinner=True)
    def get_feriados(self, year=datetime.datetime.now().year):
        try:
            holydays = self.fetch_data(endpoint=f"empleados/selfservice/holidays/{year}")
            data =  holydays.get("result", None)   
            st.session_state.feriados = data   

            return data
        except Exception as e:
            return {"error": str(e)}
        
    st.cache_data(ttl=60*60, show_spinner=True)
    def get_requests(self):
        try:
            requests = self.fetch_data(endpoint=f"administracion/Autorizaciones/usuario-actual")
            data =  requests.get("result", None)  
            if data: 
                filtered_data = [r for r in data if r['accion'] == "Ausencia"]
                order_data = sorted(filtered_data, key=lambda x: x["id"], reverse=True)
                st.session_state.requests = order_data   
                      
            return data
        except Exception as e:
            return {"error": str(e)}
        
        

    def get_team_requests(self):
        try:
            requests = self.fetch_data(endpoint=f"empleados/SelfService/autorizaciones/asignadas")
            data =  requests.get("result", None)  
            if data: 
                order_data = sorted(data, key=lambda x: x["id"], reverse=True)
                st.session_state.team_requests = order_data   
                      
            return data
        except Exception as e:
            return {"error": str(e)}
        
        
        
    st.cache_data(ttl=60*60, show_spinner=True)
    def get_birthdays(self):
        try:
            requests = self.fetch_data(endpoint=f"/empleados/selfservice/birthdays")
            data =  requests.get("result", None)  
            if data: 
                st.session_state.birthdays = data   
                      
            return data
        except Exception as e:
            return {"error": str(e)}
        
    st.cache_data(ttl=60*60, show_spinner=True)
    def get_promociones(self):
        try:
            requests = self.fetch_data(endpoint=f"empleados/selfservice/promotions")
            data =  requests.get("result", None)  
            st.session_state.promotions = data   
                      
            return data
        except Exception as e:
            return {"error": str(e)}
        
    
 
    def set_ausencia(self, from_date, to_date, comment, reason_code, cantidad):
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
        
        print(body)
        
        response = self.fetch_data(endpoint="empleados/TransaccionAccionPersonalEmpleado", method="POST", body_params=body)
        print(response)
        data  = response.get("result", None)
        
        return data
    
    
    st.cache_data(ttl=60*60, show_spinner=True)
    def set_reincorporacion(self, from_date, comment):
        
        body = [{
            "Id_AccionWeb": 14,
            "Id_Registro_Relacionado": ID_EMPLOYEE,
            "Fecha_Efectiva": from_date,
            "Comentario": comment,
            "aprobar_Inmediatamente": True
        }]

        response = self.fetch_data(endpoint="empleados/TransaccionAccionPersonalEmpleado", method="POST", body_params=body)
        data  = response.get("result", None)
        
        return data
 
 
    st.cache_data(ttl=60*60, show_spinner=True)
    def aplicar_a_vacante(self, id_requisicion):
        
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
        
   
        
        response = self.fetch_data(endpoint="reclutamiento/SolicitudEmpleo", method="POST", body_params=body)
        if response.get("error", None):
            return response
        else:
            st.print("Solicitud enviada con éxito")
        return response
 
    
    
    def get_image(self, show_spinner=True):
        """Obtiene la foto del empleado por id
            
        # Mostramos la imagen usando Streamlit
        st.image(image, caption='Imagen cargada desde Base64', use_column_width=True)
        """

        response = self.fetch_data(endpoint=f"empleados/ArchivoEmpleado/{ID_EMPLOYEE}", method="GET")
        result = response.get("result", None)
        
        if result:
            archivoInBase64 = result['archivoInBase64']
            #extension = data['extension']
            #image = base64_to_image(archivoInBase64)
            st.session_state.user_image = archivoInBase64
            return archivoInBase64
            
        else:
            return None
                   

    st.cache_data(ttl=60*60, show_spinner=True)
    def get_acciones(self):
        """Obtiene los acciones de un empleado por id"""
    
        try:
            response = self.fetch_data(endpoint=f"empleados/TransaccionAccionPersonalEmpleado/AI/{ID_EMPLOYEE}")
            loans = response.get("result", None)
            if loans:
                print(loans)
                #st.session_state.loans = loans
                
            return loans
        except Exception as e:
            return {"error": str(e)}
        
        
    def get_amonestaciones(self):
        """Obtiene los acciones de un empleado por id"""
    
        try:
            response = self.fetch_data(endpoint=f"empleados/transaccionaccionpersonalempleado/{ID_EMPLOYEE}/11")
            loans = response.get("result", None)
            if loans:
                st.session_state.loans = loans
                
            return loans
        except Exception as e:
            return {"error": str(e)}
        
        

    def get_comentarios(self, idEmpleado, entidad):
        
            # {"SolicitudesConsult", "hrecsolmst"},
            # {"RequisicionConsult", "hrecreqmst"},
            # {"DetalleAutorizaciones","xsdaautorizmst" },
            # {"PeriodoConsult", "PeriodosNominaViewModel"},
            # {"PrestamosEmpleados","hnomprestamosempdet"},
            # {"Cumpleanios","SelfServiceCumpleanios"},
            # {"Promociones","SelfServicePromociones"}

        body = {
                "id": idEmpleado,
                "entidad": entidad
            }
    
        response = self.fetch_data(endpoint="administracion/comentarios/obtener", method="POST", body_params=body)
        data  = response.get("result", None)
        
        return data
    
    

    def set_comentario(self, id_empleado_festejado, contenido, entidad):
        """
        Guarda un comentario para un empleado específico.
        """
        # Obtener el id del usuario de la sesión        
        id_usuario = st.session_state.user['id']
    

        body = {
            "Contenido": f"<p>{contenido}</p>",
            "Entidad": entidad,
            "Id_Registro": id_empleado_festejado,
            "Id_Usuario": id_usuario
        }
        
        response = self.fetch_data(endpoint="administracion/comentarios", method="POST", body_params=body)
        data  = response.get("result", None)
        
        return data
    

    def set_documento(self, id_transaccion, archivoInBase64, nombre_archivo,  extension, fecha_creacion=datetime.datetime.now()):
        """
        Guarda un documento para un empleado específico.
        """

        body = {
            "id_transaccion": id_transaccion,
            "ArchivoInBytes": archivoInBase64,
            "nombreArchivo": nombre_archivo,
            "fechaCreacion": fecha_creacion,
            "extension": extension,
            
        }
        
        response = self.fetch_data(endpoint="empleados/ArchivoAusencia", method="POST", body_params=body)
        print("SET DOCUMENT", response)
        data  = response.get("result", None)
        
        return data
    
    
    st.cache_data(ttl=60*60, show_spinner=True)
    def delete_comentario(self, id_comentario):
        """
        Elimina un comentario para un empleado específico.
        """

        response = self.fetch_data(endpoint=f"administracion/comentarios/{id_comentario}", method="DELETE")

        data  = response.get("result", None)
        return data
    
    
    
    
    def reest_password(self, email):
        """Reestablece la contraseña del usuario por su email"""
        # Obtener el id del usuario de la sesión        
    
        body = {
            "Email": email
        }
        
        response = self.fetch_data(endpoint="empleados/SelfService/register-user", method="POST", body_params=body)
        data  = response.get("result", None)
        return data
    
            
    def sign_in(self, email, password):
        """
        Inicia sesión con las credenciales proporcionadas.
        """
        try:
            params = {"UserName": email, "Password": password}
            data = self.fetch_data(endpoint="administracion/fmk/users/Authenticate", method="POST", body_params=params)
 
            if "error" in data:
                return False



            return  data
        except Exception as e:
            return {"error": str(e)}


if __name__ == "__main__":
    core = Core()
    # Example usage
    user_data = core.sign_in(email="esmerlinep", password="Hol@0000")
    print(user_data)