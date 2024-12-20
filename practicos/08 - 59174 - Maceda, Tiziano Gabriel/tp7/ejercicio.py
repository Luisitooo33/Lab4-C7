import streamlit as st
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import matplotlib.pyplot as plt


datos = pd.read_csv('ventas.csv')

class RedNeuronal(nn.Module):
    def __init__(self, entrada, oculta, salida):
        super(RedNeuronal, self).__init__()
        self.cap_oculta = nn.Linear(entrada, oculta)
        self.cap_salida = nn.Linear(oculta, salida)
        self.activacion = nn.ReLU()
    
    def forward(self, x):
        x = self.activacion(self.cap_oculta(x))
        x = self.cap_salida(x)
        return x

st.title("Estimación de Ventas Diarias")
st.sidebar.header("Parámetros de Entrenamiento")

tasa_aprendizaje = st.sidebar.number_input("Tasa de Aprendizaje", min_value=0.0, max_value=1.0, value=0.1, step=0.01)
epocas = st.sidebar.number_input("Número de Épocas", min_value=10, max_value=10000, value=100, step=10)
neuronas_ocultas = st.sidebar.number_input("Número de Neuronas en la Capa Oculta", min_value=1, max_value=100, value=5, step=1)
boton_entrenar = st.sidebar.button("Entrenar")


entradas = torch.tensor(datos['dia'].values, dtype=torch.float32).view(-1, 1)
salidas = torch.tensor(datos['ventas'].values, dtype=torch.float32).view(-1, 1)


entradas /= entradas.max()
salidas /= salidas.max()

if boton_entrenar:
    modelo = RedNeuronal(entrada=1, oculta=neuronas_ocultas, salida=1)
    funcion_error = nn.MSELoss()
    optimizador = torch.optim.SGD(modelo.parameters(), lr=tasa_aprendizaje)


    progreso = st.progress(0)
    errores = []
    for epoca in range(int(epocas)):
        prediccion = modelo(entradas)
        error = funcion_error(prediccion, salidas)

        optimizador.zero_grad()
        error.backward()
        optimizador.step()

        errores.append(error.item())
        progreso.progress((epoca + 1) / epocas)

        st.sidebar.text(f"Época {epoca+1}/{epocas} - Error: {error.item():.6f}") 

    st.success("Entrenamiento exitoso")
    
 
    fig_error, ax = plt.subplots()
    ax.plot(range(1, int(epocas) + 1), errores, label="Errores", color="green")
    ax.set_xlabel("Época")
    ax.set_ylabel("Error")
    ax.legend()
    st.pyplot(fig_error)

    
    with torch.no_grad():
        prediccion_final = modelo(entradas) * datos['ventas'].max()

    fig_resultados, ax = plt.subplots()
    ax.scatter(datos['dia'], datos['ventas'], label="Datos Reales", color="blue")
    ax.plot(datos['dia'], prediccion_final.numpy(), label="Curva de Ajuste", color="red")
    ax.set_xlabel("Día del Mes")
    ax.set_ylabel("Ventas")
    ax.legend()
    st.pyplot(fig_resultados)

st.title('Estimación de Ventas Diarias')