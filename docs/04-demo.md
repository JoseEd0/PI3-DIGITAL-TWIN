# Demostración del sistema — simulador, tablero y modelo en vivo

> Qué se enseña en la exposición mientras la instrumentación no está instalada, y
> por qué eso no es una maqueta sino la primera versión del sistema.
> El detalle técnico y los comandos están en [demo/README.md](../demo/README.md).
> Última actualización: **10/09/2026** (semana 5).

## 1. Qué es

La carpeta `demo/` es la realización de **RF-11 (simulador y modo demostración)**.
Contiene tres piezas que se usan juntas:

| Pieza | Qué hace | Requisitos que demuestra |
|---|---|---|
| Simulador y servidor | Genera las lecturas de los seis nodos con el contrato de datos real y las sirve por una API REST y un flujo de eventos | RF-05, RF-06, RF-08, RF-10, RF-11, RF-13 |
| Tablero web | Muestra el laboratorio en vivo: plano, energía, ambiente, ocupación, puerta, alertas, salud y consumo fantasma | RF-01, RF-02, RF-03, RF-04, RF-07, RF-12 |
| Modelo SysML en vivo | Escribe cada magnitud dentro de la propiedad del bloque que le corresponde en `modelo/campus-twin-l419.gaphor`, y colorea los bloques según su estado | Trazabilidad del modelo con el sistema |

## 2. Por qué se hizo antes que el hardware

El plan (S5–S6) pone el simulador antes de la compra por tres razones:

1. **Desacopla el software del hardware.** El servidor, la API, las reglas y el
   tablero se desarrollan y se prueban desde la semana 5. Si la Raspberry Pi 5 o
   los sensores se demoran, el cronograma no se cae (riesgo 4).
2. **El modo demostración deja de ser una tarea de última semana.** RF-11 estaba
   planificado para S13; hacerlo primero convierte el respaldo de la demo en la
   herramienta diaria de desarrollo.
3. **Obliga a cerrar el contrato de datos.** Para simular hay que decidir tópicos,
   unidades, periodos y numeración de muestras, que es justamente la tarea de S6.

## 3. Qué encontró la demo

Construirla sirvió para corregir dos cosas del propio proyecto:

- **RF-13 daba por caído al nodo de puerta cada quince minutos.** El criterio
  "sin datos por más de 5 min" choca con el latido de 30 min que exige la
  autonomía del nodo (RNF-04). Ahora el umbral son tres periodos del propio nodo,
  con un mínimo de cinco minutos, y así quedó escrito en el documento maestro.
- **Las muestras perdidas no se pueden medir contra el reloj.** Se miden por los
  huecos en la secuencia de cada nodo, que es información que el propio nodo
  entrega y que además sirve para descartar duplicados (RF-05).

También agregó al modelo la propiedad `estadoPuerta` del `Nodo de Puerta`, que
faltaba: el nodo medía batería pero no el estado de la puerta, que es su razón de
ser (RF-04).

Y obligó a declarar **qué magnitud entrega cada sensor**, no solo cada nodo. El
diagrama de instrumentación ahora muestra, debajo de cada nodo, la lectura de cada
sensor con su unidad: la corriente de la pinza SCT-013, el CO₂ del SCD41, el
conteo del ToF, la vibración del SW-420. Eso hizo aparecer dos magnitudes que el
simulador no publicaba y que los requisitos sí exigían: el movimiento del PIR
(RF-03, que es distinto de la presencia del radar) y la vibración del SW-420
(RF-04).

## 4. Qué es simulado y qué no

Lo que se queda cuando lleguen los sensores: el contrato de datos, el descarte de
duplicados, la lógica de las reglas, el cálculo de consumo fantasma, la API, el
tablero y las pruebas.

Lo que se reemplaza: el simulador por los nodos ESP32 publicando en Mosquitto, y
el histórico en memoria por la base de series temporales.

Lo que todavía no existe en la demo: el copiloto de voz (S12), la autenticación
(RNF-08) y la persistencia en disco (RF-06).

El modelo físico del simulador es deliberadamente simple. No predice el
laboratorio: hace que cada magnitud se mueva por la razón correcta, para que las
relaciones que el sistema explota —gente y CO₂, luces e iluminancia, ausencia y
consumo— se vean como se van a ver.

## 5. Guion de la exposición

Con el día simulado a 240× (un día en seis minutos), desde los botones del
tablero:

| Paso | Qué se ve | Requisito |
|---|---|---|
| Entra un grupo | Sube la ocupación, el CO₂ pasa 1000 ppm, salta la alerta y el bloque `Nodo Ambiental` se pinta en Gaphor | RF-03, RF-02, RF-08 |
| Se van y dejan luces | El aula queda vacía consumiendo; a los 15 min empieza a sumar el reporte de consumo fantasma en kWh, soles y kg CO₂ | RF-10 |
| Abren de madrugada | Evento de puerta fuera de horario con alerta crítica | RF-04, RF-08 |
| Se cae un nodo | El nodo deja de reportar, aparece caído en el panel de salud y gris en el modelo | RF-13 |
| Señal débil | Suben las muestras perdidas del nodo del fondo | RF-05, RF-13 |

## 6. Relación con los entregables

La demo no reemplaza ningún entregable: es el punto 6 de la lista del
[documento maestro](00-idea-principal.md#13-entregables) y el respaldo declarado de
la demo en vivo del 13/11. El modelo SysML que se muestra en pantalla es el
entregable de la semana 4; la demo trabaja sobre una copia y no lo modifica.
