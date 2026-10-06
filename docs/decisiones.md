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
