import streamlit as st
import psycopg2
import pandas as pd
import time

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

#Función para insertar al conductor en la base de datos
def insert_conductor(dni, plazas, fechaInicio, fechaFin, horarioIdaLunes, horarioVueltaLunes, horarioIdaMartes, horarioVueltaMartes, horarioIdaMiércoles, horarioVueltaMiércoles, horarioIdaJueves, horarioVueltaJueves, horarioIdaViernes, horarioVueltaViernes):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            query = "INSERT INTO Australpool.Conductor (iduser, plazas, fecha_inicio, fecha_fin, lunes_ida, lunes_vuelta, martes_ida, martes_vuelta, miercoles_ida, miercoles_vuelta, jueves_ida, jueves_vuelta, viernes_ida, viernes_vuelta) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cur.execute(query, (dni, plazas, fechaInicio, fechaFin, horarioIdaLunes, horarioVueltaLunes, horarioIdaMartes, horarioVueltaMartes, horarioIdaMiércoles, horarioVueltaMiércoles, horarioIdaJueves, horarioVueltaJueves, horarioIdaViernes, horarioVueltaViernes))
            conn.commit()
        return True
    except psycopg2.Error as e:
        st.error(f"Se produjo un error al guardar el usuario: {e}")
        return False
    finally:
        conn.close()

st.set_page_config(page_title='Austral Pool', page_icon='logoCarPool.jpg', layout="centered", initial_sidebar_state="auto", menu_items=None)

#Le pido los datos necesarios al usuario para que sea un conductor
st.title('Alta Conductor')
st.write('Acá podrás darte de alta como conductor, donde podrás ofrecerle ayuda a compañeros que necesiten ir los mismos días y horarios que vos.')
dni = st.session_state['user_id']
plazas = st.number_input('¿Cuántas personas estás dispuestas a llevar en tu auto? Sin contarte a vos.', min_value=0, format='%d')
fechaInicio = st.date_input("Fecha donde planeás empezar a ofrecerte como conductor", value=None)
fechaFin = st.date_input("Fecha donde planeás dejar de ofrecerte como conductor", value=None)

# Variable para controlar la validez de las fechas
fechas_validas = True

if fechaInicio and fechaFin:  # Asegurarse de que ambas fechas están seleccionadas
    if fechaInicio >= fechaFin:
        st.error('La fecha de inicio debe ser anterior a la fecha de fin. Por favor, selecciona las fechas correctamente.')
        fechas_validas = False  # Marcar las fechas como inválidas

# Mapeo de las palabras completas a sus abreviaturas
horarios_map = {
    'Mañana': 'M',
    'Tarde': 'T',
    'Noche': 'N'
}

# Inicializar todas las variables de horario como None antes de las condiciones
horarioIdaLunes = None
horarioVueltaLunes = None
horarioIdaMartes = None
horarioVueltaMartes = None
horarioIdaMiércoles = None
horarioVueltaMiércoles = None
horarioIdaJueves = None
horarioVueltaJueves = None
horarioIdaViernes = None
horarioVueltaViernes = None

# Mostrar el botón de dar de alta solo si las fechas son válidas
if fechas_validas:
    st.write('Seleccione los días en los que va a la facultad y los horarios: Mañana , Tarde o Noche.')
    df = pd.DataFrame({'first column': list(horarios_map.keys())})  # Usar las palabras completas para la selección

    if st.checkbox('Lunes'):
        horarioIdaLunes = st.selectbox('Horario ida lunes', df['first column'])
        horarioVueltaLunes = st.selectbox('Horario vuelta lunes', df['first column'])
        horarioIdaLunes = horarios_map.get(horarioIdaLunes)
        horarioVueltaLunes = horarios_map.get(horarioVueltaLunes)

    if st.checkbox('Martes'):
        horarioIdaMartes = st.selectbox('Horario ida martes', df['first column'])
        horarioVueltaMartes = st.selectbox('Horario vuelta martes', df['first column'])
        horarioIdaMartes = horarios_map.get(horarioIdaMartes)
        horarioVueltaMartes = horarios_map.get(horarioVueltaMartes)

    if st.checkbox('Miércoles'):
        horarioIdaMiércoles = st.selectbox('Horario ida Miércoles', df['first column'])
        horarioVueltaMiércoles = st.selectbox('Horario vuelta Miércoles', df['first column'])
        horarioIdaMiércoles = horarios_map.get(horarioIdaMiércoles)
        horarioVueltaMiércoles = horarios_map.get(horarioVueltaMiércoles)

    if st.checkbox('Jueves'):
        horarioIdaJueves = st.selectbox('Horario ida Jueves', df['first column'])
        horarioVueltaJueves = st.selectbox('Horario vuelta Jueves', df['first column'])
        horarioIdaJueves = horarios_map.get(horarioIdaJueves)
        horarioVueltaJueves = horarios_map.get(horarioVueltaJueves)

    if st.checkbox('Viernes'):
        horarioIdaViernes = st.selectbox('Horario ida Viernes', df['first column'])
        horarioVueltaViernes = st.selectbox('Horario vuelta Viernes', df['first column'])
        horarioIdaViernes = horarios_map.get(horarioIdaViernes)
        horarioVueltaViernes = horarios_map.get(horarioVueltaViernes)

    if st.button("Dar de alta"):
        success = insert_conductor(dni, plazas, fechaInicio, fechaFin, horarioIdaLunes, horarioVueltaLunes, horarioIdaMartes, horarioVueltaMartes, horarioIdaMiércoles, horarioVueltaMiércoles, horarioIdaJueves, horarioVueltaJueves, horarioIdaViernes, horarioVueltaViernes)
        progress_text = "Operation in progress. Please wait."
        my_bar = st.progress(0, text=progress_text)
        for percent_complete in range(100):
            time.sleep(0.01)
            my_bar.progress(percent_complete + 1, text=progress_text)
        time.sleep(1)
        my_bar.empty()
        
        if success:
            st.success("Te has dado de alta como conductor exitosamente.")
            st.markdown("""
            <span style='font-size: 20px; font-weight: bold; color: Black;'>
            Ahora puedes ver tus viajes programados en la página de Viajes.
            </span>
            """, unsafe_allow_html=True)
        
        

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
