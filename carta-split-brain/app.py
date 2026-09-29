"""Interfaz local (Streamlit). Correr con:  streamlit run app.py

Streamlit corre en TU computadora (127.0.0.1), igual que Ollama: el "dispositivo"
del split brain es esta máquina. Ver .streamlit/config.toml (telemetría apagada,
servidor solo en localhost) y D-03 en docs/decisiones.md.
"""
from __future__ import annotations

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from splitbrain.local_llm import ClienteOllama  # noqa: E402
from splitbrain.nube import ClienteGemini, hay_conexion  # noqa: E402
from splitbrain.orquestador import generar  # noqa: E402
from splitbrain.perfil import Perfil  # noqa: E402

st.set_page_config(page_title="Carta Split Brain", page_icon="✉️", layout="wide")
st.title("✉️ Carta de interés · split brain")
st.caption("Tu salario y tu nota de negociación nunca salen de esta computadora.")

with st.sidebar:
    st.subheader("Estado")
    modelo_local = st.selectbox("Modelo local (Ollama)", ["gemma4:e4b", "qwen3.5:4b"],
                                help="Cámbialo según lo que tengas en `ollama list`.")
    local = ClienteOllama(modelo_local)
    nube = ClienteGemini()
    st.write("🖥️ Ollama:", "✅ listo" if local.disponible() else "❌ no disponible")
    conectado = hay_conexion()
    st.write("☁️ Internet:", "✅" if conectado else "❌ sin conexión")
    st.write("🔑 Gemini API key:", "✅" if nube.configurado() else "❌ falta en .env")
    usar_nube = st.toggle("Usar la nube para la carta", value=True,
                          help="Apágalo para simular modo sin conexión.")

c1, c2 = st.columns(2)
with c1:
    st.subheader("🔒 Solo en este dispositivo")
    nombre = st.text_input("Tu nombre")
    empleador = st.text_input("Empleador actual")
    moneda = st.selectbox("Moneda", ["Q", "US$", "€", "MXN$"])
    actual = st.number_input("Salario mensual actual", min_value=0.0, step=500.0)
    deseado = st.number_input("Salario mensual deseado", min_value=0.0, step=500.0)
with c2:
    st.subheader("☁️ Puede ir a la nube (sanitizado)")
    puesto_actual = st.text_input("Puesto actual")
    puesto_obj = st.text_input("Puesto al que aplicas")
    empresa_obj = st.text_input("Empresa a la que aplicas")
    experiencia = st.text_area("Resumen de tu experiencia", height=90)
    logros = st.text_area("Logros concretos", height=90)
oferta = st.text_area("Oferta de trabajo (opcional, pégala completa)", height=140)

if st.button("Generar", type="primary"):
    perfil = Perfil(
        nombre=nombre, empleador_actual=empleador, salario_actual=actual,
        salario_deseado=deseado, moneda=moneda, puesto_actual=puesto_actual,
        puesto_objetivo=puesto_obj, empresa_objetivo=empresa_obj,
        resumen_experiencia=experiencia, logros=logros, oferta_texto=oferta,
    )
    with st.spinner("Generando…"):
        r = generar(perfil, local=local, nube=nube, usar_nube=usar_nube)

    etiquetas = {"nube": "☁️ Gemini", "local": f"🖥️ {modelo_local}", "plantilla": "📄 plantilla"}
    a, b = st.columns(2)
    with a:
        st.subheader(f"Carta de interés · {etiquetas[r.origen_carta]}")
        st.text_area("Lista para enviar", r.carta, height=420)
        st.download_button("Descargar .txt", r.carta, file_name="carta_interes.txt")
    with b:
        st.subheader(f"🔒 Nota privada · {'🖥️ ' + modelo_local if r.origen_nota == 'local' else '📐 reglas'}")
        st.info(r.nota)

    if r.requisitos:
        st.caption("🖥️ Requisitos detectados en local: " + " · ".join(r.requisitos))
    for aviso in r.avisos:
        st.warning(aviso)

    with st.expander("🔍 Exactamente lo que salió a la nube", expanded=not r.envio_nube):
        if r.payload is None:
            st.error("Nada: el guardián bloqueó el envío.")
        else:
            st.caption("Enviado ✅" if r.envio_nube else "No se envió (modo local), pero esto habría salido:")
            st.code(r.payload.como_texto(), language="json")
            st.write("Reemplazos hechos por el sanitizador:", r.payload.reemplazos or "ninguno")
    if r.metricas:
        with st.expander("⏱️ Métricas"):
            st.json(r.metricas)
