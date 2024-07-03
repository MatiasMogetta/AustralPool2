import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime

if 'estado' not in st.session_state or st.session_state['estado'] != 'Autorizado':
    st.warning("No autorizado. Por favor, inicie sesión.")
        #Boton que lo lleve a iniciar sesion
    col1, col2, col3 = st.columns(3)

    with col1:
    # CSS para cambiar el color de los botones
        st.markdown("""
            <style>
            div.stButton > button:first-child {
                background-color: white;  # Color blanco para el primer botón
                color: black;
            }
            div.stButton > button:nth-child(2) {
                background-color: #4CAF50;  # Color verde para el segundo botón
                color: white;
            }
            </style>""", unsafe_allow_html=True)
    with col2:
        if st.button("Iniciar sesión"):
            st.switch_page("pages/2Iniciar Sesion.py")
    #fondo de la app
    page_bg_img = f"""
    <style>
    [data-testid="stAppViewContainer"] > .main {{
    background-image: url("https://i.postimg.cc/4xgNnkfX/Untitled-design.png");
    background-size: cover;
    background-position: center center;
    background-repeat: no-repeat;
    background-attachment: local;
    }}
    [data-testid="stHeader"] {{
    background: rgba(0,0,0,0);
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)
    
    st.stop()

def get_db_connection():
    user='postgres.qaqarqxmcujaagjnhysc'
    password='AustralCarPool.'
    host='aws-0-sa-east-1.pooler.supabase.com'
    port='6543'
    dbname='postgres'
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    return conn

def buscar_viaje(codigoPostal, dia_semana, horario, sentido, fechaDeViaje):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            dia_column_ida = f"{dia_semana.lower()}_ida"
            dia_column_vuelta = f"{dia_semana.lower()}_vuelta"
            
            if sentido == 'I':
                dia_column = dia_column_ida
            else:
                dia_column = dia_column_vuelta
            
            query = f"""
            SELECT u.iduser, u.codigo_postal, u.nombre_apellido, u.telefono_celular, u.email, c.plazas
            FROM AustralPool.Usuarios u
            JOIN AustralPool.Conductor c ON u.iduser = c.iduser
            WHERE u.codigo_postal = %s 
              AND c.{dia_column} = %s
              AND %s BETWEEN c.fecha_inicio AND c.fecha_fin
              AND %s BETWEEN c.fecha_inicio AND c.fecha_fin
            """
            cur.execute(query, (codigoPostal, horario, fechaDeViaje, fechaDeViaje))
            results = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            df = pd.DataFrame(results, columns=columns)
            return df
    except psycopg2.Error as e:
        st.error(f"Se produjo un error al buscar el viaje: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def reservar_viaje(idConductor, idPasajero, fechaViaje, sentido, dia_semana):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Verificar plazas disponibles
            query_plazas = """
            SELECT plazas FROM AustralPool.Conductor WHERE idUser = %s
            """
            cur.execute(query_plazas, (int(idConductor),))  # Convertir a int
            plazas_disponibles = cur.fetchone()[0]

            # Verificar plazas ocupadas
            query_ocupados = """
            SELECT COUNT(*) FROM AustralPool.Viajes 
            WHERE idConductor = %s AND fechaViaje = %s AND sentido = %s AND dia_semana = %s
            """
            cur.execute(query_ocupados, (int(idConductor), fechaViaje, sentido, diaMayuscula(dia_semana)))
            result = cur.fetchone()
            plazas_ocupadas = result[0] if result else 0

            if plazas_ocupadas < plazas_disponibles:
                # Insertar nueva reserva
                query_insert = """
                INSERT INTO AustralPool.Viajes (idConductor, idPasajero, fechaViaje, sentido, dia_semana)
                VALUES (%s, %s, %s, %s, %s)
                """
                cur.execute(query_insert, (int(idConductor), int(idPasajero), fechaViaje, sentido, diaMayuscula(dia_semana)))
                conn.commit()
                st.success("Reserva realizada con éxito.")
                st.experimental_rerun()  # Rerun the page to reflect the changes
                return True
            else:
                st.warning(f"No hay plazas disponibles para este viaje. Plazas disponibles: {plazas_disponibles}, Plazas ocupadas: {plazas_ocupadas}")
                return False
    except psycopg2.Error as e:
        st.error(f"Se produjo un error al reservar el viaje: {e}")
        return False
    finally:
        conn.close()

def cargar_viajes_futuros(idUser):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            query = """
            SELECT v.idConductor AS DNI, v.fechaViaje, v.sentido, v.dia_semana, c.nombre_apellido AS conductor, c.email AS email, c.telefono_celular AS celular
            FROM AustralPool.Viajes v
            JOIN AustralPool.Usuarios c ON v.idConductor = c.idUser
            WHERE v.idPasajero = %s AND v.fechaViaje >= CURRENT_DATE
            """
            cur.execute(query, (int(idUser),))  # Convertir a int
            results = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            df = pd.DataFrame(results, columns=columns)
            return df
    except psycopg2.Error as e:
        st.error(f"Se produjo un error al cargar los viajes reservados: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def cargar_viajes_pasados(idUser):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            query = """
            SELECT v.idConductor AS DNI, v.fechaViaje, v.sentido, v.dia_semana, c.nombre_apellido AS conductor, c.email AS email, c.telefono_celular AS celular
            FROM AustralPool.Viajes v
            JOIN AustralPool.Usuarios c ON v.idConductor = c.idUser
            WHERE v.idPasajero = %s AND v.fechaViaje < CURRENT_DATE
            """
            cur.execute(query, (int(idUser),))  # Convertir a int
            results = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            df = pd.DataFrame(results, columns=columns)
            return df
    except psycopg2.Error as e:
        st.error(f"Se produjo un error al cargar el historial de viajes: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

#Viajes como conductor
def cargar_datos_conductor(idUser):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            query = """
            SELECT plazas, fecha_inicio, fecha_fin, 
                   lunes_ida, lunes_vuelta, 
                   martes_ida, martes_vuelta, 
                   miercoles_ida, miercoles_vuelta, 
                   jueves_ida, jueves_vuelta, 
                   viernes_ida, viernes_vuelta
            FROM AustralPool.Conductor
            WHERE idUser = %s AND fecha_fin > CURRENT_DATE
            """
            cur.execute(query, (int(idUser),))
            results = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            df = pd.DataFrame(results, columns=columns)
            return df
    except psycopg2.Error as e:
        st.error(f"Se produjo un error al cargar los datos del conductor: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def diaMayuscula(dia):
    if dia == 'miercoles':
        return 'X'
    else:
        return dia[0].upper()

def obtener_codigo_postal_usuario(id_usuario):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            query = """
            SELECT codigo_postal FROM AustralPool.Usuarios WHERE iduser = %s
            """
            cur.execute(query, (id_usuario,))
            result = cur.fetchone()
            return result[0] if result else ''
    except psycopg2.Error as e:
        st.error(f"Se produjo un error al obtener el código postal: {e}")
        return ''
    finally:
        conn.close()

st.set_page_config(page_title='Austral Pool', page_icon='logoCarPool.jpg', layout="centered", initial_sidebar_state="auto", menu_items=None)

st.image('Imagenderecha.jpg', 
         use_column_width=True
         )
st.title('Viajes')
st.write('Acá podés ver los viajes que ya tenés reservados y buscar nuevos viajes')

# Inicializar variables de sesión
if 'idUser' not in st.session_state:
    st.session_state['idUser'] = None

if 'confirmar_reserva' not in st.session_state:
    st.session_state['confirmar_reserva'] = False

if 'selected_index' not in st.session_state:
    st.session_state['selected_index'] = None

if 'viaje_buscado' not in st.session_state:
    st.session_state['viaje_buscado'] = False

idUser = st.session_state['user_id']

if idUser:
    try:
        idUser = int(idUser)
        st.session_state['idUser'] = idUser
    except ValueError:
        st.error("El ID de usuario debe ser un número entero.")

if st.session_state['idUser']:
    st.title('Mis viajes')
    
    # Obtener y mostrar el nombre del usuario
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            query = "SELECT nombre_apellido FROM AustralPool.Usuarios WHERE iduser = %s"
            cur.execute(query, (st.session_state['idUser'],))
            result = cur.fetchone()
            if result:
                nombre_usuario = result[0]
                query_sexo = "SELECT genero FROM AustralPool.Usuarios WHERE iduser = %s"
                cur.execute(query_sexo, (st.session_state['idUser'],))
                sexo_result = cur.fetchone()
                if sexo_result and sexo_result[0].lower() == 'f':
                    st.write(f"Bienvenida, {nombre_usuario}")
                else:
                    st.write(f"Bienvenido, {nombre_usuario}")
    except psycopg2.Error as e:
        st.error(f"Se produjo un error al obtener el nombre del usuario: {e}")
    finally:
        conn.close()

    # Utilizando tabs para mostrar los viajes de conductor, futuros y pasados
    tabs = st.tabs(["Como pasajero", "Como Conductor", "Historial"])
    
    with tabs[0]:
        st.write("Mis viajes como pasajero")
        df_mis_viajes = cargar_viajes_futuros(st.session_state['idUser'])
        df_mis_viajes.fillna('-', inplace=True)  # Reemplazar None por guión
        st.dataframe(df_mis_viajes, hide_index=True)

    with tabs[1]:
        st.write("Viajes como Conductor")
        df_viajes_conductor = cargar_datos_conductor(st.session_state['idUser'])
        df_viajes_conductor.fillna('-', inplace=True)  # Reemplazar None por guión
        st.dataframe(df_viajes_conductor, hide_index=True)

        st.write("Pasajeros confirmados")
        query_pasajeros = """
        SELECT p.nombre_apellido AS Pasajero, v.fechaViaje AS "Fecha Viaje", v.sentido AS Sentido
        FROM AustralPool.Viajes v
        JOIN AustralPool.Usuarios p ON v.idPasajero = p.idUser
        WHERE v.idConductor = %s
        """
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query_pasajeros, (st.session_state['idUser'],))
                results = cur.fetchall()
                columns = [desc[0] for desc in cur.description]
                df_viajes = pd.DataFrame(results, columns=columns)
                df_viajes.fillna('-', inplace=True)  # Reemplazar None por guión
                st.dataframe(df_viajes, hide_index=True)
        except psycopg2.Error as e:
            st.error(f"Se produjo un error al cargar los pasajeros confirmados: {e}")
        finally:
            conn.close()
            

    with tabs[2]:
        st.write("Historial de viajes")
        df_historial = cargar_viajes_pasados(st.session_state['idUser'])
        df_historial.fillna('-', inplace=True)  # Reemplazar None por guión
        st.dataframe(df_historial, hide_index=True)

    st.title('Buscar viajes')

    idUser = st.session_state.get('idUser')
    if idUser:
        codigoPostal = obtener_codigo_postal_usuario(idUser)
    else:
        codigoPostal = ''

    fechaDeViaje = st.date_input("¿Qué día necesitás transporte para la universidad?", value=None)

    opcionesDireccion = pd.DataFrame({'first column': ['I', 'V']})
    idaOVuelta = st.selectbox('¿Querés ir hacia la universidad (IDA=I) o volver de la universidad (VUELTA=V)?', opcionesDireccion['first column'])

    opcionesHorario = pd.DataFrame({'first column': ['M', 'T', 'N']})
    if idaOVuelta == 'I':
        horario = st.selectbox('¿En qué horario querés ir a la universidad?', opcionesHorario['first column'])
    else:
        horario = st.selectbox('¿En qué horario querés volver de la universidad?', opcionesHorario['first column'])

    dias_semana_es = {
        0: 'lunes',
        1: 'martes',
        2: 'miercoles',
        3: 'jueves',
        4: 'viernes',
        5: 'sábado',
        6: 'domingo'
    }

    if st.button("Buscar viaje"):
        dia_semana = dias_semana_es[fechaDeViaje.weekday()]  # Obtener el nombre del día en español
        df_resultados = buscar_viaje(codigoPostal, dia_semana, horario, idaOVuelta, fechaDeViaje)
        
        if df_resultados.empty:
            st.warning("No se encontraron viajes disponibles para los criterios seleccionados.")
        else:
            st.session_state['viaje_buscado'] = True
            st.session_state['df_resultados'] = df_resultados
            st.session_state['dia_semana'] = dia_semana
            st.session_state['fechaDeViaje'] = fechaDeViaje
            st.session_state['idaOVuelta'] = idaOVuelta

    if st.session_state['viaje_buscado']:
        df_resultados = st.session_state['df_resultados']
        dia_semana = st.session_state['dia_semana']
        fechaDeViaje = st.session_state['fechaDeViaje']
        idaOVuelta = st.session_state['idaOVuelta']

        st.write("Selecciona el viaje que deseas reservar:")
        selected_index = st.selectbox("Viajes disponibles:", range(len(df_resultados)), format_func=lambda x: f"Nombre: {df_resultados.iloc[x]['nombre_apellido']}, Teléfono: {df_resultados.iloc[x]['telefono_celular']}, Plazas: {df_resultados.iloc[x]['plazas']}")
        st.session_state['selected_index'] = selected_index
        selected_row = df_resultados.iloc[selected_index]

        st.write(f"Confirme la reserva con el conductor {selected_row['nombre_apellido']}")
        if st.button("Confirmar reserva"):
            exito = reservar_viaje(int(selected_row['iduser']), st.session_state['idUser'], fechaDeViaje, idaOVuelta, dia_semana)
            if exito:
                st.success("Reserva realizada con éxito.")
            else:
                st.error("Error en la reserva.")

# Fondo de la app
page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
background-image: url("https://i.postimg.cc/4xgNnkfX/Untitled-design.png");
background-size: cover;
background-position: center center;
background-repeat: no-repeat;
background-attachment: local;
}}
[data-testid="stHeader"] {{
background: rgba(0,0,0,0);
}}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)
