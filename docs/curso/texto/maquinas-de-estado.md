# Maquinas_de_Estado.pptx

> Texto extraído automáticamente de `docs/curso/originales/Maquinas_de_Estado.pptx` (no versionado) el 10/11/2026.
> Notación de máquinas de estado para el diagrama de estados. Para figuras y tablas, abrir el original.

### Diapositiva 1
Máquinas de Estado
Modelar, diseñar y razonar sobre el comportamiento de sistemas
Basado en Sipser (2012), Hopcroft, Motwani & Ullman (2007) y Harel (1987).
1
### Diapositiva 2
Objetivos de aprendizaje
• Explicar qué es una máquina de estados y cuándo resulta útil.
• Identificar estados, eventos, transiciones, acciones y condiciones.
• Representar un sistema mediante un diagrama y una tabla de transición.
• Distinguir máquinas de Moore y Mealy, y comprender la idea de determinismo.
• Construir y recorrer un modelo sencillo a partir de un ejemplo.
Referencia conceptual: Sipser, M. (2012). Introduction to the Theory of Computation (3rd ed.).
2
### Diapositiva 3
La idea central: el comportamiento depende del estado
ENTRADA
Evento, señal o condición que ocurre.
ESTADO
Información mínima necesaria para describir la situación actual.
SALIDA / ACCIÓN
Respuesta producida por el sistema.
Una máquina de estados no describe todo el sistema: describe su comportamiento como una secuencia de situaciones discretas y cambios provocados por eventos.
Idea general alineada con la teoría de autómatas y con el diseño de sistemas secuenciales.
3
### Diapositiva 4
¿Qué es una máquina de estados finitos (Finite State Machine - FSM)?
• Modelo matemático de un sistema con un conjunto finito de estados.
• El sistema está en un estado en cada instante.
• Un evento de entrada puede provocar una transición a otro estado.
• Las salidas pueden depender del estado, de la entrada o de ambos.
• Se usa para especificar comportamiento de sistemas reactivos y procesos discretos.
REACTIVO
Observa eventos → cambia de estado → produce una respuesta.
Sipser (2012); Hopcroft, Motwani & Ullman (2007).
4
### Diapositiva 5
Anatomía de un diagrama de estados
A
B
C
evento / condición
evento / acción
Estado = situación 
Flecha = transición
Etiqueta = evento [guardia] / acción
Estado inicial = punto de entrada
Notación simplificada para enseñanza; las convenciones pueden variar según el formalismo.
5
### Diapositiva 6
Modelo formal: la 5-tupla
M = (Q, Σ, δ, q₀, F)
Una forma clásica de definir un autómata finito determinista.
Q
conjunto finito de estados
Σ
alfabeto o conjunto de entradas
δ
función de transición: Q × Σ → Q
q₀
estado inicial
F
conjunto de estados de aceptación
Sipser (2012), cap. 1; Hopcroft, Motwani & Ullman (2007), capítulo sobre finite automata.
6
### Diapositiva 7
La función de transición: δ
δ(estado, entrada) → nuevo estado
La transición responde a la combinación de situación actual + evento.
A
B
evento: x
Determinismo
Para cada estado y entrada, existe exactamente una transición definida.
Definición basada en autómatas finitos deterministas: Sipser (2012).
7
### Diapositiva 8
Moore vs. Mealy
Máquina de Moore
La salida se asocia principalmente al estado.Estado A → salida 0Estado B → salida 1Ventaja didáctica: la salida cambia al cambiar de estado.
Máquina de Mealy
La salida se asocia a la transición (estado + entrada).A -- x / 1 --> BPuede reaccionar a la entrada sin esperar necesariamente a entrar en un nuevo estado.
Harris & Harris (2013); literatura clásica de máquinas secuenciales.
8
### Diapositiva 9
Diagrama de estados: cómo leerlo
S0
S1
S2
evento
evento
• El punto de entrada identifica el estado inicial.
• Una flecha indica una transición.
• Un ciclo representa permanencia tras un evento.
• En modelos de aceptación, un estado final se marca con doble círculo.
Convenciones derivadas de la notación estándar de autómatas finitos.
10
### Diapositiva 10
Diagrama vs. tabla de transición
{5C22544A-7EE6-4342-B048-85BDC9FD1C3A}Estado
entrada 0
entrada 1
A
A
B
B
C
B
C
A
C
¿Por qué usar una tabla?
• Hace explícitas todas las transiciones.• Facilita verificar casos faltantes.• Puede traducirse directamente a código o HDL.• Es útil para pruebas sistemáticas.
Harris & Harris (2013) y Sipser (2012).
11
### Diapositiva 11
Diagrama vs. tabla de transición con acciones
Harris & Harris (2013) y Sipser (2012).
11
{5C22544A-7EE6-4342-B048-85BDC9FD1C3A}Estado actual
Entrada
Próximo estado
Acción
Bloqueado
Moneda
Liberado
Desbloquear
Bloqueado
Empujar
Bloqueado
Activar alarma
Liberado
Moneda
Liberado
Devolver moneda
Liberado
Empujar
Bloqueado
Bloquear
### Diapositiva 12
Cómo diseñar una máquina de estados
1
Definir el comportamiento que debe modelarse
2
Identificar estados relevantes
3
Listar eventos/entradas
4
Definir transiciones y condiciones
5
Definir salidas/acciones
6
Probar escenarios y casos límite
Proceso didáctico sintetizado a partir de prácticas de modelado y diseño secuencial.
12
### Diapositiva 13
Ejemplo: torniquete de acceso
Estados
BLOQUEADO ↔ LIBERADO
Entradas
moneda / empujar
Regla
moneda libera; empujar bloquea.
Ejemplo clásico de máquina de estados; formalización adaptada para fines docentes.
13
### Diapositiva 14
Ejemplo: recorrido paso a paso
Ejemplo: recorrido paso a paso
B
L
moneda
B
empujar
• Inicio: B (bloqueado).
• Llega moneda → transición a L (liberado).
• Llega empujar → transición a B.
• Si se empuja mientras está B, el sistema permanece B y puede activar una alarma.
Aplicación ilustrativa de δ(estado, entrada) → estado siguiente.
14
### Diapositiva 15
 ┌────────────────────┐
 │ ▼
 ┌───────┐ ┌─────────┐
 │ BLOQ. │ │ LIBERADO│
 └───────┘ └─────────┘
 M
Ejemplo: recorrido paso a paso
Ejemplo: recorrido paso a paso – otra gráfica
B
B
• Inicio: B (bloqueado).
• Llega moneda → transición a L (liberado).
• Llega empujar → transición a B.
• Si se empuja mientras está B, el sistema permanece B y puede activar una alarma.
Aplicación ilustrativa de δ(estado, entrada) → estado siguiente.
14
Bloqueado
Liberado
Insertar Moneda 
Empujar 
### Diapositiva 16
Del modelo al código
state = LOCKED
on_event(event):
 if state == LOCKED:
 if event == COIN:
 state = UNLOCKED
 elif event == PUSH:
 alarm()
 elif state == UNLOCKED:
 if event == PUSH:
 state = LOCKED
Idea clave
El código implementa las mismas transiciones definidas en el modelo.
Pruebas
Cada transición debe tener al menos un escenario de prueba.
Pseudocódigo educativo; la implementación real depende del lenguaje y del sistema.
15
### Diapositiva 17
¿Qué puede salir mal?
• Estado ambiguo: dos estados describen la misma situación.
• Transición faltante: aparece un evento no contemplado.
• Estado inalcanzable: existe en el modelo pero nunca puede alcanzarse.
• Explosión de estados: combinar demasiadas variables produce muchos estados.
• Modelo incorrecto: el diagrama parece razonable, pero no representa los requisitos reales.
Regla práctica
Modelar lo necesario para explicar el comportamiento, no todo el universo del sistema.
La complejidad de los modelos motivó extensiones como Statecharts (Harel, 1987).
16
### Diapositiva 18
Cuando una FSM simple no basta: Statecharts
FSM = Finite State Machine
FSM plana
Todos los estados aparecen al mismo nivel.Problema: cuando crece el sistema, aumentan las transiciones y se repiten comportamientos.
Statecharts
Harel propone incorporar jerarquía, concurrencia y comunicación para representar sistemas complejos de forma más estructurada.
OPERANDO
PAUSA
Harel, D. (1987). Statecharts: A visual formalism for complex systems. Science of Computer Programming, 8(3), 231–274.
17
### Diapositiva 19
¿Dónde se utilizan?
Software
interfaces, flujos de autenticación, protocolos, videojuegos
Sistemas embebidos
controladores, sensores, dispositivos IoT
Hardware digital
unidades de control, secuenciadores, FPGA
Robótica
modos de operación, navegación y seguridad
Protocolos
handshakes, conexiones, sesiones y comunicación
Harris & Harris (2013); Harel (1987); Sipser (2012).
18
### Diapositiva 20
Cinco ideas para llevarse
01
Un estado es una situación relevante del sistema.
02
Una transición explica cómo un evento cambia el estado.
03
El diagrama hace visible la lógica de comportamiento.
04
La tabla de transición ayuda a verificar completitud y consistencia.
05
FSMs son potentes para sistemas discretos; Statecharts ayudan cuando la complejidad crece.
Síntesis docente basada en las referencias de las diapositivas anteriores.
19
### Diapositiva 21
Referencias académicas
Sipser, M. (2012). Introduction to the Theory of Computation (3rd ed.). Cengage Learning.
Hopcroft, J. E., Motwani, R., & Ullman, J. D. (2007). Introduction to Automata Theory, Languages, and Computation (3rd ed.). Pearson/Addison-Wesley.
Harris, D. M., & Harris, S. L. (2013). Digital Design and Computer Architecture (2nd ed.). Morgan Kaufmann.
Harel, D. (1987). Statecharts: A visual formalism for complex systems. Science of Computer Programming, 8(3), 231–274. https://doi.org/10.1016/0167-6423(87)90035-9
MIT OpenCourseWare. (2020). Theory of Computation (18.404J). Massachusetts Institute of Technology.
Stanford University. CS103: Mathematical Foundations of Computing — materiales sobre Finite Automata.
Fuentes institucionales consultadas: MIT OpenCourseWare, MIT CSAIL y Stanford University.
20
