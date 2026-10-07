# Corrida larga de Qwen (evidencia de la caída de rendimiento)

87 respuestas seguidas de `qwen3.5:4b` (nota, carta y extracción × 3 repeticiones), **sin pausas**,
con la primera versión del script de la evaluación B.

- Respuestas 1–55 (10.7 min): 20 tokens/s.
- Respuestas 56–75 (10.6 min): **6.9 tokens/s**, un tercio de lo normal. La carta pasó de 20 s a 59 s.
- Respuestas 76–87: 20 tokens/s otra vez.

No se usa para comparar modelos (solo hay uno, y las tres repeticiones de cada texto son
idénticas porque compartían semilla). Se conserva porque muestra qué le pasa a un modelo local
bajo carga sostenida. Gráfica: `docs/img/calor_qwen.png`. Ver D-30 en `docs/decisiones.md`.
