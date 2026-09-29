# Guía paso a paso (de cero a entregado)

## Fase 1 · Preparar tu computadora (una sola vez)
1. Instala **Python 3.11+** → `python --version`
2. Instala **Git** → `git --version`
3. Instala **Ollama** desde https://ollama.com/download y ábrelo.
4. Revisa en https://ollama.com/library las etiquetas exactas de Gemma y Qwen de ~4B y descárgalas:
   ```bash
   ollama pull gemma4:e4b
   ollama pull qwen3.5:4b
   ollama list        # anota el tamaño en disco de cada uno (va en D-13)
   ```
   Si las etiquetas cambian, actualízalas en `.env`, en `app.py` (selectbox) y en `bench/correr_bench.py`.
5. Crea tu API key gratuita en https://aistudio.google.com/apikey

## Fase 2 · Crear el repositorio
```bash
# 1. Descomprime el proyecto y entra
cd carta-split-brain

# 2. Inicializa git y configura tu identidad (solo la primera vez en esta máquina)
git init -b main
git config user.name "Tu Nombre"
git config user.email "tu-correo@ejemplo.com"

# 3. Verifica que .env NO aparezca (debe estar ignorado)
cp .env.example .env
git status          # .env no debe salir en la lista

# 4. Primer commit
git add .
git commit -m "Estructura inicial: núcleo split brain, pruebas, benchmark y documentación"
```

En GitHub: **New repository** → nombre `carta-split-brain` → **Public** → *sin* README ni .gitignore (ya los tienes) → **Create**. Luego:

```bash
git remote add origin https://github.com/<tu-usuario>/carta-split-brain.git
git push -u origin main
```

## Fase 3 · Instalar y verificar
```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest -v                            # deben pasar todas
streamlit run app.py                 # prueba con y sin el interruptor de nube
```

## Fase 4 · Benchmark (tu entregable fuerte)
```bash
python -m bench.correr_bench --simulado          # 1 min: confirma que todo corre
python -m bench.correr_bench --reps 3            # corrida real
```
1. Abre `resultados/evaluacion_ciega.csv` y califica cada texto (1–5) **sin abrir** `resultados/crudo/clave_ciega.json`.
2. `python -m bench.analizar` → genera `resultados/resumen.md` y las gráficas en `docs/img/`.
3. Escribe el veredicto: cuál gana, por qué (con datos) y **en qué pierde el ganador**.
4. Cambia D-13 de ⏳ a ✅ en `docs/decisiones.md`.

```bash
git add resultados/ docs/
git commit -m "Resultados del benchmark Gemma vs Qwen"
git push
```

## Fase 5 · Artículo y demo
1. Toma capturas: app completa, panel "lo que salió a la nube", modo sin conexión, gráficas.
2. Llena los ⟦PENDIENTE⟧ de `docs/articulo.md` y publícalo en Medium o Substack.
3. Graba un video corto (con conexión → sin conexión) y súbelo (YouTube no listado o Loom).
4. Pega ambos links al inicio del `README.md`, commit y push.

## Buenas prácticas de commits mientras trabajas
Un commit por decisión o cambio, con mensaje que diga el porqué:
```bash
git commit -m "Guardián: comparar también salario x12 y x14 (D-17)"
```
Así el historial de git también cuenta la historia del artículo.
