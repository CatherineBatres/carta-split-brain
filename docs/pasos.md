# Guía paso a paso (de cero a entregado)

Los comandos son para Windows (Símbolo del sistema). En Mac o Linux cambia `copy` por `cp` y `.venv\Scripts\activate` por `source .venv/bin/activate`.

## Fase 1 · Preparar tu computadora (una sola vez)
1. Instala **Python 3.11+** → `python --version`
2. Instala **Git** → `git --version`
3. Instala **Ollama** desde https://ollama.com/download y ábrelo.
4. Descarga los dos modelos locales:
   ```bash
   ollama pull gemma4:e4b
   ollama pull qwen3.5:4b
   ollama list
   ```
5. Crea tu API key de Gemini en https://aistudio.google.com/apikey

## Fase 2 · Instalar y verificar
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env          # abre .env y pega tu GEMINI_API_KEY
pytest -q                       # deben pasar todas
streamlit run app.py            # prueba con y sin el interruptor de nube
```

## Fase 3 · Guardar el proyecto en GitHub

**Qué es cada cosa**
- `git add` = elegir qué cambios guardar.
- `git commit` = tomar una "foto" del proyecto con un mensaje que explica qué cambió.
- `git push` = subir esas fotos a GitHub.

**La primera vez** (dentro de la carpeta donde está `app.py`):
```bash
git init -b main
git config user.name "Tu Nombre"
git config user.email "tu-correo@ejemplo.com"

git status
```
Revisa la lista que imprime `git status`: **`.env` no debe aparecer**. Si quieres estar segura:
```bash
git check-ignore .env
```
Debe responder `.env`. Si no responde nada, detente y revisa el archivo `.gitignore`.

```bash
git add -A
git commit -m "App split brain: carta en la nube, nota y reglas en local, con pruebas"
```

En github.com: **New repository** → nombre `carta-split-brain` → **Public** → sin README, sin .gitignore y sin licencia (ya los tienes) → **Create repository**. Luego copia la dirección que te muestra y:
```bash
git remote add origin https://github.com/TU-USUARIO/carta-split-brain.git
git push -u origin main
```
La primera vez se abre una ventana para iniciar sesión en GitHub.

**Cada vez que termines algo** (siempre los mismos cuatro comandos):
```bash
pytest -q
git add -A
git commit -m "Qué cambió y por qué"
git push
```

`pytest` va primero porque una de las pruebas revisa que ninguna clave real esté en los archivos que se suben. Si falla, no hagas el push.

**Dónde va la clave.** Solo en `.env`. El archivo `.env.example` es la plantilla que sí se sube: debe decir `GEMINI_API_KEY=pega_tu_clave_de_aistudio_aqui`. Si GitHub rechaza un push con "Push cannot contain secrets", **no uses el enlace para permitirlo**: quita la clave del archivo y rehaz el commit.

**Mensajes sugeridos para lo que viene**
| Cuándo | Mensaje |
|---|---|
| Después de instalar una actualización | `Rúbrica: comparar puesto por raíces de palabra (D-28)` |
| Después de calificar a ciegas | `Evaluación ciega de las 30 cartas (corrida 2)` |
| Después de la evaluación B | `Evaluación B: Gemma vs Qwen en nota y extracción` |
| Después de instalar D-31 | `Veredicto final Gemma vs Qwen; la nota muestra los datos exactos de las reglas (D-31)` |
| Al cerrar | `README y artículo con resultados finales y links` |

**Si algo sale mal**
| Mensaje | Qué hacer |
|---|---|
| `nothing to commit` | No hay cambios nuevos; está bien |
| `rejected` al hacer push | `git pull --rebase origin main` y luego `git push` |
| Subiste el `.env` por error | Avisa de inmediato a quien te dio la clave para que la cambie; borrarlo del repo no basta |

## Fase 4 · Evaluación A: la carta en Gemma, Qwen y Gemini
```bash
python -m bench.comparar_tres --casos c01 c08               # prueba rápida con 2 perfiles
python -m bench.comparar_tres --carpeta tres_modelos_v2     # los 10 perfiles
```
Cada corrida va en su propia carpeta; el script no deja escribir sobre una que ya existe.

Si cambia una regla de la rúbrica, se recalifica sin volver a generar:
```bash
python -m bench.comparar_tres --reevaluar --carpeta tres_modelos_v2
```

### Calificar a ciegas (la parte humana)

**Qué es.** Leer cada carta y ponerle nota **sin saber qué modelo la escribió**. Si supieras que una carta es de Gemini, podrías calificarla mejor sin darte cuenta. Por eso la hoja muestra las 30 cartas revueltas, con un código (`C000`, `C001`…) en lugar del nombre del modelo.

**Para qué.** Las métricas automáticas dicen si la carta tiene saludo, largo correcto y firma. No dicen si suena natural, si convence o si la mandarías. Eso solo lo puede decir una persona.

**Cómo hacerlo**
1. Abre `resultados\tres_modelos_v2\evaluacion_ciega_cartas.csv` con Excel (doble clic).
2. Ensancha la columna `texto` y activa "Ajustar texto" para leer la carta completa.
3. Para cada fila, lee la carta y llena:

   | Columna | Qué poner | Pregunta que respondes |
   |---|---|---|
   | `lista_para_enviar_1a5` | 1 a 5 | ¿La mandarías tal cual? 5 = sí, sin tocar nada · 3 = con arreglos · 1 = hay que reescribirla |
   | `inventa_datos_si_no` | `si` o `no` | ¿Afirma tener algo que el perfil no dice? Compara con el perfil en `bench\casos.json` |
   | `naturalidad_1a5` | 1 a 5 (opcional) | ¿Suena a una persona o a una plantilla? |
   | `persuasion_1a5` | 1 a 5 (opcional) | ¿Dan ganas de entrevistar a esta persona? |
   | `comentario` | texto (opcional) | Lo que te llame la atención |

4. Guarda (Ctrl+G). Si Excel pregunta por el formato, deja CSV.
5. **No abras `clave_ciega_cartas.json`** hasta terminar: ahí dice qué modelo escribió cada carta.
6. Pide el resumen:
   ```bash
   python -m bench.comparar_tres --ciega --carpeta tres_modelos_v2
   ```
   Muestra el promedio por modelo y lo guarda en `evaluacion_humana.md`.

**Consejos.** Las dos primeras columnas bastan (30 a 40 minutos). Puedes hacerlo en dos tandas: el comando te dice cuántas faltan. Si otra persona puede calificar también, mejor: dos opiniones valen más que una.

## Fase 5 · Evaluación B: Gemma vs Qwen en la nota y la extracción

**Qué es.** La comparación de los dos modelos locales en las tareas que solo hacen ellos: la nota de negociación y la extracción de requisitos. No usa Gemini. La carta no se repite: ya se midió en la Fase 4.

**Antes de empezar (importante).** Una versión anterior de esta prueba apagó la laptop. Para cuidar el equipo:
- conecta el cargador y pon la laptop sobre una mesa, con las rejillas libres;
- cierra el navegador y la app de Streamlit;
- corre **un modelo por vez** y deja descansar el equipo unos minutos entre los dos.

```bash
python -m bench.correr_bench --simulado                          # 1 minuto: confirma que todo corre
python -m bench.correr_bench --modelos gemma4:e4b --reiniciar    # unos 6 minutos
```
Espera 5 minutos y luego:
```bash
python -m bench.correr_bench --modelos qwen3.5:4b    # unos 8 minutos
```

**Si la computadora se apaga o cierras la ventana:** no se pierde nada. Enciéndela, espera a que enfríe y corre el mismo comando: continúa donde se quedó. Para ver cuánto falta:
```bash
python -m bench.correr_bench --estado
```
Si se apaga otra vez, no insistas: avisa y bajamos la carga (por ejemplo `--cada 8 --descanso 120`).

`--reiniciar` va solo en el primer comando: borra el progreso de corridas anteriores. Si luego cambia una regla de calificación, no hace falta volver a generar:
```bash
python -m bench.correr_bench --armar
```

Luego:
1. Abre `resultados\evaluacion_ciega.csv`: son **20 notas de negociación** cortas, revueltas. Llena `claridad_1a5`, `utilidad_1a5` e `inventa_datos_si_no` (¿cita una cifra que no venía en los datos?). Unos 15 minutos.
2. Genera tablas y gráficas:
   ```bash
   python -m bench.analizar
   ```
   Escribe `resultados\resumen.md` y las gráficas en `docs\img\` (calidad, latencia, memoria y ritmo). Mira la tabla "Ritmo": si muchas respuestas salieron "a ritmo lento", el equipo se calentó y conviene repetir con más descansos.
3. **Lee las notas antes de concluir.** Están en `resultados\crudo\progreso.jsonl` y en la hoja ciega. La tabla "Alertas de la nota" de `resumen.md` dice cuántas hablan en primera persona ("mi salario…") y cuántas traen una cifra que no venía en los datos: esas son las primeras que hay que leer.
4. Con eso se escribe el veredicto final: cuál gana, por qué y **en qué pierde el ganador** (README, sección 8.6 y conclusión 1).

Si `resumen.md` muestra un aviso ⚠️ debajo de la evaluación humana, una columna de la hoja quedó vacía o con el mismo valor en todas las filas: esa columna no sirve para comparar modelos.

## Fase 6 · Artículo y demo

Para las demostraciones en vivo hay cinco formularios ficticios que se cargan de un clic (barra lateral, sección 🎬 Demostración) y un guion con qué mostrar y qué decir: [`demo.md`](demo.md).

1. Capturas de la app (se abre con `streamlit run app.py` y luego http://127.0.0.1:8501). Usa **solo datos ficticios**: carga el formulario 1 de la sección 🎬 Demostración:

   | # | Qué debe verse | Cómo llegar |
   |---|---|---|
   | 1 | La app completa: carta a la izquierda, nota privada a la derecha | Llena el formulario y presiona **Generar**, con la nube encendida |
   | 2 | La nota con el bloque **"Datos exactos (calculados por reglas)"** | La misma pantalla, acercando la columna derecha |
   | 3 | El panel **"Exactamente lo que salió a la nube"** abierto | Clic en ese panel, debajo de la carta |
   | 4 | El modo local: la carta dice 🖥️ y el panel dice "No se envió (modo local)" | Apaga el interruptor *"Usar la nube para la carta"* y genera de nuevo. Con el wifi apagado aparece además un aviso amarillo |
   | 5 | (Opcional) La barra lateral con Ollama ✅ e Internet ✅ | Sin cambiar nada |

   Antes de tomar cada captura revisa que no se vea tu clave de Gemini, tu correo ni otras ventanas. No presiones el botón **Deploy** de arriba a la derecha.
2. Guarda las capturas en `docs\img\` y enlázalas desde `README.md` y `docs\articulo.md`.
3. Haz el último commit y push. El artículo se lee directamente en GitHub: [`articulo.md`](articulo.md).
