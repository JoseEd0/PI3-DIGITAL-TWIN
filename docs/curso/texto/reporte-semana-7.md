# Reporte Semana 7 - Grupo 1 (13 de 16).pdf

> Texto extraído automáticamente de `docs/curso/originales/Reporte Semana 7 - Grupo 1 (13 de 16).pdf` (no versionado) el 10/11/2026.
> Reporte del grupo, base técnica de la EC3. Para figuras y tablas, abrir el original.

UNIVERSIDAD DE INGENIERÍA Y TECNOLOGÍA

 Reporte de “Campus Twin”

 Curso:

 Proyectos interdisciplinarios III

 Docente:

 Jorge Fernando Figueroa Nuñez Del Prado

 Landeo Quispe, Luhana Landeo (Bioingeniería)

 Huamáni, José Eduardo (Ciencias de la

 Computación)

 Sotomayor, Esteban Matias (Ciencias de la

 Computación)

 Carlos Victor Duamel Davila Cabezas (Ciencias

 de la Computación)

 Lima - Perú

 2026 - 2

 1
1.​ Abstracto
 Este proyecto presenta Campus Twin, un gemelo digital diseñado para optimizar el
 consumo de energía y la gestión operativa dentro de la Universidad de Ingeniería y
 Tecnología (UTEC). El punto de partida es una realidad clara: las edificaciones
 representan cerca del 40% de las emisiones globales. En Lima, la infraestructura
 sostenible avanza con firmeza, sumando cerca de 900 edificios de oficinas de clase
 A certificados bajo estándares verdes como LEED o EDGE, los cuales demuestran
 ahorros energéticos de entre el 20% y el 40%. Ante este escenario, Campus Twin
 nace como una alternativa de innovación local enfocada en la eficiencia
 arquitectónica.

 La propuesta consiste en conectar datos en tiempo real provenientes de sensores de
 iluminación, sistemas de climatización (HVAC) y control de ocupación con un
 mapa digital interactivo del campus. El software opera mediante dos interfaces
 estratégicas: un panel web para el administrador, diseñado para monitorear el gasto
 de energía y detectar fallas operativas, y un copiloto de voz automatizado para el
 personal de seguridad, encargado de entregar reportes automáticos y resolver
 consultas orales durante las rondas nocturnas.

 Con el fin de demostrar la viabilidad de la idea, se desarrolló un Producto Mínimo
 Viable (MVP) aplicado directamente en aulas piloto del campus UTEC. Aunque el
 mercado global de gestión energética está altamente comoditizado y dominado por
 corporaciones como Schneider y Siemens, este proyecto demuestra que es posible
 estructurar un prototipo funcional, medible y de alto impacto local. De este modo,
 la iniciativa se alinea con los Objetivos de Desarrollo Sostenible (ODS) de las
 Naciones Unidas para promover la energía limpia, el desarrollo de ciudades
 sostenibles y la acción por el clima.

2.​ Introducción
 En la actualidad, las ciudades enfrentan el reto crítico de mitigar su impacto
 ambiental mediante estrategias eficientes de descarbonización. A nivel global, el
 crecimiento de la demanda de energía y la necesidad de reducir de forma acelerada
 las emisiones de dióxido de carbono (CO₂) han impulsado la búsqueda de
 alternativas tecnológicas en los sectores de mayor consumo, siendo la
 infraestructura urbana uno de los focos de atención prioritarios
 (Carrillo-Hernández, 2012). Dentro de las edificaciones, el gasto en iluminación y
 climatización representa una de las mayores fuentes de ineficiencia operativa. De
 hecho, se estima que el uso de luminarias equivale al 19% del consumo eléctrico
 mundial (Pena de Loza & Ibarra-Villegas, 2024). Ante este escenario, la
 digitalización y el monitoreo inteligente emergen como herramientas
 indispensables para transformar la gestión de los recursos energéticos en entornos

 2
 corporativos y educativos.

 La adopción de tecnologías basadas en el Internet de las Cosas (IoT) y la
 automatización mediante sensores de presencia ha demostrado ser altamente
 efectiva para corregir consumos innecesarios y optimizar el rendimiento energético
 en tiempo real (Pena de Loza & Ibarra-Villegas, 2024). No obstante, a pesar de que
 el mercado actual ofrece soluciones comerciales robustas, muchas organizaciones
 sufren de una falta de centralización de la información. Esto evita que los
 administradores tomen decisiones rápidas basadas en datos visuales y excluye al
 personal operativo cotidiano, como los equipos de supervisión nocturna, de los
 flujos de optimización de la infraestructura.

 Para responder a esta problemática, este proyecto plantea el desarrollo de Campus
 Twin, un gemelo digital diseñado como un ecosistema interactivo a escala piloto
 dentro de la Universidad de Ingeniería y Tecnología (UTEC). La propuesta integra
 la recolección de datos provenientes de sensores de iluminación, sistemas de
 climatización (HVAC) y control de aforo dentro de un mapa digital interactivo de la
 infraestructura. A diferencia de las soluciones cerradas provistas por corporaciones
 dominantes en el mercado como Schneider Electric o Siemens, Campus Twin
 introduce un enfoque de accesibilidad operativa mediante dos interfaces
 diferenciadas: un panel web analítico para la toma de decisiones administrativas y
 un copiloto basado en procesamiento de voz automatizado para optimizar las
 auditorías del personal de seguridad durante sus rondas. Mediante un Producto
 Mínimo Viable (MVP), este estudio busca demostrar la viabilidad y el impacto de
 la innovación abierta local en el cumplimiento de los Objetivos de Desarrollo
 Sostenible (ODS).

3.​ Descripción del proyecto
 a.​ Requisitos de alto nivel de los interesados
 i.​ Quienes son los interesados
 Los interesados del proyecto comprenden una red que conecta el
 entorno de experimentación de la Universidad de Ingeniería y
 Tecnología (UTEC) con los actores clave del sector inmobiliario
 comercial. En el núcleo interno del proyecto se encuentra el equipo
 de desarrollo, compuesto por los alumnos investigadores encargados
 de la ingeniería de software, la instalación de sensores IoT y el
 diseño del gemelo digital. Este grupo interactúa de forma directa con
 los usuarios finales operativos del campus, representados por el
 personal de seguridad nocturna. En el contexto empresarial real,
 estos vigilantes equivalen a los técnicos de operaciones y
 supervisores de primera línea, quienes requieren herramientas
 intuitivas que optimicen sus flujos de trabajo sin añadir complejidad
 tecnológica a sus rondas diarias.

 3
 Un escalón más arriba en la toma de decisiones se ubica el usuario
 final administrativo, que en este ecosistema corresponde a la
 Dirección de Operaciones e Infraestructura de UTEC. Esta entidad
 asume la responsabilidad de costear los servicios públicos y velar
 por el mantenimiento integral del campus. En el mercado
 corporativo de edificios clase A, este rol está perfectamente alineado
 con las funciones de un Facility Manager o administrador
 inmobiliario, cuyo objetivo principal es reducir los costos operativos
 globales. Asimismo, el proyecto responde ante interesados clave
 como el jurado académico y el comité de investigación de la
 universidad, quienes actúan bajo el mismo rol que la alta gerencia o
 un comité de inversión empresarial, evaluando si el Producto
 Mínimo Viable (MVP) y la demostración en vivo justifican el
 esfuerzo técnico frente a las alternativas comerciales del mercado.

 Finalmente, el ecosistema de interesados se extiende hacia factores
 externos que definen los estándares de éxito de la propuesta. Por un
 lado, se encuentran los organismos internacionales encargados de las
 certificaciones LEED y EDGE, cuyos auditores e inspectores exigen
 reportes de datos históricos confiables para validar el rendimiento
 energético de cualquier infraestructura sostenible. Por otro lado, en
 el panorama competitivo tecnológico global, corporaciones
 consolidadas como Schneider Electric y Siemens actúan como
 interesados indirectos. Estas empresas no solo marcan la pauta
 tecnológica actual de la industria frente a la cual se debe contrastar
 Campus Twin, sino que también representan el mercado
 comoditizado que este proyecto busca democratizar a través de una
 solución de innovación abierta local.

ii.​ Qué quieren los interesados
 Las expectativas y requerimientos de los interesados se dividen
 según su nivel de interacción con la plataforma, equilibrando los
 objetivos académicos de la universidad con las demandas de
 rentabilidad del mercado comercial [JLL, 2025]. En el nivel
 operativo, el personal de seguridad nocturna de la UTEC y los
 operarios de mantenimiento corporativo exigen que el copiloto de
 voz automatizado funcione de manera intuitiva y fluida. Su
 prioridad es optimizar el tiempo durante las rondas y recibir alertas
 claras sin verse obligados a interactuar constantemente con pantallas
 portátiles. Lo que buscan es una herramienta de soporte que
 automatice el traspaso de información entre turnos y les permita
 reportar incidencias críticas de forma oral en tiempo real,

 4
 garantizando la seguridad del campus sin generar sobrecarga laboral.

 Por su parte, el usuario administrativo de la Dirección de
 Operaciones de la UTEC, al igual que cualquier Facility Manager de
 un edificio corporativo de clase A, tiene como meta principal la
 eficiencia en costos y el cumplimiento de metas de sostenibilidad.
 Este actor estratégico requiere que el dashboard web provea datos
 precisos, centralizados y en tiempo real sobre el consumo de
 iluminación, climatización (HVAC) y aforo de las aulas. Su interés
 central radica en identificar patrones de desperdicio energético,
 anticipar fallas operativas mediante alertas automáticas y,
 fundamentalmente, exportar reportes analíticos limpios que sirvan
 como evidencia técnica para postular o mantener certificaciones
 sostenibles de alto prestigio como LEED o EDGE.

 Finalmente, el equipo de desarrollo, los evaluadores académicos y
 los organismos reguladores externos comparten la expectativa de
 validar la efectividad de la innovación tecnológica local. Mientras
 que los alumnos investigadores buscan demostrar la viabilidad
 técnica de los sensores IoT y el gemelo digital en un entorno
 controlado como las aulas piloto de la UTEC, el jurado evaluador y
 los comités de inversión exigen que la demostración en vivo sea
 impecable y de alto impacto visual. Lo que estos actores demandan
 es evidencia empírica de que un software de innovación abierta
 puede competir en usabilidad y costo frente a los sistemas cerrados
 de grandes corporaciones como Schneider Electric o Siemens,
 demostrando un impacto directo en los Objetivos de Desarrollo
 Sostenible (ODS).

b.​ Ingeniería de Sistemas de la NASA
 i.​ Definición del sistema
 Para organizar el proyecto usamos el enfoque del NASA Systems
 Engineering Handbook (NASA, 2016). La idea es simple: primero
 entender qué necesitan los interesados, luego convertir eso en
 requisitos que se puedan medir, dividir el sistema en partes más
 pequeñas y avanzar por fases, revisando el trabajo al final de cada
 una. Como es un proyecto de un ciclo, lo aplicamos de forma
 simplificada.

 Campus Twin es un gemelo digital del laboratorio L-419 de UTEC,
 que funciona como aula piloto. Seis nodos con ESP32 miden el
 consumo de energía, la temperatura, la humedad, el CO₂, la
 iluminación, si hay gente en el laboratorio y si se abre la puerta. Los

 5
 datos viajan por Wi-Fi a una Raspberry Pi 5, que los guarda y los
 muestra en el dashboard web del administrador y en el copiloto de
 voz, que corre en el celular del vigilante nocturno.

 Lo que más nos interesa es el consumo fantasma: cuánta energía se
 gasta cuando el laboratorio está vacío. Todo funciona en una red
 local, sin internet ni nube. Dejamos fuera del alcance el control de
 equipos (el sistema avisa, pero no apaga nada), las cámaras y el
 escalamiento a otros ambientes del campus.

ii.​ Descomposición del sistema
 Dividimos el sistema en cuatro niveles, desde el sistema completo
 hasta los componentes que compramos:

 Tabla 1. Descomposición del sistema.
 Nivel Elementos
 0. Sistema Campus Twin L-419
 1. Subsistemas Sensado, Servidor, Dashboard Web, Copiloto de Voz, Red
 Local y Alimentación
 2. Módulos Nodos de Energía, Ambiental, Ocupación (×2) y Puerta;
 servicios del servidor (broker MQTT, base de datos, API,
 reglas y alertas, voz, salud, simulador y hora local); app de
 voz en el celular
 3. Componentes PZEM-004T y pinza SCT-013, enchufes con Tasmota,
 SHT31, BH1750, SCD41, radar LD2410C, PIR, sensor
 ToF VL53L1X, sensor magnético, sensor de vibración
 SW-420, batería LiPo, ESP32 y Raspberry Pi 5

iii.​ Requisitos para cada nivel de la descomposición
 En el nivel más alto están las necesidades de los interesados (NS),
 que salen de lo descrito en la sección 3.a. De ellas se derivan los
 requisitos funcionales (RF) y no funcionales (RNF), que se reparten
 entre los subsistemas y, finalmente, se traducen en lo que debe
 cumplir cada componente. Cada requisito tiene un valor medible y
 una prueba (CP) que lo verifica.

 6
 Tabla 2. Ejemplos de requisitos por nivel.
 Nivel Tipo de Ejemplos
 requisito
 0. Sistema Necesidades de El administrador necesita evidencia del
 los interesados consumo para reducirlo (NS-2). El
 (NS-1 a NS-7) vigilante necesita conocer el estado del
 laboratorio sin cargar una laptop
 (NS-1).
 1. Subsistemas Requisitos Funcionar sin internet (RNF-05).
 generales del Operar 72 h seguidas sin intervención
 sistema (RNF) (RNF-06). Costar como máximo S/
 2808 (RNF-03). No usar cámaras ni
 guardar audio (RNF-02).
 2. Módulos Requisitos Nodo de Energía: medir cada 10 s con
 funcionales error ≤ ±2 % (RF-01). Motor de reglas:
 asignados calcular el consumo fantasma (RF-10).
 (RF-01 a RF-13) Copiloto: responder en ≤ 5 s (RF-09).
 Dashboard: actualizarse cada ≤ 5 s
 (RF-07).
 3. Componentes Especificaciones SCD41: CO₂ con error de ±50 ppm.
 de cada pieza Radar + PIR: detectar presencia con ≥
 95 % de acierto. Nodo de puerta: durar
 ≥ 30 días con batería.

iv.​ Fases del proceso
 Ubicamos las fases del ciclo de vida de la NASA dentro del
 calendario del curso. Cada fase termina con un hito que funciona
 como revisión. Actualmente (semana 7) estamos pasando de la Fase
 B a la Fase C.

 Tabla 3. Fases del proyecto.
 Fase NASA Semanas Qué hacemos
 Pre-A · Concepto S1–S3 Idea inicial y pre-formulación
 A · Definición S4 Requisitos, modelo SysML y plan en
 Asana
 B · Diseño preliminar S5–S6 Entrevistas, permisos, compras,
 simulador y definición del formato de
 datos
 C · Diseño final y S7–S9 Firmware, servidor y armado de los seis
 construcción nodos
 D · Integración y S10–S13 API, dashboard, copiloto de voz y
 pruebas pruebas del sistema completo
 E · Operación S9–S14 Sistema midiendo en el laboratorio
 durante al menos 4 semanas

 7
 Fase NASA Semanas Qué hacemos
 F · Cierre S14 Informe final y demostración en vivo
 (13/11)

c.​ SysML y Modelaje en Gaphor
 i.​ Definición del sistema (¿cuál es el sistema que se
 está desarrollando y describiendo?)
 El sistema que modelamos es Campus Twin L-419: el laboratorio
 físico, su copia digital en el servidor y el flujo de datos que los
 conecta (sensores → ESP32 → Wi-Fi → servidor → dashboard y
 voz). Siguiendo la idea de gemelo digital de Grieves y Vickers
 (2017), el modelo describe tanto la parte física como la digital del
 sistema.

 El modelo está hecho en SysML (Object Management Group, 2019)
 con la herramienta Gaphor y tiene 12 diagramas organizados en
 cuatro paquetes:

 Tabla 4. Organización del modelo en Gaphor.
 Paquete Contenido
 00 Vista general Todo el sistema en un diagrama y el mapa completo de
 requisitos
 01 Requisitos Necesidades, requisitos funcionales y no funcionales, y
 qué bloque cumple cada requisito
 02 Estructura Arquitectura, nodos con sus sensores, servidor y tipos de
 datos con sus unidades
 03 Verificación Qué prueba verifica cada requisito

 ii.​ Descripción digital del sistema usando diagramas
 de SysML (creado en Gaphor)
 La Figura 1 muestra el sistema completo en un diagrama de
 definición de bloques (bdd). Los rombos negros significan "está
 compuesto por" y los triángulos significan "es un tipo de"
 (Friedenthal et al., 2014). Dentro de cada nodo aparecen las
 magnitudes que mide, con su unidad. Las Figuras 2 y 3 muestran en
 detalle los nodos y el servidor.

 8
Figura 1. Diagrama de bloques del sistema completo: seis subsistemas, los cuatro tipos de nodo con sus
 sensores, los servicios del servidor y los actores externos.

 9
Figura 2. Nodos e instrumentación: cada tipo de nodo hereda del nodo ESP32 base y se compone de sus
 sensores.

 Figura 3. Servidor y software: los servicios de la Raspberry Pi y las partes del copiloto de voz.

 En los diagramas de requisitos, cada requisito está conectado con el
 bloque que lo cumple («satisfy») y con la prueba que lo verifica
 («verify»). La Tabla 5 lo resume:

 Tabla 5. Trazabilidad de los requisitos funcionales.
 Requisito Bloque que lo cumple Prueba
 RF-01 y RF-12 · Energía total y Nodo de Energía CP-01
 por equipo
 RF-02 · Ambiente Nodo Ambiental CP-07
 RF-03 · Ocupación Nodo de Ocupación CP-02
 RF-04 · Eventos de puerta Nodo de Puerta CP-08
 RF-05 · Transporte de datos Red Local CP-03
 RF-06 y RF-07 · Histórico y Base de datos y Dashboard CP-09
 dashboard Web

 10
 Requisito Bloque que lo cumple Prueba
 RF-08 y RF-10 · Alertas y Motor de Reglas y Alertas CP-10, CP-06
 consumo fantasma
 RF-09 · Copiloto de voz Copiloto de Voz CP-04
 RF-11 · Modo demo Simulador y Modo Demo CP-11
 RF-13 · Salud del sistema Supervisor de Salud CP-15

iii.​ El modelo de SysML como referencia del sistema
 actual, o gemelo digital: ¿Qué usos se pueden dar al
 modelo de SysML?
 Además de servir para diseñar, conectamos el modelo con el sistema
 funcionando: un script abre el modelo en Gaphor y, cada segundo,
 escribe dentro de cada bloque el valor que está midiendo (por
 ejemplo, co2 = 1180 ppm en el Nodo Ambiental) y cambia el color
 del bloque según su estado. Así, el modelo se puede usar para lo
 siguiente:
 1.​ Monitoreo
 Permite ver el estado del laboratorio directamente en el
 modelo. El bloque se pinta de ámbar si hay una alerta (por
 ejemplo, CO₂ por encima de 1000 ppm) y de gris si un nodo
 deja de reportar. El dashboard web muestra la misma
 información para el administrador.

 2.​ Análisis y Evaluación
 Permite revisar si cada requisito se cumple siguiendo sus
 relaciones con bloques y pruebas. Al poner datos sobre el
 modelo encontramos errores de diseño; por ejemplo, el nodo
 de puerta aparecía como "caído" porque solo envía datos
 cada 30 minutos para ahorrar batería, y corregimos el
 requisito. También se analiza el consumo fantasma, cruzando
 energía, iluminación y presencia.

 3.​ Toma de decisiones
 El reporte de consumo fantasma entrega una cifra en soles y
 en kg de CO₂ con la que el administrador puede decidir, por
 ejemplo, apagar equipos de noche. La trazabilidad del
 modelo también muestra qué bloques y pruebas se afectan si
 un requisito cambia.

 4.​ Inteligencia
 Las reglas del servidor cruzan varias mediciones para sacar

 11
 conclusiones que un solo sensor no da, como "laboratorio
 vacío pero consumiendo energía". Con más semanas de datos
 se podría predecir la ocupación por horario o detectar
 consumos anómalos, lo que queda como trabajo futuro.

 5.​ Operación autónoma
 El sistema funciona solo, sin internet y sin intervención
 durante días, y se recupera por su cuenta después de un corte
 de energía. Controlar equipos (por ejemplo, apagar el
 proyector si no hay nadie) queda como mejora futura, ya que
 los enchufes con Tasmota lo permitirían.

d.​ Gestión del Proyecto
 i.​ Descripción de la gestión
 Organizamos el trabajo por semanas (S4 a S14), siguiendo las fases
 de la sección 3.b.iv. Nuestras reglas de trabajo son:
 -​ Cada tarea tiene un solo responsable y dura como máximo una
 semana.
 -​ Cada fase termina con un hito que revisamos en grupo.
 -​ Nos reunimos todos los viernes para revisar el avance y, cada
 dos semanas, los riesgos.
 -​ Las tareas llevan el código del requisito o de la prueba que
 atienden (por ejemplo, "CP-01 Ensayo de exactitud de energía").
 -​ Hicimos primero un simulador para avanzar con el software
 aunque los sensores se demoren en llegar.

 Tabla 6. Reparto de responsabilidades.
 Integrante Rol en el proyecto
 José Eduardo Huamán Servidor, API, reglas, dashboard e integración
 Esteban Sotomayor Nodos de ocupación y puerta, copiloto de voz
 Luhana Landeo Modelo SysML, documentación, nodo ambiental y
 pruebas

 ii.​ Detalles de la gestión en ASANA
 El proyecto está en Asana como "PI3 — Campus Twin L-419",
 con los integrantes del grupo como miembros, del 31/08/2026 al
 13/11/2026. El tablero está dividido en secciones por fase:

 12
Tabla 7. Secciones del proyecto en Asana.
 Sección en Asana Fechas Hito
 S4 · Formulación y 31/08–06/09 Requisitos y modelo SysML
 modelado listos
 S5–S6 · Especificación, 07/09–20/09 Componentes comprados y
 permisos y compras simulador funcionando
 S7 · Firmware base y 21/09–27/09 Primer nodo enviando datos
 servidor
 S8–S9 · Integración de nodos 28/09–11/10 Los seis nodos instalados
 S10–S11 · API, reglas y 12/10–25/10 Dashboard con datos reales
 dashboard
 S12 · Copiloto de voz 26/10–01/11 Copiloto respondiendo en el
 celular
 S13 · Pruebas de sistema 02/11–08/11 Todas las pruebas ejecutadas
 S14 · Entrega final 09/11–13/11 Presentación y demo en vivo
 Gestión y transversales Todo el ciclo Reuniones semanales y
 seguimiento de riesgos

Cada tarea tiene responsable, fecha de inicio y fecha de entrega. Las
pruebas de cada nodo son tareas aparte, ubicadas en la misma fase
que el nodo. El reporte y la presentación también están como tareas
en la sección S14: "Informe final de resultados" (Luhana) y "Póster
y presentación" (Esteban).

 13
4.​ Conclusión y Recomendaciones
 El desarrollo del prototipo de Gemelo Digital en las instalaciones piloto de la
 Universidad de Ingeniería y Tecnología demuestra la viabilidad técnica y operativa
 de implementar una solución de bajo costo para la gestión sostenible de la
 infraestructura. Al integrar nodos de sensor distribuido con un servidor de
 procesamiento local, la plataforma logra operar con total independencia de redes
 externas o servicios en la nube, resguardando la privacidad de la comunidad
 académica al evitar el uso de cámaras o grabaciones de voz[3]. Esta arquitectura
 centralizada permite visibilizar y cuantificar en tiempo real el consumo fantasma
 ,aquel gasto energético involuntario en espacios sin ocupación, transformando
 mediciones aisladas de iluminación, clima y aforo en indicadores de impacto
 económico y ambiental que fundamentan de manera directa la postulación a
 certificaciones de edificación sostenible.

 Frente a las alternativas comerciales cerradas y de elevado costo que dominan el
 mercado tradicional de gestión de edificios, este proyecto aporta una propuesta de
 innovación abierta que democratiza el acceso a la información operativa[2]. A
 través de dos herramientas complementarias —un panel web analítico concebido
 para la dirección de infraestructura y un copiloto de voz automatizado pensado para
 el personal de seguridad durante sus rondas nocturnas— se logra integrar a la

 14
 supervisión de primera línea en la toma de decisiones energéticas. Asimismo, la
 adopción del marco metodológico de ingeniería de sistemas y el modelado formal
 de arquitectura garantizaron una trazabilidad integral entre las necesidades de los
 usuarios, los requisitos del sistema y sus pruebas de verificación, alineando la
 tecnología local con los objetivos globales de desarrollo sostenible.

 Para potenciar el impacto de la plataforma a futuro, se recomienda avanzar desde el
 monitoreo pasivo hacia la automatización activa de controles, permitiendo que la
 plataforma desvincule el suministro eléctrico de luminarias o equipos auxiliares de
 manera autónoma al confirmar la ausencia de personas. De igual modo, resulta
 conveniente proyectar el escalamiento progresivo del despliegue hacia otros
 laboratorios y áreas comunes de la universidad, incorporando modelos analíticos de
 inteligencia predictiva que permitan anticipar patrones de ocupación y detectar
 anomalías de consumo antes de que generen sobrecostos. Finalmente, es importante
 ajustar los temporizadores de diagnóstico en la red para aquellos componentes que
 transmiten con menor frecuencia para preservar su energía, evitando falsas alertas
 dentro del monitoreo de salud del sistema.

5.​ Bibliografía
 -​ Carrillo-Hernández, O. F. (2012). Tendencias mundiales de producción y
 consumo de energía y reducción de emisiones de CO2. Legado de
 Arquitectura y Diseño, 7(11), 61-78.
 https://legadodearquitecturaydiseno.uaemex.mx/article/view/14035

 -​ de Loza, F. P., & Villegas, F. J. I. (2024). Implementación de tecnologías
 IoT para la reducción del consumo energético en oficinas inteligentes
 mediante el control de la iluminación. Revista de Ciencias Tecnológicas,
 7(3), e332-e332. https://recit.uabc.mx/index.php/revista/article/view/332

 -​ Friedenthal, S., Moore, A., & Steiner, R. (2014). A practical guide to
 SysML: The Systems Modeling Language (3.ª ed.). Morgan Kaufmann.

 -​ Gaphor. (s. f.). Gaphor documentation. https://docs.gaphor.org

 -​ Grieves, M., & Vickers, J. (2017). Digital twin: Mitigating unpredictable,
 undesirable emergent behavior in complex systems. En F.-J. Kahlen, S.
 Flumerfelt y A. Alves (Eds.), Transdisciplinary perspectives on complex
 systems (pp. 85–113). Springer.

 -​ National Aeronautics and Space Administration. (2016). NASA systems
 engineering handbook (NASA/SP-2016-6105 Rev2). NASA.

 -​ Object Management Group. (2019). OMG Systems Modeling Language

 15
(OMG SysML), versión 1.6. OMG.

 16
