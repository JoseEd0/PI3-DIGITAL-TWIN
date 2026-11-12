# El modelo SysML en vivo

Abre el modelo oficial del proyecto en Gaphor y, cada segundo, consulta
`GET http://localhost:8000/api/estado` del servicio del grupo (`demo/servidor/gemelo`).
Con cada respuesta hace dos cosas:

1. **Escribe los valores.** En el bloque de cada uno de los 7 sensores pone los campos que
   su nodo reportó: el bloque `MH-Z1911A` pasa a mostrar `co2_ppm = 425`, el `INMP441`
   `leq_db = 38.4` y `tonal = 0.15` (índice de 0 a 1), y así los 7. Cada propiedad del modelo se
   llama igual que el campo del JSON del Gateway.
2. **Pinta cada bloque según la condición de su RA.** El bloque de un sensor y el de su caja
   toman el color del peor de los RA que dependen de ese nodo.

| Nodo | Bloque del sensor | RA que lo pintan |
|---|---|---|
| 1 | `MH-Z1911A` | RA-03 |
| 2 | `INMP441` | RA-07 |
| 3 | `MQ-2` | RA-05 |
| 4 | `BH1750 (GY-302)` | RA-04, RA-08 |
| 5 | `MLX90640 32x24` | RA-04, RA-06, RA-08, RA-09 |
| 6 | `KY-024 (Hall SS49E)` | RA-06, RA-08, RA-09 |
| 7 | `BME280 (GY-BME280)` | RA-01, RA-02 |

RA-10 (salud del sistema) no pinta a los nodos que sí reportan: un nodo caído se ve gris, y el
bloque del Gateway se ve gris si el Gateway está fuera de línea. La tabla está en `enlace.py` y
una prueba (`demo/servidor/pruebas/test_gaphor_vivo.py`) la compara con `config/nodos.yaml`,
`config/requisitos_ra.yaml` y los bloques que declara `modelo/tools/build_model.py`.

**Los datos son los del servicio.** Con el simulador (`python -m gemelo --simular`) son
simulados, y la nota del diagrama lo dice en su primera línea (`DATOS SIMULADOS`). Con el
Gateway real, dirá `DATOS REALES`.

## Correrlo

Con el servicio del grupo ya levantado (`cd demo/servidor && .venv/bin/python -m gemelo --simular`):

```bash
./lanzar.sh
```

Variables opcionales: `API` (por defecto `http://localhost:8000`), `PERIODO`
(segundos entre consultas), `GAPHOR` (ruta al ejecutable), `MODELO` y `COPIA`.

Al abrirse, Gaphor muestra el diagrama **06 Demo en vivo · 1 bdd [Demo] Estado en vivo del
L-419**: una nota con el estado del aula y la condición de los diez RA, la leyenda de colores y
los bloques de los 7 sensores y del Gateway. Los demás diagramas también se actualizan solos, porque
son los mismos bloques: vale la pena abrir **02 Estructura › 0 Arquitectura oficial EC3 › 2 bdd
Cajas de los 7 nodos**.

## Qué toca y qué no

El entregable `modelo/campus-twin-l419.gaphor` **no se modifica nunca**. El
lanzador hace una copia (`campus-twin-l419-demo.gaphor`, ignorada por git), le
agrega el paquete de demostración y abre esa copia. Si al cerrar Gaphor pregunta
si guardar, da igual lo que respondas.

## Cómo funciona

| Archivo | Responsabilidad |
|---|---|
| `enlace.py` | La tabla de los 7 sensores (bloque, RA), cómo se escribe cada campo, la condición y el color de cada bloque, y el texto de la nota |
| `preparar_modelo.py` | Carga el modelo, arma el diagrama de demostración y guarda la copia |
| `campus_twin_vivo.py` | Abre Gaphor, consulta el API en un hilo aparte y escribe los valores en el modelo |
| `lanzar.sh` | Encadena los dos pasos y avisa si falta algo |

Los tres corren con el intérprete que trae Gaphor, así que **solo usan la
biblioteca estándar**: no hay nada que instalar.

Probado el 12/11/2026 contra el simulador: los 37 campos de los 7 nodos se escriben en cada
consulta; con el escenario `gas` el bloque `MQ-2` y la caja del nodo 3 se pintan de rojo oscuro
(RA-05 crítico), y con `nodo-sin-bateria` los bloques del nodo 5 quedan en gris, y también los del
nodo 4, cuyos RA no se pueden evaluar sin el 5. No se probó con el Gateway real.

## Los colores

El lienzo va en tema oscuro fijo, definido por la propia demo y no heredado de
Gaphor. La razón es un defecto concreto: Gaphor, en modo oscuro, pinta el texto de
blanco por su cuenta (`@media dark-mode { * { color: white } }` en su hoja de
estilo). Si la demo pone fondos claros en los bloques, queda letra blanca sobre
fondo claro y no se lee nada.

Fijando fondo **y** texto aquí, el modelo se ve igual con Gaphor en claro o en
oscuro, y la exportación a PNG sale con los mismos colores.

| Elemento | Color | Contraste del texto |
|---|---|---|
| Lienzo | `#14181c` | — |
| Bloque en estado normal | `#1f2830` | 12.8 |
| Bloque con RA en alerta | `#6b4e0f` | 6.9 |
| Bloque con RA crítico | `#56201a` | 10.5 |
| Nodo caído o RA sin dato | `#2a2f34` con texto apagado | 5.1 |
| Notas | `#1b2329` | 13.6 |

Todos superan el 4.5 que pide la norma de accesibilidad para texto. Los cuatro
estados se distinguen por claridad además de por tono, así que siguen siendo
distintos para quien no separa el rojo del verde. Los bordes van más apagados
(`#9db0bb`) que el texto (`#e8eef2`): una línea blanca de 2 px sobre fondo oscuro
cansa la vista y compite con lo que hay que leer.

Tres detalles que costaron encontrarse:

- Gaphor crea la sesión *antes* de terminar de leer el archivo. Si se indexa el
  modelo apenas aparece la sesión, no hay ningún bloque todavía y no se escribe
  nada. El script espera a que aparezcan los bloques y, unos instantes más, el diagrama de la
  demo: los diagramas se leen después de los bloques.
- Los valores se escriben en el `defaultValue` de la propiedad, que es lo que
  Gaphor dibuja como `+ co2_ppm: CO2 [ppm] = 425`.
- Los colores salen de la hoja de estilo del modelo, con reglas del tipo
  `block[name="MQ-2"]`. Se reescribe entera en cada actualización.

Todo cambio va dentro de una transacción de Gaphor; si no, la ventana no se entera
de que el modelo cambió.

## Si algo falla

| Síntoma | Qué pasa |
|---|---|
| "No encuentro Gaphor" | Instálalo desde gaphor.org o exporta `GAPHOR=/ruta/al/ejecutable` |
| Los bloques no muestran valores | El servicio no responde en `API`; el registro lo dice y reintenta cada 3 s. Levántalo con `python -m gemelo --simular` |
| "la copia no tiene el diagrama de demo" | Corre `preparar_modelo.py` otra vez, o borra la copia y usa `lanzar.sh` |
| `Invalid ID for reference` al abrir | Quedó un diario de recuperación de una sesión cerrada de golpe. `lanzar.sh` ya los borra; a mano están en `~/.cache/gaphor/sessions` |
