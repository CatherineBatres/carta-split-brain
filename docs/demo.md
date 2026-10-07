# Guion para demostraciones en vivo

Cinco formularios ficticios, listos para usar, y el orden en que conviene mostrarlos. Los datos viven en [`demo/formularios.json`](../demo/formularios.json).

## Cómo cargar un formulario

1. Abre la app: `streamlit run app.py` y luego http://127.0.0.1:8501.
2. En la barra lateral, sección **🎬 Demostración**, elige un formulario.
3. Presiona **Cargar formulario**. Se llenan los 11 campos.
4. Presiona **Generar**.

Después de cargar puedes cambiar cualquier campo a mano. **Vaciar formulario** lo deja en blanco.

Si prefieres escribir en vivo, o el botón no aparece, cada formulario trae abajo su tabla para copiar y pegar.

## Antes de empezar (5 minutos antes)

| Revisa | Cómo |
|---|---|
| Ollama está abierto y tiene los modelos | `ollama list` muestra `gemma4:e4b` |
| La app abre | http://127.0.0.1:8501 |
| La barra lateral dice Ollama ✅, Internet ✅ y Gemini API key ✅ | Si la clave dice ❌, revisa el archivo `.env` |
| **El modelo ya está cargado** | Carga el formulario 1 y presiona **Generar** una vez. La primera respuesta tarda entre 10 y 20 segundos más porque Ollama carga el modelo; las siguientes ya no |
| La laptop está conectada al cargador y sobre una mesa | — |
| No se ve nada privado en pantalla | Cierra el `.env`, el correo y otras pestañas |

No presiones el botón **Deploy** de arriba a la derecha: publicaría la app en un servidor ajeno.

## Orden sugerido (unos 6 minutos)

| # | Qué haces | Qué señalas | Qué dices |
|---|---|---|---|
| 1 | Cargas el **formulario 1** y generas, con la nube encendida | Carta a la izquierda (☁️ Gemini), nota a la derecha (🖥️) | "La carta la escribe la nube. La nota, con el salario, se queda aquí" |
| 2 | Bajas a **Datos exactos (calculados por reglas)** | +16.7 %, razonable, dentro del rango | "Esto no lo calculó un modelo: es una división. Un modelo se puede equivocar en una resta" |
| 3 | Abres **Exactamente lo que salió a la nube** | `[[NOMBRE]]`, `[[EMPLEADOR_ACTUAL]]`, `[MONTO]`, `[CORREO]`, `[TELÉFONO]` | "Escribí mi nombre, mi salario y mi teléfono dentro de la experiencia. Nada de eso viajó" |
| 4 | Vuelves a la carta y señalas la firma | *Ana Lucía Pérez* al final | "La nube firmó con un marcador. El nombre lo puso mi computadora" |
| 5 | Apagas **Usar la nube para la carta** y generas de nuevo | La carta ahora dice 🖥️ y el panel dice "No se envió (modo local)" | "Sin la nube sigue funcionando: la carta la escribe el modelo local y no sale nada" |
| 6 | Cargas el **formulario 2** y generas | +77.8 %, muy ambiciosa, por encima del rango | "Las mismas reglas, otro caso: aquí aconsejan no poner la cifra por escrito" |
| 7 | (Si hay tiempo) **formulario 4** | La frase de la carta sobre Salesforce e inglés | "La oferta lo pide y la persona nunca dijo tenerlo. Por eso hay que leer lo que escribe un modelo" |

**Para mostrar el último nivel de respaldo:** cierra Ollama (ícono junto al reloj → *Quit Ollama*), apaga la nube y genera. La carta sale de una plantilla (📄) y la nota de las reglas (📐): sin modelo y sin internet, la app todavía entrega algo útil.

## Qué es fijo y qué cambia

- **Fijo, siempre igual:** los datos exactos (%, clasificación, rango, cuándo mencionarla) y los reemplazos del panel de lo enviado. Los puedes anunciar antes de presionar el botón.
- **Cambia de una vez a otra:** el texto de la carta y de la nota. No prometas una frase concreta.
- **Tiempos habituales** en la laptop de pruebas, con el modelo ya cargado: unos 15 segundos con la nube, unos 16 todo en local con Gemma y unos 36 con Qwen.

---

## Formulario 1 · Caso base

**Para qué sirve:** el recorrido completo. Los datos sensibles están escondidos dentro del texto.

| Campo | Qué escribir |
|---|---|
| Tu nombre | Ana Lucía Pérez |
| Empleador actual | Distribuidora El Quetzal |
| Moneda | Q |
| Salario mensual actual | 9000 |
| Salario mensual deseado | 10500 |
| Puesto actual | Asistente contable |
| Puesto al que aplicas | Contadora general |
| Empresa a la que aplicas | Grupo Andino |
| Resumen de tu experiencia | Soy Ana Lucía Pérez. Llevo 4 años en Distribuidora El Quetzal llevando contabilidad de pymes y cierres mensuales; hoy gano Q9,000 al mes. Pueden escribirme a ana.perez@correo.com o al 5555-1234. |
| Logros concretos | Reduje el cierre mensual de 10 a 6 días. |
| Oferta de trabajo | Contador(a) general. Requisitos: CPA colegiado, Excel avanzado, manejo de SAT. Presencial en zona 10. Salario Q10,000 - Q12,000. |

**Qué debe aparecer**

| Dónde | Resultado |
|---|---|
| Datos exactos | Pasar de Q9,000 a Q10,500 es un cambio de **+16.7 %**: expectativa **razonable** |
| | La oferta publica Q10,000–Q12,000; **dentro del rango** |
| | Compartirla cuando RR. HH. la pida en la primera llamada; anclar en la mitad superior del rango |
| Lo que salió a la nube | *"Soy [[NOMBRE]]. Llevo 4 años en [[EMPLEADOR_ACTUAL]]… hoy gano [MONTO] al mes. Pueden escribirme a [CORREO] o al [TELÉFONO]."* |
| Reemplazos | nombre 1 · empleador 1 · monto 3 · correo 1 · teléfono 1 |
| Requisitos detectados | CPA colegiado · Excel avanzado · manejo de SAT (el modelo puede redactarlos distinto) |

## Formulario 2 · Muy ambiciosa

**Para qué sirve:** mostrar que el juicio sobre la expectativa viene de reglas. Usa otra moneda.

| Campo | Qué escribir |
|---|---|
| Tu nombre | Sofía Ramírez |
| Empleador actual | Apps del Istmo |
| Moneda | US$ |
| Salario mensual actual | 1800 |
| Salario mensual deseado | 3200 |
| Puesto actual | QA manual |
| Puesto al que aplicas | QA automation |
| Empresa a la que aplicas | Nearshore Labs |
| Resumen de tu experiencia | 3 años de QA manual en apps móviles. |
| Logros concretos | Diseñé 400 casos de prueba y bajé los errores en producción. |
| Oferta de trabajo | QA Automation Engineer. Selenium, Cypress, API testing, inglés B2. Remoto. Salario US$2,000 - US$2,800. |

**Qué debe aparecer**

| Dónde | Resultado |
|---|---|
| Datos exactos | Pasar de US$1,800 a US$3,200 es un cambio de **+77.8 %**: expectativa **muy ambiciosa** |
| | La oferta publica US$2,000–US$2,800; **por encima del rango** |
| | No ponerla por escrito todavía; esperar a después de la entrevista técnica y justificarla con logros |
| Reemplazos | monto 2 (el rango de la oferta) |

**Detalle para comentar:** el puesto "QA manual" no dice si la persona es hombre o mujer, y la nube no conoce el nombre. Fíjate si la carta dice "motivada", "motivado" o evita el adjetivo.

## Formulario 3 · Pide menos de lo que gana

**Para qué sirve:** un caso raro que una regla detecta sola. La oferta no publica rango.

| Campo | Qué escribir |
|---|---|
| Tu nombre | Roberto Chávez |
| Empleador actual | Manufacturas del Sur |
| Moneda | Q |
| Salario mensual actual | 15000 |
| Salario mensual deseado | 13000 |
| Puesto actual | Jefe de planta |
| Puesto al que aplicas | Coordinador de sostenibilidad |
| Empresa a la que aplicas | Fundación Verde |
| Resumen de tu experiencia | 12 años en manufactura; quiero pasar al área ambiental. |
| Logros concretos | Reduje el consumo de agua de la planta y lideré un equipo de 80 personas. |
| Oferta de trabajo | Coordinador de sostenibilidad. Gestión de proyectos, reportes GRI, trabajo con comunidades. Híbrido. |

**Qué debe aparecer**

| Dónde | Resultado |
|---|---|
| Datos exactos | Pasar de Q15,000 a Q13,000 es un cambio de **−13.3 %**: expectativa **por debajo de lo que ganas hoy** |
| | Compartirla cuando la pidan en la primera conversación con RR. HH. |
| | **"Estás pidiendo menos de lo que ganas hoy: confirma que es intencional."** |
| Reemplazos | ninguno |

## Formulario 4 · Requisitos que no tiene

**Para qué sirve:** mostrar por qué hay que leer lo que genera un modelo. La oferta pide Salesforce e inglés; la persona no dijo tener ninguno.

| Campo | Qué escribir |
|---|---|
| Tu nombre | José Ángel Barrios |
| Empleador actual | Distribuidora Central |
| Moneda | Q |
| Salario mensual actual | 11000 |
| Salario mensual deseado | 13000 |
| Puesto actual | Ejecutivo de ventas |
| Puesto al que aplicas | Key account manager |
| Empresa a la que aplicas | SaaS Latam |
| Resumen de tu experiencia | 5 años como ejecutivo de ventas atendiendo cuentas corporativas. |
| Logros concretos | Cerré 12 contratos nuevos en 2024. |
| Oferta de trabajo | KAM B2B. CRM (Salesforce), negociación, inglés. Remoto. |

**Qué debe aparecer**

| Dónde | Resultado |
|---|---|
| Datos exactos | Pasar de Q11,000 a Q13,000 es un cambio de **+18.2 %**: expectativa **razonable** |
| Requisitos detectados | CRM (Salesforce) · negociación · inglés |
| En la carta | Lee en voz alta la frase sobre Salesforce y sobre inglés |

- Si dice *"disposición para aprender"* o *"interés en"*: la instrucción funcionó.
- Si dice *"cuento con experiencia en Salesforce"* o *"me comunico con fluidez en inglés"*: el modelo inventó. Es el hallazgo principal del proyecto, ocurriendo en vivo. No es un fallo de la demo.

## Formulario 5 · Oferta en inglés

**Para qué sirve:** el modelo local entiende una oferta en otro idioma, y las reglas leen el rango igual.

| Campo | Qué escribir |
|---|---|
| Tu nombre | Andrea Fuentes |
| Empleador actual | Contact Center Maya |
| Moneda | Q |
| Salario mensual actual | 8000 |
| Salario mensual deseado | 9500 |
| Puesto actual | Agente bilingüe |
| Puesto al que aplicas | Customer success specialist |
| Empresa a la que aplicas | Helpdesk Global |
| Resumen de tu experiencia | 4 años atendiendo clientes en inglés por chat y teléfono. |
| Logros concretos | Mantuve una satisfacción de clientes de 96 % durante dos años. |
| Oferta de trabajo | Customer Success Specialist. Fluent English, Zendesk, SaaS experience. Remote. Salary Q9,000 - Q10,500. |

**Qué debe aparecer**

| Dónde | Resultado |
|---|---|
| Datos exactos | Pasar de Q8,000 a Q9,500 es un cambio de **+18.8 %**: expectativa **razonable** |
| | La oferta publica Q9,000–Q10,500; **dentro del rango** |
| Requisitos detectados | Inglés fluido · Zendesk · experiencia en SaaS (en español o en inglés) |
| La carta | En español, aunque la oferta esté en inglés |

---

## Si algo falla

| Qué ves | Qué hacer |
|---|---|
| La barra lateral dice "Ollama: ❌ no disponible" | Abre Ollama desde el menú de inicio y recarga la página (F5) |
| "Gemini API key: ❌" o "La nube falló" | Sigue con el modo local: apaga el interruptor de la nube. La demo funciona igual |
| La primera respuesta tarda mucho | Es la carga del modelo. Explícalo: "la primera vez, el modelo sube del disco a la memoria" |
| Todo va lento | Cambia a `gemma4:e4b` en la barra lateral: tarda la mitad que Qwen |
| Aparece un aviso amarillo sobre la nota | Es la revisión por reglas: el modelo escribió una cifra que no venía o redactó la nota como mensaje a la empresa. Muéstralo: es una función, no un error |
| No aparece la sección 🎬 Demostración | Falta `demo/formularios.json`. Usa las tablas de este documento |

## Preguntas que suelen hacer

| Pregunta | Respuesta corta |
|---|---|
| ¿Cómo sabes que el salario no sale? | El campo del salario no está en la lista de lo que puede salir, y un guardián revisa el envío. Hay pruebas automáticas (`pytest`) que lo comprueban |
| ¿Por qué no hacer todo en local? | Se puede: es un interruptor. La nube escribió la carta algo mejor (4.40 contra 4.20 a ciegas), por un margen pequeño |
| ¿Por qué no todo en la nube? | La nota necesita el salario. Ahí la privacidad pesa más que la calidad |
| ¿Por qué Gemma y no Qwen? | Casi el mismo tamaño y el doble de rápido; mejor en la carta. Pierde en la nota, donde no usa las cifras, y por eso las cifras las muestran las reglas |
| ¿Qué no detecta el filtro? | Cifras escritas en letras ("nueve mil"). Por eso el salario tiene su propio campo numérico, que nunca se envía |
| ¿Puedo usarla desde otra computadora? | No. La app escucha solo en esta máquina, a propósito |
