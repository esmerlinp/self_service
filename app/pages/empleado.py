import streamlit as st
from app.core import get_employee_by_id, get_vacaciones_by_id
import datetime
import pandas as pd
from app.util import tiempo_transcurrido, parse_fecha
from app.fragments import ausencias
import app
def employee_detail(**kargs):
    
    employeeId = kargs.get("employeeId")
    from_screen = kargs.get("from_screen", "this")
    
    e = get_employee_by_id(employeeId=employeeId)
    
    if not e:
        st.info(f"Not implemented {kargs}")
        return

    
    nombre = e['primerNombreEmpleado']
    apellido = e['primerApellidoEmpleado']
    imagen = e.get('imageUrl', None)
    
    if not imagen:
        imagen = f"https://ui-avatars.com/api/?background=random&name={nombre}+{apellido}=100%bold=true&background=61a1af&color=fdfdfd"

    
    # Determinar el color según el estado del empleado
    estado = e['estadoEmpleado']
    nombre_estado = e['nombre_EstadoEmpleado']

    solicitudes = get_vacaciones_by_id(e['idEmpleado'], vacaciones=False)

    if estado == 1:  # Activo
        color = "green"
    elif estado == 4:  # Vacaciones
        color = "orange"
    elif estado == 5:  # Licencia
        color = "orange"
    elif estado == 2:  # Inactivo
        color = "red"
    else:  # Cualquier otro estado
        color = "orange"

    # Asignar el estado con el color correspondiente
    estado_html = f'<b style="font-weight: bold; color: {color};">{nombre_estado}</b>'
    
    _, col, _ = st.columns([1,4,1])

    with col:
        if st.button(":gray[/ Inicio /] :blue[Employee]", type="tertiary"):
            app.switch_page("home")
            
            
        st.markdown(f"""
            <div style="display: flex; flex-direction: row; align-items: center; margin-bottom: 8px; gap: 12px;">
                <div>
                    <img src="{imagen}" style="width: 100px; height: 100px; border-radius: 50%; object-fit: cover;">
                </div>
                <div style="display: flex; flex-direction: column; align-items: flex-start;">
                    <span style="font-weight: bold; font-size: 18px; color: #333;">{e['nombreCompletoEmpleado']}</span>
                    <span style="font-size: 14px; color: #666;">{e['nombre_Puesto']} - {estado_html} </span>
                    <span style="font-size: 14px; color: #666;">{e['idEmpleado']} - email: {e['email_trabajo']} </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        
        
            # Verificar si el empleado está de vacaciones o en licencia
        if estado in [4, 5]:  # Vacaciones o Licencia
            fecha_actual = datetime.datetime.now()
            ultima_solicitud = None

            for sol in sorted(
                solicitudes,
                key=lambda x: datetime.datetime.strptime(x["fecha_Inicio"], "%Y-%m-%dT%H:%M:%S") if x["fecha_Inicio"] else datetime.datetime.min,
                reverse=True
            ):
                # Validar fechas de inicio y fin
                if not sol["fecha_Inicio"]:
                    continue

                if not sol["fecha_Fin"]:
                    sol["fecha_Fin"] = sol["fecha_Inicio"]

                fecha_inicio = datetime.datetime.strptime(sol["fecha_Inicio"], "%Y-%m-%dT%H:%M:%S")
                fecha_fin = datetime.datetime.strptime(sol["fecha_Fin"], "%Y-%m-%dT%H:%M:%S")

                # Verificar si la fecha actual está dentro del rango
                if fecha_inicio <= fecha_actual <= fecha_fin:
                    ultima_solicitud = sol
                    break

            if ultima_solicitud:
                fecha_inicio_formateada = datetime.datetime.strptime(ultima_solicitud['fecha_Inicio'], "%Y-%m-%dT%H:%M:%S").strftime("%d-%m-%Y")
                fecha_fin_formateada = datetime.datetime.strptime(ultima_solicitud['fecha_Fin'], "%Y-%m-%dT%H:%M:%S").strftime("%d-%m-%Y")
                st.warning(f"El empleado se encuentra  de {nombre_estado.lower()} desde el {fecha_inicio_formateada} hasta el {fecha_fin_formateada}.")

    
        st.markdown("&nbsp;")
        if from_screen == "this":
            render_options()
        
        
        
        render_actividades_recientes(solicitudes, from_screen)
        ausencias.resumen_permisos(employeeId=e['idEmpleado'])
        render_historial_vacaciones(employeeId)
        render_horario_trabajo(e['horario_trabajo'])

    
        
        # st.write(e['email_trabajo'])
        # st.write(e['telefonoPersonal'])
        # st.write(e['fechaNacimiento'])
    

        
        



def render_options():
    
    options_container = st.container(border=False)
    with options_container:            
        # Opciones para las pills
        options = ["🚯 Desvinculación", "👨🏼‍🎓 Amonestación", "🛠️ Herramientas de Trabajo"]

        # Inicializar el estado si no existe
        if "pills_selection_team" not in st.session_state:
            st.session_state["pills_selection_team"] = None

        # Función para manejar el cambio de selección
        def handle_pills_team_change():
            selection = st.session_state["pills_selection_team"]
            if selection == "🚯 Desvinculación":
                print("ok")
            elif selection == "🛠️ Herramientas de Trabajo":
                print("ok")
            elif selection == "👨🏼‍🎓 Amonestación":
                print("ok")

            # Reiniciar la selección de las pills
            st.session_state["pills_selection_team"] = None

        # Renderizar las pills
        st.pills(
            "Qué deseas hacer ?",
            options,
            key="pills_selection_employee",
            on_change=handle_pills_team_change,
            disabled=True
        )

@st.fragment
def render_historial_vacaciones(empleadoid):
    
    with st.expander("Historial de vacaciones", expanded=False):

    
        vacaciones = get_vacaciones_by_id(empleadoid)
        
        if not vacaciones:
            st.caption("No se encontraron vacaciones registradas para este empleado.")
            return

        vacaciones = [v for v in vacaciones if  v['fecha_Inicio']]
        # Calcular días tomados por año
        dias_tomados_por_ano = {}
        for vaca in vacaciones:
            
            if not vaca["fecha_Inicio"]:
                continue
            
            if not vaca["fecha_Fin"]:
                vaca["fecha_Fin"] = vaca["fecha_Inicio"]
                
            # Obtener el año de la fecha de inicio
            ano = datetime.datetime.strptime(vaca["fecha_Inicio"], "%Y-%m-%dT%H:%M:%S").year
            dias_tomados_por_ano[ano] = dias_tomados_por_ano.get(ano, 0) + vaca["cantidad"]

        # Ordenar las vacaciones por fecha (más recientes primero)
        vacaciones_ordenadas = sorted(
            vacaciones,
            key=lambda x: datetime.datetime.strptime(x["fecha_Inicio"], "%Y-%m-%dT%H:%M:%S"),
            reverse=True
        )


        # Crear un DataFrame para los registros de vacaciones
        data = [
            {
                "Fecha Inicio": datetime.datetime.strptime(vaca["fecha_Inicio"], "%Y-%m-%dT%H:%M:%S").strftime("%d/%m/%Y"),
                "Fecha Fin": datetime.datetime.strptime(vaca["fecha_Fin"], "%Y-%m-%dT%H:%M:%S").strftime("%d/%m/%Y"),
                "Días Tomados": vaca["cantidad"],
                "Comentario": vaca["comentario"] or "Sin comentario"
            }
            for vaca in vacaciones_ordenadas
        ]

        df = pd.DataFrame(data)


        # Ordenar días tomados por año de mayor a menor
        dias_tomados_por_ano_ordenados = sorted(dias_tomados_por_ano.items(), key=lambda x: x[0], reverse=True)
        
        # Mostrar días tomados por año
        st.markdown("#### Días por Año")
        for ano, dias_tomados in dias_tomados_por_ano_ordenados:
            st.markdown(f"- **{ano}:** Tomados: {dias_tomados} días")
            
            
        # Mostrar el DataFrame
        st.markdown("#### Registros de Vacaciones")
        st.dataframe(df, use_container_width=True)
        
        

def render_horario_trabajo(horario_trabajo):
    with st.expander("Horario de Trabajo"):
        if horario_trabajo:
            # Crear un DataFrame a partir del horario
            data = []
            total_horas = 0

            for dia, horas in horario_trabajo.items():
                if horas and len(horas) == 2:  # Validar que existan ambas horas (inicio y fin)
                    hora_inicio = datetime.datetime.strptime(horas[0], "%H:%M")
                    hora_fin = datetime.datetime.strptime(horas[1], "%H:%M")
                    horas_trabajadas = (hora_fin - hora_inicio).seconds / 3600  # Convertir a horas
                    total_horas += horas_trabajadas
                    data.append({"Día": dia, "Hora Inicio": horas[0], "Hora Fin": horas[1], "Horas Trabajadas": horas_trabajadas})
                else:
                    data.append({"Día": dia, "Hora Inicio": "N/A", "Hora Fin": "N/A", "Horas Trabajadas": 0})

            # Crear el DataFrame
            df = pd.DataFrame(data)

            # Mostrar el DataFrame en Streamlit
            st.markdown("### Horario de Trabajo")
            st.dataframe(df, use_container_width=True)

            # Mostrar el total de horas trabajadas
            st.markdown(f"**Total de Horas por Semana:** {total_horas:.2f} horas")

            # Mostrar advertencia si el total de horas es cero
            if total_horas == 0:
                st.warning("El horario de trabajo no tiene horas definidas. Esto podría afectar la precisión de otros procesos.")
        else:
            st.warning("No se ha configurado un horario de trabajo para este empleado. Esto podría afectar la precisión de otros procesos.")
        
        
            
@st.fragment(run_every=60*60)
def render_actividades_recientes(solicitudes, from_screen = "this"):
     
        with st.expander("🕒 Actividades Recientes", expanded=True):
            # Actividades recientes
            
            if not solicitudes:
                st.caption("Sin registros de actividades en este momento.")
                return
            # Número inicial de registros a mostrar
            if "num_registros" not in st.session_state:
                st.session_state.num_registros = 4  # Mostrar inicialmente 5 registros

            # Filtrar las solicitudes pendientes para incluir solo las de los colaboradores
            solicitudes_filtradas = sorted(
                [
                    sol for sol in solicitudes
                ],
                key=lambda x: parse_fecha(x['fecha_Autorizacion']) if x['fecha_Autorizacion'] else parse_fecha(x['fecha_Registro']),
                reverse=True  # Mostrar las más recientes primero
            )[:10]
            
            solicitudes_mostradas = solicitudes_filtradas[:st.session_state.num_registros]

            
            if not solicitudes_filtradas:
                st.caption("Sin registros de actividades en este momento.")
                return
        
            # Mostrar las solicitudes filtradas
            for sol in solicitudes_mostradas:    
                if not sol["fecha_Inicio"]:
                    continue
                
                if not sol["fecha_Fin"]:
                    sol["fecha_Fin"] = sol["fecha_Inicio"]
                                       
                span = '<span class="material-symbols-outlined">approval_delegation</span>'
                
                if sol['estado'] == 1:
                    span = '<span class="material-symbols-outlined" style="color: #48752C;">done_all</span>'
                elif sol['estado'] == 2:
                    span = '<span class="material-symbols-outlined" style="color: #EA3323;">remove_done</span>'

                                

                # Determinar unidad
                unidad = "hora" if sol["tipo_Ausencia"] == 4 else "día"
                if not sol['cantidad']:
                    sol['cantidad'] = 0
                    
                cantidad = f"{int(sol['cantidad'])} {unidad}" + ("s" if sol["cantidad"] > 1 else "")

                # Parsear fechas
                fecha_desde = datetime.datetime.strptime(sol["fecha_Inicio"], "%Y-%m-%dT%H:%M:%S").strftime("%d de %B de %Y")
                fecha_hasta = datetime.datetime.strptime(sol["fecha_Fin"], "%Y-%m-%dT%H:%M:%S").strftime("%d de %B de %Y")

                # Generar rango de fechas si no es "PERMISOS HORA"
                if sol["tipo_Ausencia"] == 4:
                    fecha_texto = f"con fecha del {fecha_desde}"
                else:
                    fecha_texto = f"con fecha desde el {fecha_desde} hasta el {fecha_hasta}"

                # Construcción del título y subtítulo
                #fecha = datetime.datetime.strptime(sol['fecha_Registro'], "%Y-%m-%dT%H:%M:%S.%f").strftime("%d-%m-%Y")
                #fecha = tiempo_transcurrido(datetime.datetime.strptime(sol['fecha_Registro'], "%Y-%m-%dT%H:%M:%S.%f"))
                fecha = tiempo_transcurrido(parse_fecha(sol['fecha_Registro']))

                span_fecha = f"""<span style="font-size: 12px; color: #666;"> {fecha} </span>"""
                titulo = f"Creó  una solicitud de  \"{sol['nombre_Tipo_Ausencia'].strip()}\" "
                subtitulo = (
                    f"Se ha registrado una solicitud de {sol['nombre_Tipo_Ausencia'].lower()} "
                    f"{fecha_texto} por {cantidad}."
                )
                
                
                # Agregar línea de autorización si existe
                aditional_text = ""
                if sol["fecha_Autorizacion"]:
                    fecha_aut = datetime.datetime.strptime(sol["fecha_Autorizacion"], "%Y-%m-%dT%H:%M:%S.%f").strftime("%d de %B de %Y")
                    if sol["codigo_Estado"] == 1:
                        aditional_text = f" * La solicitud fue autorizada el {fecha_aut}."
                    elif sol["codigo_Estado"] == 2:
                        aditional_text = f" * La solicitud fue rechazada el {fecha_aut}."

                st.markdown(f"""
                    <div style="display: flex; flex-direction: row; align-items: center; margin-bottom: 8px; gap: 12px;">
                        <div style="display: flex; flex-direction: column; align-items: flex-start;">
                            <span style="font-size: 14px; color: #333;">{span_fecha} {titulo}</span>
                            <span style="font-size: 12px; color: #666;">{subtitulo} </span>
                            <span style="font-size: 12px; color: #666;">{aditional_text}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                                

               
            # Botón dinámico para mostrar más o menos registros
            if len(solicitudes_filtradas) > 4:  # Mostrar el botón solo si hay más de 5 registros
                if st.session_state.num_registros > 4:
                    button_label = ":red[Mostrar menos]"
                else:
                    button_label = ":blue[Mostrar más]"

                if st.button(button_label, type="tertiary", key=f"employee_more_less_{from_screen}"):
                    if st.session_state.num_registros > 4:
                        st.session_state.num_registros = 4  # Reducir a 5 registros
                    else:
                        st.session_state.num_registros += 4  # Incrementar en 5 registros
                    st.rerun(scope="fragment")

