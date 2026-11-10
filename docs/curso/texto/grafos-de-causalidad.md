# Razonamiento por Grafos de Causalidad.pdf

> Texto extraído automáticamente de `docs/curso/originales/Razonamiento por Grafos de Causalidad.pdf` (no versionado) el 10/11/2026.
> SymCure (Kapadia, 2003): contexto de gestión de fallas. Para figuras y tablas, abrir el original.

Razonamiento
por Grafos de
Causalidad
Symcure: Ejemplo de plataforma de implementación
Fernando Figueroa Núñez del Prado, Ph.D.
Sistemas de Informacion
UTEC

SymCure: enfoque basado en modelos para la gestión de fallas

• Basado en Ravi Kapadia (2003).

• Traducción y adaptación didáctica del artículo.

• Tema: diagnóstico, predicción, pruebas y recuperación mediante
grafos causales dirigidos.
SymCure — Kapadia (2003)

¿Qué es SymCure?

• Metodología gráfica, orientada a objetos y basada en modelos.

• Integra diagnóstico automático e interactivo, pruebas,
recuperación y predicción.

• Combina modelos genéricos con información específica y eventos
entrantes.
SymCure — Kapadia (2003)

El problema de la gestión de fallas

• Pocas causas raíz pueden generar numerosos mensajes y alarmas.

• La sobrecarga del operador dificulta identificar la causa real.

• Las fallas pueden producir paradas, daños, riesgos y pérdidas de
productividad.
SymCure — Kapadia (2003)

Ocho capacidades requeridas
• Monitoreo
de síntomas.

• Análisis
postmortem.

• Diagnóstico
de causas raíz.

• Correlación
de eventos.

• Notificación.

•
Recuperación
automatizada.

• Predicción
de impactos.

• Pruebas.

SymCure — Kapadia (2003)

Monitoreo y diagnóstico

• Los síntomas son manifestaciones de causas
subyacentes.
• El monitoreo detecta síntomas.
• El diagnóstico identifica causas raíz
compatibles con lo observado.
• Se destaca el gran esfuerzo dedicado a
identificar causas raíz.
SymCure — Kapadia (2003)

Correlación de eventos

• Reconoce
grupos de
eventos
relacionados
causalmente.

SymCure — Kapadia (2003)

Predicción de impactos
• Permite
anticipar
efectos
antes de
que se
manifiesten.

SymCure — Kapadia (2003)

Pruebas y recuperación

• Las pruebas verifican causas sospechadas.
• Las acciones de recuperación permiten reparar
objetos.
• Pueden ser automáticas, manuales o mixtas.
SymCure — Kapadia (2003)

Arquitectura de SymCure
• Entradas:
conocimiento,
GFPM, dominio
y eventos.
•
Procesamiento:
construcción del
modelo
específico de
fallas.
• Salidas: causas
raíz,
explicaciones,
pruebas,
reparaciones y
alarmas.

SymCure — Kapadia (2003)

Representación del dominio

• Representación gráfica
orientada a objetos.
• Incluye clases, instancias y
relaciones.
• Las relaciones incluyen
conectividad y contención.
• Ejemplo: horno F-1 conectado
aguas abajo de bombas P-1 y P-2.
SymCure — Kapadia (2003)

Eventos entrantes

• Incluye síntomas y resultados de pruebas.

• Los síntomas son detectados por mecanismos externos.

• Puede usar sensores, lecturas, y datos procesados.
SymCure — Kapadia (2003)

Conocimiento diagnóstico

• Dos tipos: propagación de fallas y conocimiento
procedimental.
• GFPM (Generic Fault Propagation Management):
relaciones causales para diagnóstico, correlación y
predicción.
• Procedimientos: pruebas y acciones de reparación.

SymCure — Kapadia (2003)

Modelos de falla vs. comportamiento normal

• Los modelos de falla describen causalidad
entre fallas y síntomas.
• Ejemplo: falla de tarjeta IP → pérdida de
comunicación.
• Ejemplo: falla de bomba → detención del
flujo.
• Son más abstractos que una simulación
detallada del comportamiento normal.
SymCure — Kapadia (2003)

Generic Fault Propagation Model (GFPM)
• Captura relaciones causales entre eventos de clases genéricas.
• Es independiente de una configuración concreta.
• Puede reutilizarse ante cambios de topología.
• Puede derivarse de primeros principios, expertos o FMEA.

SymCure — Kapadia (2003)

Ventaja de los GFPM

• Desacopla el conocimiento
diagnóstico de una instalación
específica.
• Favorece herencia y reutilización.

• La independencia de la topología
facilita aplicaciones reutilizables.
Figura original del artículo — Fig. 3.

SymCure — Kapadia (2003)

Procedimientos de gestión de fallas

• SymCure incorpora
pruebas y reparaciones.

• Cada procedimiento
tiene acciones asociadas.

• Puede incluir
condiciones, recursos,
costos y programación.

• Se vincula a eventos del
GFPM.

SymCure — Kapadia (2003)

Grafo causal dirigido
• Los nodos representan
eventos.
• Las aristas dirigidas
representan causalidad.
• La dirección indica el
sentido causal.
• Un evento genérico se
identifica por nombre y
clase objetivo.

Figura original del artículo — Fig. 4.

SymCure — Kapadia (2003)

Lógica de propagación

• Los enfoques tradicionales usan OR y/o AND.
• SymCure admite lógica causal más amplia.
• Puede representar umbrales, fracciones y
condiciones de estado.
SymCure — Kapadia (2003)

Por qué AND/OR no siempre basta

• Un evento puede requerir una fracción de
causas activas.
• El ruido puede ocultar síntomas.
• La propagación puede depender del estado
del sistema.
• SymCure aborda modelos incompletos e
incertidumbre contextual.
SymCure — Kapadia (2003)

Gestión de fallas en tiempo de ejecución
• Formula
hipótesis de
causas raíz.

• Notifica
resultados.

• Ejecuta
pruebas y
reparaciones.

•
Correlaciona
eventos.

• Predice
impactos.

SymCure — Kapadia (2003)

Specific Fault Propagation Model (SFPM)

• Combina GFPM,
dominio y eventos
entrantes.

• Construye un Fault
Propagation Model
especifico.

• Representa eventos de
objetos concretos.

• Registra el estado
diagnóstico y permite
generar explicaciones.

SymCure — Kapadia (2003)

Valores de los eventos en un SFPM

• suspect:
se sospecha
que ocurrió.
• unknown:
se
desconoce.

• true:
ocurrió.

• false: no
ocurrió.

SymCure — Kapadia (2003)

Algoritmo de propagación

• Usa búsqueda heurística
best-first.

• Propaga valores hacia
causas y efectos.

• La complejidad indicada
es lineal en eventos y
objetos del SFPM.

• Solo se construye el
subconjunto relevante
para el diagnóstico.

SymCure — Kapadia (2003)

Ejemplo: sistema de calentamiento
• Síntoma: “High fuel flow” en F-1.
• P-1 y P-2 son posibles fuentes.
• Se sospecha “Pump overload” en ambas.
• Se ejecutan pruebas para verificar las hipótesis.

SymCure — Kapadia (2003)

Del síntoma a la causa raíz

• El diagnóstico rastrea aguas arriba.
• La prueba identifica sobrecarga en P-1
como causa raíz.
• Una causa raíz no es causada por otro
evento del modelo.
• Eventos irrelevantes son omitidos.
SymCure — Kapadia (2003)

Del cambio del sistema al modelo dinámico

• Los GFPM no dependen de la topología concreta.

• El SFPM puede actualizarse ante cambios del dominio.

• Se agregan o eliminan eventos y aristas según sea necesario.
SymCure — Kapadia (2003)

Fortalezas de SymCure

• Diagnóstico automático e interactivo.
• Múltiples fallas simultáneas y superpuestas.
• Razonamiento entre componentes.
• Reutilización de modelos causales.
• Escalabilidad mediante modelos localizados.
SymCure — Kapadia (2003)

Limitaciones y desafíos

• Depende de la calidad de los modelos y de la instrumentación.
• No diagnostica fallas ausentes de los modelos.
• El orden temporal de eventos puede influir en intervalos muy cortos.
• No modela explícitamente retardos ni probabilidades.
• Construir modelos causales exige mucho conocimiento experto.
SymCure — Kapadia (2003)

Aplicaciones y conclusiones

• Implementado sobre G2 de Gensym.
• Aplicaciones citadas: plataformas offshore, calefacción
y software empresarial.
• Idea central: diagnosticar hacia atrás y predecir hacia
adelante mediante causalidad.
• Integra conocimiento, razonamiento, pruebas y
recuperación.
SymCure — Kapadia (2003)

Referencias y fuente principal
• Kapadia, R. (2003). SymCure: A model-based approach for fault management with causal directed graphs.
• Referencias citadas por el artículo: Stanley & Vaidhyanathan (1998); Integrity SymCure Developer’s Guide
(2002); y otras.

SymCure — Kapadia (2003)
