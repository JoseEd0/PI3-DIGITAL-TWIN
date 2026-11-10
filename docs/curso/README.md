# Material del curso

Todo lo que viene del docente (Canvas, anuncios, Drive) y los reportes ya entregados por el grupo,
en un solo lugar.

- `originales/`: los archivos tal como llegaron (pptx, docx, xlsx, pdf, zip y fotos a tamaño
  completo). **No se versiona** porque son binarios pesados. Cada integrante los baja de Canvas o
  de Drive.
- `texto/`: el texto extraído de cada original, en Markdown. **Sí se versiona** y es lo que se cita
  y se busca.
- `imagenes/`: fotos de las etiquetas de la orden de compra **OC-UTEC-004033-26** (Naylamp), con el
  QR de cada sensor. El docente pidió cargarlas en Gaphor y en Asana (anuncio del 11/10). Están
  reducidas a 1200 px.
- `brief-ec3.md`: el brief de la EC3 (v3, 10/11/2026), que es la guía de trabajo hasta el 13/11.
  Sus errores de hecho están corregidos en [../AUDITORIA.md](../AUDITORIA.md).

El código del docente no está aquí, sino en [../../vendor/gemelo_iot_profesor/](../../vendor/gemelo_iot_profesor/),
y su formato está documentado en [../CONTRATO_DATOS.md](../CONTRATO_DATOS.md).

## Qué sirve para qué

| Archivo | Texto | Para qué se usa |
|---|---|---|
| EC3 - Pautas para el reporte.pptx | [ec3-pautas](texto/ec3-pautas.md) | **Índice del reporte EC3.** Son los 4 bloques que se evalúan: sensores y procesadores, razonamiento con grafos, interfaz, y Gaphor con Asana. |
| Razonamiento con Grafos dirigidos - SymCure ES-1.pptx | [symcure-grafos-dirigidos](texto/symcure-grafos-dirigidos.md) | **Especificación del motor causal:** lógicas OR, AND, N/M e IF, y propagación aguas arriba y aguas abajo. |
| Razonamiento por Grafos de Causalidad.pdf | [grafos-de-causalidad](texto/grafos-de-causalidad.md) | Contexto de SymCure (Kapadia, 2003) para la bibliografía. |
| PI3 - Proyecto.docx | [pi3-proyecto](texto/pi3-proyecto.md) | Pide eventos nominales y no nominales, footprint con log, simulación, objetos del aula y gestión en Asana. |
| IP3 Asignación de Sensores y Procesador.pptx | [asignacion-sensores](texto/asignacion-sensores.md) | Asignación de cajas (**al Grupo 1 de la Sección 8 no le tocó ninguna**) y conteo con Hall + MLX90640. |
| Caja de instrumentos y procesador.docx | [caja-instrumentos](texto/caja-instrumentos.md) | Requisitos de las cajas: apertura, energía, recarga con luz, encendido y apagado, impresión 3D. |
| Ejemplos de temas EC2.docx | [ejemplos-ec2](texto/ejemplos-ec2.md) | Diagramas que se esperan en Gaphor: requisitos de cajas, BDD, actividades, estados y casos de uso. |
| Maquinas_de_Estado.pptx | [maquinas-de-estado](texto/maquinas-de-estado.md) | Notación para el diagrama de estados del salón y de los nodos. |
| Instrucciones Evaluación Continua C2.docx | [instrucciones-ec2](texto/instrucciones-ec2.md) | Estructura de la EC2 (NASA SE y usos del modelo), que conviene mantener. |
| Instrumentación ... Compra.xlsx | [lista-de-compra](texto/lista-de-compra.md) | Hardware oficial, con las cantidades sacadas de las fotos. |
| Semana 1 - PI3 - Figueroa.pptx | [semana-1-introduccion](texto/semana-1-introduccion.md) | Marco teórico del curso: sistemas autónomos pensantes, NASA SE (NPR 7123.1 y el handbook), cadena necesidad → problema → causas → solución, stakeholders y ODS. Sirve para la introducción y el abstracto del reporte. |
| Instrumentación de un Espacio de Enseñanza (aula laboratorio).pdf | [instrumentacion-espacio-ensenanza](texto/instrumentacion-espacio-ensenanza.md) | Entrega del grupo del 27/08: la arquitectura y el BOM originales. Es histórico, pero sirve para explicar la migración en la EC3. |
| Instrumentacion_L419.xlsx | — | BOM v1 del grupo. Su contenido está en `docs/data/instrumentacion-l419.csv`. |
| Reporte Semana 7 (13/16) | [reporte-semana-7](texto/reporte-semana-7.md) | **Base técnica** de la EC3. |
| Reporte EC2 (12/16) | [reporte-ec2](texto/reporte-ec2.md) | Solo sirven los interesados, la introducción y la bibliografía. |
| nodo_co2_ModelMH-Z1911A.ino | — | Igual a `vendor/.../nodo_co2/nodo_co2.ino`, salvo `SSID_ROUTER`. |
| Gemelo_IoT-…zip | — | Descomprimido en `vendor/gemelo_iot_profesor/`. |
| brief-ec3-v2.md | — | Versión anterior del brief, reemplazada por `brief-ec3.md`. |

No se guardó la versión de "IP3 Asignación" sin "(1)": es la misma diapositiva de cajas, ya incluida
en la otra.

## Anuncios del docente que no están en archivos

Están resumidos en la sección 4 del [brief](brief-ec3.md):

| Fecha | Anuncio |
|---|---|
| 14/10 | El hardware está en el L-414, con cita de Open Lab. |
| 11/10 | Hay que pasar las imágenes con QR a Gaphor y a Asana. |
| 21/10 | El MQ-2 reemplaza al detector de humo Tuya. |
| 29/10 | Las cajas ya están listas. |
| 02/11 | La comunicación es por ESP-NOW, se entregan archivos .ino por sensor y **también los grupos sin caja programan uno**. |
| 06/11 | Cada grupo diseña su propio dashboard, accesible desde cualquier laptop por Wi-Fi. |
| 07/11 | Arquitectura final: 7 nodos, Gateway y laptop con Docker. |
