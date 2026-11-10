# Plan de cierre — EC3 (13/11) y fin del proyecto

> Escrito el 10/11/2026, a partir de la [auditoría](AUDITORIA.md) y del [brief](curso/brief-ec3.md).
> Las tareas, responsables y fechas viven en Asana y se reflejan en [03-plan.md](03-plan.md). Este
> documento explica **la estrategia**: qué se construye, sobre qué base y en qué orden.

## 1. Situación

- **Lo que hay:**
  - el código del docente para 6 de los 7 nodos, el Gateway y el servidor (`vendor/`);
  - el software propio del grupo, que funciona pero sobre la arquitectura vieja (`demo/`);
  - el modelo SysML con 12 diagramas;
  - la documentación.
- **Lo que no hay:**
  - ningún nodo armado ni medición real;
  - nada de lo nuevo que pide la EC3: RA, grafos, motor causal, log, dashboard con causas, y
    Gaphor con comportamiento.
- **Al grupo no le tocó caja** (es el Grupo 1 de la Sección 8). Su aporte es la **integración**:
  convertir los datos del Gateway en el estado del salón frente a los requisitos, con diagnóstico
  causal, una interfaz y el gemelo en Gaphor. Es justo lo que evalúan tres de los cuatro bloques
  de la pauta EC3.

## 2. Decisiones

1. **Se adopta la arquitectura del docente sin modificarla.** Los servicios del grupo se suscriben a
   Mosquitto o leen InfluxDB y se agregan en un `docker-compose.override.yml`. El formato es el de
   [CONTRATO_DATOS.md](CONTRATO_DATOS.md).
2. **`demo/` evoluciona; no se tira.**
   - El simulador pasa a publicar el JSON del Gateway en `utec/gemelo/sim/nodo<id>/<tipo>`.
   - El servidor FastAPI deja el bus en memoria y pasa a leer de MQTT e InfluxDB.
   - El tablero React suma los tres mínimos de la EC3.
   - Gaphor en vivo pasa a leer de InfluxDB.

   Las 51 pruebas actuales protegen la refactorización.
3. **El consumo fantasma se estima por proxy.** Se cuentan las luces encendidas (salto de lux con
   `luces_cambio`, o `lux` por encima de la luz natural esperada) con ocupación cero
   (`ocupacion_est`) y se multiplica por la potencia nominal del inventario. El reporte lo
   presenta como **estimación**. Si el docente integra el PZEM, se reemplaza el proxy.
4. **El .ino propio del grupo es el nodo MQ-2.** Es el único nodo de la arquitectura sin programa, y
   su paquete y su tópico ya existen. Sigue la estructura de `nodo_co2.ino`: calentamiento, R0 en
   aire limpio, `rs_r0`, `do_alarma` y bits de anomalía. Debe compilar con `arduino-cli`.
5. **Los RA se alinean con los umbrales del docente** cuando existen: CO₂ en 1000 y 1500 ppm, confort
   de 20 a 26 °C, humedad del 70 % y 300 lx sobre la mesa. Así, la condición que muestra el
   dashboard coincide con los bits de anomalía de los nodos.
6. **El motor causal sigue a SymCure tal como lo enseña el docente:**
   - los eventos valen verdadero, falso, sospechoso o desconocido;
   - la entrada usa lógica OR, AND, N/M o IF;
   - la salida usa lógica AND u OR;
   - hay propagación aguas arriba y aguas abajo.

   Las observaciones son los bits de anomalía y las condiciones RA. El motor escribe sus
   diagnósticos en el log y en InfluxDB.
7. **Honestidad en el reporte.** Cada cosa se rotula como **real**, **simulado** o **pendiente**. El
   código de los nodos y del servidor se presenta como **del docente**, reutilizado e integrado.

## 3. Orden de trabajo hasta el viernes

| Día | Qué queda listo | Quién | Depende de |
|---|---|---|---|
| Mar 10 | Material centralizado, auditoría, contrato de datos y Asana reorganizado ✅. Ramas integradas | J | — |
| Mié 11 | Stack del docente corriendo en la laptop. Simulador en formato Gateway con datos en InfluxDB y Grafana | J, C | — |
| Mié 11 | `config/` con RA-01..10 y grafos causales en YAML | E | — |
| Mié 11 | Motor causal con pruebas | J | Grafos (puede empezar con dos) |
| Jue 12 | API y dashboard propio con mediciones, semáforo por RA, causas, efectos, recomendaciones y log | J | Motor y simulador |
| Jue 12 | Gaphor: hardware oficial, IBD, paquetes 04 y 05, fotos con QR y modelo en vivo desde InfluxDB | L, J | — |
| Jue 12 | `MQ-2.ino` que compile y análisis de energía de las cajas | C | — |
| Jue 12 | Documento maestro y requisitos migrados al hardware oficial | L | — |
| Vie 13 | Reporte EC3 en un solo archivo (L), ensayo de la demo (C), presentación (E) y copiloto si sobra tiempo (E) | todos | todo lo anterior |

Lo que se recorta primero si no alcanza el tiempo: el copiloto, la grabación y reproducción del
simulador, y el NTP local.

## 4. Mapa de la EC3 (pauta → evidencia)

| Bloque de la pauta | Evidencia que va al reporte |
|---|---|
| Sensores y procesadores | Los 7 sensores (principio, rango, interfaz y limitaciones), ESP-NOW y el Gateway (`paquetes.h`), el `MQ-2.ino` propio, la arquitectura final y el acceso desde una laptop por Wi-Fi a Grafana y al dashboard, y la energía de las cajas |
| Razonamiento lógico | Tabla de RA-01..10, metodología SymCure, un grafo por RA y un ejemplo de propagación sobre un escenario simulado |
| Interfaz | Capturas del dashboard con los 3 mínimos y la interactividad |
| Gaphor y Asana | Tabla de cambios del modelo frente a la Semana 7, diagramas nuevos y capturas reales del tablero de Asana, explicando la reorganización del 10/11 |

## 5. Después de la EC3

Fecha supuesta: 20/11. Hay que ajustarla al calendario real del curso.

1. Cita en el L-414 para cargar el código del docente y el `MQ-2.ino`, y ver los datos reales en la
   laptop.
2. Ensayos con hardware: CP-02 (conteo), CP-07 (ambiente), CP-08 (puerta) y CP-03 (resiliencia).
3. Instalar los nodos en el L-419, coordinando con S1 G1 (procesador central y CO₂) y con los grupos
   de cada caja.
4. Cambiar la fuente de datos: el grupo `sim` pasa al grupo real, sin tocar el código.
5. NTP local y retención de 60 días en InfluxDB.
6. Si el curso continúa, hacer la maratón de 72 h (CP-05) y la auditoría de consumo fantasma con
   datos reales (CP-06).

## 6. Riesgos inmediatos

| Riesgo | Mitigación |
|---|---|
| No hay tiempo para todo | Seguir el orden de la tabla y recortar primero lo que dice la sección 3 |
| Docker no corre en la laptop de la demo | Probarlo el miércoles. El dashboard propio puede leer directo de MQTT como respaldo |
| Sin internet, el Gateway real no tiene hora | En la demo se usan datos simulados con `ts` propio. El NTP local queda para después de la EC3 |
| El reporte promete cosas que no existen | Toda afirmación lleva una figura, una tabla o código, y su rótulo real, simulado o pendiente |
