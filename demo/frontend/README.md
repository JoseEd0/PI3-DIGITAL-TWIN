# Tablero web

Interfaz del administrador de infraestructura (RF-07). React con Vite, sin
librerías de gráficos: los gráficos son SVG propio, para que el tablero cargue
completo dentro de la red del laboratorio sin pedir nada a internet (RNF-05).

## Correrlo

```bash
npm install
npm run build     # el servidor de la demo lo sirve en http://127.0.0.1:8000
```

Para trabajar en la interfaz, con recarga en caliente:

```bash
npm run dev       # http://127.0.0.1:5173, con proxy de /api al puerto 8000
```

El servidor de la demo tiene que estar corriendo en las dos formas.

## Qué muestra cada panel

| Panel | Requisito |
|---|---|
| Plano del laboratorio con los nodos, las luminarias, la puerta y la gente | RF-07 |
| Energía: potencia, energía acumulada, tensión, corriente y factor de potencia | RF-01, RF-12 |
| Ocupación y puerta, con el último evento | RF-03, RF-04 |
| Ambiente: CO₂ contra su umbral, temperatura, humedad e iluminancia | RF-02 |
| Consumo fantasma, con reparto por carga y por franja horaria | RF-10 |
| Alertas activas y últimas disparadas | RF-08 |
| Salud de los nodos: señal, estado y muestras perdidas | RF-13 |
| Mensajes de los nodos, tal como llegarían por MQTT | RF-05 |

## Cómo está armado

- `useGemelo.js` mantiene el estado al día. Se conecta al flujo SSE y, si el
  servidor no responde, cae a consultas cada tres segundos y avisa en la barra.
  Las series de los gráficos se siembran con el histórico del servidor y luego
  crecen con cada evento.
- `componentes/Chispa.jsx` dibuja las líneas de tendencia. Una serie por gráfico,
  sin ejes ni leyenda: el valor actual se lee en la cifra grande de al lado.
- `estilos.css` define los colores como variables y los vuelve a definir para modo
  oscuro. Los números usan cifras tabulares para que no cambien de ancho al
  actualizarse dos veces por segundo.
- Los colores del reparto de cargas salen de una paleta validada para daltonismo;
  los colores de estado (bien, atención, crítico) nunca se usan como color de
  serie y siempre van acompañados de texto.
