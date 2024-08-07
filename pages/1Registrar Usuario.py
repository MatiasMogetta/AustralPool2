import streamlit as st
import pandas as pd
import time
import psycopg2
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title='Austral Pool', page_icon='logoCarPool.jpg', layout="centered", initial_sidebar_state="auto", menu_items=None)

#Función para conectarme a la base de datos
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

#Función para chequear si el mail ingresa existe o no en la BBDD
def email_exists(email):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            query = "SELECT * FROM Australpool.Usuarios WHERE email = %s"
            cur.execute(query, (email,))
            result = cur.fetchone()
            return result is not None
    finally:
        conn.close()



# Modificar la función insert_user para incluir latitud y longitud
def insert_user(iduser, nombreYApellido, codigoPostal, contactoTelefono, email, genero, fechaDeNacimiento, contraseña, latitud=None, longitud=None):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            query = """
            INSERT INTO Australpool.Usuarios (iduser, nombre_apellido, codigo_postal, telefono_celular, email, genero, fecha_nacimiento, contraseña, latitud, longitud)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cur.execute(query, (iduser, nombreYApellido, codigoPostal, contactoTelefono, email, genero, fechaDeNacimiento, contraseña, latitud, longitud))
            conn.commit()
    except psycopg2.Error as e:
        st.error(f"Se produjo un error al guardar el usuario: {e}")
    finally:
        conn.close()

#Sección donde se piden los datos de registro de usuario
st.title('✅ Registrar Usuario')

email = st.text_input("Email")
password = st.text_input("Contraseña", type="password") 
confirm_password = st.text_input("Confirmar contraseña", type="password")
if confirm_password and password and confirm_password != password:
   st.error("Verifique su contraseña")
    
st.title('Llenar datos')
st.write('Para poder proveerte de la mejor experiencia necesitamos que llenes los siguientes datos por única vez. Es obligatorio para poder registrarte como usuario.')
dni = st.text_input("DNI")
nombreYApellido = st.text_input("Nombre y Apellido")
codigoPostal = st.text_input("Código postal")
# Añadir la casilla de verificación
ubicacion_precisa = st.checkbox("Desea agregar su ubicación de forma más precisa para mejorar la visualización")

# Mostrar los campos de entrada para latitud y longitud si la casilla está seleccionada
if ubicacion_precisa:
    latitud = st.text_input("Latitud")
    longitud = st.text_input("Longitud")
else:
    latitud = None
    longitud = None
contactoTelefono = st.text_input("Número de celular")
df = pd.DataFrame({'first column': ['F', 'M']})
genero = st.selectbox(
    'Género',
    df['first column'])
fechaDeNacimiento =  st.date_input("Fecha de Nacimiento", max_value=datetime.today())

#Botón de registrar usuario, acá se chequea que estén todos los datos correspondientes
#Si están todos los datos, se inserta al usuario en la BBDD, sino se piden los datos
if st.button("Registrar Usuario"):
    if not dni or not nombreYApellido or not codigoPostal or not contactoTelefono or not email or not genero or not fechaDeNacimiento:
        st.error("Por favor, completa todos los campos.")
    elif fechaDeNacimiento >= datetime.today().date():
        st.error("La fecha de nacimiento debe ser anterior a la fecha actual.")
    elif email_exists(email):
        st.error("El email ya está registrado. Por favor, utiliza otro email.")
    else:
        insert_user(dni, nombreYApellido, codigoPostal, contactoTelefono, email, genero, fechaDeNacimiento, password, latitud, longitud)
        progress_text = "Operation in progress. Please wait."
        my_bar = st.progress(0, text=progress_text)
        for percent_complete in range(100):
            time.sleep(0.01)
            my_bar.progress(percent_complete + 1, text=progress_text)
        time.sleep(1)
        my_bar.empty()
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
