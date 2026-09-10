# Demo — el proyecto funcionando antes de tener los sensores

Esta carpeta es el **modo demostración** que pide RF-11: un simulador que genera
los datos de los seis nodos del L-419, un tablero web que los muestra y un enlace
que escribe esos mismos valores dentro del modelo SysML de Gaphor, en vivo.

Sirve para dos cosas:

1. **Enseñar el proyecto terminado** en la exposición, sin depender de que el
   hardware llegue o coopere.
2. **Adelantar el software**: servidor, API, reglas y tablero se desarrollan y se
   prueban contra el simulador desde la semana 5, y cuando lleguen los ESP32 en la
   semana 6 lo único que cambia es de dónde salen las muestras.

Nada de lo que hay aquí inventa requisitos nuevos. Cada panel del tablero y cada
regla del simulador lleva el identificador del requisito que demuestra
([docs/00-idea-principal.md](../docs/00-idea-principal.md)).

## Las tres piezas

| Carpeta | Qué es | Equivale, en el sistema real, a |
|---|---|---|
| [servidor/](servidor/) | Simulador de los nodos + API REST + flujo de eventos | Los ESP32, el broker MQTT, la base de series temporales y la API de la Raspberry Pi |
| [frontend/](frontend/) | Tablero web en React | El mismo tablero, servido por la Pi en la LAN (RF-07) |
| [gaphor-vivo/](gaphor-vivo/) | Enlace que escribe los valores en el modelo SysML | No tiene equivalente: es una herramienta de demostración |

## Cómo levantarla

El único requisito previo es Python 3.11+, Node 20+ y Gaphor 3.x. Los tres
bloques empiezan en la raíz del repositorio, y el orden importa: el tablero se
construye antes de levantar el servidor, porque el servidor lo sirve desde
`frontend/dist`.

```bash
# 1. Preparar, una sola vez
cd demo/frontend && npm install && npm run build
cd ../servidor && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

# 2. Levantar el simulador y el tablero, y dejarlo corriendo
cd demo/servidor && .venv/bin/python -m campus_twin_demo --velocidad 240

# 3. En otra terminal, el modelo SysML en vivo
cd demo/gaphor-vivo && ./lanzar.sh
```

Con eso quedan abiertos el tablero en `http://127.0.0.1:8000` y la ventana de
Gaphor con el diagrama **04 Demo en vivo · Estado en vivo del L-419**.

Si reconstruyes el tablero con el servidor ya levantado, reinícialo: decide si
sirve el tablero al arrancar.

## Cómo se ve en la exposición

El día simulado corre acelerado: con `--velocidad 240` un día entero dura seis
minutos, así que en la exposición se ve la jornada completa sin esperar.

Guion sugerido, con los botones del tablero:

1. **Entra un grupo.** Sube la ocupación, el CO₂ pasa los 1000 ppm y salta la
   alerta de confort. En Gaphor, el bloque `Nodo Ambiental` se pinta de ámbar y
   sus propiedades muestran el CO₂ del momento.
2. **Se van y dejan luces.** El aula queda vacía con las luminarias y los PC
   encendidos. A los 15 minutos simulados el reporte de consumo fantasma empieza a
   sumar kWh, soles y kg de CO₂.
3. **Abren de madrugada.** Evento de puerta fuera de horario, con alerta crítica.
4. **Se cae un nodo.** El nodo ambiental deja de reportar; a los tres periodos
   aparece como caído en el panel de salud y el bloque se pone gris en Gaphor.
5. **Señal débil.** El nodo de ocupación del fondo pierde muestras; el porcentaje
   de muestras perdidas sube y se ve en el modelo.

## Qué es real y qué no

**Es real:** el contrato de datos (tópicos, secuencia, unidades), el descarte de
duplicados, la lógica de las reglas, el cálculo del consumo fantasma, la API, el
tablero y el enlace con el modelo. Todo eso se queda cuando lleguen los sensores.

**Es simulado:** las mediciones. El modelo físico es sencillo a propósito (mezcla
de CO₂, curva de temperatura, cargas eléctricas conmutadas): no predice el
laboratorio, solo hace que cada magnitud se mueva por la razón correcta.

**No está:** el broker MQTT real, la base de datos en disco, el copiloto de voz y
la autenticación. El simulador publica en un bus en proceso con los mismos
tópicos, y el histórico vive en memoria. El cambio a Mosquitto e InfluxDB es
reemplazar [servidor/campus_twin_demo/bus.py](servidor/campus_twin_demo/bus.py) y
[almacen.py](servidor/campus_twin_demo/almacen.py); el resto no se entera.

## Pruebas

```bash
cd demo/servidor && .venv/bin/python -m pytest
```

45 pruebas: el simulador (perfil del día, contrato de topicos, periodos de envío,
autonomía del nodo de puerta), el almacén (duplicados, salud, muestras perdidas),
las reglas, el auditor de consumo fantasma y la API, incluido un servidor real
levantado en un hilo para comprobar el flujo de eventos.
