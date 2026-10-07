# Guía para calificar a ciegas las notas de negociación

Se califica `resultados/evaluacion_ciega.csv`: 20 notas (10 perfiles × 2 modelos), revueltas y
sin el nombre del modelo. No abras `resultados/crudo/clave_ciega.json` hasta terminar.

Para cada nota, mira el `caso` (c01 a c10), busca su fila en la tabla de hechos y llena tres columnas.

## Hechos correctos por perfil

Esto es lo que las reglas calcularon y lo que se le entregó al modelo. La nota debe apoyarse
en estos datos y en ninguno más.

| Caso | Salario actual → deseado | Cambio | Expectativa | Rango de la oferta | Posición | Cuándo mencionarla |
|---|---|---|---|---|---|---|
| c01 | Q9,000 → Q10,500 | +16.7 % | razonable | Q10,000–Q12,000 | dentro | Cuando RR. HH. la pida en la primera llamada; anclar en la mitad superior del rango |
| c02 | Q6,000 → Q12,000 | +100.0 % | muy ambiciosa | sin rango | — | Dejar que la empresa dé el primer número; después de la primera entrevista, con logros |
| c03 | US$1,800 → US$3,200 | +77.8 % | muy ambiciosa | US$2,000–US$2,800 | por encima | No ponerla por escrito; después de la entrevista técnica, justificada con logros |
| c04 | Q7,000 → Q7,500 | +7.1 % | conservadora | Q9,000–Q11,000 | por debajo | No mencionarla primero; al preguntar, anclar cerca del máximo del rango |
| c05 | Q5,500 → Q6,000 | +9.1 % | conservadora | sin rango | — | Cuando la pidan en la primera conversación con RR. HH. |
| c06 | Q15,000 → Q13,000 | −13.3 % | por debajo de lo que gana hoy | sin rango | — | Cuando la pidan; confirmar que pedir menos es intencional |
| c07 | Q10,000 → Q13,500 | +35.0 % | ambiciosa | Q12,000–Q15,000 | dentro | Cuando RR. HH. la pida en la primera llamada; anclar en la mitad superior del rango |
| c08 | Q11,000 → Q13,000 | +18.2 % | razonable | sin rango | — | Cuando la pidan en la primera conversación con RR. HH. |
| c09 | Q8,000 → Q9,500 | +18.8 % | razonable | Q9,000–Q10,500 | dentro | Cuando RR. HH. la pida en la primera llamada; anclar en la mitad superior del rango |
| c10 | Q14,000 → Q14,000 | 0.0 % | conservadora | sin rango | — | Cuando la pidan en la primera conversación con RR. HH. |

## `claridad_1a5` — ¿se entiende a la primera?

| Nota | Criterio |
|---|---|
| **5** | Se entiende en una sola lectura. Frases completas, orden lógico, sin repeticiones ni errores de idioma. |
| **4** | Se entiende bien; tiene un detalle menor (una frase larga, una repetición, un error de concordancia). |
| **3** | Se entiende, pero hay que releer alguna parte: una frase confusa, ideas desordenadas o relleno. |
| **2** | Cuesta seguirla: varias frases confusas, o mezcla idiomas, o se contradice en un punto. |
| **1** | No se entiende qué recomienda, o está cortada, o es incoherente. |

## `utilidad_1a5` — ¿le sirve a la persona para negociar?

Una nota útil responde tres preguntas: **qué tan realista** es la expectativa, **cuándo** mencionarla y **con qué argumento** defenderla.

| Nota | Criterio |
|---|---|
| **5** | Responde las tres preguntas, con los datos de este perfil (su %, su rango) y un argumento concreto. La persona sabe qué hacer. |
| **4** | Responde las tres, pero alguna queda general (por ejemplo, el argumento es "destaca tus logros" sin más). |
| **3** | Responde dos de las tres, o las tres de forma genérica: podría servir para cualquier persona. |
| **2** | Responde una sola, o da un consejo que contradice los hechos (por ejemplo, dice "razonable" cuando es "muy ambiciosa"). |
| **1** | No orienta: repite los datos sin recomendar nada, o recomienda algo que perjudica a la persona. |

## `inventa_datos_si_no` — ¿dice algo que no venía en los hechos?

Escribe **si** cuando la nota:
- cita una **cifra distinta** a las de la tabla: otro porcentaje, otro salario, otro rango, o un monto "sugerido" que nadie le dio;
- da **datos de mercado** que no se le entregaron ("el promedio del sector es…", "lo habitual es un 20 %");
- afirma **algo sobre la persona** que no está en el perfil.

Escribe **no** cuando solo usa las cifras de la tabla. No cuenta como inventar:
- redondear de forma evidente (16.7 % → "casi 17 %");
- mencionar un requisito de la oferta que sí existe (por ejemplo "ISO 14001");
- dar un consejo general de negociación sin cifras.

## Reglas para calificar bien

1. **Usa toda la escala.** Si todas tus notas son 3 o 5, la calificación no distingue nada.
2. **Las tres columnas son independientes.** Una nota puede ser muy clara (5), poco útil (2) e inventar una cifra (si). Califica cada cosa por separado.
3. **Compara contra los hechos, no contra tu opinión.** No importa si tú habrías aconsejado otra cosa: importa si la nota respeta lo que se le dio.
4. **Si dudas entre dos notas, pon la más baja** y escribe por qué en `comentario`.
5. **Califica todas de corrido**, con los mismos criterios de principio a fin.
