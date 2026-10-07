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
| D-22 | Comparar la carta en los tres modelos (Gemma, Qwen, Gemini) | ✅ | 🎯 justifica la nube |
| D-23 | Ampliar el criterio "saludo y despedida" y poder recalificar sin regenerar | ✅ | 🎯 (hallazgo real) |
| D-24 | Alerta de "requisitos sin respaldo" + regla en el prompt + columna humana | ✅ | 🎯 (hallazgo real) |
| D-25 | Guardar más métricas por carta, mediana correcta, calentar también a Gemini, una carpeta por corrida | ✅ | Medición |
| D-26 | Veredicto provisional: Gemma 4 E4B como modelo local; la carta en la nube queda en revisión | ⏳ | 🎯 ⚡ |
| D-27 | No pisar corridas, descargar modelos entre corridas, memoria según Ollama y alerta sin valor de puntaje | ✅ | Medición (errores reales) |
| D-28 | Lectura de las 30 cartas: fidelidad, rúbrica saturada, costo de la privacidad; la carta se queda en la nube | ✅ | 🎯 🔒 (hallazgos reales) |
| D-29 | Evaluación ciega: la carta se queda en la nube por margen estrecho. Evaluación B ligera y con guardado continuo | ✅ | 🎯 📴 (error real) |
| D-30 | Clave casi publicada; caída de rendimiento bajo carga; correcciones a la rúbrica de la nota y a la medición | ✅ | 🔒 ⚡ (errores reales) |

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
- **Propuesta:** `gemma4:e4b` vs `qwen3.5:4b` (clase ~4B, caben en 8–16 GB de RAM). Ambas etiquetas existen y corrieron en la máquina de pruebas. Primer resultado en D-26.
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

## D-22 · Comparar la carta en Gemma, Qwen y Gemini (`bench/comparar_tres.py`)
- **Por qué:** D-04 manda la carta a la nube "porque escribe mejor". Eso es una hipótesis hasta medirla. Este script la pone a prueba con los mismos 10 perfiles.
- **Solo la carta:** es la única tarea que hacen tanto la nube como lo local. ❌ *Mandar la nota a Gemini para compararla:* descartado, porque la nota lleva el salario, aunque sean perfiles ficticios; la regla no tiene excepciones.
- **A Gemini se le envía lo mismo que en la app:** el payload que pasó por `preparar_envio()`. Así la prueba también confirma que la nube escribe bien con datos sanitizados.
- **Temperatura 0.2 para los tres:** en la app Gemini usa 0.7 (más variedad), pero para comparar hay que igualar condiciones.
- **Pausa de 4 s entre llamadas a Gemini:** evita el límite de peticiones por minuto de la capa gratuita. Por eso la latencia de Gemini se mide por llamada y no por lote.
- **Un modelo a la vez, con calentamiento (corrección tras la primera prueba real):** en la prueba con c01 y c08, Qwen tardó 33.5 s en c01 y 13.3 s en c08. La diferencia era la carga del modelo a memoria en la primera llamada, más las recargas por alternar Gemma → Qwen → Gemini en cada perfil. Ahora cada modelo corre todos los perfiles seguidos, después de una llamada de calentamiento que no se mide.
- **Limitación conocida:** Gemini puede "pensar" antes de responder, mientras que en Gemma y Qwen eso está apagado (D-12). Su latencia no es 100 % comparable.
- **Qué mirar:** calidad (rúbrica + ciega) contra latencia. Si la diferencia de calidad es pequeña, se debilita la razón 🎯 para usar la nube y conviene decirlo en el artículo.

## D-23 · El criterio "saludo y despedida" era demasiado estrecho (hallazgo de la primera prueba real)
- **Qué pasó:** en la prueba con c01 y c08, los tres modelos sacaron 1.0 en todo salvo Gemini en c08, que obtuvo 0.833 por fallar `saludo_y_despedida` (ver `docs/img/metricas_c01_c08.png`).
- **Dos lecturas posibles, y hay que distinguirlas leyendo la carta:**
  1. *Gemini de verdad omitió el saludo o la despedida* → es un fallo del modelo.
  2. *Gemini usó una fórmula válida que la rúbrica no conocía* (por ejemplo "Respetable equipo" o "Un cordial saludo") → es un fallo de **mi rúbrica**, no del modelo.
- **Por qué importa:** la versión inicial solo aceptaba 4 saludos y 4 despedidas. Una rúbrica tan estrecha premia a quien escribe "como espera la regla", no a quien escribe mejor.
- **Decisión:** ampliar las listas (`SALUDO_RE`, `DESPEDIDA_RE` en `bench/rubrica.py`) con fórmulas comunes en español, con 5 pruebas nuevas. Además, `comparar_tres.py` ahora guarda las cartas crudas (`cartas_crudas.jsonl`) y acepta `--reevaluar`, para recalificar con la rúbrica nueva **sin volver a llamar a los modelos** (ahorra tiempo y llamadas a la API).
- **Protección:** `--reevaluar` no reescribe la hoja ciega, para no borrar calificaciones humanas ya puestas.
- **Por qué no:** ❌ *Quitar el criterio:* una carta sin saludo ni despedida no está lista para enviar. ❌ *Dejarlo como estaba y reportar "Gemini falló":* sería una conclusión que no he verificado.
- **Resultado (verificado leyendo la carta):** era la lectura 2. La carta de Gemini cerraba con **"Un cordial saludo,"**. La regla vieja buscaba `saludos` (plural), `atentamente`, `cordialmente` o `gracias`, y ninguna coincide con "Un cordial saludo" ni con "Agradezco el tiempo…". **Falló la rúbrica, no el modelo.** Con la regla ampliada esa misma carta obtiene 1.0 (comprobado sobre el texto real).

## D-24 · La carta afirmaba habilidades que la persona nunca dijo tener (hallazgo al leer la carta)
- **Qué pasó:** al leer la carta de Gemini en c08 para resolver D-23 apareció un problema más serio que el saludo. El perfil solo decía: *ejecutivo de ventas, 5 años, cerró contratos en 2024*. La oferta pedía: *CRM (Salesforce), negociación, inglés*. La carta afirmó: *"cuento con experiencia en el uso de Salesforce"* y *"me comunico con fluidez en inglés"*. El modelo **convirtió los requisitos de la oferta en experiencia de la persona**.
- **Por qué es grave:** la carta se envía con el nombre real de la persona. Afirmar un idioma o una herramienta que no domina es justo lo que se descubre en la primera entrevista.
- **Por qué no lo vimos antes:** la rúbrica automática le dio 1.0 a esa carta. Ningún criterio mide fidelidad a los datos. Mientras tanto, la misma rúbrica le había quitado puntos por una despedida correcta (D-23): **midió mal lo trivial y no midió lo importante.**
- **Decisión, en tres capas:**
  1. **Prompt (regla 6):** "Los requisitos de la oferta NO son experiencia de la persona…". Es el mismo prompt para los tres modelos, así que la comparación sigue siendo justa.
  2. **Alerta automática** `requisitos_sin_respaldo` (`bench/rubrica.py`): lista los requisitos de la oferta que la carta menciona y que no están en la experiencia, logros o puesto actual. Sobre la carta real de c08 marca: *salesforce; negociación; inglés*.
  3. **Columna humana** `inventa_datos_si_no` en las hojas ciegas.
- **Por qué la alerta NO entra en la nota de calidad:** es una heurística con falsos positivos conocidos ("me gustaría aprender Salesforce" la dispara; "negociación" es razonable en alguien de ventas). Sirve para decir *"revisa esta carta"*, no para restar puntos sola. Acabo de aprender (D-23) lo que pasa cuando una regla frágil decide la nota.
- **Por qué no:** ❌ *No enviar la oferta a la nube:* la carta perdería lo que la hace específica. ❌ *Detectarlo con otro modelo:* otro componente probabilístico que también habría que verificar.
- **Efecto en resultados:** la prueba de 2 perfiles (c01, c08) se hizo con el prompt anterior. La corrida de 10 perfiles usa el prompt nuevo; no se mezclan en una misma tabla.
- **Pendiente:** ⏳ revisar si Gemma y Qwen hicieron lo mismo en c08, y si la regla 6 lo reduce.

## D-25 · Mejoras de medición tras la corrida de 10 perfiles
- **Mediana mal calculada (error real):** el resumen en pantalla tomaba el valor central superior (`sorted(x)[n//2]`) en vez de la mediana. Con 10 datos imprimió 10.37 s (Gemma), 22.28 s (Qwen) y 10.74 s (Gemini); las medianas correctas son 10.32, 22.10 y 9.34 s. El orden entre Gemma y Gemini **se invierte**. Ahora se usa `statistics.median` y se reportan también mínimo, máximo y desviación.
- **Más métricas por carta:** la corrida 1 solo guardó la latencia total. Ahora se guardan tiempo al primer token, tokens/s, RAM pico de Ollama, tamaño del modelo en memoria y tokens de entrada y salida de Gemini (para estimar costo). *Por qué no se hizo antes:* el script nació para comparar calidad; al usarlo para decidir, hacía falta el resto.
- **Calentar también a Gemini:** su primera llamada paga la conexión. Si los locales se calientan y la nube no, la comparación favorece a los locales.
- **Una carpeta por corrida (`--carpeta`):** la corrida 2 usa un prompt distinto (D-24). Guardarla aparte permite comparar antes y después en vez de pisar los resultados.
- **`resumen.md` y `latencia.png` por corrida:** la tabla y la gráfica se generan solas, para que el README y el artículo salgan de los datos y no de transcribir la terminal.
- **Gráfica elegida:** un punto por carta y una marca en la mediana. *Por qué no barras:* una barra con la mediana esconde justo lo más interesante de esta corrida, que Gemini varía entre 6 y 15 s y Gemma casi no varía.

## D-26 · Veredicto provisional con la corrida 1 (30 cartas, prompt anterior a la regla 6)
| Modelo | Calidad (rúbrica) | Mediana | Mín–máx | Desv. | Arranque |
|---|---|---|---|---|---|
| gemma4:e4b | 1.00 (10/10) | 10.3 s | 9.5–10.7 s | 0.34 s | 19.4 s |
| qwen3.5:4b | 0.98 (9/10) | 22.1 s | 20.1–24.2 s | 1.38 s | 12.4 s |
| gemini | 1.00 (10/10) | 9.3 s | 6.2–14.6 s | 2.95 s | — |

- **Modelo local: Gemma 4 E4B (provisional).** Mitad de latencia que Qwen en los 10 perfiles, cuatro veces más estable, 10/10 en la rúbrica. **Pierde en el arranque** (19.4 s contra 12.4 s).
- **La razón 🎯 calidad de D-04 para mandar la carta a la nube queda en revisión.** La rúbrica no muestra ventaja de Gemini sobre Gemma, y la ventaja de latencia (1 s) es menor que la variación de Gemini. A favor de lo local hay tres razones que no dependen de medir: 🔒 privacidad, 📴 disponibilidad y 💰 costo.
- **Regla de decisión, escrita antes de ver los datos que faltan** (para no acomodarla después): si en la evaluación ciega Gemini no supera a Gemma por al menos 0.5 puntos (de 5) en "lista para enviar", el valor por defecto de la app pasa a **carta local** y la nube queda como opción.
- **Por qué no decidir ya:** faltan la evaluación humana, la memoria, la alerta de fidelidad sobre las 30 cartas y las otras dos tareas locales. La rúbrica automática sola ya demostró que puede equivocarse (D-23, D-24).
- **Pendiente de verificar:** el fallo de Qwen en c05 (`menciona_puesto_y_empresa`) puede ser otro criterio demasiado estricto; hay que leer la carta.

## D-27 · Lo que enseñaron las corridas 1b y 2
**Datos (latencia mediana por carta)**

| Modelo | Corrida 1 | Corrida 1b | Corrida 2 (referencia) | Alertas c1b | Alertas c2 |
|---|---|---|---|---|---|
| gemma4:e4b | 10.3 s | 10.5 s | 9.5 s | 8/10 | 8/10 |
| qwen3.5:4b | 22.1 s | 58.4 s | 22.8 s | 9/10 | 9/10 |
| gemini | 9.3 s | 11.8 s | 8.0 s | 9/10 | 9/10 |

1. **Una corrida pisó a otra (error real).** La corrida 1b se guardó en `resultados/tres_modelos`, la misma carpeta de la corrida 1, y reemplazó sus 30 cartas. Se perdió el "antes" de la regla 6. **Decisión:** el script se detiene si la carpeta ya tiene una corrida, y pide `--carpeta` nueva o `--sobrescribir`. *Por qué no una carpeta con fecha automática:* llenaría `resultados/` de carpetas de pruebas rápidas; es mejor que elegir el nombre sea un acto consciente.
2. **Qwen tardó 58 s en la corrida 1b y 22 s en las otras dos.** Mismo prompt (las alertas de Gemma y Qwen son idénticas en 1b y 2, porque usan semilla fija), mismo equipo. Hipótesis no comprobada: la máquina estaba ocupada, o Gemma seguía cargado y ambos modelos no cabían en la memoria de la tarjeta gráfica. **Decisión:** descargar cada modelo local al terminar (`keep_alive: 0`) y antes de calentarlo, para que el arranque sea en frío de verdad y ningún modelo le quite memoria al siguiente. La corrida 1b se conserva como evidencia de variabilidad, no para el veredicto.
3. **"RAM pico = 97.6 MB" no es la memoria del modelo (error real).** Ese número es la memoria principal del proceso de Ollama. Un modelo de ~4B ocupa varios GB; un valor tan bajo indica que está en la tarjeta gráfica. **Decisión:** el dato de memoria que se reporta es el de Ollama (`/api/ps`: tamaño total y parte en GPU); la RAM del proceso queda como dato secundario con su aclaración.
4. **La alerta `requisitos_sin_respaldo` se dispara en 26 de 30 cartas, igual en los tres modelos.** Consecuencias:
   - No es un problema exclusivo de la nube (corrige la impresión que dejaba D-24, basada en una sola carta de Gemini).
   - No sirve como puntaje: no distingue "domino X" de "me interesa aprender X", y una buena carta debe mencionar los requisitos.
   - No demuestra si la regla 6 funcionó. Eso se decide leyendo (columna `inventa_datos_si_no`).
   - *Por qué no quitarla:* sigue siendo útil para saber qué frases revisar. *Por qué no afinarla ya:* sin leer las cartas reales, cualquier ajuste sería adivinar; primero la lectura, luego la regla.
5. **El arranque no es concluyente:** Gemma 19.4 / 11.8 / 20.9 s; Qwen 12.4 / 17.7 / 13.1 s. Hasta ahora el calentamiento no partía de un modelo descargado. La medición controlada queda para la evaluación B.
6. **Veredicto de D-26: se mantiene.** Gemma fue más rápido que Qwen en las 30 comparaciones perfil a perfil. Cambia un matiz: en la corrida 2 ambos locales empatan en la rúbrica (0.98) y Gemini los supera por una carta.

## D-28 · Lo que mostró leer las 30 cartas de la corrida 2
**Equipo:** AMD Ryzen 7 4800H, 16 GB de RAM, Ollama 0.35.1. Ollama reporta ambos modelos al 100 % en la GPU (3,096 MB Gemma; 2,988 MB Qwen).

### 1. Fidelidad: quién afirma cosas que la persona no dijo
| Modelo | Cartas que inventan | Casos |
|---|---|---|
| Gemini | 0 de 10 | — |
| Gemma 4 E4B | 2 de 10 | c03 (inglés B2), c04 (licencia de conducir) |
| Qwen 3.5 4B | 5 de 10 | c01 (título colegiado, Excel avanzado, SAT), c02 (bases de datos, Git), c04 (licencia), c06 (historial en GRI), c09 (mercado SaaS) |

- **Criterio:** cuenta solo cuando la carta *afirma tener* algo que no está en el perfil. "Me interesa aprender X" no cuenta. Los adornos de logros ("cientos de predios") se anotan aparte.
- **Límite:** lectura no ciega y de una sola pasada, hecha con ayuda de un asistente de IA. Se confirma con la columna `inventa_datos_si_no` de la hoja ciega.
- **Antes y después de la regla 6 (Gemini, c08):** de *"cuento con experiencia en el uso de Salesforce"* a *"disposición para familiarizarme con el uso de Salesforce"*. La regla funciona en el modelo grande; los pequeños la obedecen a veces.

### 2. Decisión: la carta se queda en la nube, y cambia la razón
- D-04 decía "🎯 calidad: escribe mejor". La rúbrica de forma no lo confirma (empate). La lectura sí muestra una ventaja, en **fidelidad**.
- **Decisión:** carta en la nube cuando hay conexión; Gemma como respaldo sin conexión.
- **Por qué no pasar la carta a local por defecto** (lo que D-26 dejaba abierto): Gemma inventó en 2 de 10 cartas, y la carta se envía con el nombre de la persona. La privacidad no lo exige, porque a la nube solo llegan datos sanitizados.
- **Enmienda a la regla de D-26, escrita antes de la evaluación ciega:** la regla de los 0.5 puntos en "lista para enviar" sigue en pie. Si esa nota y la fidelidad apuntan en direcciones distintas, pesa más la fidelidad.
- **Veredicto local (D-26) confirmado:** Gemma. Doble de tokens/s (41.9 contra 20.1), primer token en 1.4 s contra 3.8 s, e inventa menos de la mitad. Pierde en memoria por 108 MB (3.5 %).

### 3. La rúbrica de forma quedó saturada
- **Otro criterio demasiado estricto (error real):** `menciona_puesto_y_empresa` exigía la frase exacta. Rechazó la carta de Gemma en c05 por decir "Coordinación Académica" cuando el puesto era "Coordinadora académica". **Decisión:** comparar por raíces de palabra (`rubrica.menciona`).
- **Efecto:** las 30 cartas sacan 1.00. La rúbrica ya no distingue modelos. *Por qué no agregar criterios hasta que vuelva a distinguir:* sería ajustar la regla al resultado que uno espera. Lo honesto es decir que la forma está resuelta en los tres y que la diferencia está en la fidelidad.
- *Por qué la corrección no favorece a nadie a propósito:* quita una penalización a Gemma (c05) y otra a Qwen (c06) por igual.

### 4. La alerta: dos errores de coincidencia
- "api" coincidía con "r**ápi**damente", y "project" con el título "Project Manager". **Decisión:** buscar palabras completas y quitar el título del puesto antes de buscar.
- Sigue sin distinguir "domino X" de "quiero aprender X". Se mantiene como guía de lectura (D-27).

### 5. Lo que la privacidad le costó a la calidad ⏳ (propuestas sin aplicar)
- **Sin nombre no hay género.** En c03 y c09 nada en los datos indica el género; Gemma (1) y Qwen (2) escribieron en masculino. Qwen además falló en c01, donde el puesto decía "Contadora". Gemini escribió en neutro. *Propuesta:* regla en el prompt: "si no conoces el género, redacta sin adjetivos de género". *Por qué no enviar el género a la nube:* es un dato personal más, y la redacción neutra lo resuelve sin enviarlo.
- **El sanitizador borra números que no son dinero.** "5,000 predios" → `[MONTO]`; "ISO 14001" → `[MONTO]`. *Propuesta:* sanitizar un número sin moneda solo si cerca hay una palabra de dinero; el guardián sigue bloqueando el salario en cualquier formato. También hay un error de espaciado ("Digitalicé[MONTO]").
- **Por qué no se aplican ahora:** cambiarían lo que reciben los modelos a mitad de la evaluación, y las corridas dejarían de ser comparables. Se aplican después de la evaluación B, o quedan como trabajo futuro.
- **Lección:** son errores del lado seguro. Ninguna prueba de privacidad los detecta, porque no se filtra nada.

### 6. Herramientas para la evaluación humana
- `bench/hoja.py` lee la hoja ciega aunque Excel la guarde con punto y coma o en Windows-1252, y acepta "sí", "si", "x" o "1".
- `python -m bench.comparar_tres --ciega --carpeta tres_modelos_v2` une la hoja con la clave y escribe `evaluacion_humana.md`.
- En la evaluación B, la hoja ciega incluye **solo las notas** (20 textos cortos). *Por qué:* las cartas ya se califican en la evaluación A; calificar 40 textos más no cambiaría ninguna decisión.
- La evaluación B reporta la memoria según Ollama, no la RAM del proceso (D-27).

## D-29 · Evaluación ciega de las 30 cartas, y una evaluación B que no apague la computadora

### 1. Resultados de la evaluación ciega (corrida 2)
| Modelo | Lista para enviar (1–5) | Marcadas "inventa datos" | Lectura estricta de D-28 |
|---|---|---|---|
| Gemini | 4.40 | 3 de 9 | 0 de 10 |
| Gemma 4 E4B | 4.20 | 5 de 10 | 2 de 10 |
| Qwen 3.5 4B | 3.40 | 8 de 10 | 5 de 10 |

- **Las dos lecturas coinciden en el orden y no en las cantidades.** La ciega marcó más cartas en los tres modelos. La lectura de D-28 solo contaba afirmaciones de una herramienta, título o idioma concretos; la ciega usó un criterio más amplio. ⏳ Falta compararlas carta por carta.
- **Corrección a D-28:** "Gemini, 0 de 10" solo vale con el criterio estricto. No se puede decir que el modelo de la nube no inventa.
- **Límites:** una sola persona; no se calificaron naturalidad ni persuasión; una carta de Gemini sin respuesta en "inventa"; 10 cartas por modelo.

### 2. Aplicación de las reglas fijadas de antemano
- **D-26:** si Gemini no supera a Gemma por 0.5 en "lista para enviar", la carta pasa a local. La diferencia fue **0.2**: no alcanza.
- **Enmienda de D-28:** si esa nota y la fidelidad apuntan en direcciones distintas, pesa más la fidelidad. En fidelidad Gemini va adelante en las dos lecturas (3 de 9 contra 5 de 10; 0 contra 2).
- **Decisión:** la carta **se queda en la nube** cuando hay conexión; Gemma es el respaldo.
- **Con qué confianza:** poca. Son 2 cartas de diferencia sobre 10 y 0.2 puntos sobre 5, con una sola calificadora. Es una decisión por margen estrecho, y así se reporta.
- **Por qué no cambiar a local de todos modos:** las reglas se escribieron antes de ver los datos justamente para no acomodarlas después. Aplicadas tal cual, dan nube.
- **Por qué alguien razonable elegiría local:** privacidad total, costo cero, funciona sin conexión y latencia estable, a cambio de 0.2 puntos. La app lo permite con un interruptor; el valor por defecto es una preferencia, no una necesidad técnica.
- **Modelo local confirmado: Gemma.** 4.20 contra 3.40 y 5 contra 8 cartas marcadas, además de la velocidad (D-28).

### 3. La evaluación B apagó la computadora (error real)
- **Qué pasó:** `python -m bench.correr_bench --reps 3` hacía 174 generaciones seguidas (2 modelos × 29 tareas × 3 repeticiones), sin pausas. La laptop se apagó sola durante la corrida. Causa probable, no confirmada: protección por temperatura. Todo lo generado se perdió, porque los resultados se escribían al final.
- **Decisiones:**
  1. **Guardado continuo:** cada respuesta se agrega a `resultados/crudo/progreso.jsonl` y se fuerza a disco. Al volver a correr el mismo comando, se salta lo ya hecho.
  2. **Reparación:** si el apagón dejó una línea a medias, se elimina antes de continuar. Sin esto, la siguiente respuesta se pegaba a la línea rota y también se perdía (lo detectó una prueba).
  3. **Pausas:** 3 s entre respuestas y 60 s cada 15.
  4. **Menos carga:** por defecto mide solo la **nota** y la **extracción**, con 2 repeticiones (76 generaciones en total). *Por qué quitar la carta:* ya se midió tres veces en la evaluación A, y es la tarea más larga y la que más calienta el equipo.
  5. **Un modelo por comando**, con descanso entre ambos.
  6. La hoja ciega no se regenera si ya existe con las mismas notas, para no borrar calificaciones.
- **Por qué no simplemente "dejar que enfríe y repetir":** un apagón por calor repetido puede dañar el equipo, y sin guardado continuo se perdería todo otra vez.
- **Por qué no correrlo en la nube o en otra máquina:** el área del proyecto es medir modelos locales en el equipo real; el límite térmico es parte del resultado.
- **Lección para el artículo:** en la nube, medir más es mandar más peticiones; en local, es calor.

## D-30 · Una clave casi publicada, un "modo lento" del equipo y cuatro correcciones de medición

### 1. La clave de Gemini quedó en `.env.example` (error real)
- **Qué pasó:** la clave real se pegó en `.env.example`, la plantilla que sí se sube, en vez de quedar solo en `.env`. Al hacer `git push`, la protección de GitHub detectó la clave y rechazó la subida. No llegó a publicarse.
- **Cómo se corrigió:** se devolvió el texto de ejemplo a la plantilla y se rehízo el commit a partir de lo que ya estaba en GitHub (`git reset --soft origin/main`), para que ningún commit con la clave se subiera. *Por qué no usar el enlace "permitir el secreto" de GitHub:* habría publicado la clave en un repositorio público.
- **Para que no se repita:** `tests/test_secretos.py` falla si `.env.example` no trae el texto de ejemplo, si `.env` no está en `.gitignore`, o si algún archivo del proyecto contiene algo con forma de clave de Google. Regla de trabajo: `pytest` antes de cada `git push`.
- **Por qué no confiar solo en GitHub:** esa protección funcionó, pero es la última barrera y depende del proveedor. La prueba local avisa antes de hacer el commit.
- **Ironía útil para el artículo:** la app protege el salario con tres capas, y lo que casi se filtra fue la configuración de quien la construyó.

### 2. El equipo tiene un "modo lento" bajo carga sostenida (hallazgo)
Corrida larga de `qwen3.5:4b`: 87 respuestas seguidas, sin pausas (`resultados/corrida_larga_qwen/`).

| Tramo | Respuestas | Duración | Tokens/s | Carta |
|---|---|---|---|---|
| Normal | 1–55 | 10.7 min | 20.0 | 20 s |
| Lento | 56–75 | 10.6 min | 6.9 | 58 s |
| Recuperado | 76–87 | 1.6 min | 20.5 | 16–20 s |

- **Interpretación:** mismo modelo, mismo prompt, misma memoria en GPU; cambia la velocidad. Es el patrón de un equipo que limita su rendimiento por temperatura. No se midió la temperatura, así que queda como causa probable.
- **Corrige a D-27:** la hipótesis de que en la corrida 1b los dos modelos no cabían juntos en la GPU pierde fuerza. Los 58 s de Qwen coinciden con este modo lento (58 s de mediana), y la caída empezó en la última carta de Gemma (30 s en vez de 10).
- **Corrige a D-28 y D-29:** se retira la afirmación de que Gemma "aguanta mejor" una máquina ocupada. Los dos modelos se frenan en la misma proporción; a Qwen le tocó correr durante la caída.
- **Consecuencia para medir:** las pausas de D-29 no son solo para proteger el equipo: sin ellas, casi una de cada cuatro mediciones puede salir tres veces más lenta por una causa ajena al modelo. `bench/analizar.py` ahora marca las respuestas "a ritmo lento" y dibuja la velocidad en orden de ejecución (`ritmo.png`).

### 3. Cuatro correcciones de medición que salieron de esa corrida
1. **Las repeticiones eran idénticas.** Con semilla fija (42), las tres repeticiones de cada texto salían iguales palabra por palabra: servían para medir latencia, no calidad. **Decisión:** semilla `42 + repetición`. Cada repetición es una muestra distinta y sigue siendo reproducible. *Por qué no quitar la semilla:* se perdería la reproducibilidad.
2. **El tiempo al primer token estaba inflado a la baja.** En las repeticiones 2 y 3 el prompt ya está en la caché de Ollama: 0.3 s contra 1.3–3.7 s en la primera. **Decisión:** reportar el primer token solo de la primera repetición.
3. **`cita_porcentaje` fallaba por diseño en 3 de 10 perfiles.** Para un cambio de 16.67 % buscaba "17", pero a la nota se le entrega "+16.7 %" y lo natural es que cite eso. **Decisión:** aceptar el valor con un decimal, truncado o redondeado (`rubrica.cita_el_porcentaje`).
4. **"ISO 14001" contaba como cifra inventada.** **Decisión:** en la nota solo cuenta como cifra lo que se presenta como dinero (con moneda o con "k"/"mil").
- **Para no repetir corridas por un cambio de regla:** la evaluación B guarda el texto de cada respuesta y califica al armar los archivos. `python -m bench.correr_bench --armar` recalifica sin usar el modelo.
- **Los textos crudos ya se publican:** se quitó `resultados/crudo/` de `.gitignore`. Son perfiles ficticios, y sin ellos nadie podría verificar la calificación.
- **La hoja ciega se reconoce por su contenido:** antes se comparaba la cantidad de notas, y una hoja vieja con 10 notas de un modelo podía pasar por la actual con 10 notas de otro. Ahora se comparan caso y texto, y al regenerarla se conservan las calificaciones ya puestas.

### 4. Comparación carta por carta de las dos lecturas de fidelidad (cierra el pendiente de D-29)
- De 29 cartas con respuesta: 7 marcadas por ambas lecturas, 9 solo por la ciega, 0 solo por la estricta, 13 por ninguna.
- **Las 7 de la lectura estricta están contenidas en las 16 de la ciega.** Las 9 adicionales (3 por modelo) son afirmaciones más suaves.
- **La nota "lista para enviar" no es independiente de "inventa":** solo se usaron 3 y 5, y casi siempre 3 cuando la carta inventa (una excepción). El 4.40 / 4.20 / 3.40 es, en la práctica, otra forma de escribir 3, 5 y 8 cartas marcadas.
- **Consecuencia:** el empate de reglas de D-29 (nota contra fidelidad) no era tal: son la misma señal. La decisión no cambia, y su base queda más clara: Gemini tuvo 2 cartas menos marcadas que Gemma, de 10.

## D-31 · Evaluación B: veredicto final entre Gemma y Qwen, y la nota deja de depender del modelo para las cifras

### 1. Resultados (76 respuestas, 38 por modelo, sin ninguna a ritmo lento)

| Tarea | Medida | Gemma 4 E4B | Qwen 3.5 4B |
|---|---|---|---|
| Extracción | Calidad (rúbrica) | 1.00 | 0.98 |
| | Latencia mediana | 1.7 s | 3.8 s |
| Nota | Calidad (rúbrica) | 0.79 | 0.89 |
| | Utilidad a ciegas (1–5) | 3.8 | 4.4 |
| | Latencia mediana | 5.0 s | 9.6 s |
| Las dos | Tokens/s | 43.9 | 20.5 |
| | Memoria | 3,096 MB | 2,988 MB |
| | Carga en frío | 11.6 s | 9.0 s |

### 2. Antes de concluir se leyeron las 40 notas (lección de D-23 y D-28)
- **Contexto:** Gemma sacó 0 de 20 en `cita_porcentaje`. Las dos veces anteriores que un criterio dio un resultado así de extremo, la regla estaba mal.
- **Qué se encontró:** esta vez la regla estaba bien. Gemma no cita el % en ninguna nota, y 19 de 20 no usan ninguna cifra del caso.
  - *Salvedad:* en el perfil c10 el cambio es 0 %, y el criterio solo se cumple escribiendo "0 %". Fallan las 4 notas de ese perfil, 2 por modelo. Sin él: Gemma 0 de 18, Qwen 14 de 18. No cambia el resultado.
- **Lo que no medía nadie:** 13 de 20 notas de Qwen (y 5 de Gemma) no aconsejan a la persona: son un mensaje de la persona para la empresa. En 12 de las de Qwen aparece el salario actual. La instrucción decía "hablas en segunda persona".
- **Cifras alteradas por Qwen (3 de 20 notas):** "Q1,100" por Q11,000; un ancla de "Q14,000" que nadie dio; un logro inventado con "40 %". Además leyó el requisito "GRI" como "griego" en las dos repeticiones.
- **Extracción:** de los dos perfiles donde Qwen perdió puntos, uno es un falso negativo de la rúbrica ("Fluent English" → "Inglés fluido") y el otro un error real (tomó "CRM (Salesforce)" como el puesto).
  - ❌ *Por qué no se corrigió ese criterio:* cambia la calidad de Qwen de 0.98 a 0.99 y no altera ninguna conclusión. Queda documentado.

### 3. Dos alertas nuevas en la rúbrica de la nota (no cambian la calidad)
- **Decisión:** agregar `primera_persona` (la nota dice "mi salario" o "mi expectativa") y `cita_alguna_cifra`. Se calculan después de la calidad; la nota de 0.79 y 0.89 es la misma que antes.
- **Por qué:** una afirmación como "13 de 20" debe poder repetirse con un comando (`--armar`), no depender solo de una lectura.
- **Qué tan buena es la alerta:** coincide con la lectura en 38 de 40 notas. Falla con una nota correcta que incluye, entre comillas, una frase para decirle a RR. HH., y no ve una nota que mezcla las dos voces sin decir "mi salario".
- **Por qué no meterla en la calidad:**
  - ❌ Cambiaría el resultado después de verlo, con un criterio elegido sabiendo a quién perjudica.
  - ❌ Tiene falsos positivos conocidos. Como alerta sirve; como nota, no.

### 4. La evaluación ciega de las notas: qué se usa y qué no
- **Se usa:** utilidad (Qwen 4.4, Gemma 3.8; 10 notas por modelo).
- **No se usa:** `claridad_1a5` quedó vacía; `inventa_datos_si_no` quedó en "Sí" en las 20 notas, incluidas varias cuyo comentario dice que los datos son correctos. No distingue entre modelos.
- **Hueco de la guía de calificación:** preguntaba por realismo, momento y argumento; no por el destinatario. Por eso 4 de las 6 notas de Qwen escritas para la empresa recibieron 5.
- **Decisión:** `bench/analizar.py` ahora avisa cuando una columna de la hoja está vacía o tiene un solo valor.
- **Por qué no pedir que se califique de nuevo:** una segunda pasada, ya conociendo los resultados, dejaría de ser ciega.

### 5. Veredicto: Gemma 4 E4B es el modelo local de la app
- **Por qué:** gana la carta (4.20 contra 3.40 a ciegas; inventa menos), empata la extracción y es el doble de rápido en las tres tareas (más rápido en las 68 comparaciones respuesta a respuesta). Sigue mejor las instrucciones.
- **En qué pierde:** en la nota no usa los datos (rúbrica 0.79 contra 0.89; utilidad 3.8 contra 4.4); 108 MB más de memoria; carga más lenta en 3 de 4 mediciones (ver la corrección en D-33: deja de contarse).
- **Por qué no Qwen para la nota, si ganó lo medido:**
  - ❌ Su defecto es el peor posible para esta app: redacta el salario actual en un texto dirigido a la empresa (12 de 20 notas).
  - ❌ Alteró cifras en 3 de 20 notas. Una cifra equivocada en una negociación es peor que una cifra ausente.
  - ❌ Tarda el doble.
- **Por qué no un modelo para cada tarea (Qwen para la nota, Gemma para lo demás):**
  - ❌ Dos modelos de 3 GB cargados a la vez en un equipo que ya mostró límites de temperatura, o 9–12 s de carga en cada cambio.
  - ❌ La ventaja de Qwen (usar las cifras) se consigue sin modelo: ver el punto 6.
- **Honestidad:** las dos señales medidas favorecen a Qwen en la nota y la decisión se apoya en una lectura no ciega. Quien dé más peso a lo medido puede elegir Qwen en la app (es un selector).

### 6. Cambio en la app: las cifras de la nota las ponen las reglas
- **Contexto:** la app mostraba solo la nota del modelo. Con Gemma, la persona no veía el % exacto que las reglas ya habían calculado. Con Qwen podía ver un salario equivocado.
- **Decisión:**
  1. Debajo de la nota del modelo se muestran los **datos exactos** (`reglas.datos_exactos`): salarios, % de cambio, rango, posición y cuándo mencionarla.
  2. `reglas.problemas_en_nota` revisa la nota y **avisa** si trae una cifra que no viene de los datos o si está en primera persona.
- **Por qué:** es la misma idea que el guardián de la nube, aplicada hacia adentro: lo que escribe un modelo se revisa con algo que no comete ese error. Y cubre el punto débil de Gemma sin cambiar de modelo.
- **Por qué avisar y no reemplazar la nota por la de reglas:**
  - ❌ La alerta de primera persona tiene falsos positivos; descartar notas correctas sería peor que avisar.
  - ❌ La persona ya tiene los datos exactos al lado: puede decidir con ambos.
- **Por qué no quitar el modelo de la nota y dejar solo las reglas:**
  - ❌ La nota del modelo aporta el argumento y el tono; la de reglas es una lista de hechos. La evaluación ciega valoró esa redacción (3.8 y 4.4 de 5).
  - ✅ Sigue siendo el respaldo cuando Ollama no está.
- **Pruebas:** `tests/test_nota.py` (9), con frases reales de la evaluación. Total: 76.
- **No cambia la evaluación:** el modelo recibe exactamente lo mismo que antes.

### 7. Tres mejoras al prompt de la nota: propuestas, no aplicadas
1. Decir quién la lee ("es para la persona; no es un mensaje para la empresa").
2. Quitar de los hechos el recordatorio sobre la carta: Qwen lo aplicó a la propia nota ("No incluyas cifras en esta nota").
3. Pasar los logros de la persona. Hoy recibe los requisitos de la oferta y no los logros, así que arma el argumento presentando los requisitos como habilidades. La nota es local: no hay razón de privacidad para ocultarle los logros.
- **Por qué no se aplican ahora:** cambian lo que recibe el modelo, así que los resultados publicados dejarían de describir la app. Aplicarlas exige repetir la evaluación B (unos 15 minutos de carga en un equipo que ya se apagó una vez).
- **Lo que sí se reconoce:** estos defectos son del prompt, no de los modelos. Afectan a los dos por igual, por lo que la comparación es justa; la calidad absoluta de las notas podría ser mayor.

### 8. El calor, cerrado con datos
- Sin pausas: 20 de 87 respuestas a menos del 60 % de la velocidad normal (19 de ellas a un tercio), y un apagado en otra corrida.
- Con pausas de 3 s, descanso de 60 s cada 15 respuestas y un modelo por vez: 0 de 76 respuestas lentas. Gemma entre 40.2 y 45.3 tokens/s; Qwen entre 20.4 y 21.1.
- **Decisión:** las pausas quedan como valor por defecto del script. No se midió la temperatura; la causa térmica sigue siendo la explicación más probable, no un hecho medido.
- **Corrección menor:** la gráfica de calidad mostraba la mediana (0.80 y 0.90) y la tabla el promedio (0.79 y 0.89). Ahora las dos usan el promedio.

## D-32 · Formularios de ejemplo para demostraciones

- **Contexto:** en una demostración en vivo hay que llenar 11 campos. Escribirlos frente al público toma tiempo y es fácil equivocarse; y usar datos reales en pantalla contradice lo que la app defiende.
- **Decisión:** cinco formularios ficticios en `demo/formularios.json` y, en la barra lateral, una sección **🎬 Demostración** que llena el formulario de un clic. El guion está en `docs/demo.md`.
- **Qué cubre cada uno:** el recorrido completo con datos sensibles escondidos en el texto; una expectativa muy ambiciosa por encima del rango; pedir menos de lo que se gana; una oferta que pide lo que la persona no dijo tener; una oferta en inglés.
- **Por qué:**
  - Lo que se enseña en una demo debe poder repetirse: los datos exactos y los reemplazos del sanitizador son los mismos cada vez, y el guion los anuncia.
  - Los ejemplos son los mismos casos difíciles de la evaluación, así que la demo muestra lo que se midió.
- **Por qué no:**
  - ❌ *Un documento con los datos para copiar y pegar, sin tocar la app:* son 11 copias por formulario frente al público. Se dejó como respaldo (las tablas de `docs/demo.md`).
  - ❌ *Dejar el formulario precargado al abrir la app:* quien la use de verdad tendría que borrar datos ajenos, y una captura de pantalla podría confundir un ejemplo con una persona real.
  - ❌ *Reusar `bench/casos.json` directamente:* ese archivo es de la evaluación; cambiarlo para una demo cambiaría lo medido.
  - ❌ *Un formulario que haga saltar al guardián:* no existe una entrada escrita en el formulario que lo logre, porque el sanitizador limpia antes cualquier cifra. El guardián es la segunda barrera y se demuestra con `pytest`, no en pantalla.
- **Si falta el archivo:** la app funciona igual y simplemente no muestra la sección.
- **Pruebas:** `tests/test_demo.py` (4): cada formulario llena todos los campos, ninguno deja salir nombre, empleador ni salarios, el primero dispara los cinco tipos de reemplazo, y entre todos cubren los casos del guion. Total: 80.

## D-33 · La nube falló en uso real: el respaldo funcionó y el panel de transparencia mintió

### 1. Qué pasó
- En una prueba normal de la app (internet ✅, clave ✅), Gemini no terminó dentro del límite de 20 s (`GEMINI_TIMEOUT_MS`) y respondió `504 DEADLINE_EXCEEDED`.
- La app pasó al modelo local, como estaba diseñado (D-05): la carta la escribió `gemma4:e4b` en 9.9 s, con un aviso en pantalla.
- Tiempos: nota 16.3 s (11.2 s de carga del modelo + 5.1 s), unos 20 s de espera a la nube y 9.9 s de carta. Unos 46 s en total, contra unos 15 cuando la nube responde.
- **Coincide con lo medido:** 5.1 s para la nota (5.0 en la evaluación B), 9.9 s para la carta (9.5 en la A), 41.2 tokens/s (41.9).

### 2. Error encontrado: el panel decía "No se envió" y sí se había enviado
- **Contexto:** `envio_nube` se ponía en verdadero solo cuando la nube devolvía la carta. Con un 504, el panel mostraba *"No se envió (modo local), pero esto habría salido:"*.
- **Por qué está mal:** el 504 lo responde el servidor, así que la petición llegó. Lo que salió estaba sanitizado, pero el panel existe para decir con exactitud qué salió del equipo.
- **Decisión:** nuevo campo `envio_intentado`, verdadero desde el momento en que se llama a la nube. El panel ahora dice *"Se envió ⚠️, pero la nube no devolvió la carta (la escribió el modelo local). Esto es lo que salió:"*.
- **Por qué no dejarlo como estaba, si los datos iban limpios:**
  - ❌ La garantía de la app no es solo "lo sensible no sale": es "puedes ver exactamente qué salió". Una pantalla que afirma lo contrario de lo ocurrido rompe la segunda mitad.
- **Por qué "se intentó" y no "se envió con certeza":**
  - Si el fallo es de red antes de conectar, puede que nada haya salido. Ante la duda, la app dice que salió: es el error del lado seguro para quien usa la app.
- **Lección:** había pruebas para lo que se envía y ninguna para lo que la app *dice* haber enviado. Ahora hay dos (`tests/test_offline.py`).

### 3. Error menor: espacios sobrantes
- Un empleador escrito con un espacio al final aparecía en la carta como *"Universidad X , he desarrollado…"*, porque el nombre se vuelve a poner tal cual se escribió.
- **Decisión:** `Perfil` quita los espacios al inicio y al final de cada texto.
- ❌ *Por qué no corregirlo en la carta ya escrita:* habría que adivinar qué espacios sobran; es más simple no dejarlos entrar.

### 4. Lo que la prueba confirmó de D-31
- La nota de Gemma abrió con *"Aquí tienes una propuesta para tu nota privada"*, habló en primera persona a la empresa y no citó ninguna cifra: los tres rasgos de la sección 8.6, fuera del benchmark.

### 5. La misma prueba con la nube apagada
- Mismo formulario, interruptor de la nube apagado: nota 4.6 s, carta 8.2 s (42.9 tokens/s), unos 13 s en total.
- **Texto idéntico al de la prueba anterior** (161 y 318 tokens en las dos). Confirma que la carta de la primera prueba era de Gemma, y que con temperatura 0.2 y semilla fija el modelo local es reproducible.
- **Cómo leer la diferencia (46 s contra 13 s):** 11 s son carga del modelo y unos 20 s son la espera a la nube. No es una comparación de velocidad entre nube y local; esa está en la evaluación A.
- Primer token de la carta: 1.5 s en la primera prueba y 0.3 s en la segunda, por la caché de prompt de Ollama (mismo efecto de D-30).

### 6. La misma prueba con Qwen
- Nota 34.7 s (24.2 s de carga del modelo + 10.5 s), carta 22.4 s a 20.2 tokens/s, 2,988.1 MB.
- **La nota:** *"Estimado/a responsable de RR.HH.… Mi salario actual es de Q5,000 y busco una revisión al 10%…"*. Cifras correctas, dirigida a la empresa, con el salario actual: el patrón de 13 de 20 notas de la evaluación B.
- **La carta** agrega lo que la persona no dijo: "graduada recientemente", "clases reconocidas por su claridad pedagógica", "lidero proyectos de investigación colaborativa". La de Gemma, menos: "mi formación en física", "gestión de equipos especializados".
- **Corrige a D-31 sobre el arranque:** se decía que Gemma cargaba más lento en 3 de 4 mediciones. Con esta, son 3 de 5, y aquí fue Qwen el lento (24.2 s contra 11.2 s), porque antes hubo que sacar a Gemma de la memoria. **Decisión:** el arranque deja de contarse como desventaja de Gemma; se reporta como "sin ventaja clara, entre 9 y 24 s según el estado del equipo".
- **Alcance:** es un ejemplo, no una medición. Se publica porque coincide con las evaluaciones A y B, no como evidencia nueva.

### 7. Qué no se cambió
- **El límite de 20 s.** En la evaluación A Gemini tardó entre 7 y 18 s; un límite más alto alarga la espera cuando la nube está caída. Se puede ajustar con `GEMINI_TIMEOUT_MS`.
- **No se reintenta la llamada a la nube.** ❌ Un reintento duplica la espera y vuelve a enviar los datos; el modelo local está a 10 s.
- **Capturas:** se publican las de la carta, el panel y las métricas. No se publica la del formulario lleno, porque junta un nombre de persona con una institución real y un salario.

Total de pruebas: 83.

