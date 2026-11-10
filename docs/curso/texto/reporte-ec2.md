# Reporte EC2 - Grupo 1 (12 de 16).pdf

> Texto extraído automáticamente de `docs/curso/originales/Reporte EC2 - Grupo 1 (12 de 16).pdf` (no versionado) el 10/11/2026.
> Reporte del grupo de la EC2. Para figuras y tablas, abrir el original.

UNIVERSIDAD DE INGENIERÍA Y TECNOLOGÍA

 Reporte de “Campus Twin”

 Curso:

 Proyectos interdisciplinarios III

 Docente:

 Jorge Fernando Figueroa Nuñez Del Prado

 Landeo Quispe, Luhana Landeo

 Sotomayor Reyna, Esteban Matias

 Huamani Ñaupas, José Eduardo

 Duamel Davila Cabezas, Carlos Victor

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
 corporativos y educativos.

 2
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

 Un escalón más arriba en la toma de decisiones se ubica el usuario

 3
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
 garantizando la seguridad del campus sin generar sobrecarga laboral.

 4
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
 El sistema Campus Twin es un gemelo digital desarrollado para la
 Universidad de Ingeniería y Tecnología (UTEC), cuyo objetivo es optimizar
 el consumo energético y mejorar la gestión operativa del campus. Integra
 información en tiempo real de sensores de iluminación, climatización
 (HVAC) y ocupación en un mapa digital interactivo. Cuenta con un panel
 web para los administradores y un copiloto de voz para el personal de
 seguridad, facilitando el monitoreo, la detección de fallas y la toma de
 decisiones.

 ii.​ Descomposición del sistema
El sistema Campus Twin se divide en los siguientes subsistemas:

 1.​ Subsistema de sensores IoT: recopila datos sobre iluminación, climatización y

 5
 ocupación de las aulas.
 2.​ Subsistema de comunicación y procesamiento: recibe, procesa y organiza los datos
 recopilados por los sensores.
 3.​ Subsistema del gemelo digital: representa la infraestructura del campus mediante
 un mapa digital interactivo.
 4.​ Subsistema de administración web: permite visualizar el consumo energético,
 identificar anomalías y generar reportes.
 5.​ Subsistema de copiloto de voz: permite al personal de seguridad realizar consultas
 y reportar incidencias mediante comandos de voz.
 6.​ Subsistema de almacenamiento: conserva los datos históricos para analizar el
 consumo y evaluar el rendimiento energético.

 iii.​ Requisitos para cada nivel de la descomposición
El sistema Campus Twin debe cumplir con los siguientes requisitos en cada nivel:

 ●​ Sistema general: integrar los componentes necesarios para monitorear y optimizar
 el consumo energético de la UTEC.
 ●​ Sensores IoT: recopilar datos de iluminación, climatización y ocupación de las
 aulas.
 ●​ Procesamiento de datos: recibir y procesar la información de los sensores en tiempo
 real.
 ●​ Gemelo digital: representar la infraestructura del campus mediante un mapa
 interactivo.
 ●​ Panel web: mostrar el consumo energético, las alertas y los reportes para los
 administradores.
 ●​ Copiloto de voz: permitir al personal de seguridad realizar consultas y registrar
 incidencias mediante comandos de voz.
 ●​ Almacenamiento: guardar datos históricos para analizar el consumo energético y
 detectar patrones.

 iv.​ Fases del proceso
Para desarrollar Campus Twin se consideran las siguientes fases de ingeniería de sistemas:

 1.​ Análisis de necesidades: identificar los problemas energéticos y las necesidades de
 los usuarios.
 2.​ Definición de requisitos: establecer las funciones y características que debe cumplir
 el sistema.
 3.​ Diseño: definir la arquitectura, los subsistemas y las conexiones entre los
 componentes.

 6
 4.​ Implementación: desarrollar el software e integrar los sensores y las interfaces.
 5.​ Integración y verificación: comprobar que todos los componentes funcionen
 correctamente.
 6.​ Validación: realizar pruebas en las aulas piloto de la UTEC para verificar que el
 sistema satisfaga las necesidades identificadas.
 7.​ Operación y mejora: evaluar el funcionamiento y realizar mejoras continuas.

 c.​ SysML y Modelaje en Gaphor
 i.​ Definición del sistema (¿cuál es el sistema que se
 está desarrollando y describiendo?)
 Campus Twin es un sistema de gemelo digital que representa la
 infraestructura de la UTEC y permite monitorear el consumo
 energético mediante información recopilada por sensores IoT.
 Integra un mapa digital interactivo, un panel web para
 administradores y un copiloto de voz para el personal de seguridad,
 facilitando la supervisión de las instalaciones y la toma de
 decisiones.

 ii.​ Descripción digital del sistema usando diagramas
 de SysML (creado en Gaphor)
El modelado de Campus Twin mediante SysML en Gaphor permite representar la
estructura y el funcionamiento del sistema. Para ello, se pueden utilizar los siguientes
diagramas:

 ●​ Diagrama de requisitos: muestra las necesidades del sistema, como el monitoreo
 energético, la visualización de datos y la generación de alertas.
 ●​ Diagrama de bloques (BDD): representa los componentes principales, como los
 sensores IoT, el procesamiento de datos, el gemelo digital, el panel web y el
 copiloto de voz.
 ●​ Diagrama de bloques internos (IBD): describe cómo se conectan los componentes y
 cómo circula la información desde los sensores hasta las interfaces.
 ●​ Diagrama de actividades: representa el proceso de recopilación, procesamiento y
 visualización de los datos energéticos.

Estos diagramas permiten comprender la arquitectura de Campus Twin, sus componentes y
las relaciones entre ellos. Los diagramas deben elaborarse en Gaphor para documentar el
diseño del sistema.

 iii.​ El modelo de SysML como referencia del sistema

 7
 actual, o gemelo digital: ¿Qué usos se pueden dar al
 modelo de SysML?
 El modelo SysML sirve como referencia estructural
 y funcional de Campus Twin. Permite comprender
 cómo está organizado el sistema y cómo
 interactúan sus componentes. Sus principales usos
 son los siguientes:
 1.​ Monitoreo
 El modelo permite identificar los componentes encargados
 de recopilar y mostrar los datos de iluminación,
 climatización y ocupación. Esta información facilita la
 supervisión del consumo energético y del funcionamiento de
 las instalaciones.
 2.​ Análisis y Evaluación
 Permite estudiar las relaciones entre los componentes y
 analizar los datos recopilados para identificar patrones de
 consumo, posibles desperdicios energéticos y fallas
 operativas.
 3.​ Toma de decisiones
 El modelo facilita la comprensión del funcionamiento del
 sistema y ayuda a los administradores a decidir qué acciones
 tomar para mejorar la eficiencia energética y planificar el
 mantenimiento.

 4.​ Inteligencia
 La integración de datos históricos y actuales permite
 identificar patrones de consumo y generar alertas sobre
 posibles anomalías. Esto contribuye a mejorar el análisis y la
 planificación de las operaciones del campus.

 5.​ Operación autónoma
 Campus Twin puede evolucionar hacia una operación más
 automatizada mediante el uso de sensores y reglas de control
 que permitan detectar condiciones anormales y activar
 alertas. Para ejecutar acciones automáticas sobre la
 iluminación o la climatización, será necesario integrar los
 sistemas de control correspondientes.

d.​ Gestión del Proyecto
 i.​ Descripción de la gestión

 8
La gestión del proyecto Campus Twin comprende la planificación, organización y
supervisión de las actividades necesarias para desarrollar el producto mínimo viable
(MVP). El equipo debe distribuir las responsabilidades, establecer plazos y verificar el
cumplimiento de los objetivos.

La gestión también incluye el seguimiento del desarrollo del software, la integración de los
sensores IoT, la elaboración del gemelo digital y las pruebas en las aulas piloto de la
UTEC. Una adecuada organización permite identificar retrasos, resolver problemas y
asegurar que el proyecto responda a las necesidades de los usuarios.

 ii.​ Detalles de la gestión en ASANA
ASANA puede utilizarse como herramienta de gestión para organizar las actividades y
realizar el seguimiento del proyecto Campus Twin. Su implementación puede estructurarse
de la siguiente manera:

 ●​ Planificación: registrar las tareas necesarias para desarrollar el sistema y establecer
 fechas de entrega.
 ●​ Asignación de responsabilidades: distribuir las actividades entre los integrantes del
 equipo.
 ●​ Seguimiento de tareas: utilizar estados como pendiente, en proceso y completado
 para controlar el avance.
 ●​ Gestión de plazos: establecer fechas límite para el desarrollo del software, la
 integración de sensores y las pruebas.
 ●​ Comunicación: registrar comentarios, avances y dificultades para mantener
 informado al equipo.
 ●​ Control de resultados: verificar el cumplimiento de las actividades y los objetivos
 establecidos.

De esta manera, ASANA facilita la coordinación del equipo, el control del progreso y el
cumplimiento de los objetivos del proyecto Campus Twin.

 4.​ Conclusión y Recomendaciones (Luhana)
El desarrollo de Campus Twin demuestra la importancia de los gemelos digitales para
mejorar la eficiencia energética y la gestión operativa de la UTEC. Mediante la integración
de sensores IoT, un mapa digital interactivo, un panel web y un copiloto de voz, se busca
facilitar el monitoreo de las instalaciones, detectar posibles fallas y optimizar el consumo
de energía.

Asimismo, la aplicación de la ingeniería de sistemas de la NASA permite organizar el

 9
proyecto en subsistemas, definir requisitos y establecer fases para su desarrollo y
validación. El uso de SysML en Gaphor contribuye a representar la estructura y las
relaciones entre los componentes, mientras que ASANA facilita la planificación y
coordinación de las tareas del equipo.

Finalmente, Campus Twin representa una propuesta tecnológica con potencial para
promover una infraestructura universitaria más sostenible. Su implementación y
evaluación en las aulas piloto permitirán identificar mejoras y comprobar su utilidad para
la gestión energética de la universidad.

 5.​ Bibliografía
 -​ Carrillo-Hernández, O. F. (2012). Tendencias mundiales de producción y
 consumo de energía y reducción de emisiones de CO2. Legado de
 Arquitectura y Diseño, 7(11), 61-78.
 https://legadodearquitecturaydiseno.uaemex.mx/article/view/14035

 -​ de Loza, F. P., & Villegas, F. J. I. (2024). Implementación de tecnologías
 IoT para la reducción del consumo energético en oficinas inteligentes
 mediante el control de la iluminación. Revista de Ciencias Tecnológicas,
 7(3), e332-e332. https://recit.uabc.mx/index.php/revista/article/view/332

 10
