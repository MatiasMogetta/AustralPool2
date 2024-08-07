import streamlit as st
import numpy as np
import pandas as pd
import psycopg2
from PIL import Image

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

st.set_page_config(page_title='Austral Pool', page_icon='logoCarPool.jpg', layout="centered", initial_sidebar_state="auto", menu_items=None)

# CSS para centrar el título usando HTML en st.markdown
st.markdown("""
    <style>
    h1 {
        text-align: center;
    }
    </style>
    <h1>PoolAustral</h1><br>
""", unsafe_allow_html=True)

# Cargar la imagen
image = Image.open('Imagenderecha.jpg')

# Mostrar la imagen con un ancho específico
st.image(image, width=800)  # Ajusta el valor de 300 a lo que mejor se adapte a tus necesidades

st.markdown('''
<style>
verdana-text  {
    font-family: "Verdana";
    font-size: 20px;
}
</style>
<div class="verdana-text">
    <p>DESCRIPCIÓN DE LA APLICACIÓN:<br>
    Bienvenido a la aplicación de Carpool para la Universidad Austral. Esta plataforma está diseñada para facilitar 
    el transporte compartido entre los alumnos de nuestra universidad. Para comenzar, debes registrarte como 
    usuario utilizando tu correo electrónico de mail.austral.edu.ar y 
    completar con tus datos personales.<br></p>
<div class="verdana-text">
    <p>Nuestra aplicación te permite conectarte con otros estudiantes para coordinar viajes 
    hacia y desde la universidad. Puedes registrarte como conductor si tienes un 
    vehículo y deseas ofrecer un viaje, o como pasajero si buscas unirte a un viaje 
    existente. La aplicación funciona utilizando el código postal para asegurar 
    que las conexiones sean convenientes y seguras.<br></p>
<div class="verdana-text">
    <p>¡Únete a la comunidad de carpool de la Universidad Austral y contribuye a un 
    transporte más ecológico y económico!</p>
</div>
''', unsafe_allow_html=True)

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

    if st.button("Crear usuario"):
        st.switch_page("pages/1Registrar Usuario.py")

with col3:
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