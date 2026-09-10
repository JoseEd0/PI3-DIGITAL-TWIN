# El modelo SysML en vivo

Abre el modelo del proyecto en Gaphor y va escribiendo, cada segundo, el valor de
cada magnitud dentro de la propiedad del bloque que le corresponde. El bloque
`Nodo Ambiental` que se entregó en la semana 4 pasa a mostrar el CO₂ de este
momento, y se pinta de ámbar cuando pasa el umbral.

## Correrlo

Con el servidor de la demo ya levantado:

```bash
./lanzar.sh
```

Variables opcionales: `API` (por defecto `http://127.0.0.1:8000`), `PERIODO`
(segundos entre consultas), `GAPHOR` (ruta al ejecutable), `MODELO` y `COPIA`.

Al abrirse, Gaphor muestra el diagrama **04 Demo en vivo · 1 bdd [Demo] Estado en
vivo del L-419**: un panel de texto con el resumen del laboratorio y los bloques
de los nodos con sus valores. Los demás diagramas del modelo también se actualizan
solos, porque son los mismos bloques; vale la pena abrir **02 Estructura · 2 bdd
Nodos e instrumentación** para verlo.

## Qué toca y qué no

El entregable `modelo/campus-twin-l419.gaphor` **no se modifica nunca**. El
lanzador hace una copia (`campus-twin-l419-demo.gaphor`, ignorada por git), le
agrega el paquete de demostración y abre esa copia. Si al cerrar Gaphor pregunta
si guardar, da igual lo que respondas.

## Cómo funciona

| Archivo | Responsabilidad |
|---|---|
| `enlace.py` | La tabla que dice qué magnitud va a qué propiedad de qué bloque, los colores por estado y el texto del panel |
| `preparar_modelo.py` | Carga el modelo, arma el diagrama de demostración y guarda la copia |
| `campus_twin_vivo.py` | Abre Gaphor, consulta el API en un hilo aparte y escribe los valores en el modelo |
| `lanzar.sh` | Encadena los dos pasos y avisa si falta algo |

Los tres corren con el intérprete que trae Gaphor, así que **solo usan la
biblioteca estándar**: no hay nada que instalar.

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
| Bloque con alerta de atención | `#6b4e0f` | 6.9 |
| Bloque con alerta crítica | `#56201a` | 10.5 |
| Bloque sin reportar | `#2a2f34` con texto apagado | 5.1 |
| Notas | `#1b2329` | 13.6 |

Todos superan el 4.5 que pide la norma de accesibilidad para texto. Los cuatro
estados se distinguen por claridad además de por tono, así que siguen siendo
distintos para quien no separa el rojo del verde. Los bordes van más apagados
(`#9db0bb`) que el texto (`#e8eef2`): una línea blanca de 2 px sobre fondo oscuro
cansa la vista y compite con lo que hay que leer.

Tres detalles que costaron encontrarse:

- Gaphor crea la sesión *antes* de terminar de leer el archivo. Si se indexa el
  modelo apenas aparece la sesión, no hay ningún bloque todavía y no se escribe
  nada. El script espera a que aparezcan los bloques.
- Los valores se escriben en el `defaultValue` de la propiedad, que es lo que
  Gaphor dibuja como `+ potencia: Potencia [W] = 916`.
- Los colores salen de la hoja de estilo del modelo, con reglas del tipo
  `block[name="Nodo Ambiental"]`. Se reescribe entera en cada actualización.

Todo cambio va dentro de una transacción de Gaphor; si no, la ventana no se entera
de que el modelo cambió.

## Si algo falla

| Síntoma | Qué pasa |
|---|---|
| "No encuentro Gaphor" | Instálalo desde gaphor.org o exporta `GAPHOR=/ruta/al/ejecutable` |
| Los bloques no muestran valores | El servidor no responde; el registro lo dice y reintenta cada 3 s |
| "la copia no tiene el diagrama de demo" | Corre `preparar_modelo.py` otra vez, o borra la copia y usa `lanzar.sh` |
