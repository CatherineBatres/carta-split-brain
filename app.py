"""Interfaz local (Streamlit). Correr con:  streamlit run app.py

Streamlit corre en TU computadora (127.0.0.1), igual que Ollama: el "dispositivo"
del split brain es esta máquina. Ver .streamlit/config.toml (telemetría apagada,
servidor solo en localhost) y D-03 en docs/decisiones.md.
"""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from splitbrain.local_llm import ClienteOllama  # noqa: E402
from splitbrain.nube import ClienteGemini, hay_conexion  # noqa: E402
from splitbrain.orquestador import generar  # noqa: E402
from splitbrain.perfil import Perfil  # noqa: E402

# Formularios ficticios para demostraciones (D-32). Cada campo del formulario tiene una
# clave "f_<campo>" para poder llenarlo de un clic en vez de escribirlo en vivo.
CAMPOS_FORM = ["nombre", "empleador_actual", "moneda", "salario_actual", "salario_deseado",
               "puesto_actual", "puesto_objetivo", "empresa_objetivo", "resumen_experiencia",
               "logros", "oferta_texto"]
MONEDAS = ["Q", "US$", "€", "MXN$"]


def leer_formularios() -> list[dict]:
    ruta = Path(__file__).parent / "demo" / "formularios.json"
    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []  # sin el archivo, la app funciona igual: solo no ofrece ejemplos


def llenar_formulario(perfil: dict | None) -> None:
    """Pone en el formulario los datos de un ejemplo (o lo deja vacío con None)."""
    for campo in CAMPOS_FORM:
        if campo in ("salario_actual", "salario_deseado"):
            valor = float(perfil[campo]) if perfil else 0.0
        elif campo == "moneda":
            valor = perfil[campo] if perfil and perfil[campo] in MONEDAS else MONEDAS[0]
        else:
            valor = perfil[campo] if perfil else ""
        st.session_state[f"f_{campo}"] = valor


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

    formularios = leer_formularios()
    if formularios:
        st.divider()
        st.subheader("🎬 Demostración")
        elegido = st.selectbox("Formulario de ejemplo", formularios,
                               format_func=lambda f: f["titulo"],
                               help="Personas y empresas ficticias (demo/formularios.json).")
        st.caption(elegido["que_muestra"])
        st.button("Cargar formulario", on_click=llenar_formulario, args=(elegido["perfil"],),
                  use_container_width=True)
        st.button("Vaciar formulario", on_click=llenar_formulario, args=(None,),
                  use_container_width=True)

c1, c2 = st.columns(2)
with c1:
    st.subheader("🔒 Solo en este dispositivo")
    nombre = st.text_input("Tu nombre", key="f_nombre")
    empleador = st.text_input("Empleador actual", key="f_empleador_actual")
    moneda = st.selectbox("Moneda", MONEDAS, key="f_moneda")
    actual = st.number_input("Salario mensual actual", min_value=0.0, step=500.0,
                             key="f_salario_actual")
    deseado = st.number_input("Salario mensual deseado", min_value=0.0, step=500.0,
                              key="f_salario_deseado")
with c2:
    st.subheader("☁️ Puede ir a la nube (sanitizado)")
    puesto_actual = st.text_input("Puesto actual", key="f_puesto_actual")
    puesto_obj = st.text_input("Puesto al que aplicas", key="f_puesto_objetivo")
    empresa_obj = st.text_input("Empresa a la que aplicas", key="f_empresa_objetivo")
    experiencia = st.text_area("Resumen de tu experiencia", height=90,
                               key="f_resumen_experiencia")
    logros = st.text_area("Logros concretos", height=90, key="f_logros")
oferta = st.text_area("Oferta de trabajo (opcional, pégala completa)", height=140,
                      key="f_oferta_texto")

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
        if r.origen_nota == "local":
            # D-31: el modelo redacta el consejo; las cifras exactas las ponen las reglas.
            st.markdown("**📐 Datos exactos (calculados por reglas, sin modelo)**")
            st.markdown(r.datos_exactos)

    if r.requisitos:
        st.caption("🖥️ Requisitos detectados en local: " + " · ".join(r.requisitos))
    for aviso in r.avisos:
        st.warning(aviso)

    with st.expander("🔍 Exactamente lo que salió a la nube", expanded=not r.envio_nube):
        if r.payload is None:
            st.error("Nada: el guardián bloqueó el envío.")
        else:
            if r.envio_nube:
                st.caption("Enviado ✅")
            elif r.envio_intentado:
                # D-33: antes decía "No se envió" aunque la petición ya había salido.
                st.caption("Se envió ⚠️, pero la nube no devolvió la carta (la escribió el "
                           "modelo local). Esto es lo que salió:")
            else:
                st.caption("No se envió (modo local), pero esto habría salido:")
            st.code(r.payload.como_texto(), language="json")
            st.write("Reemplazos hechos por el sanitizador:", r.payload.reemplazos or "ninguno")
    if r.metricas:
        with st.expander("⏱️ Métricas"):
            st.json(r.metricas)
