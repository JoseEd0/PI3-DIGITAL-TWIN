# Campus Twin L-419

Gemelo digital del aula laboratorio **L-419** de UTEC (PI3, Sección 8, Grupo 1). Usa la
arquitectura oficial del curso: 7 nodos ESP32 envían por ESP-NOW a un Gateway, que publica por
MQTT en una laptop con Mosquitto, Telegraf, InfluxDB y Grafana. Encima, el grupo agrega el motor
causal, el tablero propio, el log de eventos, el gemelo en Gaphor y el copiloto de voz.

> **Estado al 10/11/2026:** el plan está en [docs/05-plan-cierre.md](docs/05-plan-cierre.md) y lo
> que existe y lo que no, en [docs/AUDITORIA.md](docs/AUDITORIA.md). La demo de `demo/` es de
> septiembre y usa la arquitectura anterior, con una Raspberry Pi y sensores propios. Se está
> migrando al formato del Gateway ([docs/CONTRATO_DATOS.md](docs/CONTRATO_DATOS.md)).

Proyecto del curso PI3. Este repositorio guarda todo: idea, requisitos,
instrumentación costeada, modelo SysML, plan y código.

- **Qué problema resuelve:** hoy el laboratorio es una caja negra. No se sabe
  cuánta energía consume, en qué condiciones se dicta clase ni qué pasa de noche.
- **El diferenciador:** cruzar energía, iluminancia y ocupación para responder
  cuánta energía se gasta con el laboratorio vacío. Es el reporte de **consumo
  fantasma** (RF-10).
- **Entrega final:** viernes 13/11/2026.

## Por dónde empezar

| Si quieres… | Ve a |
|---|---|
| Saber qué falta para la EC3 (13/11) | [docs/05-plan-cierre.md](docs/05-plan-cierre.md) |
| Ver el material y los anuncios del docente | [docs/curso/README.md](docs/curso/README.md) |
| Ver el código oficial de los nodos y el Gateway | [vendor/README.md](vendor/README.md) |
| Entender el proyecto completo | [docs/00-idea-principal.md](docs/00-idea-principal.md) |
| Ver qué se compra y cuánto cuesta | [docs/02-instrumentacion-l419.md](docs/02-instrumentacion-l419.md) |
| Saber quién hace qué y para cuándo | [docs/03-plan.md](docs/03-plan.md) |
| Ver el sistema funcionando ahora mismo | [demo/README.md](demo/README.md) |
| Abrir el modelo SysML | [modelo/README.md](modelo/README.md) |

## Qué hay en cada carpeta

```
docs/     documentación del proyecto: idea, requisitos, plan, auditoría, contrato de datos
          └── curso/   material del docente (texto extraído, fotos con QR, brief EC3)
vendor/   código oficial del docente: nodos, Gateway y servidor (no se modifica)
modelo/   modelo SysML en Gaphor, diagramas exportados y el script que lo genera
demo/     el sistema funcionando con datos simulados (RF-11)
          ├── servidor/     simulador de los nodos + API REST + flujo de eventos
          ├── frontend/     tablero web en React
          └── gaphor-vivo/  enlace que muestra los datos dentro del modelo SysML
```

Cuando llegue la instrumentación (semana 6) se agregan `firmware/`, `servidor/` y
`dashboard/` como carpetas de primer nivel, cada una con su README.

## Cómo correr todo

Hace falta **Python 3.11+**, **Node 20+** y **Gaphor 3.x**. Nada más: la demo no
usa internet ni servicios en la nube.

**Todos los bloques de abajo empiezan en la raíz del repositorio.** El orden
importa: el tablero se construye antes de levantar el servidor, porque el servidor
lo sirve desde `demo/frontend/dist`.

### 1. Preparar, una sola vez

```bash
cd demo/frontend && npm install && npm run build
cd ../servidor && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

### 2. Levantar el simulador y el tablero

```bash
cd demo/servidor && .venv/bin/python -m campus_twin_demo --velocidad 240
```

El tablero queda en **http://127.0.0.1:8000**. Déjalo corriendo: las dos piezas
que siguen se conectan a él.

`--velocidad` es cuántos segundos simulados pasan por segundo real: `240` hace
que un día del laboratorio dure seis minutos, `60` que dure veinticuatro, y `1`
lo deja en tiempo real.

### 3. Ver el modelo SysML en vivo

En **otra terminal**, con el servidor ya corriendo:

```bash
cd demo/gaphor-vivo && ./lanzar.sh
```

Abre Gaphor con una copia del modelo y escribe los valores de los sensores dentro
de los bloques cada segundo. El diagrama que se abre solo es **04 Demo en vivo ·
Estado en vivo del L-419**; vale la pena abrir también **02 Estructura · 2 bdd
Nodos e instrumentación** para ver el modelo del curso con datos encima.

El entregable `modelo/campus-twin-l419.gaphor` no se toca: la demo trabaja sobre
una copia. Si Gaphor no está en la ruta habitual:

```bash
cd demo/gaphor-vivo && GAPHOR=/ruta/a/gaphor ./lanzar.sh
```

### 4. Trabajar en la interfaz

Solo si vas a tocar el tablero. Con recarga en caliente, en otra terminal:

```bash
cd demo/frontend && npm run dev      # http://127.0.0.1:5173
```

Si en cambio reconstruyes con `npm run build` mientras el servidor está levantado,
reinícialo: decide si sirve el tablero al arrancar.

### 5. El modelo SysML a secas

```bash
# abrir el modelo
open -a Gaphor modelo/campus-twin-l419.gaphor

# regenerar el modelo desde cero cuando cambian los requisitos
/Applications/Gaphor.app/Contents/MacOS/gaphor exec modelo/tools/build_model.py

# exportar los 12 diagramas a SVG (o pdf, o png)
/Applications/Gaphor.app/Contents/MacOS/gaphor export -f svg -u \
    -o modelo/export modelo/campus-twin-l419.gaphor
```

`build_model.py` **sobrescribe** el archivo del modelo e imprime al final si algún
requisito quedó sin bloque que lo satisfaga o sin caso de prueba.

### 6. Las pruebas

```bash
cd demo/servidor && .venv/bin/python -m pytest
```

## Trazabilidad

Los identificadores de requisito (NS-1…7, RF-01…13, RNF-01…08, CP-01…15) son los
mismos en tres sitios, y los tres se actualizan juntos:

1. [docs/00-idea-principal.md](docs/00-idea-principal.md)
2. el modelo SysML de [modelo/](modelo/)
3. el proyecto [PI3 — Campus Twin L-419](https://app.asana.com/1/1218151758126339/project/1218156351516043) en Asana

El tablero de la demo muestra el requisito que demuestra cada panel, para poder
seguir esa cadena en pantalla.

## Equipo

| Integrante | Responsabilidad |
|---|---|
| José Eduardo Huamani | Servidor, base de datos, API, reglas, tablero web e integración |
| Carlos Dávila | Firmware ESP32, nodo de energía, red local y alimentación |
| Esteban Sotomayor | Nodos de ocupación y puerta, copiloto de voz |
| Luhana Landeo | Modelo SysML y documentación, stakeholders, compras, nodo ambiental y pruebas |
