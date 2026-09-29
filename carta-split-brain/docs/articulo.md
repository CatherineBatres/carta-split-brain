# Tu salario no tiene por qué viajar a la nube: cómo construí una app "split brain" con modelos locales

*Borrador · Para publicar en Medium/Substack · Las marcas ⟦PENDIENTE⟧ se llenan con los resultados reales del benchmark y las capturas.*

---

## El problema: le estás contando todo a un servidor

Imagina que vas a pedirle ayuda a una IA para escribir tu carta de presentación. Para que te aconseje bien, le cuentas lo que ganas hoy, cuánto quieres ganar y en qué empresa trabajas. Todo eso viaja a un servidor que no controlas.

Ahora imagina otra opción: la parte de la app que necesita saber tu salario corre **en tu computadora**, y a la nube solo va lo que de verdad necesita para redactar bien. Eso es una arquitectura **split brain** ("cerebro dividido"): una mitad piensa en tu dispositivo y la otra en la nube.

En este artículo te cuento cómo construí una app así en Python, qué aprendí comparando dos modelos locales (Gemma y Qwen) y en qué me equivoqué por el camino.

⟦CAPTURA: la app con la carta a la izquierda y la nota privada a la derecha⟧

## Qué hace la app

Le cuentas tu situación con franqueza: qué haces, cuánto ganas, qué quieres y cuánto quieres ganar. Si quieres, pegas la oferta. La app te devuelve:

1. **Una carta de interés**, lista para enviar con tu CV.
2. **Una nota privada de negociación**, solo para ti: qué tan realista es tu expectativa y cuándo te conviene mencionarla. Esta nota nunca sale de tu computadora.

## Split brain en una imagen

⟦DIAGRAMA: versión simplificada del diagrama del README: caja "Tu computadora" (reglas, sanitizador, router, Ollama) y caja "Nube" (Gemini), con una sola flecha entre ellas etiquetada "solo lo permitido"⟧

La pregunta central es: **¿qué va dónde, y por qué?** Hay cinco buenas razones para mandar algo a un lado o al otro:

- 🔒 **Privacidad:** hay datos que no deben salir del dispositivo.
- ⚡ **Latencia:** hay respuestas que no pueden esperar un viaje por la red.
- 💰 **Costo:** no toda petición merece una llamada a una API de pago.
- 📴 **Disponibilidad:** sin internet, la app debe seguir sirviendo.
- 🎯 **Calidad:** hay tareas que un modelo pequeño no resuelve bien.

Mi reparto quedó así:

| Tarea | Dónde | Por qué |
|---|---|---|
| Calcular tu % de aumento y si es realista | Tu computadora, con **reglas** | ⚡ 🎯 📴 |
| Detectar tu nombre, salario, correo… | Tu computadora, con **regex** | 🔒 |
| Escribir la nota de negociación | Tu computadora, con un **modelo local** | 🔒 usa tu salario |
| Escribir la carta | **Nube** (Gemini) | 🎯 escribe mejor · 💰 capa gratuita |
| Escribir la carta sin internet | Tu computadora | 📴 |

Lo curioso: la nube escribe mejor, y aun así **la nota no va a la nube**. La nota necesita tu salario, y en este caso la privacidad le gana a la calidad. Esa es la esencia del split brain: no hay un lado "mejor", hay un lado correcto para cada tarea.

## Lección 1: lo local no siempre es un modelo

Mi primer impulso fue pedirle todo al modelo local: "calcula cuánto aumento es pasar de Q12,500 a Q16,000 y dime si es razonable". Pero un modelo de 4 mil millones de parámetros puede equivocarse en una resta, y yo no tengo forma de garantizar que no lo haga.

Así que dividí el trabajo:

```python
# reglas.py — esto NUNCA lo hace un modelo
pct = (deseado - actual) / actual * 100      # 28.0 %, siempre
clasificacion = clasificar_incremento(pct)   # "ambiciosa"
```

Y el modelo solo **redacta** a partir de esos hechos ya calculados. Si en la nota aparece una cifra que no vino de las reglas, mi rúbrica la marca como **cifra inventada**.

Regla práctica: **si la respuesta tiene una única respuesta correcta, no uses un modelo.** Porcentajes, rangos, formatos, validaciones: código. Redactar, resumir, entender lenguaje libre: modelo.

## Lección 2: quién decide qué sale a la nube

Una tentación peligrosa es pedirle al modelo local que "limpie" los datos sensibles antes de enviarlos. El problema: un modelo es probabilístico. Puede hacerlo bien 99 veces y fallar la número 100, y con tu salario no hay margen.

Por eso la decisión la toma **código explícito**, en tres capas:

1. **Lista de permitidos:** solo viajan los campos que alguien decidió que viajan. Si mañana agrego un campo "teléfono" y olvido clasificarlo, **no sale**, y además una prueba se pone en rojo hasta que lo decida.
2. **Sanitizador:** reemplaza tu nombre por `[[NOMBRE]]`, tu empresa por `[[EMPLEADOR_ACTUAL]]` y cualquier monto por `[MONTO]`.
3. **Guardián:** revisa el paquete final. Si encuentra tu salario (en cualquier formato), bloquea el envío y la carta se hace en local.

⟦CAPTURA: el panel "Exactamente lo que salió a la nube" con el JSON sanitizado⟧

Y la nube escribe `[[NOMBRE]]` al firmar. Tu computadora lo cambia por tu nombre real al final. La carta sale firmada sin que la nube sepa quién eres.

## El error que me enseñó más

⟦Elegir UNO o DOS para el artículo; los tres ocurrieron al construir la app⟧

**Opción A — Los años que parecían teléfonos.** Mi regex para teléfonos guatemaltecos buscaba el patrón `dddd-dddd`. Al escribir las pruebas con un perfil ficticio que decía "trabajé de 2019-2023", el sanitizador lo convertía en `[TELÉFONO]`. La carta perdía información útil por proteger algo que no era sensible. Lo corregí con una excepción para rangos de años, y ahora hay una prueba que lo vigila. Moraleja: **una regla de privacidad también tiene falsos positivos, y cuestan calidad.**

**Opción B — El salario disfrazado de logro.** Un perfil de prueba decía "ahorré Q150,000 al año". Suena inocente, pero es exactamente 12 × Q12,500: el salario anual. En Guatemala además se habla de salario ×14 (aguinaldo y bono 14). Desde entonces el guardián compara contra el monto mensual, ×12 y ×14.

**Opción C — La carta que decía "cobro [MONTO]".** Todas mis pruebas de privacidad pasaban. Entonces corrí la app de punta a punta, sin internet y sin Ollama, para ver el peor caso. La carta decía: *"llevo 5 años en mi empresa y cobro [MONTO]. Tel [TELÉFONO]"*. Mi sistema protegía perfectamente el dato… y dejaba el hueco a la vista. Las pruebas revisaban que nada sensible saliera, pero ninguna revisaba que la carta se pudiera enviar. Ahora las frases con datos censurados se eliminan antes de redactar, y hay una prueba para eso. Moraleja: **probar la privacidad no es lo mismo que probar la experiencia.**

⟦Agregar aquí cualquier error que aparezca al correr el benchmark real, por ejemplo: un modelo que ignoró el marcador [[NOMBRE]], o que devolvió JSON inválido⟧

## Gemma vs Qwen: ¿cuál es mejor para esta app?

Comparé **Gemma 4 (E4B)** y **Qwen 3.5 (4B)**, dos modelos de tamaño similar, en las tres tareas locales de la app: la nota de negociación, la carta sin conexión y la extracción de requisitos de la oferta.

Para que la comparación fuera justa: mismos 10 perfiles ficticios, mismos prompts, misma temperatura y semilla, un solo modelo en memoria a la vez, el arranque en frío medido aparte y tres repeticiones de cada caso. También desactivé el modo de "razonamiento" en ambos: para una nota de 150 palabras solo agrega espera.

Medí tres cosas:

- **Calidad:** una rúbrica automática (¿cita el % correcto? ¿inventa cifras? ¿dice cuándo mencionarla?) y una evaluación **a ciegas**, en la que califiqué los textos sin saber qué modelo los escribió.
- **Latencia:** tiempo total, tiempo al primer token y tokens por segundo.
- **Memoria:** el pico de RAM de Ollama mientras genera.

⟦GRÁFICA: docs/img/calidad.png⟧
⟦GRÁFICA: docs/img/latencia.png⟧
⟦GRÁFICA: docs/img/memoria.png⟧

⟦PENDIENTE: tabla resumen de resultados/resumen.md⟧

### Veredicto

⟦PENDIENTE — plantilla para llenar con datos:⟧

Para esta app gana **⟦modelo⟧**, porque ⟦razón principal con dato: p. ej. "inventó cifras en X de 30 notas contra Y del otro"⟧. En una app de negociación salarial, inventar un número es el peor error posible, así que ese criterio pesa más que la velocidad.

**Dónde pierde el ganador:** ⟦p. ej. "es N s más lento en la carta" o "usa N MB más de RAM" o "su JSON fue inválido en X casos"⟧.

## Si vas a construir tu propia app split brain

1. **Haz primero la tabla de qué va dónde**, con una razón por fila. Si no puedes justificar una fila, está mal ubicada.
2. **Usa código para todo lo que tenga una sola respuesta correcta.**
3. **La privacidad se decide con código probable, no con un modelo.**
4. **Diseña la degradación desde el día uno:** nube → modelo local → regla. Mi app, sin internet y sin Ollama, todavía te da el % exacto y una carta base.
5. **Mide antes de elegir modelo**, y con las mismas condiciones para todos.

El código, las pruebas y el registro completo de decisiones están en ⟦link al repo⟧.

---

*¿Qué parte de tu app mandarías a la nube y cuál dejarías en tu dispositivo?*
