# Tablero propio (EC3)

Dashboard del Grupo 1 sobre la arquitectura oficial: lo sirve el servicio `gemelo` en
`http://<ip-de-la-laptop>:8000` para cualquier laptop de la misma red Wi-Fi.

Cubre los tres mínimos de la pauta de la EC3 y del anuncio del 06/11:

1. **Mediciones** de los 7 nodos: valor, unidad, tendencia, anomalías y detalle del nodo.
2. **Condición del salón** frente a cada requisito de alto nivel RA-01..10, como semáforo.
3. **Causas, consecuencias y recomendaciones** de cada violación, con el grafo causal (SymCure)
   coloreado en vivo.

Además tiene el plano 2D con los nodos, el consumo fantasma estimado, la salud de los nodos y del
Gateway, el log de eventos con filtros y exportación a CSV, los botones de escenarios y la franja
**DATOS SIMULADOS**, siempre visible cuando el grupo es `sim`.

```bash
npm install && npm run build   # genera dist/, que sirve el servicio
npm run dev                    # desarrollo en :5173 con proxy a :8000
```

Cytoscape va empaquetado, sin CDN, para que el tablero funcione en una red sin internet (RNF-05).
