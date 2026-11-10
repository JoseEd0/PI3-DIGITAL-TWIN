# Razonamiento con Grafos dirigidos - Symcure - Figueroa ES-1.pptx

> Texto extraído automáticamente de `docs/curso/originales/Razonamiento con Grafos dirigidos - Symcure - Figueroa ES-1.pptx` (no versionado) el 10/11/2026.
> Metodología de razonamiento con grafos dirigidos (lógicas OR/AND/N-M/IF y propagación). Para figuras y tablas, abrir el original.

### Diapositiva 1
1
Metodología para razonamiento lógico usando grafos dirigidos
Metodología para razonamiento lógico usando grafos dirigidos
### Diapositiva 2
Docente: Fernando Figueroa
Correo: jfigueroan@utec.edu.pe
Cuando escriban, por favor identificarse, señalar nombre y sección del curso
Información general
### Diapositiva 3
Relaciones causales
Para comprender las complejas interacciones entre las relaciones causales de eventos discretos, considere el siguiente grafo dirigido causal, compuesto por las causas raíz F1, F2 y F3, y sus efectos correspondientes S1, S2 y S3.
Suponga que F2 es verdadero. Considere el conjunto de relaciones causales en la «salida» del evento F2:
F2 -> S1
F2 -> S2
F2 -> S3
Si estas relaciones son «iguales» en todos los aspectos, la propagación ocurre de manera idéntica a través de las tres relaciones y deben producirse S1, S2 y S3. Nos referimos a este tipo de relación causal como lógica AND en la salida de F2.
### Diapositiva 4
Relaciones causales
En el mundo real, la propagación puede no ocurrir de manera uniforme en todas las vías de interacción causal. Ante retrasos de propagación, errores de umbral y sensores ruidosos, a veces un síntoma posterior a una causa raíz se informa incorrectamente como falso cuando debería ser verdadero, o viceversa. Por lo tanto, es posible que no se manifiesten todos los eventos S1, S2 y S3 cuando F2 es verdadero. Esta situación motiva una interpretación alternativa de la propagación causal que admite lógica OR en la salida de F2.
Por último, en el mundo real, el valor de un evento puede depender del estado del sistema y no de ninguna de sus causas. Esta situación se conoce como lógica de propagación dependiente del contexto, denominada lógica IF. Más adelante en esta sección se presenta un ejemplo. Por lo tanto, es posible que ninguno de los eventos S1, S2 y S3 se manifieste a menos que se cumplan determinadas condiciones externas.
### Diapositiva 5
Relaciones causales
Suponga que S1 es verdadero. Considere el conjunto de relaciones causales en la «entrada» del evento S1:
F1 -> S1
F2 -> S1
F3 -> S1
Suponga que existen dependencias entre las relaciones causales. Por ejemplo, F1, F2 y F3 podrían tener que ser verdaderos para que S1 sea verdadero. Esta dependencia da lugar al concepto de lógica AND en la entrada de un evento, donde el evento es verdadero si y solo si todas sus entradas son verdaderas. Por otro lado, las relaciones causales también pueden ser independientes entre sí, de modo que la aparición de cualquiera de F1, F2 o F3 puede causar S1. Esta interpretación se conoce como lógica OR en la entrada de un evento. En situaciones reales también puede haber dependencias parciales entre las relaciones causales; por ejemplo, el 50 % o más de las causas de S1 deben ser verdaderas para que S1 sea verdadero. Caracterizamos este tipo de relación causal como lógica de propagación fraccionaria de eventos, denominada lógica N/M.
At a high level, SymCure performs event propagation in a fault model, as follows:
for any incoming event e do
 propagate upstream to causes = all causes of e;
 propagate downstream to effects = all effects of causes + e;
end for
### Diapositiva 6
Relaciones causales
En la figura, suponga que el evento entrante es D. En este ejemplo:
causas = {A, B, E}
efectos = {C, F, H}
Observe que el evento G no se ve afectado como respuesta al evento entrante D.
Los valores calculados para los eventos dependen de la lógica de propagación de eventos.
### Diapositiva 7
Relaciones causales
Lógica de eventos
Cada vez que un evento e recibe un nuevo valor, debe propagarse aguas arriba y aguas abajo hacia las causas y los efectos del evento. Esto requiere los siguientes cálculos:
En función de su lógica de propagación, su nuevo valor y su estado anterior, e debe calcular qué valores proponer para sus entradas y salidas.
Cada causa y efecto de e que reciba los valores propuestos por e debe decidir si acepta o no estos cambios.
### Diapositiva 8
Tabla de verdad lógica
El valor de un evento puede obtenerse mediante observación. En este documento, el valor observado de un evento suele denominarse valor entrante o valor especificado. La siguiente tabla muestra cómo una observación afecta el valor de cualquier evento, independientemente de su lógica de propagación.
### Diapositiva 9
Lógica de propagación
En general, cuando el evento desencadenante está aguas abajo de un evento e, el valor de e cambia debido al evento desencadenante. Esto se representa mediante lógica AND en la salida del evento.
Cuando el evento desencadenante está aguas arriba de un evento e, el valor de e se calcula analizando todos los eventos que podrían causarlo, según la lógica de entrada de e: OR, AND, N/M o IF.
Reglas prácticas para calcular los valores propuestos para las causas y los efectos de cualquier evento. Tenga en cuenta que estas son solo pautas: el cálculo de los valores depende de varios factores, como la lógica de propagación, la topología del modelo de fallas en su entorno y la naturaleza de los eventos vecinos, que pueden prevalecer sobre estas reglas.
Si un evento tiene una sola causa (entrada) desconocida y el evento es verdadero, podemos concluir que su única causa también es verdadera. (Los eventos con lógica OR y N/M y múltiples efectos pueden ser excepciones a esta regla).
Siempre que sea posible, se intenta conciliar la información nueva con el conocimiento existente. Por ello, se ignora los valores desconocidos y se da prioridad a lo que ya se sabe sobre un evento. Sin embargo, los valores existentes se reemplazan cuando no son coherentes con la nueva información.
En general, se procesa un evento solo cuando cambia su valor. La única ocasión en que procesa un evento cuyo valor no ha cambiado es cuando su estado pasa a ser especificado.
### Diapositiva 10
Evento OR-AND
Un evento OR-AND utiliza lógica OR en su entrada y lógica AND en su salida. El valor de un evento OR-AND es verdadero si una o más de sus causas son verdaderas.
Evento OR-AND
### Diapositiva 11
Propagación aguas arriba
Esta tabla describe las reglas que proponen valores para las entradas de un evento OR-AND cuando su valor cambia durante la propagación aguas arriba:
### Diapositiva 12
Propagación aguas abajo
Se calcula el valor de un evento OR-AND durante la propagación aguas abajo cuando cambia el valor de un evento desencadenante situado aguas arriba.
En general, se utiliza la lógica OR tradicional para calcular el valor del evento, de la siguiente manera:
Si hay al menos una entrada verdadera, concluir que el evento es verdadero;
De lo contrario, si hay al menos una entrada sospechosa, concluir que el evento es sospechoso;
De lo contrario, si hay al menos una entrada desconocida, concluir que el evento es desconocido;
En caso contrario, concluir que el evento es falso.
### Diapositiva 13
Evento AND-AND
Un evento AND-AND utiliza lógica AND tanto en su entrada como en su salida. El valor de un evento AND-AND es verdadero si todas sus causas son verdaderas.
Evento AND-AND
En este ejemplo, «Falla de la fuente de alimentación» es causada por la conjunción de «Falla de la alimentación primaria» y «Falla de la alimentación de respaldo»:
### Diapositiva 14
Propagación aguas arriba
Esta tabla muestra los valores propuestos para las entradas de un evento AND-AND cuando el valor del evento cambia durante la propagación aguas arriba:
### Diapositiva 15
Propagación aguas abajo
Se calcula el valor de un evento AND-AND durante la propagación aguas abajo cuando cambia el valor de un evento desencadenante situado aguas arriba.
Se utiliza la lógica AND tradicional para calcular el valor del evento de la siguiente manera:
Si todas las entradas son verdaderas, concluir que el evento es verdadero;
De lo contrario, si hay al menos una entrada sospechosa y las demás son verdaderas, concluir que el evento es sospechoso;
De lo contrario, si hay al menos una entrada desconocida y las demás son sospechosas o verdaderas, concluir que el evento es desconocido;
En caso contrario, concluir que el evento es falso.
### Diapositiva 16
Evento N/M-AND
Relación de propagación
Se ofrece lógica N/M en la entrada de un evento, que es una generalización numérica de la lógica OR. El valor de un evento N/M es verdadero si al menos la fracción N/M de sus causas es verdadera, donde N/M es un número real entre 0,0 y 1,0. El evento N/M-AND utiliza lógica AND en su salida.
Considere el caso de un proveedor de servicios de TI que utiliza varios servidores para ofrecer a sus clientes servicios como comunicaciones de datos y telefonía. Por lo general, se pueden apagar servidores individuales sin que ello afecte significativamente el servicio; sin embargo, si el número de servidores que sufren interrupciones supera cierto umbral, la calidad del servicio comienza a deteriorarse.
En el siguiente ejemplo, «Interrupción del servicio del ISP» pasa a ser verdadero cuando al menos el 50 % de los servidores requeridos por un servicio del ISP sufren una «Interrupción». La relación «requerido por» describe la relación causal entre el servicio del ISP que sufre la interrupción y los servidores de los que depende y que están fuera de servicio. Los eventos del modelo de fallas son genéricos; durante la ejecución, la representación del dominio (el gemelo digital) proporciona el número de servidores específicos que requiere un servicio determinado y el número de eventos específicos de «Interrupción» que son verdaderos.
Fracción
Evento N/M-AND
Nota: el evento N/M-AND no es probabilístico, porque solo calcula valores de verdad cualitativos para un evento (verdadero, falso, sospechoso o desconocido), no grados de confianza.
### Diapositiva 17
Propagación aguas arriba
La tabla describe las reglas que proponen valores para las entradas de un evento N/M-AND cuando su valor cambia durante la propagación aguas arriba
### Diapositiva 18
Propagación aguas abajo
propagación aguas abajo, es decir, cuando el evento desencadenante está aguas arriba del evento N/M-AND:
Si el número de causas verdaderas / número total de causas >= N/M, entonces el evento es verdadero;
De lo contrario, si (número de causas verdaderas + número de causas sospechosas) / número total de causas >= N/M, entonces el evento es sospechoso;
De lo contrario, si (número de eventos desconocidos + número de eventos sospechosos + número de eventos verdaderos) / número total de causas >= N/M, entonces el evento es desconocido;
En caso contrario, el evento es falso.
### Diapositiva 19
Evento IF-AND
Evento IF-AND
Procedimiento dependiente del estado
En casos excepcionales, el valor de un evento depende del estado de su objeto objetivo y no de ninguna de sus causas. Se ofrece propagación dependiente del contexto mediante un evento IF-AND. A este evento se le asocia un procedimiento definido por el usuario que determina dinámicamente su valor. El procedimiento dependiente del estado se ejecuta cada vez que se intenta propagar al evento un valor procedente de sus causas. El procedimiento devuelve un valor para el evento IF-AND examinando el estado de su objeto objetivo. El evento utiliza lógica AND en su salida.
«Incumplimiento» de un acuerdo de nivel de servicio relacionado. El evento «Incumplimiento» se representa en el modelo de fallas para permitir el diagnóstico de sus causas cuando ocurra. Sin embargo, no se puede concluir que haya ocurrido un «Incumplimiento» cada vez que se produce una «Interrupción» del servicio telefónico. Los incumplimientos de los acuerdos de nivel de servicio pueden depender de varios factores que no están incluidos en el modelo de fallas, como la hora del día en que ocurre la interrupción, el historial de todas las interrupciones durante un período determinado y la duración de la interrupción actual.
### Diapositiva 20
Evento IF-AND
Evento IF-AND
Procedimiento dependiente del estado
La única diferencia entre este evento y un evento OR-AND es la siguiente:
No se define el comportamiento para deducir el valor del evento a partir de sus entradas durante la propagación aguas abajo. Este comportamiento lo define el procedimiento especificado por el usuario que se asocia al evento.
Se propaga valores a un evento IF-AND cada vez que cualquiera de sus eventos aguas arriba recibe un valor, incluso si este no ha cambiado. Esto es necesario porque un evento IF-AND depende no solo de sus eventos causales, sino también del estado del sistema administrado. Activar el evento cada vez que un evento aguas arriba recibe un nuevo valor garantiza que el procedimiento dependiente del estado se ejecute cada vez que ocurre un evento, independientemente de que su valor haya cambiado.
### Diapositiva 21
Evento OR-AND
Evento OR-N/M
Fracción
El evento OR-N/M es una generalización de un evento OR-OR. Un evento OR-N/M es verdadero siempre que al menos la fracción N/M de sus efectos aguas abajo sea verdadera.
En el siguiente ejemplo, la fracción define el comportamiento del evento «Centrífuga sobrecargada». Cuando la centrífuga de una cámara de reacción se sobrecarga, provoca niveles superiores a lo normal de temperatura, caudal, presión y torque. Sin embargo, debido al ruido y a los errores de los sensores, los síntomas de temperatura, caudal, presión y torque pueden manifestarse o no. En este modelo, el evento se considera verdadero siempre que al menos el 50 % de sus síntomas sean verdaderos.
### Diapositiva 22
Propagación aguas arriba
Se calcula el valor de un evento OR-N/M durante la propagación aguas arriba cuando cambia el valor de un evento desencadenante situado aguas abajo del evento OR-N/M.
Se utiliza la lógica OR tradicional para calcular el valor del evento a partir de sus salidas, independientemente del valor del evento desencadenante, de la siguiente manera:
Si el número de salidas verdaderas / número total de salidas >= N/M, concluir que el evento es verdadero;
De lo contrario, si (suma de salidas verdaderas y sospechosas) / número total de salidas >= N/M, concluir que el evento es sospechoso;
De lo contrario, si (suma de salidas verdaderas, sospechosas y desconocidas) / número total de salidas >= N/M, concluir que el evento es desconocido;
En caso contrario, concluir que el evento es falso.
La tabla para proponer valores a las entradas de un evento OR-N/M durante la propagación aguas arriba es idéntica a la del evento OR-AND.
### Diapositiva 23
Propagación aguas abajo
propagación cuando cambia el valor de un evento desencadenante situado aguas arriba del evento OR-N/M.
Se utiliza la misma lógica que para un evento OR-AND al calcular el valor de un evento OR-N/M durante la propagación aguas abajo.
Considere los valores que un evento OR-N/M propaga a sus efectos cuando cambia su valor:
Si Fracción = 1, el evento OR-N/M se comporta como un evento OR-AND.
Si Fracción = 0, el evento OR-N/M se comporta como un evento OR-OR.
Si 0 < Fracción < 1, el comportamiento del evento OR-N/M se describe en la tabla.
### Diapositiva 24
Evento N/M-N/M
El evento N/M-N/M es una generalización de todos los tipos de eventos que permite configurar la lógica de entrada y salida. Puede utilizarse en lugar de cualquiera de los siguientes eventos:
OR-AND
AND-AND
N/M-AND
OR-N/M
OR-OR
El evento N/M-N/M proporciona dos fracciones, la Fracción de entrada y la Fracción de salida, que configuran la lógica del evento de la siguiente manera:
Lógica de entrada:
Fracción de entrada = 0,0 -> lógica OR
0,0 < Fracción de entrada < 1,0 -> lógica N/M
Fracción de entrada = 1,0 -> lógica AND
Lógica de salida:
Fracción de salida = 0,0 -> lógica OR
0,0 < Fracción de salida < 1,0 -> lógica N/M
Fracción de salida = 1,0 -> lógica AND
### Diapositiva 25
Evento N/M-N/M
La lógica OR en la entrada (salida) implica que, si el evento es verdadero, al menos una de sus causas (efectos) debe ser verdadera; es posible que algunas causas (efectos) sean falsas mientras el evento es verdadero.
Cuando un evento con lógica OR en la entrada (salida) pasa a ser verdadero, si tiene una sola causa (efecto), esta también debe ser verdadera. Si tiene varias causas (efectos), al menos una debe ser verdadera; si no se puede identificar al menos una causa (efecto) que pueda ser verdadera o sospechosa, considera sospechosas todas las causas (efectos).
La lógica AND en la entrada (salida) implica que, cuando el evento es verdadero, todas sus causas (efectos) deben ser verdaderas.
La lógica AND en la salida es de tipo «todo o nada» cuando un evento es verdadero; es decir, si se infiere u observa que un solo efecto es verdadero, tanto el evento como todos los demás efectos deben ser verdaderos.
Cuando cualquiera de los efectos del evento pasa a ser falso, al aplicar la lógica AND el propio evento se vuelve falso; sin embargo, esto no afecta a los efectos restantes, que pueden seguir siendo verdaderos.
Para todos los tipos de eventos, excepto N/M-N/M, se supone que cuando todos los efectos de un evento pasan a ser falsos, el propio evento también debe ser falso; es decir, su causa raíz subyacente debe haberse corregido. Sin embargo, no existe una razón fundamental para preferir esta suposición frente a otra. Por ejemplo, un retraso de propagación podría impedir que se manifieste cualquiera de los efectos del evento.
### Diapositiva 26
Evento N/M-N/M
El evento N/M-N/M con lógica OR en la salida, es decir, con una fracción de salida = 0,0, puede conservar un valor verdadero o sospechoso si su estado es «especificado» o «inferido aguas abajo», incluso cuando todos sus efectos son falsos. Para ello, el evento N/M-N/M ofrece una opción denominada «Independiente de los efectos». Si está habilitada, permite que un evento N/M-N/M con lógica OR, especificado o inferido aguas abajo, conserve un valor verdadero o sospechoso incluso cuando todos sus efectos se observan o infieren como falsos. De forma predeterminada, esta opción está deshabilitada.
En el ejemplo, todos los eventos son eventos N/M-N/M, que se comportan de manera diferente según las fracciones de entrada y salida. Por ejemplo, el evento «Falla de alimentación» tiene una Fracción de entrada de 1 y una Fracción de salida de 0, lo que significa que se comporta como un evento AND-OR. Por otro lado, el evento «Explosión del gigante verde» tiene una Fracción de entrada de 0 y una Fracción de salida de 1, por lo que se comporta como un evento OR-AND.
### Diapositiva 27
Evento OR-OR
Un evento OR-OR utiliza lógica OR en su salida. Cuando el evento es verdadero, esta lógica de propagación permite que conserve su valor incluso después de que uno o más de sus efectos aguas abajo pasen a ser falsos, siempre que al menos uno de los efectos aguas abajo sea sospechoso o verdadero. De este modo, se puede modelar situaciones en las que algunos efectos de un evento verdadero podrían no manifestarse.
En el ejemplo, la «Acumulación de suciedad» provoca «Vibración», «Aumento de la presión diferencial» y «Ensuciamiento» en una cámara de reacción.
Suponga que la «Vibración» no es fácil de detectar. Suponga también que inicialmente se consideran sospechosos la «Acumulación de suciedad», la «Vibración», el «Aumento de la presión diferencial» y el «Ensuciamiento». Si la «Acumulación de suciedad» se modela como un evento OR-AND, la ausencia de «Vibración» podría llevar a concluir prematuramente que la «Acumulación de suciedad» ya no es verdadera y que los problemas que la causan se han solucionado. Entonces se concluiría que el «Aumento de la presión diferencial» y el «Ensuciamiento» son falsos, porque el evento que los causa es falso. Utilizar un evento OR-OR para la «Acumulación de suciedad» permite que se mantenga la hipótesis de que esta es sospechosa mientras el «Aumento de la presión diferencial» y el «Ensuciamiento» sigan siendo sospechosos. El evento OR-OR utiliza lógica OR en su entrada; por tanto, la «Acumulación de suciedad» es verdadera si una o ambas de sus causas son verdaderas.
### Diapositiva 28
Propagación aguas arriba
Se calcula el valor de un evento OR-OR durante la propagación aguas arriba cuando cambia el valor de un evento desencadenante situado aguas abajo del evento OR-OR.
Se utiliza la lógica OR tradicional para calcular el valor del evento a partir de sus salidas, independientemente del valor del evento desencadenante, de la siguiente manera:
Si hay al menos una salida verdadera, concluir que el evento es verdadero;
De lo contrario, si hay al menos una salida sospechosa, concluir que el evento es sospechoso;
De lo contrario, si hay al menos una salida desconocida, concluir que el evento es desconocido;
En caso contrario, concluir que el evento es falso.
Esta es la única diferencia entre un evento OR-OR y uno OR-AND. El resto del comportamiento del evento OR-OR es idéntico al del evento OR-AND. Este comportamiento permite que un evento OR-OR conserve un valor verdadero o sospechoso a pesar de que una o más de sus salidas sean falsas, lo que lo distingue de un evento OR-AND.
### Diapositiva 29
Propagación aguas abajo
Cuando un evento OR-N/M con una Fracción de 0,0 pasa a estar especificado como verdadero o se infiere como verdadero aguas abajo, la aplicación de lógica OR en su salida exige que cualquiera de sus efectos sea verdadero. Por ello, se intenta propagar el estado sospechoso a cada efecto.
Cuando un evento OR-OR pasa a estar especificado como verdadero o se infiere como verdadero aguas abajo, al aplicar lógica AND se intenta que todos los efectos del evento sean verdaderos, incluso si algunos ya lo son. En otras palabras, el evento OR-OR se comporta como un evento OR-AND cuando su valor se especifica como verdadero o se infiere como verdadero aguas abajo.
### Diapositiva 30
ACTIVIDAD GRUPALCrear Lógica con Grafos Dirigidos
Crear grafos de eventos aplicados a vuestros sistemas de cada grupo, que permitan resolver posibles problemas con la operación o estado de salud del sistema.
Crear una presentación y presentar.
### Diapositiva 31
Gracias
