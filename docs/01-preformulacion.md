# Pre-formulación — Campus Twin

> Fuente: `Organización de ideas.pdf` (transcripción íntegra a Markdown).

> Nota: También colocar los **stakeholders** de las ideas.

## Ejemplo de formulación de ideas

| | |
|---|---|
| **Necesidad:** Estado deseado por una persona. *"Necesito desplazarme de forma segura."* | **Problema:** Obstáculo que impide satisfacer esa necesidad. *"El transporte público es inseguro de noche."* |
| **Causas:** Raíces del obstáculo que deben investigarse antes de actuar. | **Solución:** Respuesta diseñada para resolver el problema. *"Sistema inteligente de transporte compartido."* |

## ODS

- **ODS 3 — Salud**: Bienestar físico y mental de las comunidades.
- **ODS 4 — Educación**: Acceso a educación inclusiva y de calidad.
- **ODS 6 — Agua Limpia**: Saneamiento y gestión sostenible del agua.
- **ODS 9 — Innovación**: Industria, innovación e infraestructura resiliente.
- **ODS 11 — Ciudades**: Comunidades urbanas sostenibles e inclusivas.
- **ODS 12 — Consumo**: Producción y consumo responsables.
- **ODS 13 — Clima**: Acción urgente contra el cambio climático.

Se desarrollarán elementos de Interacción Humano-Computador para optimizar la eficiencia
del uso de gemelos digitales por operadores y personal de vigilancia, así como para informar
al personal responsable de los sistemas representados por gemelos digitales. Los elementos
de Interacción Humano-Computador incluirán, por ejemplo, pantallas y/o sistemas de audio.
Los productos se evaluarán utilizando una simulación del sistema elegido como prototipo. El
proyecto puede ser abordado por estudiantes de distintas carreras aportando cada uno desde
su área.

## Propuesta

### 4. Campus Twin — Gemelo digital de edificio/campus con copiloto energético

*Se basa en:* que los edificios generan ~40% de las emisiones globales y los certificados
LEED/EDGE en Perú demuestran ahorros de 20-40% en energía (Lima ya tiene 900 edificios
clase A sostenibles).

- **Qué es:** gemelo del edificio (consumo, HVAC, ocupación) con dashboard para el
  administrador y copiloto de voz para el vigilante nocturno, que recibe briefings de turno y
  consulta el estado durante su ronda.
- **Beneficios:** el más fácil de prototipar (el propio campus UTEC es el laboratorio, con
  evidencia propia medible) y demo en vivo garantizada.
- **Contra:** es el mercado más comoditizado, con Schneider y Siemens dominando.
- **ODS:** 7, 11 y 13.

## DigitalTwin — Requerimientos de la propuesta

### Datos para poder medir y conectar

- *Sensores y medidores:* Datos en tiempo real de consumo de luz, aire acondicionado (HVAC)
  y cuánta gente hay en las aulas o pasillos.
- *Un mapa digital:* Una representación sencilla (en 2D o un modelo 3D básico) del campus
  UTEC para ver los edificios por dentro.

### Plataformas para ordenar las ideas del software

- *Dashboard para el administrador:* Una pantalla web para ver el consumo de energía, alerta
  si algo está fallando y reportes de ahorro (ideal para apuntar certificaciones como LEED o
  EDGE).
- *Copiloto de voz para el vigilante:* Que haya un briefing automático al empezar una ronda
  nocturna e incluso que se puedan realizar consultas de forma oral con la plataforma.

### Lo necesario para la demo (MVP)

- *Elegir una zona piloto:* Usar un solo aula o, en caso se pueda, más de uno del campus UTEC
  como laboratorio de pruebas.
- *Demostración en vivo:* Mostrar el funcionamiento del Dashboard y la consulta de voz en
  tiempo real durante la presentación para garantizar el impacto y la eficiencia del proyecto.

## Preguntas para el stakeholder

*(Pendiente de completar.)*

## Lista de sensores/instrumentos

> Nota del documento original: *luego colocar en otro docs para la entrega.* El detalle
> completo y costeado vive en [02-instrumentacion-l419.md](02-instrumentacion-l419.md).

### 1. Lista

**ESP32 NodeMCU**

Posee un microcontrolador de bajo costo con Wi-Fi y Bluetooth integrado, doble núcleo y
múltiples pines de E/S (GPIO), además posee fácil manejo con Arduino.

Su aporte a nuestro proyecto es que este sirve de "cerebro" en el aula piloto: nos ayudará a
recolectar datos de todos los sensores físicos. Gracias a su conectividad inalámbrica,
transmite los datos en tiempo real hacia la nube o servidor local para alimentar el Dashboard
web del administrador sin requerir costosos mazos de cableado estructurado.

**Módulo PZEM-004T + Pinza SCT-013**

Es un medidor digital de parámetros eléctricos *(voltaje, corriente, potencia activa en Watts
y energía acumulada en kWh)* con aislamiento galvánico de alta seguridad frente a la red de
alta tensión. La pinza *(SCT-013)* permite lectura no invasiva por inducción magnética.

**X** — *Propiedades…* *(pendiente)*

### 2. Dónde comprar y costos generales

Ver [02-instrumentacion-l419.md](02-instrumentacion-l419.md) — incluye tienda, enlace, SKU,
cantidad y precio por ítem.

### 3. Justificación de la extracción de datos

Justificar cómo es que se extrae la información detectada por los sensores y cómo se conecta
a la red. *(Pendiente — la cadena de datos propuesta está en
[02-instrumentacion-l419.md](02-instrumentacion-l419.md#1-cómo-funciona).)*
