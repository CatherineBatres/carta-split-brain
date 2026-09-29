# Registro de decisiones

Cada decisión sigue el mismo formato: **contexto → opciones → decisión → por qué → por qué NO las otras**.
Las razones del split brain se etiquetan así: 🔒 Privacidad · ⚡ Latencia · 💰 Costo · 📴 Disponibilidad · 🎯 Calidad.

Estado: ✅ aceptada · ❌ descartada · ⏳ pendiente de validar con datos del benchmark.

| ID | Decisión | Estado | Razones |
|----|----------|--------|---------|
| D-01 | App web local (corre en la computadora) | ✅ | Requisito Ollama |
| D-02 | Python | ✅ | Preferencia + ecosistema |
| D-03 | Streamlit en 127.0.0.1, telemetría apagada | ✅ | 🔒 |
| D-04 | Reparto de tareas local/nube | ✅ | 🔒 ⚡ 💰 📴 🎯 |
| D-05 | Cálculos y "cuándo mencionarlo" con reglas, no con modelo | ✅ | ⚡ 🎯 📴 |
| D-06 | Detección de sensibles con regex, no con modelo ni NER | ✅ | 🔒 (cond. 3) |
| D-07 | Allowlist + prueba que obliga a clasificar cada campo | ✅ | 🔒 |
| D-08 | Salario en campo numérico propio | ✅ | 🔒 |
| D-09 | Gemini (`gemini-flash-latest`) en la nube | ✅ | 💰 🎯 |
| D-10 | API REST de Ollama con `requests` | ✅ | Medición |
| D-11 | Degradación en 3 niveles | ✅ | 📴 |
| D-12 | `think: false` en ambos modelos | ✅ | ⚡ justicia |
| D-13 | Gemma 4 E4B vs Qwen 3.5 4B | ⏳ | Tamaño comparable |
| D-14 | Rúbrica automática binaria | ✅ | Reproducible |
| D-15 | Evaluación humana ciega | ✅ | 🎯 |
| D-16 | Marcadores `[[NOMBRE]]` rehidratados en local | ✅ | 🔒 🎯 |
| D-17 | Salario ×12 y ×14 también cuentan como fuga | ✅ | 🔒 |
| D-18 | Demo en video, no despliegue en la nube | ✅ | 🔒 |
| D-19 | La nota nunca se guarda ni se registra | ✅ | 🔒 |
| D-20 | Extracción de requisitos con modelo local | ✅ | ⚡ 📴 |
| D-21 | Quitar frases censuradas antes de redactar | ✅ | 🎯 (error real) |

---

## D-01 · Plataforma: app web que corre en la propia computadora
- **Contexto:** el reto indica que Ollama corre en la computadora y pide tenerlo en cuenta al elegir plataforma.
- **Opciones:** Android (como Excusa Legendaria) · app de escritorio (Tkinter/PyQt) · web local · CLI.
- **Decisión:** web local servida en `127.0.0.1`. El "dispositivo" del split brain es la laptop.
- **Por qué:** Ollama y la interfaz viven en la misma máquina, así que "no sale del dispositivo" es literal y verificable.
- **Por qué no:**
  - ❌ *Android:* Ollama no corre nativamente en el teléfono; tendría que llamar a la laptop por la red y ya no sería local.
  - ❌ *Tkinter/PyQt:* más tiempo en interfaz y menos en modelos, que es mi área.
  - ❌ *CLI:* funciona, pero es pobre para capturas del artículo y para una persona no técnica.

## D-02 · Lenguaje: Python
- **Por qué:** preferencia personal, y todo lo necesario existe en Python: cliente HTTP para Ollama, SDK de Gemini, pandas/matplotlib para el benchmark y pytest para las pruebas. Un solo lenguaje para app, pruebas y análisis.
- **Por qué no:** ❌ *JavaScript/Kotlin:* obligaría a usar dos lenguajes (app + análisis).

## D-03 · Streamlit, pero amarrado a localhost y sin telemetría
- **Opciones:** Streamlit · FastAPI + HTML propio · Gradio.
- **Decisión:** Streamlit, con `.streamlit/config.toml`: `server.address = "127.0.0.1"` y `gatherUsageStats = false`.
- **Por qué:** es la forma más rápida de tener formulario y resultados en Python.
- **Hallazgo real:** por defecto Streamlit envía estadísticas de uso y escucha en todas las interfaces de red. Para una app que promete privacidad, las dos cosas se apagan explícitamente.
- **Por qué no:**
  - ❌ *Streamlit Community Cloud:* rompería todo: el "dispositivo" pasaría a ser un servidor ajeno que recibiría el salario.
  - ❌ *FastAPI + HTML:* más código sin aportar nada al área de modelos.
  - ❌ *Gradio:* válido, pero su opción `share=True` crea un túnel público con un solo parámetro; es un riesgo fácil de activar por error.

## D-04 · Qué corre dónde
| Tarea | Dónde | Cómo | Razones |
|---|---|---|---|
| Calcular % de aumento, clasificar expectativa, rango de la oferta, cuándo mencionarlo | Local | Reglas (`reglas.py`) | ⚡ 🎯 📴 |
| Detectar y reemplazar datos sensibles | Local | Regex (`sensibles.py`) | 🔒 |
| Decidir qué campos salen | Local | Allowlist (`router.py`) | 🔒 (cond. 3) |
| Extraer requisitos de la oferta | Local | Modelo (Ollama) | ⚡ 📴 💰 |
| Redactar la nota de negociación | Local | Modelo (Ollama) → reglas | 🔒 📴 |
| Redactar la carta | Nube | Gemini | 🎯 💰 (capa gratuita) |
| Carta sin conexión | Local | Modelo → plantilla | 📴 |
| Rehidratar nombre y empleador | Local | Reemplazo de texto | 🔒 |

**Por qué la carta va a la nube:** es la tarea donde más importa la calidad de redacción, y es el único texto que la persona enviará a un tercero. Un modelo de 4B escribe cartas aceptables, pero más genéricas (se valida en el benchmark). Además la carta no necesita el salario, así que puede salir sin exponer lo sensible.

**Por qué la nota NO va a la nube, aunque la nube escriba mejor:** la nota necesita el salario, y el salario no puede salir. Aquí la privacidad pesa más que la calidad.

## D-05 · Los números los calcula código, no un modelo
- **Decisión:** `reglas.analizar()` calcula el % exacto, la clasificación (umbrales 10/25/40 %), la posición frente al rango y cuándo mencionarlo. El modelo solo redacta a partir de esos hechos.
- **Por qué:** un modelo pequeño puede equivocarse en aritmética simple; una resta y una división no. Además es instantáneo, funciona sin Ollama y se prueba con pytest en milisegundos.
- **Sobre los umbrales:** son una convención explícita y ajustable, no un dato de mercado. Su valor es que son predecibles y se pueden discutir.
- **Por qué no:** ❌ *Pedirle al modelo que calcule:* no se puede garantizar el resultado ni probarlo de forma determinista.

## D-06 · Detectar sensibles con regex, no con un modelo ni con NER
- **Decisión:** regex para correos, DPI (13 dígitos), teléfonos y montos; búsqueda exacta (sin importar tildes ni mayúsculas) para el nombre y el empleador, que la persona ya escribió en sus campos.
- **Por qué:** la condición 3 exige que la decisión sea explícita y probable. Además, no hace falta "adivinar" nombres: ya los tenemos, así que se busca el texto exacto.
- **Error real encontrado al diseñar las pruebas:** la regex de teléfonos (`dddd-dddd`) también atrapaba rangos de años como `2019-2023`, y los borraba de la experiencia. Se agregó una excepción para rangos de años y una prueba que lo protege.
- **Por qué no:**
  - ❌ *Pedirle al LLM local que anonimice:* no es determinista; puede omitir un dato una de cada N veces.
  - ❌ *spaCy NER:* dependencia pesada y no garantiza reconocer nombres o empresas locales; la búsqueda exacta es más fiable para este caso.
- **Límite conocido:** no detecta cifras escritas en letras ("doce mil"). Se mitiga con D-08.

## D-07 · Allowlist, no blocklist, y una prueba que obliga a decidir
- **Decisión:** solo salen los campos en `CAMPOS_NUBE`. Una prueba falla si un campo de `Perfil` no está clasificado.
- **Por qué:** con una lista de bloqueados, un campo nuevo que nadie clasificó saldría por omisión. Con permitidos, sale solo si alguien lo decidió.
- **Capas:** allowlist → sanitizador → guardián (`verificar_payload`), que **falla cerrado**: si detecta algo, no se envía nada y la carta se hace en local.

## D-08 · El salario tiene su propio campo numérico
- **Por qué:** así el salario nunca pasa por el texto libre que se envía. La regex es la segunda defensa, no la primera.

## D-09 · Nube: Gemini
- **Decisión:** SDK `google-genai`, modelo configurable (`GEMINI_MODEL`, por defecto `gemini-flash-latest`).
- **Por qué:** capa gratuita en Google AI Studio (costo cero para el curso), buen español y es el patrón del proyecto de referencia. El nombre va en `.env` porque los modelos cambian seguido.
- **Por qué no:** ❌ *Un modelo "Pro":* para una carta de 250 palabras no justifica el costo extra. ❌ *Otros proveedores sin capa gratuita:* costo.

## D-10 · Llamar a Ollama por su API REST con `requests`
- **Por qué:** la respuesta de `/api/chat` trae `load_duration`, `eval_count` y `eval_duration`; con streaming medimos también el tiempo al primer token. `/api/ps` reporta la memoria del modelo cargado. Con HTTP plano el README puede mostrar la llamada exacta.
- **Por qué no:** ❌ *Paquete `ollama` o LangChain:* capas extra que esconden justo lo que quiero medir.

## D-11 · Degradación en tres niveles
- Carta: nube → modelo local → plantilla. Nota: modelo local → reglas.
- **Por qué:** la condición 4 pide que sin conexión la app siga siendo útil. Con este diseño, aun sin internet **y** sin Ollama, entrega una nota con el % exacto y una carta base.

## D-12 · `think: false` para los dos modelos
- **Por qué:** los modelos recientes pueden "razonar" antes de responder, lo que multiplica la latencia y los tokens. Para redactar una nota de 150 palabras no aporta, y dejarlo activo en un modelo y no en el otro haría injusta la comparación. Si un modelo no acepta el parámetro, el cliente reintenta sin él.

## D-13 · Modelos a comparar ⏳
- **Propuesta:** `gemma4:e4b` vs `qwen3.5:4b` (clase ~4B, caben en 8–16 GB de RAM).
- **Pendiente:** confirmar las etiquetas exactas en ollama.com/library y anotar el tamaño en disco que muestra `ollama list`. Ojo: los modelos "E" de Gemma se nombran por parámetros *efectivos*; si el tamaño en disco difiere mucho, documentarlo como limitación de la comparación.
- **Controles:** mismos casos, mismos prompts, mismas opciones (`temperature 0.2`, `seed 42`, `num_ctx 4096`, `num_predict 700`), un modelo cargado a la vez, arranque en frío medido aparte, calentamiento antes de medir, 3 repeticiones.

## D-14 · Rúbrica automática binaria
- **Por qué:** cada criterio (0/1) se explica en una línea y se puede auditar. El criterio clave de la nota es **"sin cifras inventadas"**: cualquier monto o % que no venga de los hechos calculados cuenta como alucinación.
- **Por qué no:** ❌ *Usar Gemini como juez:* habría que enviar la nota a la nube, y la nota contiene el salario.

## D-15 · Evaluación humana ciega
- **Por qué:** lo que una regla no mide (naturalidad, persuasión) lo califica una persona sin saber qué modelo escribió cada texto. La clave se guarda aparte y se une después (`bench/analizar.py`).

## D-16 · Marcadores que se rehidratan en local
- La nube escribe `[[NOMBRE]]` y el dispositivo lo reemplaza por el nombre real.
- **Por qué:** la carta sale firmada sin que la nube conozca el nombre. Si el modelo altera el marcador, `problemas_en_carta` lo avisa.

## D-17 · Salario ×12 y ×14 también es fuga
- **Por qué:** en Guatemala se habla de salario mensual, anual con 12 pagos o con 14 (aguinaldo y bono 14). Un logro como "ahorré Q150,000" coincide con 12 × Q12,500, así que el guardián compara contra las tres formas.

## D-18 · Demo en video, no despliegue público
- **Por qué:** la app necesita Ollama en la máquina de quien la usa; desplegarla en un servidor contradice la arquitectura. El "link al demo" será un video corto (con y sin conexión).

## D-19 · La nota no se guarda ni se registra
- Vive solo en la sesión de Streamlit (memoria). No hay logs con el salario. El benchmark sí guarda notas, pero de perfiles ficticios.

## D-20 · Extraer requisitos de la oferta con el modelo local
- **Por qué con modelo:** los requisitos vienen en lenguaje libre y variado; una regla no generaliza. **Por qué local:** respuesta inmediata en pantalla (⚡), funciona sin conexión para la carta local (📴) y no gasta tokens de la nube (💰).
- **Por qué no la nube:** la nube ya recibe la oferta completa para redactar; extraer también ahí duplicaría llamadas.

## D-21 · Las frases con `[MONTO]`, `[TELÉFONO]`... no llegan a la carta (error real)
- **Qué pasó:** al correr la app de punta a punta **sin internet y sin Ollama**, la plantilla pegó la experiencia sanitizada tal cual y la carta decía: *"llevo 5 años en Telefonía Chapina y cobro [MONTO]. Tel [TELÉFONO], [CORREO]"*. Las pruebas unitarias no lo atraparon porque probaban la privacidad (no salía nada sensible), no la **calidad** de la carta resultante.
- **Lección:** proteger un dato no basta; hay que decidir qué hacer con el hueco que deja.
- **Decisión:** `sin_frases_censuradas()` elimina de la plantilla las frases (separadas por `.`, `!`, `?` o `;`) que contienen marcas ciegas; el prompt de la carta pide omitirlas; `problemas_en_carta` avisa si quedó alguna; y una prueba de regresión lo vigila.
- **Por qué no:** ❌ *Reemplazar `[MONTO]` por "una cifra":* produce frases vacías ("cobro una cifra"). ❌ *No sanitizar la plantilla porque es local:* el texto ya estaba sanitizado para la nube y reusarlo mantiene un solo camino de datos.
